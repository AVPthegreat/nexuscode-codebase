from utils.api import APIView
from account.decorators import login_required
from submission.models import Submission, JudgeStatus
from ..models import Problem
from contest.models import Contest, ContestStatus


class ProblemEditorialAPI(APIView):
    @login_required
    def get(self, request):
        """
        Get problem editorial (only if user has solved it or contest has ended)
        """
        problem_id = request.GET.get("problem_id")
        if not problem_id:
            return self.error("Problem ID is required")
        
        try:
            problem = Problem.objects.get(id=problem_id, visible=True)
        except Problem.DoesNotExist:
            return self.error("Problem does not exist")
        
        # Check if editorial exists
        if not problem.editorial:
            return self.error("Editorial not available for this problem")
        
        # Check permission: user must have solved the problem OR contest has ended
        can_view = False
        
        # For contest problems, check if contest has ended
        if problem.contest_id:
            contest = Contest.objects.get(id=problem.contest_id)
            if contest.status == ContestStatus.CONTEST_ENDED:
                can_view = True
        
        # Check if user has an accepted submission for this problem
        if not can_view:
            has_accepted = Submission.objects.filter(
                user_id=request.user.id,
                problem_id=problem.id,
                result=JudgeStatus.ACCEPTED
            ).exists()
            
            if has_accepted:
                can_view = True
        
        # Admins can always view
        if request.user.is_super_admin() or (problem.contest_id and request.user.is_contest_admin(Contest.objects.get(id=problem.contest_id))):
            can_view = True
        
        if not can_view:
            return self.error("You must solve this problem or wait for the contest to end to view the editorial")
        
        return self.success({
            "editorial": problem.editorial,
            "problem_id": problem.id,
            "problem_title": problem.title
        })
