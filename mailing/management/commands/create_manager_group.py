from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from mailing.models import Mailing, Message, Recipient
from users.models import User


class Command(BaseCommand):
    help = "Создание группы и назначение ей прав."

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Менеджеры")
        # Получаем ContentType для всех моделей
        mailing_ct = ContentType.objects.get_for_model(Mailing)
        message_ct = ContentType.objects.get_for_model(Message)
        recipient_ct = ContentType.objects.get_for_model(Recipient)
        user_ct = ContentType.objects.get_for_model(User)

        # Получаем все permissions для менеджеров
        permissions = Permission.objects.filter(
            content_type__in=[mailing_ct, message_ct, recipient_ct, user_ct]
        )

        # Добавляем permissions в группу
        group.permissions.set(permissions)

        if created:
            self.stdout.write(self.style.SUCCESS("Группа создана, права назначены."))
        else:
            self.stdout.write(self.style.WARNING("Группа уже существует."))

        # Создание тестового пользователя-модератора
        user, user_created = User.objects.get_or_create(
            email="manager@example.com",
            defaults={
                "is_active": True,
                "is_staff": True,
            },
        )

        if user_created:
            user.set_password("manager123")
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "Тестовый пользователь-менеджер создан: manager@example.com (пароль: manager123)"
                )
            )
        else:
            user.set_password("manager123")
            user.is_active = True
            user.is_staff = True
            user.save()
            self.stdout.write(
                self.style.WARNING(
                    "Пользователь manager@example.com уже существует. Пароль обновлен."
                )
            )

        # Добавляем пользователя в группу модераторов
        user.groups.add(group)
        self.stdout.write(
            self.style.SUCCESS("Пользователь добавлен в группу 'Менеджеры'")
        )
