from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, BooleanField, CheckboxInput, FileInput

from users.models import User


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField) or isinstance(
                field.widget, CheckboxInput
            ):
                field.widget.attrs["class"] = "form-check-input"

            elif isinstance(field.widget, FileInput):
                field.widget.attrs["class"] = "form-control"

            else:
                field.widget.attrs["class"] = "form-control"
                # Используем help_text как placeholder для текстовых полей
                if field.help_text:
                    field.widget.attrs["placeholder"] = field.help_text
                    field.help_text = ""


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")


class UserUpdateForm(StyleFormMixin, ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "avatar")
