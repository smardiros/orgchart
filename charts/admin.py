from django.contrib import admin
from .models import Employee, Department
from dal import autocomplete

from django import forms

class EmployeeForm(forms.ModelForm):
    name = autocomplete.Select2ListChoiceField(
        choice_list=Employee.objects.all(),
        widget=autocomplete.ListSelect2(url='name-autocomplete')
    )

    manager = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=autocomplete.ModelSelect2(url='manager-autocomplete')
    )

    class Meta:
        model = Employee
        fields = ('__all__')


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_departments', 'title')
    form = EmployeeForm

    def get_departments(self, obj):
    	return ", ".join([p.name for p in obj.departments.all()])


# Register your models here.
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department)