import random
from django.db.models import Q, Count
from utils.api import APIView
from account.decorators import check_contest_permission
from ..models import ProblemTag, Problem, ProblemRuleType
from ..serializers import ProblemSerializer, TagSerializer, ProblemSafeSerializer
from contest.models import ContestRuleType


class ProblemTagAPI(APIView):
    def get(self, request):
        qs = ProblemTag.objects
        keyword = request.GET.get("keyword")
        if keyword:
            qs = ProblemTag.objects.filter(name__icontains=keyword)
        tags = qs.annotate(problem_count=Count("problem")).filter(problem_count__gt=0)
        return self.success(TagSerializer(tags, many=True).data)


class PickOneAPI(APIView):
    def get(self, request):
        problems = Problem.objects.filter(contest_id__isnull=True, visible=True)
        count = problems.count()
        if count == 0:
            return self.error("No problem to pick")
        return self.success(problems[random.randint(0, count - 1)]._id)


class ProblemAPI(APIView):
    @staticmethod
    def _add_problem_status(request, queryset_values):
        if request.user.is_authenticated:
            profile = request.user.userprofile
            acm_problems_status = profile.acm_problems_status.get("problems", {})
            oi_problems_status = profile.oi_problems_status.get("problems", {})
            # paginate data
            results = queryset_values.get("results")
            if results is not None:
                problems = results
            else:
                problems = [queryset_values, ]
            for problem in problems:
                if problem["rule_type"] == ProblemRuleType.ACM:
                    problem["my_status"] = acm_problems_status.get(str(problem["id"]), {}).get("status")
                else:
                    problem["my_status"] = oi_problems_status.get(str(problem["id"]), {}).get("status")

    def get(self, request):
        # 问题详情页
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = Problem.objects.select_related("created_by") \
                    .get(_id=problem_id, contest_id__isnull=True, visible=True)
                problem_data = ProblemSerializer(problem).data
                self._add_problem_status(request, problem_data)
                return self.success(problem_data)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist")

        limit = request.GET.get("limit")
        if not limit:
            return self.error("Limit is needed")

        problems = Problem.objects.select_related("created_by").filter(contest_id__isnull=True, visible=True)
        # 按照标签筛选
        tag_text = request.GET.get("tag")
        if tag_text:
            problems = problems.filter(tags__name=tag_text)

        # 搜索的情况
        keyword = request.GET.get("keyword", "").strip()
        if keyword:
            problems = problems.filter(Q(title__icontains=keyword) | Q(_id__icontains=keyword))

        # 难度筛选
        difficulty = request.GET.get("difficulty")
        if difficulty:
            problems = problems.filter(difficulty=difficulty)
        # 根据profile 为做过的题目添加标记
        data = self.paginate_data(request, problems, ProblemSerializer)
        self._add_problem_status(request, data)
        return self.success(data)


class ContestProblemAPI(APIView):
    def _add_problem_status(self, request, queryset_values):
        if request.user.is_authenticated:
            profile = request.user.userprofile
            if self.contest.rule_type == ContestRuleType.ACM:
                problems_status = profile.acm_problems_status.get("contest_problems", {})
            else:
                problems_status = profile.oi_problems_status.get("contest_problems", {})
            for problem in queryset_values:
                problem["my_status"] = problems_status.get(str(problem["id"]), {}).get("status")

    @check_contest_permission(check_type="problems")
    def get(self, request):
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = Problem.objects.select_related("created_by").get(_id=problem_id,
                                                                           contest=self.contest,
                                                                           visible=True)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist.")
            if self.contest.problem_details_permission(request.user):
                problem_data = ProblemSerializer(problem).data
                self._add_problem_status(request, [problem_data, ])
            else:
                problem_data = ProblemSafeSerializer(problem).data
            return self.success(problem_data)

        contest_problems = Problem.objects.select_related("created_by").filter(contest=self.contest, visible=True)
        if self.contest.problem_details_permission(request.user):
            data = ProblemSerializer(contest_problems, many=True).data
            self._add_problem_status(request, data)
        else:
            data = ProblemSafeSerializer(contest_problems, many=True).data
        return self.success(data)


class ProblemHintAPI(APIView):
    def post(self, request):
        data = request.data
        problem_id = data.get("problem_id")
        code = data.get("code")
        language = data.get("language")
        question = data.get("question")
        
        if not problem_id or not code:
            return self.error("Problem ID and code are required")

        try:
            problem = Problem.objects.get(_id=problem_id, visible=True)
        except Problem.DoesNotExist:
            return self.error("Problem does not exist")

        import google.generativeai as genai
        from django.conf import settings

        if not settings.GEMINI_API_KEY:
            return self.error("AI service is not configured")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        You are an expert coding tutor. A student is working on a competitive programming problem.
        
        Problem Title: {problem.title}
        Problem Description: {problem.description}
        Input Description: {problem.input_description}
        Output Description: {problem.output_description}
        
        Student's Code ({language}):
        ```
        {code}
        ```
        
        Student's Question/Context: {question if question else "I'm stuck, please give me a hint without revealing the full solution."}
        
        Please provide a helpful, encouraging hint. Do NOT write the full correct code. Focus on logic, edge cases, or syntax errors if present. Keep it concise (under 200 words).
        """

        try:
            response = model.generate_content(prompt)
            return self.success(response.text)
        except Exception as e:
            return self.error(str(e))


class DailyChallengeAPI(APIView):
    def get(self, request):
        from django.utils import timezone
        from ..models import DailyChallenge
        import random
        
        today = timezone.now().date()
        
        try:
            challenge = DailyChallenge.objects.get(date=today)
        except DailyChallenge.DoesNotExist:
            # Pick a random public problem that is not in a contest
            problems = Problem.objects.filter(contest_id__isnull=True, visible=True)
            count = problems.count()
            if count == 0:
                return self.error("No problems available for daily challenge")
            
            random_problem = problems[random.randint(0, count - 1)]
            challenge = DailyChallenge.objects.create(problem=random_problem, date=today)
            
        data = {
            "problem_id": challenge.problem._id,
            "title": challenge.problem.title,
            "difficulty": challenge.problem.difficulty,
            "date": str(challenge.date)
        }
        return self.success(data)
