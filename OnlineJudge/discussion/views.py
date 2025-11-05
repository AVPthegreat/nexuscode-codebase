from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils.api import JSONResponse
from .models import DiscussionMessage
from .serializers import DiscussionMessageSerializer
from problem.models import Problem

class DiscussionListCreateAPI(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        qs = DiscussionMessage.objects.all()
        problem_id = request.GET.get('problem_id')
        if problem_id:
            qs = qs.filter(**{'problem___id': problem_id})
        data = DiscussionMessageSerializer(qs[:200], many=True).data
        return JSONResponse.success(data)

    def post(self, request):
        problem_id = request.data.get('problem_id')
        message = request.data.get('message', '').strip()
        if not problem_id or not message:
            return JSONResponse.error('problem_id and message required')
        try:
            problem = Problem.objects.get(_id=problem_id)
        except Problem.DoesNotExist:
            return JSONResponse.error('Problem does not exist')
        obj = DiscussionMessage.objects.create(problem=problem, user=request.user, username=request.user.username, message=message)
        return JSONResponse.success(DiscussionMessageSerializer(obj).data)
