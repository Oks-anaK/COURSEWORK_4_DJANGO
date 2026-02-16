from django.forms import ModelForm

from mailing.models import Attempt, Mailing, Message, Recipient


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
