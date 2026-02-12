from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, ImageField


class User(AbstractUser):
    username = None
    first_name = CharField(
        verbose_name="first name",
        max_length=150,
        blank=True,
        null=True,
        help_text="Введите имя.",
    )
    last_name = CharField(
        verbose_name="last name",
        max_length=150,
        blank=True,
        null=True,
        help_text="Введите фамилию.",
    )
    email = CharField(max_length=150, verbose_name="Email", help_text="Введите ваш email.", unique=True)
    avatar = ImageField(
        upload_to="users/avatars",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Добавьте свое фото.",
    )

    USERNAME_FIELD = ("email",)
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"Почта: {self.USERNAME_FIELD}."

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
