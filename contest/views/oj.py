import io

import xlsxwriter
from django.http import HttpResponse
from django.utils.timezone import now
from django.core.cache import cache

from problem.models import Problem
from utils.api import APIView, validate_serializer
from utils.constants import CacheKey, CONTEST_PASSWORD_SESSION_KEY
from utils.shortcuts import datetime2str, check_is_id
from account.models import AdminType
from account.decorators import login_required, check_contest_permission, check_contest_password

from utils.constants import ContestRuleType, ContestStatus
from ..models import ContestAnnouncement, Contest, OIContestRank, ACMContestRank, ContestAttempt, ContestAttemptProblemStat
from ..serializers import ContestAttemptSerializer
from ..serializers import ContestAnnouncementSerializer
from ..serializers import ContestSerializer, ContestPasswordVerifySerializer
from ..serializers import OIContestRankSerializer, ACMContestRankSerializer


class ContestAnnouncementListAPI(APIView):
    @check_contest_permission(check_type="announcements")
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error("Invalid parameter, contest_id is required")
        data = ContestAnnouncement.objects.select_related("created_by").filter(contest_id=contest_id, visible=True)
        max_id = request.GET.get("max_id")
        if max_id:
            data = data.filter(id__gt=max_id)
        return self.success(ContestAnnouncementSerializer(data, many=True).data)


class ContestAPI(APIView):
    def get(self, request):
        id = request.GET.get("id")
        if not id or not check_is_id(id):
            return self.error("Invalid parameter, id is required")
        try:
            contest = Contest.objects.get(id=id, visible=True)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        data = ContestSerializer(contest).data
        data["now"] = datetime2str(now())
        return self.success(data)


class ContestListAPI(APIView):
    def get(self, request):
        contests = Contest.objects.select_related("created_by").filter(visible=True)
        keyword = request.GET.get("keyword")
        rule_type = request.GET.get("rule_type")
        status = request.GET.get("status")
        if keyword:
            contests = contests.filter(title__contains=keyword)
        if rule_type:
            contests = contests.filter(rule_type=rule_type)
        if status:
            cur = now()
            if status == ContestStatus.CONTEST_NOT_START:
                contests = contests.filter(start_time__gt=cur)
            elif status == ContestStatus.CONTEST_ENDED:
                contests = contests.filter(end_time__lt=cur)
            else:
                contests = contests.filter(start_time__lte=cur, end_time__gte=cur)
        return self.success(self.paginate_data(request, contests, ContestSerializer))


class ContestPasswordVerifyAPI(APIView):
    @validate_serializer(ContestPasswordVerifySerializer)
    @login_required
    def post(self, request):
        data = request.data
        try:
            contest = Contest.objects.get(id=data["contest_id"], visible=True, password__isnull=False)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        if not check_contest_password(data["password"], contest.password):
            return self.error("Wrong password or password expired")

        # password verify OK.
        if CONTEST_PASSWORD_SESSION_KEY not in request.session:
            request.session[CONTEST_PASSWORD_SESSION_KEY] = {}
        request.session[CONTEST_PASSWORD_SESSION_KEY][contest.id] = data["password"]
        # https://docs.djangoproject.com/en/dev/topics/http/sessions/#when-sessions-are-saved
        request.session.modified = True
        return self.success(True)


class ContestAccessAPI(APIView):
    @login_required
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error()
        try:
            contest = Contest.objects.get(id=contest_id, visible=True, password__isnull=False)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        session_pass = request.session.get(CONTEST_PASSWORD_SESSION_KEY, {}).get(contest.id)
        return self.success({"access": check_contest_password(session_pass, contest.password)})


