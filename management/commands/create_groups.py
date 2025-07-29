from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Mailing


class Command(BaseCommand):
    help = 'Создает группы пользователей и назначает права'

    def handle(self, *args, **kwargs):
        # Группа менеджеров
        manager_group, created = Group.objects.get_or_create(name='Managers')

        # Разрешения для менеджеров
        content_type = ContentType.objects.get_for_model(Mailing)
        permissions = Permission.objects.filter(content_type=content_type)
        manager_group.permissions.set(permissions)

        # Добавляем специальное разрешение для блокировки пользователей
        user_content_type = ContentType.objects.get(model='user')
        disable_perm, _ = Permission.objects.get_or_create(
            codename='can_disable_user',
            name='Can disable user',
            content_type=user_content_type
        )
        manager_group.permissions.add(disable_perm)

        self.stdout.write(self.style.SUCCESS('Группы и разрешения успешно созданы'))