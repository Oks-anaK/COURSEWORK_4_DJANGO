from django.urls import path

from mailing.apps import MailingConfig
from mailing.views import MailingListView, MailingDetailView, MailingCreateView, MailingUpdateView, MailingDeleteView, \
    MessageDetailView

app_name = MailingConfig.name

urlpatterns = [
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailings/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"
    ),
    path(
        "mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path(
        "mailings/message/<int:pk>/",
        MessageDetailView.as_view(),
        name="message_detail",
    ),
]