from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(
        _('first name'),
        max_length=30, blank=False, null=False)
    last_name = models.CharField(
        _('last name'),
        max_length=150, blank=False, null=False)
    email = models.EmailField(_('email address'), blank=False, null=False)
