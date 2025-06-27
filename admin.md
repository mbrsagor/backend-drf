### Admin panel UI

```bash
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Profile, OTPVerification

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'fullname', 'phone', 'role', 'is_active', 'is_staff']
    ordering = ['email']
    search_fields = ['email', 'fullname']
    fieldsets = (
        (None, {"fields": ("password",)}),
        ("Personal info", {"fields": ("fullname", "email", "phone", "role")}),
        # ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_online", "is_hoa")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

admin.site.register(User, CustomUserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ['user', 'gender', 'points', 'country', 'city']
    search_fields = ['user__email', 'user__fullname', 'country']
    list_filter = ['user__role']
admin.site.register(Profile, ProfileAdmin)


class OTPVerificationAdmin(admin.ModelAdmin):
    model = OTPVerification
    list_display = ['email', 'otp', 'created_at']
    search_fields = ['email', 'otp']
    list_filter = ['email']
admin.site.register(OTPVerification, OTPVerificationAdmin)
```
