from django.views.generic import ListView, DetailView
from .models import Mailing


class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Обновляем статусы для всех рассылок в списке
        for mailing in queryset:
            mailing.update_status()
        return queryset


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # пересчёт и сохранение статуса
        return obj
