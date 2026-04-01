from django.contrib import admin
from .models import User

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'can_be_contacted', 'can_data_be_shared', 'age')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('can_be_contacted', 'can_data_be_shared')
    
admin.site.register(User, UserAdmin)