from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from catalog.models import Product
from users.models import User


class Command(BaseCommand):
    help = "Создание группы и назначение ей прав."

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Модератор продуктов")
        content_type = ContentType.objects.get_for_model(Product)

        permission_unpublish = Permission.objects.get(
            codename="can_unpublish_product", content_type=content_type
        )
        permission_delete = Permission.objects.get(
            codename="delete_product", content_type=content_type
        )

        group.permissions.add(permission_unpublish, permission_delete)

        if created:
            self.stdout.write(self.style.SUCCESS("Группа создана, права назначены."))
        else:
            self.stdout.write(self.style.WARNING("Группа уже существует."))

        # Создание тестового пользователя-модератора
        user, user_created = User.objects.get_or_create(
            email="moderator@example.com",
            defaults={
                "is_active": True,
                "is_staff": True,
            },
        )

        if user_created:
            user.set_password("moderator123")
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "Тестовый пользователь-модератор создан: moderator@example.com (пароль: moderator123)"
                )
            )
        else:
            user.set_password("moderator123")
            user.is_active = True
            user.is_staff = True
            user.save()
            self.stdout.write(
                self.style.WARNING(
                    "Пользователь moderator@example.com уже существует. Пароль обновлен."
                )
            )

        # Добавляем пользователя в группу модераторов
        user.groups.add(group)
        self.stdout.write(
            self.style.SUCCESS("Пользователь добавлен в группу 'Модератор продуктов'")
        )