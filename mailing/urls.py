from django.urls import path

from mailing.apps import MailingConfig
from mailing.views import (HomeView, MailingCreateView,
                           MailingDeleteView, MailingDetailView,
                           MailingListView, MailingUpdateView,
                           MessageCreateView, MessageDeleteView,
                           MessageDetailView, MessageUpdateView,
                           RecipientCreateView, RecipientDeleteView,
                           RecipientDetailView, RecipientListView,
                           RecipientUpdateView)

app_name = MailingConfig.name

urlpatterns = [
    # Main_page
    path("", HomeView.as_view(), name="home"),
    # Mailings
    path("list/", MailingListView.as_view(), name="mailing_list"),
    path("<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("create/", MailingCreateView.as_view(), name="mailing_create"),
    path("<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    # Messages
    path("messages/", MessageCreateView.as_view(), name="message_list"),
    path(
        "messages/<int:pk>/",
        MessageDetailView.as_view(),
        name="message_detail",
    ),
    path(
        "messages/<int:pk>/delete/",
        MessageDeleteView.as_view(),
        name="message_delete",
    ),
    path(
        "messages/<int:pk>/update/",
        MessageUpdateView.as_view(),
        name="message_update",
    ),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    # Recipients
    path("recipients/", RecipientListView.as_view(), name="recipient_list"),
    path(
        "recipients/create/",
        RecipientCreateView.as_view(),
        name="recipient_create",
    ),
    path(
        "recipients/<int:pk>/update/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "recipients/<int:pk>/delete/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    path(
        "recipients/<int:pk>/",
        RecipientDetailView.as_view(),
        name="recipient_detail",
    ),
]
