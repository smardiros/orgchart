from django.contrib import admin
from .models import Employee, Department, Team, Country
from .views import getADNames
from dal import autocomplete
from django.contrib.auth.models import User, Group
from django.db import models
from django import forms


from guardian.admin import GuardedModelAdmin
from django.contrib.admin import widgets

class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name.split('-')[1].strip()

class DepartmentsField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class EmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EmployeeForm, self).__init__(*args, **kwargs)

    name = autocomplete.Select2ListCreateChoiceField (
        choice_list=getADNames,
        widget=autocomplete.ListSelect2(url='name-autocomplete')
    )

    manager = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=autocomplete.ModelSelect2(url='employee-autocomplete'),
        required=False
    )

    
    country = CustomModelChoiceField(required=False, queryset=Group.objects.filter(name__startswith='Country'))

    departments = DepartmentsField(required=False, queryset=Department.objects.all())

    department_test = DepartmentsField(required=False, queryset=Department.objects.all())

    def clean(self):
        cleaned_data = super(EmployeeForm, self).clean()
        country = cleaned_data["country"]
        departments = cleaned_data['departments']
        director_of_departments = cleaned_data["director_of_department"]
        for director_of_department in director_of_departments:
            directors = Employee.objects.filter(director_of_department=director_of_department).filter(country=country).exclude(pk=self.instance.pk)
            if directors:
                raise forms.ValidationError(
                    ''.join(['Director of ' + director_of_department.name + ' already exists for this country.'])
                )
        if any(director_of_department not in departments for director_of_department in director_of_departments) and director_of_departments is not None:
            raise forms.ValidationError(
                'Employee cannot be director of department they are not in.'
            )
        print(country)
        print(self.request.user.groups.all())
        if not self.request.user.is_superuser and country not in self.request.user.groups.filter(name__startswith='Country'):
            raise forms.ValidationError(
                "Invalid country choice."
            )

    class Meta:
        model = Employee
        exclude = ('is_new',)
        #fields = ('__all__')




class EmployeeAdmin(admin.ModelAdmin):

    #form = EmployeeForm(request=request)

    form = EmployeeForm
    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super(EmployeeAdmin, self).get_form(request, obj, **kwargs)
        class ModelFormMetaClass(ModelForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return ModelForm(*args, **kwargs)
        return ModelFormMetaClass


    def has_module_permission(self, request, obj=None):
        print('checking if has permission to view employee')
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists()

    def get_queryset(self, request):
        qs = super(EmployeeAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        print(request.user)
        return qs.filter(country__in=request.user.groups.filter(name__startswith='Country'))

    def has_add_permission(self, request):
        # This one doesn't get an object to play with, because there is no
        # object yet, but you can still do things like:
        return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists()
        # This will allow only superusers to add new objects of this type

    def has_change_permission(self, request, obj=None):
        # Here you have the object, but this is only really useful if it has
        # ownership info on it, such as a `user` FK
        print('obj: ' +  str(obj))
        #return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists()
        if obj is not None:
            return request.user.is_superuser or obj.country in request.user.groups.filter(name__startswith='Country')
            # Now only the "owner" or a superuser will be able to edit this object
        else:
            # obj == None when you're on the changelist page, so returning `False`
            # here will make the changelist page not even viewable, as a result,
            # you'd want to do something like:
            return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists() #or \
                   #self.model._default_manager.filter(user=request.user).exists()
            # Then, users must "own" *something* or be a superuser or they
            # can't see the changelist


    list_display = ('name', 'get_departments', 'title', 'country_name')
    #form = EmployeeForm

    def get_departments(self, obj):
        return ", ".join([p.name for p in obj.departments.all()])

    def country_name(self, obj):
        if obj.country is not None:
            return obj.country.name.split(' - ')[1]
        return ''

class DepartmentForm(forms.ModelForm):
    # director = forms.ModelChoiceField(
    #     queryset=Employee.objects.all(),
    #     widget=autocomplete.ModelSelect2(url='employee-autocomplete')
    # )

    class Meta:
        model = Employee
        fields = ('__all__')

    
    country = CustomModelChoiceField(required=False, queryset=Group.objects.filter(name__startswith='Country'))

class DepartmentAdmin(admin.ModelAdmin):
    # list_display = ('name', 'get_country', 'director')
    form = DepartmentForm

    def has_module_permission(self, request, obj=None):
        print('checking if has permission to view departments')
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists()

    def get_queryset(self, request):
        qs = super(DepartmentAdmin, self).get_queryset(request)
        #if request.user.is_superuser:
        return qs
        
        #print(request.user)
        #return qs.filter(country__in=request.user.groups.filter(name__startswith='Country'))

    def has_change_permission(self, request, obj=None):
        # Here you have the object, but this is only really useful if it has
        # ownership info on it, such as a `user` FK
        print('obj: ' +  str(obj))
        #return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists()
        if obj is not None:
            return request.user.is_superuser or obj.country in request.user.groups.filter(name__startswith='Country')
            # Now only the "owner" or a superuser will be able to edit this object
        else:
            # obj == None when you're on the changelist page, so returning `False`
            # here will make the changelist page not even viewable, as a result,
            # you'd want to do something like:
            return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists() #or \
                   #self.model._default_manager.filter(user=request.user).exists()
            # Then, users must "own" *something* or be a superuser or they
            # can't see the changelist
    
    # def get_country(self, obj):
    #     if obj.country is not None:
    #         return obj.country.name.split('-')[1].strip()
    #     else:
    #         return ''

class TeamForm(forms.ModelForm):
    manager = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=autocomplete.ModelSelect2(url='employee-autocomplete')
    )
    
    # members = forms.ModelChoiceField(
    #     queryset=Employee.objects.all(),
    #     widget=autocomplete.ModelSelect2Multiple(url='employee-autocomplete')
    # )


    class Meta:
        model = Team
        fields = ('__all__')

class TeamAdmin(admin.ModelAdmin):
    form = TeamForm

class CountryAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(CountryAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(name='Swaziland')


    def has_module_permission(self, request, obj=None):
        print('checking if has permission to view')
        print(request.user)
        print(request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists())
        return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists()

    def has_add_permission(self, request):
        # This one doesn't get an object to play with, because there is no
        # object yet, but you can still do things like:
        return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists()
        # This will allow only superusers to add new objects of this type

    def has_change_permission(self, request, obj=None):
        # Here you have the object, but this is only really useful if it has
        # ownership info on it, such as a `user` FK
        print('obj: ' +  str(obj))
        return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists()
        if obj is not None:
            return request.user.groups.filter(name='Sam\'s Fabulous Org Chart Group').exists()
            # Now only the "owner" or a superuser will be able to edit this object
        else:
            # obj == None when you're on the changelist page, so returning `False`
            # here will make the changelist page not even viewable, as a result,
            # you'd want to do something like:
            return request.user.is_superuser #or \
                   #self.model._default_manager.filter(user=request.user).exists()
            # Then, users must "own" *something* or be a superuser or they
            # can't see the changelist

    #def has_delete_permission(self, request, obj=None):
        # This pretty much works the same as `has_change_permission` only
        # the obj == None condition here affects the ability to use the
        # "delete selected" action on the changelist


# Register your models here.
admin.site.register(Country,CountryAdmin)

admin.site.register(Team, TeamAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department, DepartmentAdmin)