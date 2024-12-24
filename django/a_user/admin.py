from a_user.models import User

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "user_id",
        "username",
        "phone_number",
        "email",
        "is_email_verified",
    )
    search_fields = ("user_id", "username", "email", "phone_number")
    ordering = ("id",)


# 커스텀 UserAdmin
admin.site.register(User, CustomUserAdmin)
