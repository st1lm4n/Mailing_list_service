from django.contrib.auth.backends import ModelBackend


class RoleBackend(ModelBackend):
    def has_perm(self, user, perm, obj=None):
        # Менеджеры могут просматривать все объекты
        if user.groups.filter(name="Managers").exists() and perm.startswith("view_"):
            return True

        # Пользователи могут управлять только своими объектами
        if obj and hasattr(obj, "owner") and obj.owner == user:
            return True

        return super().has_perm(user, perm, obj)
