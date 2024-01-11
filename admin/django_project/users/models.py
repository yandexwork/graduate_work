import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class MyUserManager(BaseUserManager):
    def create_user(self, login, password=None):
        if not login:
            raise ValueError('Users must have a login')

        user = self.model(login=login)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None):
        user = self.create_user(login, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    login = models.CharField(verbose_name='login', max_length=255, unique=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    USERNAME_FIELD = 'login'

    objects = MyUserManager()

    def __str__(self):
        return f'{self.login} {self.id}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
