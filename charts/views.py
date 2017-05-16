from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

from .models import Employee, Department
import os


def index(request):
	employees_list = Employee.objects.all()
	departments_list = Department.objects.all()
	employees_dict = {}
	employees_id = {}
	for employee in employees_list:
		employees_id[employee.name] = employee.employee_id
		if employee.manager is not None:
			manager_id = employee.manager.employee_id
		else:
			manager_id = None
		employees_dict[employee.employee_id] = {"name": employee.name, "title": employee.title, "class": employee.displayclass, "manager" : manager_id, "sub" : {}}
		print(employee, " ", employee.manager)

	print(employees_dict)

	while len(employees_dict) > 1:
		pop = []
		for _id, employee in employees_dict.items():
			if(employee["manager"] is not None):
				employees_dict[employee["manager"]]["sub"][employees_id[employee["name"]]] = employee
				pop.append(employees_id[employee["name"]])
		
		for _id in pop:
			employees_dict.pop(_id, None)

		print(employees_dict)

	os.getcwd()

	template = loader.get_template('charts/index.html')
	context = {'new_employees_list': employees_list,}
	return render(request, 'charts/index.html', context)