class ContestRankAPI(APIView):
    def get_rank(self):
        if self.contest.rule_type == ContestRuleType.ACM:
            return ACMContestRank.objects.filter(contest=self.contest,
                                                 user__admin_type=AdminType.REGULAR_USER,
                                                 user__is_disabled=False).\
                select_related("user").order_by("-accepted_number", "total_time")
        else:
            return OIContestRank.objects.filter(contest=self.contest,
                                                user__admin_type=AdminType.REGULAR_USER,
                                                user__is_disabled=False). \
                select_related("user").order_by("-total_score")

    def column_string(self, n):
        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string

    @check_contest_permission(check_type="ranks")
    def get(self, request):
        download_csv = request.GET.get("download_csv")
        force_refresh = request.GET.get("force_refresh")
        is_contest_admin = request.user.is_authenticated and request.user.is_contest_admin(self.contest)
        if self.contest.rule_type == ContestRuleType.OI:
            serializer = OIContestRankSerializer
        else:
            serializer = ACMContestRankSerializer

        if force_refresh == "1" and is_contest_admin:
            qs = self.get_rank()
        else:
            cache_key = f"{CacheKey.contest_rank_cache}:{self.contest.id}"
            qs = cache.get(cache_key)
            if not qs:
                qs = self.get_rank()
                cache.set(cache_key, qs)

        if download_csv:
            data = serializer(qs, many=True, is_contest_admin=is_contest_admin).data
            contest_problems = Problem.objects.filter(contest=self.contest, visible=True).order_by("_id")
            problem_ids = [item.id for item in contest_problems]

            f = io.BytesIO()
            workbook = xlsxwriter.Workbook(f)
            worksheet = workbook.add_worksheet()
            worksheet.write("A1", "User ID")
            worksheet.write("B1", "Username")
            worksheet.write("C1", "Real Name")
            if self.contest.rule_type == ContestRuleType.OI:
                worksheet.write("D1", "Total Score")
                for item in range(contest_problems.count()):
                    worksheet.write(self.column_string(5 + item) + "1", f"{contest_problems[item].title}")
                for index, item in enumerate(data):
                    worksheet.write_string(index + 1, 0, str(item["user"]["id"]))
                    worksheet.write_string(index + 1, 1, item["user"]["username"])
                    worksheet.write_string(index + 1, 2, item["user"]["real_name"] or "")
                    worksheet.write_string(index + 1, 3, str(item["total_score"]))
                    for k, v in item["submission_info"].items():
                        worksheet.write_string(index + 1, 4 + problem_ids.index(int(k)), str(v))
            else:
                worksheet.write("D1", "AC")
                worksheet.write("E1", "Total Submission")
                worksheet.write("F1", "Total Time")
                for item in range(contest_problems.count()):
                    worksheet.write(self.column_string(7 + item) + "1", f"{contest_problems[item].title}")

                for index, item in enumerate(data):
                    worksheet.write_string(index + 1, 0, str(item["user"]["id"]))
                    worksheet.write_string(index + 1, 1, item["user"]["username"])
                    worksheet.write_string(index + 1, 2, item["user"]["real_name"] or "")
                    worksheet.write_string(index + 1, 3, str(item["accepted_number"]))
                    worksheet.write_string(index + 1, 4, str(item["submission_number"]))
                    worksheet.write_string(index + 1, 5, str(item["total_time"]))
                    for k, v in item["submission_info"].items():
                        worksheet.write_string(index + 1, 6 + problem_ids.index(int(k)), str(v["is_ac"]))

            workbook.close()
            f.seek(0)
            response = HttpResponse(f.read())
            response["Content-Disposition"] = f"attachment; filename=content-{self.contest.id}-rank.xlsx"
            response["Content-Type"] = "application/xlsx"
            return response

        page_qs = self.paginate_data(request, qs)
        page_qs["results"] = serializer(page_qs["results"], many=True, is_contest_admin=is_contest_admin).data
        return self.success(page_qs)


