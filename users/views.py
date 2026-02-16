import secrets

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm, UserUpdateForm
from users.models import User


class UserDetailView(DetailView):
    model = User
    template_name = "users/profile.html"

    def get_object(self, queryset=None):
        return self.request.user


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, прейди по ссылке для подтверждения почты{url}.",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):
    try:
        user = User.objects.get(token=token)
        user.is_active = True
        user.token = None
        user.save()
        return render(request, "users/registration/email_confirm.html")
    except User.DoesNotExist:
        messages.error(request, "Токен не найден или уже использован. Пожалуйста, зарегистрируйтесь заново.")
        return redirect(reverse("users:register"))


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


class UserDeleteView(DeleteView):
    model = User

    def get_object(self, queryset=None):
        return self.request.user



