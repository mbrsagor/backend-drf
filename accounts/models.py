from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

url = "https://www.youtube.com/watch?v=lFD5uoCcvSA&list=PLJRGQoqpRwdfoa9591BcUS6NmMpZcvFsM&index=4"


class UserAccountManager(BaseUserManager):
    def create_user(self, name, email, password=None):
        if not email:
            raise ValueError("User must have email address")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=120, unique=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]

    def __str__(self):
        return self.email
