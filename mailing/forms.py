from django.forms import ModelForm

from mailing.models import Mailing, Message, Recipient, AttemptsMailing


class MailingForm(ModelForm):
    class Meta:
        model = Mailing
        fields = "__all__"


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = "__all__"


class RecipientForm(ModelForm):
    class Meta:
        model = Recipient
        fields = "__all__"


class AttemptsMailingForm(ModelForm):
    class Meta:
        model = AttemptsMailing
        fields = "__all__"
