from django.db import models
from django.conf import settings
from problem.models import Problem

class DiscussionMessage(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=32)
    message = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'discussion_message'
        ordering = ('-create_time',)
