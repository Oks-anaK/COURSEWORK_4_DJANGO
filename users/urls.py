from django.contrib.auth.views import (LoginView, LogoutView, PasswordResetCompleteView, PasswordResetConfirmView,
                                       PasswordResetDoneView, PasswordResetView)
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.views import (UserBlockView, UserCreateView, UserDeleteView, UserDetailView, UserListView, UserUpdateView,
                         email_verification)

app_name = UsersConfig.name

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(template_name="users/registration/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("email-confirm/<str:token>/", email_verification, name="email_confirm"),
    path("profile/", UserDetailView.as_view(), name="profile"),
    path("profile/update/", UserUpdateView.as_view(), name="profile_update"),
    path("profile/delete/", UserDeleteView.as_view(), name="profile_delete"),
    path("list/", UserListView.as_view(), name="user_list"),
    path("<int:pk>/block/", UserBlockView.as_view(), name="user_block"),
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="users/registration/password_reset_form.html",
            email_template_name="users/registration/password_reset_email.html",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(
            template_name="users/registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/registration/password_reset_form.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name="users/registration/password_reset_done.html"
        ),
        name="password_reset_complete",
    ),
]
