from a_apis.models.email_verification import EmailVerification
from a_user.models import User

from django.contrib import admin

# Register your models here.


admin.site.register(EmailVerification)
admin.site.register(User)
