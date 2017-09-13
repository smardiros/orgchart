from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.decorators.http import require_http_methods
from django.views.decorators.clickjacking import xframe_options_exempt
import pyad
from pyad import aduser, pyadexceptions
from dal import autocomplete




from .models import Employee, Department
import os
import json

import pythoncom


def getADNames():
    pythoncom.CoInitialize()
    q = pyad.adquery.ADQuery(options=dict(ldap_server="dc-net1.egpaf.com"))
    q.execute_query(attributes = ["distinguishedName", "description"], base_dn = "OU= - Washington DC, OU=EGPAF Users - Active Accounts, DC=egpaf, DC=com")
    l = list(q.get_results())
    qs = [x for x in [x[0].split('=')[1] for x in [[x for x in a if x.startswith("CN=")] for a in [x.split(',') for x in [x['distinguishedName'] for x in l]]] if x] if any(l.isupper() for l in x)] #Employee.objects.all()
    #qs = [x for x in qs if x.translate({ord(c): None for c in ' -.'}).isalpha()]
    return sorted(qs)

class ManagerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Employee.objects.none()

        qs = Employee.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs

class UserAutocomplete(autocomplete.Select2ListView):
    def create(self, text):
        return text
        
    def get_list(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return []

        return getADNames()
        #[x[0].split('=')[1] for x in [[x for x in a if x.startswith("CN=")] for a in [x.split(',') for x in [x['distinguishedName'] for x in l]]] if x]

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
        else:
            json[-1]["children"] = []
    return json

def director_department(employee):
    department = Department.objects.filter(director = employee)
    return department

def department_dict(department):
    employees_list = Employee.objects.filter(departments__in=[department])
    pythoncom.CoInitialize()
    director = department.director
    #print(director, "\n\n")
    
    employees_dict = {}
    employees_id = {}

    # for employee in employees_list:
    #     employees_id[employee.name] = employee.employees_id
    #     if employee.DepManager:

    

    for employee in employees_list:
        if employee.name != director.name:
            try:
                user = aduser.ADUser.from_cn(employee.name, options=dict(ldap_server="dc-net1.egpaf.com"))
                title = user.description
            except pyadexceptions.invalidResults as e:
                title = employee.title
                print(employee.name + str(e))
                pass
            print(title)
            employees_id[employee.name] = employee.employee_id
            manager_id = employee.manager.employee_id
            employees_dict[employee.employee_id] = {"name": employee.name, "title": title, "className": "", "manager" : manager_id, "collapsed": employee.collapse, "sub" : {}, "department": department.name}
            #print(employee, " ", employee.manager)
            sub_director = director_department(employee)
            color = " "
            if employee.color is not None:
                color += employee.color 
            elif department.color is not None:
                color += department.color

            if employee.picture.name:
                #print("picture + ", employee.picture)
                employees_dict[employee.employee_id]["picture"] = employee.picture.url
                employees_dict[employee.employee_id]["className"] += " picture"

            employees_dict[employee.employee_id]["className"] += color

            if sub_director is not None:
                #print(len(sub_director))
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


    #print(employees_dict)
    try:
        user = aduser.ADUser.from_cn(director.name, options=dict(ldap_server="dc-net1.egpaf.com"))
        title = user.description
    except pyadexceptions.invalidResults as e:
        title = director.title
        print(director.name + str(e))
        pass
    print(title)
    dir_entry = {"name": director.name, "title": title, "className": "", "collapsed": director.collapse, "sub" : {}, "department": department.name}
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


    #print(tree)

    return dict_to_json_format(tree)    


def index(request):
    departments_list = Department.objects.all()

    out = []

    for department in departments_list:

        out.append([department.abbr, json.dumps(department_dict(department)[0]), department.name])

    template = loader.get_template('charts/index.html')
    context = { 'employees_tree':out}
    department = request.GET.get('dep', '')
    if (department):
        context['department']=str(department)

    print(department)
    return render(request, 'charts/index.html', context)

    
@xframe_options_exempt
def embed(request):
    departments_list = Department.objects.all()

    out = []

    for department in departments_list:

        out.append([department.abbr, json.dumps(department_dict(department)[0]), department.name])

    template = loader.get_template('charts/index.html')
    context = { 'employees_tree':out}
    department = request.GET.get('dep', '')
    if (department):
        context['department']=str(department)

    print(department)
    return render(request, 'charts/embed.html', context)



def dict_to_list(employee_dict, manager=None):
    dict_list = []
    if 'children' in employee_dict:
        for child in employee_dict['children']:

            dict_list += dict_to_list(child, employee_dict['name'])

        del employee_dict['children']
    employee_dict['manager'] = manager
    dict_list += [employee_dict]
    return dict_list


def update_employee(employee):
    employees = Employee.objects.filter(name=employee['name'])
    if len(employees):
        db_emp = employees[0]
        print(db_emp.__dict__)
        db_emp.manager = Employee.objects.filter(name=employee['manager'])[0]
        print(db_emp.__dict__)
        db_emp.save()


@require_http_methods(["POST"])
def update(request):
    #employee_dict = request.POST.getlist()
    print("update!")
    updated_dict = json.loads(request.POST.get('data'))

    dep_abbr = request.POST.get('department')

    department = Department.objects.filter(abbr = dep_abbr)
    print(department[0])

    #data_base_dict = department_dict(department[0])[0]
    #employees_list = Employee.objects.filter(departments__in=[department[0]])

    updated_employees_list = dict_to_list(updated_dict)

    for employee in updated_employees_list:
        if 'changed' in employee:
            print(employee)
            update_employee(employee)


    return HttpResponse()
