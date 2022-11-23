from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_filter = [
        "username",
        "email"
    ]
    list_display = ('username', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
