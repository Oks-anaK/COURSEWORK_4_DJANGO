from django import forms
from django.forms import ModelForm

from mailing.models import Attempt, Mailing, Message, Recipient


class MailingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Настраиваем queryset для поля recipients
        if user:
            is_manager = user.groups.filter(name="Менеджеры").exists()
            if is_manager:
                # Менеджеры видят всех получателей
                self.fields["recipients"].queryset = Recipient.objects.all().order_by(
                    "username", "email"
                )
            else:
                # Обычные пользователи видят только своих получателей
                self.fields["recipients"].queryset = Recipient.objects.filter(
                    owner=user
                ).order_by("username", "email")
            # Улучшаем отображение поля recipients
            self.fields["recipients"].widget.attrs.update(
                {"class": "form-control", "size": "10"}
            )

        # Настраиваем queryset для поля message
        if user:
            is_manager = user.groups.filter(name="Менеджеры").exists()
            if is_manager:
                # Менеджеры видят все сообщения
                self.fields["message"].queryset = Message.objects.all().order_by(
                    "subject"
                )
            else:
                # Обычные пользователи видят только свои сообщения
                self.fields["message"].queryset = Message.objects.filter(
                    owner=user
                ).order_by("subject")

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

    # Поля для создания нового сообщения
    new_message_subject = forms.CharField(
        label="Тема нового сообщения",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Или создайте новое сообщение: введите тему",
            }
        ),
        help_text="Если хотите создать новое сообщение, заполните это поле и поле ниже",
    )

    new_message_body = forms.CharField(
        label="Содержание нового сообщения",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Введите содержимое письма",
            }
        ),
    )

    # Поля для создания нового получателя
    new_recipient_username = forms.CharField(
        label="ФИО нового получателя",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Или создайте нового получателя: введите ФИО",
            }
        ),
        help_text="Если хотите создать нового получателя, заполните все три поля ниже",
    )

    new_recipient_email = forms.EmailField(
        label="Email нового получателя",
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите email"}
        ),
    )

    new_recipient_comment = forms.CharField(
        label="Комментарий для нового получателя",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Введите комментарий",
            }
        ),
    )

    class Meta:
        model = Mailing
        fields = "__all__"
        exclude = [
            "owner",
            "status",
        ]  # Владелец и статус устанавливаются автоматически в view


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
