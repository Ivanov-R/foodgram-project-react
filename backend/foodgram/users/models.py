from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
        null=False
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        blank=False,
        null=False, unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name',
                       'username']


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )

    def __str__(self) -> str:
        return f'{self.user} {self.author}'