class ContestStartAPI(APIView):
    @login_required
    def post(self, request):
        contest_id = request.data.get('contest_id')
        if not contest_id:
            return self.error('contest_id required')
        try:
            contest = Contest.objects.get(id=contest_id, visible=True)
        except Contest.DoesNotExist:
            return self.error('Contest not found')
        attempt_no = 1
        existing = ContestAttempt.objects.filter(user=request.user, contest=contest).order_by('-attempt_no').first()
        if existing:
            attempt_no = existing.attempt_no + 1 if existing.started and existing.finished_at else existing.attempt_no
        attempt, _ = ContestAttempt.objects.get_or_create(user=request.user, contest=contest, attempt_no=attempt_no)
        if not attempt.started:
            attempt.started = True
            attempt.started_at = now()
            attempt.save(update_fields=['started', 'started_at'])
        # preload problem stats rows
        problems = Problem.objects.filter(contest=contest, visible=True).order_by('_id')
        for p in problems:
            ContestAttemptProblemStat.objects.get_or_create(attempt=attempt, problem=p)
        return self.success(ContestAttemptSerializer(attempt).data)


class ContestStopAPI(APIView):
    @login_required
    def post(self, request):
        attempt_id = request.data.get('attempt_id')
        if not attempt_id:
            return self.error('attempt_id required')
        try:
            attempt = ContestAttempt.objects.select_related('contest').get(id=attempt_id, user=request.user)
        except ContestAttempt.DoesNotExist:
            return self.error('Attempt not found')
        if not attempt.finished_at:
            attempt.finished_at = now()
            attempt.save(update_fields=['finished_at'])
        return self.success(ContestAttemptSerializer(attempt).data)


class ContestProctorAPI(APIView):
    @login_required
    def post(self, request):
        attempt_id = request.data.get('attempt_id')
        if not attempt_id:
            return self.error('attempt_id required')
        try:
            attempt = ContestAttempt.objects.get(id=attempt_id, user=request.user)
        except ContestAttempt.DoesNotExist:
            return self.error('Attempt not found')
        
        action = request.data.get('action')
        violation_count = request.data.get('violation_count', 0)
        timestamp = request.data.get('timestamp', datetime2str(now()))
        
        if action == 'fullscreen_exit':
            # Increment count
            attempt.fullscreen_exit_count += 1
            
            # Record detailed violation with timestamp for admin monitoring
            violations = attempt.violations if attempt.violations else []
            violations.append({
                'type': 'fullscreen_exit',
                'timestamp': timestamp,
                'violation_number': attempt.fullscreen_exit_count,
                'total_violations': violation_count,
                'user_id': request.user.id,
                'username': request.user.username,
                'contest_id': attempt.contest_id,
                'severity': 'high' if attempt.fullscreen_exit_count >= 3 else 'medium'
            })
            attempt.violations = violations
            attempt.save(update_fields=['fullscreen_exit_count', 'violations'])
            
            # Log for admin real-time monitoring
            import logging
            logger = logging.getLogger('contest_proctoring')
            logger.warning(
                f'PROCTORING VIOLATION - User: {request.user.username} (ID: {request.user.id}) | '
                f'Contest: {attempt.contest_id} | Action: fullscreen_exit | '
                f'Count: {attempt.fullscreen_exit_count}/{violation_count} | '
                f'Timestamp: {timestamp}'
            )
        
        # Handle other violation types
        violation = request.data.get('violation')
        if violation:
            violations = attempt.violations if attempt.violations else []
            violations.append({
                'type': violation,
                'timestamp': timestamp,
                'user_id': request.user.id,
                'username': request.user.username
            })
            attempt.violations = violations
            attempt.save(update_fields=['violations'])
        
        return self.success({
            'fullscreen_exit_count': attempt.fullscreen_exit_count,
            'violations': attempt.violations,
            'message': f'Violation recorded. Count: {attempt.fullscreen_exit_count}/5'
        })


