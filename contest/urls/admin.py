from django.conf.urls import url

from ..views.admin import ContestAnnouncementAPI, ContestAPI, ACMContestHelper, DownloadContestSubmissions, SendContestResultEmailAPI

urlpatterns = [
    url(r"^contest/?$", ContestAPI.as_view(), name="contest_admin_api"),
    url(r"^contest/announcement/?$", ContestAnnouncementAPI.as_view(), name="contest_announcement_admin_api"),
    url(r"^contest/acm_helper/?$", ACMContestHelper.as_view(), name="acm_contest_helper"),
    url(r"^download_submissions/?$", DownloadContestSubmissions.as_view(), name="acm_contest_helper"),
    url(r"^contest/send_results/?$", SendContestResultEmailAPI.as_view(), name="contest_send_results_email_api"),
]
