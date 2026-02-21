from django.contrib.auth.models import AbstractUser
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
    email = CharField(
        max_length=150,
        verbose_name="Email",
        help_text="Введите ваш email.",
        unique=True,
    )
    avatar = ImageField(
        upload_to="users/avatars",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Добавьте свое фото.",
    )
    phone = CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Номер телефона",
        help_text="Введите номер телефона.",
    )
    country = CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Страна",
        help_text="Введите страну.",
    )
    token = CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Токен подтверждения",
        help_text="Токен для подтверждения email.",
        unique=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"Почта: {self.USERNAME_FIELD}."

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_view_user_list", "Может просматривать список пользователей"),
            ("can_block_users", "Может блокировать пользователей"),
        ]
