from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import MailingForm, MessageForm, RecipientForm, AttemptsMailingForm
from .models import Mailing, Message, Recipient, AttemptsMailing


class MailingListView(ListView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Обновляем статусы для всех рассылок в списке
        for mailing in queryset:
            mailing.update_status()
        return queryset


class MailingDetailView(DetailView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # пересчёт и сохранение статуса
        return obj


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_create.html'


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_update.html'


class MailingDeleteView(DeleteView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_delete.html'


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_create.html'


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_update.html'


class MessageListView(ListView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_list.html'


class MessageDetailView(DetailView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_detail.html'


class MessageDeleteView(DeleteView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_delete.html'


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_create.html'


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_update.html'


class RecipientListView(ListView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_list.html'


class RecipientDetailView(DetailView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_detail.html'


class RecipientDeleteView(DeleteView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_delete.html'


class AttemptsMailingCreateView(CreateView):
    model = AttemptsMailing
    form_class = AttemptsMailingForm
    template_name = 'mailing/attempts_create.html'


class AttemptsMailingUpdateView(UpdateView):
    model = AttemptsMailing
    form_class = AttemptsMailingForm
    template_name = 'mailing/attempts_update.html'


class AttemptsMailingDeleteView(DeleteView):
    model = AttemptsMailing
    form_class = AttemptsMailingForm
    template_name = 'mailing/attempts_delete.html'


class AttemptsMailingListView(ListView):
    model = AttemptsMailing
    form_class = AttemptsMailingForm
    template_name = 'mailing/attempts_list.html'


class AttemptsMailingDetailView(DetailView):
    model = AttemptsMailing
    form_class = AttemptsMailingForm
    template_name = 'mailing/attempts_detail.html'
