from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.cache import patch_response_headers
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Attempt, Mailing, Message, Recipient


class OwnerOrManagerMixin(LoginRequiredMixin):
    """Mixin для проверки прав доступа - только владелец может редактировать/удалять."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        obj = self.get_object()
        user = request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        if not is_manager and obj.owner != user:
            raise PermissionDenied("У вас нет прав для выполнения этого действия.")

        return super().dispatch(request, *args, **kwargs)


class HomeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        stats = cache.get("home_stats")
        if not stats:
            stats = {
                "attempts_count": Mailing.objects.all().count(),
                "attempts_active": Mailing.objects.filter(
                    status="Запущена", start_time__lte=now, end_time__gte=now
                ).count(),
                "recipients_unique": Recipient.objects.distinct().count(),
            }
            cache.set("home_stats", stats, 300)  # 5 минут

        context.update(stats)
        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == "GET":
            patch_response_headers(response, cache_timeout=300)
        return response


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_name"] = "mailing:mailing"
        context["create_url"] = "mailing:mailing_create"
        return context

    def dispatch(self, request, *args, **kwargs):
        # Исправляем NULL статусы до загрузки queryset
        try:
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE mailing_mailing SET status = 'Создана' WHERE status IS NULL"
                )
        except Exception:
            pass

        try:
            response = super().dispatch(request, *args, **kwargs)
        except Exception as e:
            from django.db import connection

            if isinstance(e, IntegrityError) and "status" in str(e):
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE mailing_mailing SET status = 'Создана' WHERE status IS NULL"
                    )
                response = super().dispatch(request, *args, **kwargs)
            else:
                raise

        if request.method == "GET":
            patch_response_headers(response, cache_timeout=600)  # 10 минут
        return response

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        if not is_manager:
            queryset = queryset.filter(owner=user)

        # Обновляем статусы
        for mailing in queryset:
            mailing.update_status()
        return queryset


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        if not is_manager:
            queryset = queryset.filter(owner=user)

        return queryset

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Исправляем NULL статус, если есть
        if not obj.status:
            obj.status = "Создана"
            obj.save(update_fields=["status"])
        obj.update_status()  # пересчёт и сохранение статуса
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = self.object.attempts.all().order_by("-attempt_time")
        context["is_manager"] = self.request.user.groups.filter(
            name="Менеджеры"
        ).exists()
        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == "GET":
            patch_response_headers(response, cache_timeout=300)  # 5 минут
        return response


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        if is_manager:
            form.fields["recipients"].queryset = Recipient.objects.all().order_by(
                "username", "email"
            )
            form.fields["message"].queryset = Message.objects.all().order_by("subject")
        else:
            form.fields["recipients"].queryset = Recipient.objects.filter(
                owner=user
            ).order_by("username", "email")
            form.fields["message"].queryset = Message.objects.filter(
                owner=user
            ).order_by("subject")

        form.fields["recipients"].widget.attrs.update(
            {"class": "form-control", "size": "10"}
        )
        return form

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.owner = self.request.user
        if not mailing.status:
            mailing.status = "Создана"
        mailing.save()
        form.save_m2m()
        messages.success(self.request, "Рассылка успешно сохранена")
        return redirect(self.success_url)


class MailingUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        if is_manager:
            form.fields["recipients"].queryset = Recipient.objects.all().order_by(
                "username", "email"
            )
            form.fields["message"].queryset = Message.objects.all().order_by("subject")
        else:
            form.fields["recipients"].queryset = Recipient.objects.filter(
                owner=user
            ).order_by("username", "email")
            form.fields["message"].queryset = Message.objects.filter(
                owner=user
            ).order_by("subject")

        form.fields["recipients"].widget.attrs.update(
            {"class": "form-control", "size": "10"}
        )
        return form

    def form_valid(self, form):
        form.save()
        form.save_m2m()
        messages.success(self.request, "Рассылка успешно обновлена")
        return redirect(self.success_url)


class MailingDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Mailing
    template_name = "mailing/generic_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_name"] = "mailing:mailing"
        return context

    def post(self, request, *args, **kwargs):
        """Обработка удаления через POST"""
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Рассылка успешно удалена")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(request, f"Ошибка при удалении: {str(e)}")
            return redirect(self.success_url)


class MailingDisableView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "mailing.can_disable_mailing"

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = "Завершена"
        mailing.save()
        messages.success(request, f'Рассылка "{mailing}" отключена')
        return redirect("mailing:mailing_detail", pk=pk)


class MailingStartView(LoginRequiredMixin, View):
    """View для запуска рассылки"""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        user = request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        if not is_manager and mailing.owner != user:
            messages.error(request, "У вас нет прав для запуска этой рассылки")
            return redirect("mailing:mailing_detail", pk=pk)

        try:
            from mailing.services import start_mailing

            # force=True, чтобы разрешить ручной запуск
            start_mailing(mailing, force=True)
            mailing.status = "Запущена"
            mailing.save()
            messages.success(request, f'Рассылка "{mailing}" успешно запущена')
        except ValueError as e:
            messages.error(request, f"Ошибка при запуске рассылки: {str(e)}")
        except Exception as e:
            messages.error(request, f"Произошла ошибка: {str(e)}")

        return redirect("mailing:mailing_detail", pk=pk)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/generic_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        message = form.save(commit=False)
        message.owner = self.request.user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/generic_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/generic_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_name"] = "mailing:message"
        context["create_url"] = "mailing:message_create"
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        if not is_manager:
            queryset = queryset.filter(owner=user)

        return queryset

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == "GET":
            patch_response_headers(response, cache_timeout=600)  # 10 минут
        return response


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_detail.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        if not is_manager:
            queryset = queryset.filter(owner=user)

        return queryset


class MessageDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Message
    template_name = "mailing/generic_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_name"] = "mailing:message"
        return context


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/generic_form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def form_valid(self, form):
        recipient = form.save(commit=False)
        recipient.owner = self.request.user
        recipient.save()
        return super().form_valid(form)


class RecipientUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/generic_form.html"
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/generic_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_name"] = "mailing:recipient"
        context["create_url"] = "mailing:recipient_create"
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        if not is_manager:
            queryset = queryset.filter(owner=user)

        return queryset

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == "GET":
            patch_response_headers(response, cache_timeout=600)  # 10 минут
        return response


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_detail.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        if not is_manager:
            queryset = queryset.filter(owner=user)

        return queryset


class RecipientDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Recipient
    template_name = "mailing/generic_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_name"] = "mailing:recipient"
        return context


class StatisticsView(LoginRequiredMixin, TemplateView):
    """Статистика по рассылкам."""

    template_name = "mailing/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_manager = user.groups.filter(name="Менеджеры").exists()

        cache_key = f"statistics_{user.id}_{is_manager}"
        stats = cache.get(cache_key)

        if not stats:
            if is_manager:
                mailings = Mailing.objects.all()
            else:
                mailings = Mailing.objects.filter(owner=user)

            attempts = Attempt.objects.filter(mailing__in=mailings)
            stats = {
                "total_mailings": mailings.count(),
                "successful_attempts": attempts.filter(status="Успешно").count(),
                "failed_attempts": attempts.filter(status="Не успешно").count(),
                "total_attempts": attempts.count(),
                "total_sent_messages": attempts.filter(status="Успешно").count(),
                "is_manager": is_manager,
            }
            cache.set(cache_key, stats, 300)  # 5 минут

        context.update(stats)
        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == "GET":
            patch_response_headers(response, cache_timeout=300)  # 5 минут
        return response