class ContestUserOverviewAPI(APIView):
    @login_required
    def get(self, request):
        contest_id = request.GET.get('contest_id')
        if not contest_id:
            return self.error('contest_id required')
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return self.error('Contest not found')
        attempt = ContestAttempt.objects.filter(user=request.user, contest=contest).order_by('-attempt_no').first()
        if not attempt:
            return self.success(None)
        # aggregate latest submission stats for each problem
        stats_map = {ps.problem_id: ps for ps in attempt.problem_stats.all()}
        submissions = Submission.objects.filter(user_id=request.user.id, contest=contest).order_by('create_time')
        for sub in submissions:
            ps = stats_map.get(sub.problem_id)
            if not ps:
                continue
            ps.attempts += 1
            # derive passed cases/total cases
            testcase_list = []
            if sub.info and isinstance(sub.info.get('data'), list):
                testcase_list = sub.info['data']
            total_cases = len(testcase_list)
            passed_cases = sum(1 for tc in testcase_list if tc.get('result') == 0)
            # choose best result & score
            ps.total_cases = max(ps.total_cases, total_cases)
            ps.passed_cases = max(ps.passed_cases, passed_cases)
            # status result mapping: prefer AC (0), else PARTIALLY_ACCEPTED (8), else keep previous
            if sub.result == 0:
                ps.best_result = 0
            elif passed_cases > 0 and passed_cases < total_cases:
                if ps.best_result != 0:  # don't overwrite AC
                    ps.best_result = 8
            else:
                if ps.best_result not in (0, 8):
                    ps.best_result = sub.result
            # score compute
            score = 0
            if total_cases > 0:
                score = int(100 * passed_cases / total_cases)
            ps.score = max(ps.score, score)
            ps.save(update_fields=['attempts', 'best_result', 'passed_cases', 'total_cases', 'score'])
        return self.success(ContestAttemptSerializer(attempt).data)


class ContestUserAttemptsListAPI(APIView):
    @login_required
    def get(self, request):
        attempts = ContestAttempt.objects.filter(user=request.user).select_related('contest').order_by('-started_at')[:200]
        return self.success(ContestAttemptSerializer(attempts, many=True).data)


class ContestProctoringMonitorAPI(APIView):
    """
    Admin endpoint to monitor proctoring violations in real-time
    Returns all active contest attempts with violation details
    """
    @login_required
    def get(self, request):
        # Check if user is admin
        if not request.user.is_authenticated or request.user.admin_type not in ['Super Admin', 'Admin']:
            return self.error('Permission denied. Admin access required.')
        
        contest_id = request.GET.get('contest_id')
        
        # Get all active attempts (started but not finished)
        query = ContestAttempt.objects.select_related('user', 'contest').filter(started=True)
        
        if contest_id:
            query = query.filter(contest_id=contest_id)
        
        # Order by most recent violations first
        attempts = query.order_by('-fullscreen_exit_count', '-started_at')[:100]
        
        violation_data = []
        for attempt in attempts:
            violation_data.append({
                'attempt_id': attempt.id,
                'user_id': attempt.user.id,
                'username': attempt.user.username,
                'real_name': attempt.user.real_name if hasattr(attempt.user, 'real_name') else '',
                'contest_id': attempt.contest.id,
                'contest_title': attempt.contest.title,
                'started_at': attempt.started_at,
                'finished_at': attempt.finished_at,
                'is_active': attempt.started and not attempt.finished_at,
                'fullscreen_exit_count': attempt.fullscreen_exit_count,
                'violations': attempt.violations if attempt.violations else [],
                'total_violations': len(attempt.violations) if attempt.violations else 0,
                'severity': 'critical' if attempt.fullscreen_exit_count >= 5 else 'high' if attempt.fullscreen_exit_count >= 3 else 'medium' if attempt.fullscreen_exit_count > 0 else 'low',
                'status': 'auto_submitted' if attempt.fullscreen_exit_count >= 5 else 'active' if attempt.started and not attempt.finished_at else 'completed'
            })
        
        return self.success({
            'total_monitored': len(violation_data),
            'active_attempts': sum(1 for v in violation_data if v['is_active']),
            'high_risk_users': sum(1 for v in violation_data if v['fullscreen_exit_count'] >= 3),
            'violations': violation_data
        })
