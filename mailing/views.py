from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.cache import patch_response_headers
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Attempt, Mailing, Message, Recipient


class OwnerOrManagerMixin:
    """Mixin для проверки прав доступа - только владелец может редактировать/удалять"""
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user
        is_manager = user.groups.filter(name='Менеджеры').exists()

        if not is_manager and obj.owner != user:
            raise PermissionDenied("У вас нет прав для выполнения этого действия")
        
        return super().dispatch(request, *args, **kwargs)


class HomeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        stats = cache.get('home_stats')
        if not stats:
            stats = {
                "attempts_count": Mailing.objects.all().count(),
                "attempts_active": Mailing.objects.filter(
                    status='Запущена', start_time__lte=now, end_time__gte=now
                ).count(),
                "recipients_unique": Recipient.objects.distinct().count()
            }
            cache.set('home_stats', stats, 300)  # 5 минут
        
        context.update(stats)
        return context
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == 'GET':
            patch_response_headers(response, cache_timeout=300)
        return response


class MailingListView(ListView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name='Менеджеры').exists()
        
        if not is_manager:
            queryset = queryset.filter(owner=user)
        
        for mailing in queryset:
            mailing.update_status()
        return queryset
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == 'GET':
            patch_response_headers(response, cache_timeout=600)  # 10 минут
        return response


class MailingDetailView(DetailView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name='Менеджеры').exists()

        if not is_manager:
            queryset = queryset.filter(owner=user)
        
        return queryset

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # пересчёт и сохранение статуса
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = self.object.attempts.all().order_by("-attempt_time")
        context["is_manager"] = self.request.user.groups.filter(name='Менеджеры').exists()
        return context
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == 'GET':
            patch_response_headers(response, cache_timeout=300)  # 5 минут
        return response


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_form.html"

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.owner = self.request.user
        mailing.save()
        return super().form_valid(form)


class MailingUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_form.html"


class MailingDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_confirm_delete.html"


class MailingDisableView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'mailing.can_disable_mailing'

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = 'Завершена'
        mailing.save()
        messages.success(request, f'Рассылка "{mailing}" отключена')
        return redirect('mailing:mailing_detail', pk=pk)


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/generic_form.html"

    def form_valid(self, form):
        message = form.save(commit=False)
        message.owner = self.request.user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/generic_form.html"


class MessageListView(ListView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/generic_list.html"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name='Менеджеры').exists()
        
        if not is_manager:
            queryset = queryset.filter(owner=user)
        
        return queryset
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == 'GET':
            patch_response_headers(response, cache_timeout=600)  # 10 минут
        return response


class MessageDetailView(DetailView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_detail.html"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name='Менеджеры').exists()

        if not is_manager:
            queryset = queryset.filter(owner=user)
        
        return queryset


class MessageDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/generic_confirm_delete.html"


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/generic_form.html"

    def form_valid(self, form):
        recipient = form.save(commit=False)
        recipient.owner = self.request.user
        recipient.save()
        return super().form_valid(form)


class RecipientUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/generic_form.html"


class RecipientListView(ListView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/generic_list.html"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name='Менеджеры').exists()
        
        if not is_manager:
            queryset = queryset.filter(owner=user)
        
        return queryset
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == 'GET':
            patch_response_headers(response, cache_timeout=600)  # 10 минут
        return response


class RecipientDetailView(DetailView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_detail.html"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_manager = user.groups.filter(name='Менеджеры').exists()

        if not is_manager:
            queryset = queryset.filter(owner=user)
        
        return queryset


class RecipientDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/generic_confirm_delete.html"


class StatisticsView(LoginRequiredMixin, TemplateView):
    """Статистика по рассылкам"""
    template_name = "mailing/statistics.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_manager = user.groups.filter(name='Менеджеры').exists()

        cache_key = f'statistics_{user.id}_{is_manager}'
        stats = cache.get(cache_key)
        
        if not stats:
            if is_manager:
                mailings = Mailing.objects.all()
            else:
                mailings = Mailing.objects.filter(owner=user)
            
            attempts = Attempt.objects.filter(mailing__in=mailings)
            stats = {
                'total_mailings': mailings.count(),
                'successful_attempts': attempts.filter(status='Успешно').count(),
                'failed_attempts': attempts.filter(status='Не успешно').count(),
                'total_attempts': attempts.count(),
                'total_sent_messages': attempts.filter(status='Успешно').count(),
                'is_manager': is_manager,
            }
            cache.set(cache_key, stats, 300)  # 5 минут
        
        context.update(stats)
        return context
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == 'GET':
            patch_response_headers(response, cache_timeout=300)  # 5 минут
        return response