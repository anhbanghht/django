from django.contrib import admin

from .models import User, Department

class UserAdmin(admin.ModelAdmin):
    fields = ['user_name', 'email', 'birthday', 'department']

class DepartmentAdmin(admin.ModelAdmin):
    fields = ['name', 'parent_id', 'note']

admin.site.register(User, UserAdmin)
# admin.site.register(Department, DepartmentAdmin)
