from django.contrib.auth.mixins import UserPassesTestMixin


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Managers").exists()

    def get_queryset(self):
        if self.request.user.is_manager:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user)


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user
