from django.contrib.auth.base_user import BaseUserManager

from core.models.manager import ActiveModelManager


class UserManager(BaseUserManager, ActiveModelManager):

    def create_user(self, username, phone, password=None, is_active=True, is_admin=False):
        if not phone:
            raise ValueError('Users must have an phone number')
        if not username:
            raise ValueError('Users must have a username')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(username=username, phone=phone)
        user.set_password(password)
        user.admin = is_admin
        user.active = is_active
        user.save(using=self._db)

        return user

    def create_superuser(self, username, phone, password=None):
        user = self.create_user(
            username,
            phone,
            password=password,
            is_admin=True,
        )
        user.save(using=self._db)
        return user
