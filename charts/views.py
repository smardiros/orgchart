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

def dict_to_json_format(employees, collapsed=False):

	json = []
	for _id, employee in employees.items():
		sub = employee.pop("sub")
		json.append(employee)


		if collapsed:
			json[-1]["className"] += " slide-up"


		children = dict_to_json_format(sub,employee["collapsed"])
		
		if children:
			json[-1]["children"] = children
	return json

def director_department(employee):
	department = Department.objects.filter(director = employee)
	return department

def index(request):
	departments_list = Department.objects.all()

	out = []


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
			if employee.name != director.name:
				print(employee)
				employees_id[employee.name] = employee.employee_id
				manager_id = employee.manager.employee_id
				employees_dict[employee.employee_id] = {"name": employee.name, "title": employee.title, "className": "", "manager" : manager_id, "collapsed": employee.collapse, "sub" : {}, "department": department.name}
				print(employee, " ", employee.manager)
				sub_director = director_department(employee)
				color = " "
				if employee.color is not None:
					color += employee.color
				elif department.color is not None:
					color += department.color

				if employee.picture.name:
					print("picture + ", employee.picture)
					employees_dict[employee.employee_id]["picture"] = employee.picture.url
					employees_dict[employee.employee_id]["className"] += " picture"

				employees_dict[employee.employee_id]["className"] += color

				if sub_director is not None:
					print(len(sub_director))
					if len(sub_director) == 1:
						dep = sub_director[0]
						employees_dict[employee.employee_id]["className"] += " drill-down asso-" + dep.abbr
						employees_dict[employee.employee_id]["downDep"] = dep.name

					else:
						employees_dict[employee.employee_id]["collapsed"] = True
						temp_id = -1
						for dep in sub_director:
							temp_employee = {"name": "", "title": dep.name, "className": "slide-up drill-down asso-" + dep.abbr + color, "manager" : employee.employee_id, "collapsed": employee.collapse, "sub" : {}, "downDep": dep.name}
							employees_dict[temp_id] = temp_employee
							temp_id -= 1




		print(employees_dict)
		dir_entry = {"name": director.name, "title": director.title, "className": "", "collapsed": director.collapse, "sub" : {}, "department": department.name}
		if director.color is not None:
			dir_entry["className"] += " " + director.color
		elif department.color is not None:
			dir_entry["className"] += " " + department.color
		if director.manager is not None:
			dir_entry["className"] += " drill-up asso-" + department.abbr + " up-" + department.parent.abbr

		if director.picture.name:
			dir_entry["picture"] = director.picture.url
			dir_entry["className"] += " picture"




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

		out.append([department.abbr, json.dumps(json_tree[0])])



	template = loader.get_template('charts/index.html')
	context = {'new_employees_list': employees_list, 'employees_tree':out}
	return render(request, 'charts/index.html', context)