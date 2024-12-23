import uuid
from datetime import timedelta

from a_common.models import CommonModel

from django.db import models
from django.utils import timezone


class EmailVerification(CommonModel):
    email = models.EmailField()
    verification_code = models.UUIDField(default=uuid.uuid4, editable=False)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.email} - {'Verified' if self.is_verified else 'Not Verified'}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set expires_at when creating new object
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
