from a_common.models import CommonModel

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser, CommonModel):
    user_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "user_id"
    REQUIRED_FIELDS = ["username", "email", "phone_number"]

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.user_id
