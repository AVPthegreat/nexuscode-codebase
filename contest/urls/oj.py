from django.conf.urls import url

from ..views.oj import ContestAnnouncementListAPI
from ..views.oj import ContestPasswordVerifyAPI, ContestAccessAPI
from ..views.oj import ContestListAPI, ContestAPI
from ..views.oj import ContestRankAPI
from ..views.oj import ContestStartAPI, ContestStopAPI, ContestProctorAPI, ContestUserOverviewAPI, ContestUserAttemptsListAPI, ContestProctoringMonitorAPI

urlpatterns = [
    url(r"^contests/?$", ContestListAPI.as_view(), name="contest_list_api"),
    url(r"^contest/?$", ContestAPI.as_view(), name="contest_api"),
    url(r"^contest/password/?$", ContestPasswordVerifyAPI.as_view(), name="contest_password_api"),
    url(r"^contest/announcement/?$", ContestAnnouncementListAPI.as_view(), name="contest_announcement_api"),
    url(r"^contest/access/?$", ContestAccessAPI.as_view(), name="contest_access_api"),
    url(r"^contest_rank/?$", ContestRankAPI.as_view(), name="contest_rank_api"),
    url(r"^contest/start/?$", ContestStartAPI.as_view(), name="contest_start_api"),
    url(r"^contest/stop/?$", ContestStopAPI.as_view(), name="contest_stop_api"),
    url(r"^contest/proctor/?$", ContestProctorAPI.as_view(), name="contest_proctor_api"),
    url(r"^contest/user_overview/?$", ContestUserOverviewAPI.as_view(), name="contest_user_overview_api"),
    url(r"^contest/user_attempts/?$", ContestUserAttemptsListAPI.as_view(), name="contest_user_attempts_list_api"),
    url(r"^contest/proctoring_monitor/?$", ContestProctoringMonitorAPI.as_view(), name="contest_proctoring_monitor_api"),
]
