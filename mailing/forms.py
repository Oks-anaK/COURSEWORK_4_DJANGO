from django import forms
from django.forms import ModelForm

from mailing.models import Mailing, Message, Recipient


class MailingForm(ModelForm):
    start_time = forms.DateTimeField(
        label="Дата и время начала отправки",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"],
        help_text="Укажите дату и время начала отправки.",
    )

    end_time = forms.DateTimeField(
        label="Дата и время окончания отправки",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"],
        help_text="Укажите дату и время окончания отправки.",
    )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            from django.utils import timezone

            if start_time < timezone.now():
                raise forms.ValidationError(
                    "Дата и время начала не может быть в прошлом."
                )

            if start_time >= end_time:
                raise forms.ValidationError(
                    "Дата и время начала должна быть раньше даты окончания."
                )

        return cleaned_data

    class Meta:
        model = Mailing
        fields = "__all__"
        exclude = ["owner", "status"]


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = "__all__"
        exclude = ["owner"]  # Владелец устанавливается автоматически в view


class RecipientForm(ModelForm):
    class Meta:
        model = Recipient
        fields = "__all__"
        exclude = ["owner"]  # Владелец устанавливается автоматически в view
