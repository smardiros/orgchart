from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.contrib.staticfiles.templatetags.staticfiles import static

from .models import Employee, Department
import os
import json

def add_to_tree(tree, employee, e_id):
	for _id, tree_employee in tree.items():
		if employee["manager"] == _id:
			tree_employee["sub"][e_id] = employee
			return True
		if add_to_tree(tree_employee["sub"],employee, e_id):
			return True 

	return False

def dict_to_json_format(employees):
	json = []
	for _id, employee in employees.items():
		sub = employee.pop("sub")
		json.append(employee)
		children = dict_to_json_format(sub)
		if children:
			json[-1]["children"] = children
	return json



def index(request):
	departments_list = Department.objects.all()
	for department in departments_list:
		print(department)
		employees_list = Employee.objects.filter(departments__in=[department])

		director = department.director
		print(director, "\n\n")
		
		employees_dict = {}
		employees_id = {}

		# for employee in employees_list:
		# 	employees_id[employee.name] = employee.employees_id
		# 	if employee.DepManager:



		for employee in employees_list:
			if employee is not director:
				employees_id[employee.name] = employee.employee_id
				manager_id = employee.manager.employee_id
				employees_dict[employee.employee_id] = {"name": employee.name, "title": employee.title, "className": employee.displayclass, "manager" : manager_id, "collapsed": employee.collapse, "sub" : {}}
				print(employee, " ", employee.manager)

		print(employees_dict)
		dir_entry = {"name": director.name, "title": director.title, "className": director.displayclass, "collapsed": director.collapse, "sub" : {}}
		if director.manager is not None:
			dir_entry["className"] += " drill-up asso-" + department.abbr
		tree = {director.employee_id: dir_entry}
		employees_dict.pop(director.employee_id, None)

		while len(employees_dict) > 0:
			pop = []
			for _id, employee in employees_dict.items():
				if add_to_tree(tree, employee, _id):
					pop.append(_id)		
			for _id in pop:
				employees_dict.pop(_id, None)

			#print(employees_dict)


		print(tree)

		json_tree = dict_to_json_format(tree)
		print("\n\n\n")
		print(json_tree)

		url = os.getcwd() + "/charts/static/charts/js/asso-" + department.abbr + ".json"

		with open(url, "w+") as outfile:
			json.dump(json_tree[0], outfile, indent=4, separators=(',', ': '))



	template = loader.get_template('charts/index.html')
	context = {'new_employees_list': employees_list,}
	return render(request, 'charts/index.html', context)