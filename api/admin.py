from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Client, Automation, Workflow, Message, Log

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'status', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'status', 'client')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'status', 'client')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Client)
admin.site.register(Automation)
admin.site.register(Workflow)
admin.site.register(Message)
admin.site.register(Log)
