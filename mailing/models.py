from django.db import models
from django.db.models import CharField, TextField, ForeignKey, DateTimeField, ManyToManyField


class Recipient(models.Model):
    username = CharField(max_length=150, verbose_name="ФИО", help_text="Введите ваши ФИО.")
    email = CharField(max_length=150, verbose_name="Email", help_text="Введите ваш email.", unique=True)
    comment = TextField(verbose_name="Комментарий", help_text="Введите ваш комментарий.")

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Владелец",
        help_text="Добавьте владельца курса.",
    )

    def __str__(self):
        return f"{self.username} - {self.email}"

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"


class Message(models.Model):
    subject = CharField(max_length=250, verbose_name="Тема письма", help_text="Напишите тему письма.")
    body = TextField(verbose_name="Содержание письма", help_text="Добавьте содержимое письма.")

    def __str__(self):
        return f"Название: {self.subject}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    start_time = DateTimeField(verbose_name="Дата и время начала отправки", help_text="Укажите дату и время начала отправки.")
    end_time = DateTimeField(verbose_name="Дата и время окончания отправки", help_text="Укажите дату и время окончания отправки.")
    status = CharField()
    message = ForeignKey(Message,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Сообщение",
        help_text="Добавьте сообщение для этой рассылки.",
    )
    recipients = ManyToManyField(Recipient,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Получатель рассылки",
        help_text="Добавьте получателя для этой рассылки.",
    )

    def __str__(self):
        return f"Название: {self.message}, статус: {self.status}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"