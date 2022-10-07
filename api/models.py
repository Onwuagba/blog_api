from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from mainapp.models import TimeStamp


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):

        if not username:
            raise ValueError("Username is required")

        user = self.model(
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if password is None:
            raise TypeError('Superusers must have a password.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser, TimeStamp):
    email  = None
    username = models.CharField(
        db_index=True, max_length=255, unique=True, verbose_name='username')
    first_name = models.CharField(
        max_length=150, null=False, blank=False, verbose_name='first name')
    last_name = models.CharField(
        max_length=150, null=False, blank=False, verbose_name='last name')
    password = models.CharField(
        max_length=128, null=False, blank=False, verbose_name='password')
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.first_name