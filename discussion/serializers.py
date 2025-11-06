from rest_framework import serializers
from .models import DiscussionMessage

class DiscussionMessageSerializer(serializers.ModelSerializer):
    problem_id = serializers.CharField(source='problem._id', read_only=True)
    problem_title = serializers.CharField(source='problem.title', read_only=True)

    class Meta:
        model = DiscussionMessage
        fields = ['id', 'problem_id', 'problem_title', 'username', 'message', 'create_time']
