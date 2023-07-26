from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from accounts.models import *



class AccountAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'username', 'email', 'userid','date_joined', 'auth_provider', 'last_login', 'is_admin', 'is_staff', 'is_verified')
    list_display_links = ['email', 'date_joined',]
    search_fields = ('email',)
    readonly_fields = ('id', 'date_joined', 'last_login')
    filter_horizontal = ()
    list_filter = ('is_admin', 'is_staff', 'is_verified')
    fieldsets = ()
    ordering = ("email",)

admin.site.register(Account, AccountAdmin),

