from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

from .models import Employee


def index(request):
    new_employees_list = Employee.objects.all()[:5]
    template = loader.get_template('charts/index.html')
    context = {'new_employees_list': new_employees_list,}
    return render(request, 'charts/index.html', context)