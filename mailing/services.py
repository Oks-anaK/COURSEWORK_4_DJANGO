from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail


def update_status(start_time, end_time):
    try:
        if start_time >= end_time:
            raise Exception("Дата и время начала и окончания заданы неверно.")

        now = datetime.now()

        if now < start_time:
            return 'Создана'
        elif start_time <= now <= end_time:
            return 'Запущена'
        else:  # now > end_time
            return 'Завершена'
    except Exception as e:
        print(f"Что-то пошло не так: {e}.")


def start_mailing(mailing):
    # Импорт внутри функции для избежания циклического импорта
    from mailing.models import AttemptsMailing

    now = datetime.now()

    if not (mailing.start_time <= now <= mailing.end_time):
        raise ValueError("Время неподходящее для клиентов.")

    recipients = mailing.recipients.all()

    if not recipients.exists():
        raise ValueError("Нет получателей для рассылки")

    if not mailing.message:
        raise ValueError("Не указано сообщение для рассылки")

    for recipient in recipients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,

            )

            AttemptsMailing.objects.create(
                mailing=mailing,
                status='Успешно',
                server_response='Письмо успешно отправлено'
            )

        except Exception as e:
            AttemptsMailing.objects.create(
                mailing=mailing,
                status='Не успешно',
                server_response=f"Произошла ошибка при отправке: {str(e)}"
            )








