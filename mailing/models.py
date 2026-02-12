from django.db import models
from django.db.models import CharField, TextField, ForeignKey, DateTimeField, ManyToManyField

from mailing.services import update_status


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
        return f"Название: {self.subject}."

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    start_time = DateTimeField(verbose_name="Дата и время начала отправки", help_text="Укажите дату и время начала отправки.")
    end_time = DateTimeField(verbose_name="Дата и время окончания отправки", help_text="Укажите дату и время окончания отправки.")
    status = CharField(
        max_length=50,
        verbose_name="Статус",
        blank=True,
        default='Создана'
    )
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

    def update_status(self):
        """Пересчитывает и сохраняет статус рассылки в БД"""
        new_status = update_status(self.start_time, self.end_time)
        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def __str__(self):
        return f"Название: {self.message}, статус: {self.status}."

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class AttemptsMailing(models.Model):
    attempt_time = DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки отправки", help_text="Укажите дату и время попытки отправки.")
    status = CharField(
        max_length=50,
        choices=[
            ('Успешно', 'Успешно'),
            ('Не успешно', 'Не успешно')
        ],
        verbose_name="Статус"
    )
    server_response = TextField(verbose_name=" Ответ почтового сервера", help_text="Введите ответ почтового сервера.")
    mailing = ForeignKey(Mailing,
         on_delete=models.CASCADE,
         blank=True,
         null=True,
         verbose_name="Рассылка",
         help_text="Добавьте рассылку этой попытки.",
    )

    def __str__(self):
        return f"{self.mailing}, статус: {self.status} - {self.attempt_time}."

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
