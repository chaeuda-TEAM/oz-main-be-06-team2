from a_common.models import CommonModel

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser, CommonModel):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, blank=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
