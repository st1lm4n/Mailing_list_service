from django.contrib.auth import views as auth_views
from django.urls import path

from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("recipients/", RecipientListView.as_view(), name="recipient_list"),
    path("recipient/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path("recipient/update/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipient/detail/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("recipient/delete/", RecipientDeleteView.as_view(), name="recipient_delete"),
    path("massages/", MassageListView.as_view(), name="message_list"),
    path("massage/create/", MessageCreateView.as_view(), name="message_create"),
    path("massage/update/", MessageUpdateView.as_view(), name="message_update"),
    path("massage/detail/", MessageDetailView.as_view(), name="message_detail"),
    path("massage/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailing/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/update/", MailingCreateView.as_view(), name="mailing_update"),
    path("mailing/detail/", MailingCreateView.as_view(), name="mailing_detail"),
    path("mailing/delete/", MailingCreateView.as_view(), name="mailing_delete"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
