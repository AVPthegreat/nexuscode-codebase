from django.conf.urls import url
from .views import DiscussionListCreateAPI

urlpatterns = [
    url(r"^discussion/?$", DiscussionListCreateAPI.as_view(), name="discussion_list_create_api"),
]
