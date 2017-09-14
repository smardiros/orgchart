from django.contrib import admin
from .models import Employee, Department
from .views import getADNames
from dal import autocomplete

from django import forms

class EmployeeForm(forms.ModelForm):
    name = autocomplete.Select2ListCreateChoiceField (
        choice_list=getADNames,
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

class DepartmentForm(forms.ModelForm):
    director = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=autocomplete.ModelSelect2(url='manager-autocomplete')
    )

    class Meta:
        model = Employee
        fields = ('__all__')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'director')
    form = DepartmentForm


# Register your models here.
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department, DepartmentAdmin)