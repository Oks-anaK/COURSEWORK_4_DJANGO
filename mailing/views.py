from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Attempt, Mailing, Message, Recipient


class HomeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        now = timezone.now()
        context = super().get_context_data(**kwargs)
        context["attempts_count"] = Mailing.objects.all().count()
        context["attempts_active"] = Mailing.objects.filter(
            status='Запущена', start_time__lte=now, end_time__gte=now
        ).count()
        context["recipients_unique"] = Recipient.objects.distinct().count()
        return context


class MailingListView(ListView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Обновляем статусы для всех рассылок в списке
        for mailing in queryset:
            mailing.update_status()
        return queryset


class MailingDetailView(DetailView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # пересчёт и сохранение статуса
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = self.object.attempts.all().order_by("-attempt_time")
        return context


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_form.html"

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.owner = self.request.user
        mailing.save()
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_form.html"


class MailingDeleteView(DeleteView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/generic_confirm_delete.html"


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/generic_form.html"

    def form_valid(self, form):
        message = form.save(commit=False)
        message.owner = self.request.user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/generic_form.html"


class MessageListView(ListView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/generic_list.html"


class MessageDetailView(DetailView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_detail.html"


class MessageDeleteView(DeleteView):
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


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/generic_form.html"


class RecipientListView(ListView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/generic_list.html"


class RecipientDetailView(DetailView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_detail.html"


class RecipientDeleteView(DeleteView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/generic_confirm_delete.html"
