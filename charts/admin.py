from django.contrib import admin
from .models import Employee, Department

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_departments', 'title')

    def get_departments(self, obj):
    	return ", ".join([p.name for p in obj.departments.all()])


# Register your models here.
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department)