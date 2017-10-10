from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.decorators.http import require_http_methods
from django.views.decorators.clickjacking import xframe_options_exempt
import pyad
from pyad import aduser, pyadexceptions
from dal import autocomplete

from django.contrib.auth.models import User, Group


from .models import Employee, Department, Team
import os, io
import json, csv

import pythoncom


def gen_abbr(department_name):
    abbr = ''
    for word in department_name.split(' '):
        abbr = ''.join([abbr,word[0]])
    
    count = 0

    while True:
        department_query = Department.objects.filter(abbr=abbr)
        if not len(department_query):
            return abbr + (count if count else '')
        count += 1
        

def handle_csv_data(csv_file):
    csv_file = io.TextIOWrapper(csv_file)  # python 3 only
    dialect = csv.Sniffer().sniff(csv_file.read(1024), delimiters=";,")
    csv_file.seek(0)
    reader = csv.reader(csv_file, dialect)
    lines = list(reader)
    for line in lines:
        print(line)

    departments = list(set([line[2] for line in lines]))
    print(departments)

    for department in departments:
        department_object = Department.objects.filter(name=department)
        print(department)
        print(department_object)
        if not len(department_object):
            Department.objects.create(name=department, abbr=gen_abbr(department))
    countries = list(set([line[3] for line in lines]))
    #print(countries)
    for country in countries:
        country_group = Group.objects.filter(name=''.join(['Country - ', country]))
        if not len(country_group):
            Group.objects.create(name=''.join(['Country - ', country]))

    for line in lines:
        employee_query = Employee.objects.filter(name=line[0])
        if not len(employee_query):
            employee = Employee.objects.create(name=line[0])
        else:
            employee = Employee.objects.get(name=line[0])
        if line[1] is not '':
            employee.director_of_department.add(Department.objects.get(name=line[1]))
        if line[2] is not '':
            employee.departments.add(Department.objects.get(name=line[1]))
        employee.country = Group.objects.get(name=''.join(['Country - ', line[3]]))
        employee.save()

    return lines


def upload_csv(request):
    csv_content=[]
    if request.method == 'POST':
        csv_file = request.FILES['file'].file
        csv_content = handle_csv_data(csv_file)  
    return render(request, 'upload.html', {'content':csv_content})

def getADNames():
    pythoncom.CoInitialize()
    q = pyad.adquery.ADQuery(options=dict(ldap_server="dc-net1.egpaf.com"))
    q.execute_query(attributes = ["displayName", "description", "telephoneNumber", "logonCount","mail","department"], base_dn = "OU= - Washington DC, OU=EGPAF Users - Active Accounts, DC=egpaf, DC=com")
    l = list(q.get_results())
    #qs = [x for x in [x[0].split('=')[1] for x in [[x for x in a if x.startswith("CN=")] for a in [x.split(',') for x in [x['distinguishedName'] for x in l]]] if x] if any(l.isupper() for l in x)] #Employee.objects.all()
    qs = [x["displayName"] for x in l if x["displayName"] is not None and x["logonCount"] and any(c.isupper() for c in x["displayName"])]
    #qs = [x for x in qs if x.translate({ord(c): None for c in ' -.'}).isalpha()]
    return sorted(qs)

class EmployeeAutocomplete(autocomplete.Select2QuerySetView):
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

def dict_to_json_format(employees, collapsed=False, showall=False):
    print(showall)
    json = []
    for _id, employee in employees.items():
        sub = employee.pop("sub")
        json.append(employee)


        if collapsed and not showall:
            json[-1]["className"] += " slide-up"

        if showall:
            json[-1]["collapsed"] = False
            
        children = dict_to_json_format(sub,employee["collapsed"],showall)
        
        if children:
            json[-1]["children"] = children
        else:
            json[-1]["children"] = []
    return json

def director_department(employee):
    department = Department.objects.filter(director_of = employee)
    return department

def get_parent_department(department, country):
    director = Employee.objects.filter(director_of_department=department).get(country=country).filter(is_new=False)
    departments = director.manager.departments
    if len(departments.all()) > 1:
        return Department.objects.filter(employee=director).get(employee=director.manager)   


def department_dict(department, country):
    print(department.abbr)
    if department.abbr != "egpaf":
        employees_list = Employee.objects.filter(departments__in=[department]).filter(country=country).filter(is_new=False)
    else:
        employees_list = Employee.objects.filter(country=country).filter(is_new=False)
    pythoncom.CoInitialize()
    director = department.director_of.get(country=country)
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
                mail = user.mail
                title = user.description
                phone = user.telephoneNumber
                dep = user.department
            except pyadexceptions.invalidResults as e:
                user = None
                title = employee.title
                print(employee.name + str(e))
                pass
            print(title)
            employees_id[employee.name] = employee.employee_id
            if(employee.manager is not None):
                manager_id = employee.manager.employee_id
                employees_dict[employee.employee_id] = {"name": employee.name, "title": title, "className": "", "manager" : manager_id, "collapsed": employee.collapse, "sub" : {}, "department": department.name, "details": {}, "teams":{ "permanent":[], "temporary":[]}}
                
                for team in employee.teams.all():
                    if team.permanent:
                        employees_dict[employee.employee_id]["teams"]["permanent"].append({"name": team.name, "abbr": team.abbr})
                    else:
                        employees_dict[employee.employee_id]["teams"]["temporary"].append({"name": team.name, "abbr": team.abbr})

                if user is not None:
                    employees_dict[employee.employee_id]["details"] = {"mail" : mail, "phone" : phone, "department" : dep}
                #print(employees_dict[employee.employee_id])
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

                if len(sub_director) > 0 and department.abbr != "egpaf":
                    print("subdirector : " + employee.name)
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
        mail = user.mail
        title = user.description
        phone = user.telephoneNumber
        dep = user.department
    except pyadexceptions.invalidResults as e:
        user = None
        title = director.title
        print(director.name + str(e))
        pass

    dir_entry = {"name": director.name, "title": title, "className": "", "collapsed": director.collapse, "sub" : {}, "department": department.name, "details": {}, "teams":{ "permanent":[], "temporary":[]}}
    for team in director.teams.all():
        if team.permanent:
            dir_entry["teams"]["permanent"].append({"name": team.name, "abbr": team.abbr})
        else:
            dir_entry["teams"]["temporary"].append({"name": team.name, "abbr": team.abbr})

    if user is not None:
        dir_entry["details"] = {"mail" : mail, "phone" : phone, "department" : dep}
    if director.color is not None:
        dir_entry["className"] += " " + director.color
    elif department.color is not None:
        dir_entry["className"] += " " + department.color
    if director.manager.pk is not director.pk:
        dir_entry["className"] += " drill-up asso-" + department.abbr + " up-" + get_parent_department(department,country).attr

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


    return dict_to_json_format(tree, showall=(department.abbr == "egpaf"))   
    
def team_dict(team):
    employees_list = Employee.objects.filter(teams=team).filter(is_new=False)
    pythoncom.CoInitialize()
    manager = team.manager


    employees_dict = {}
    employees_id = {}

    for employee in employees_list:
        if employee.name != manager.name:
            try:
                user = aduser.ADUser.from_cn(employee.name, options=dict(ldap_server="dc-net1.egpaf.com"))
                mail = user.mail
                title = user.description
                phone = user.telephoneNumber
                dep = user.department
            except pyadexceptions.invalidResults as e:
                user = None
                title = employee.title
                print(employee.name + str(e))
                pass
            print(title)
            employees_id[employee.name] = employee.employee_id
            manager_id = manager.employee_id
            employees_dict[employee.employee_id] = {"name": employee.name, "title": title, "className": "", "manager" : manager_id, "collapsed": False, "sub" : {}, "details": {}, "teams":{ "permanent":[], "temporary":[]}}
            
            for team in employee.teams.all():
                if team.permanent:
                    employees_dict[employee.employee_id]["teams"]["permanent"].append({"name": team.name, "abbr": team.abbr})
                else:
                    employees_dict[employee.employee_id]["teams"]["temporary"].append({"name": team.name, "abbr": team.abbr})

            if user is not None:
                employees_dict[employee.employee_id]["details"] = {"mail" : mail, "phone" : phone, "department" : dep}
            #print(employees_dict[employee.employee_id])
            #print(employee, " ", employee.manager)
            sub_director = director_department(employee)
            color = " "
            if employee.color is not None:
                color += employee.color 


            if employee.picture.name:
                #print("picture + ", employee.picture)
                employees_dict[employee.employee_id]["picture"] = employee.picture.url
                employees_dict[employee.employee_id]["className"] += " picture"

    try:
        user = aduser.ADUser.from_cn(manager.name, options=dict(ldap_server="dc-net1.egpaf.com"))
        title = user.description
        mail = user.mail
        title = user.description
        phone = user.telephoneNumber
        dep = user.department
    except pyadexceptions.invalidResults as e:
        user = None
        title = manager.title
        print(manager.name + str(e))
        pass

    manager_entry = {"name": manager.name, "title": title, "className": "", "collapsed": False, "sub" : {}, "details": {}, "teams":{ "permanent":[], "temporary":[]}}
    for team in manager.teams.all():
        if team.permanent:
            manager_entry["teams"]["permanent"].append({"name": team.name, "abbr": team.abbr})
        else:
            manager_entry["teams"]["temporary"].append({"name": team.name, "abbr": team.abbr})

    try:
        user = aduser.ADUser.from_cn(manager.name, options=dict(ldap_server="dc-net1.egpaf.com"))
        title = user.description
        mail = user.mail
        title = user.description
        phone = user.telephoneNumber
        dep = user.department
    except pyadexceptions.invalidResults as e:
        user = None
        title = director.title
        print(director.name + str(e))
        pass

    if user is not None:
        manager_entry["details"] = {"mail" : mail, "phone" : phone, "department" : dep}
    if manager.color is not None:
        manager_entry["className"] += " " + manager.color


    if manager.picture.name:
        manager_entry["picture"] = manager.picture.url
        manager_entry["className"] += " picture"


    tree = {manager.employee_id : manager_entry}
    employees_dict.pop(manager.employee_id, None)
    while len(employees_dict) > 0:
        pop = []
        for _id, employee in employees_dict.items():
            if add_to_tree(tree, employee, _id):
                pop.append(_id)        
        for _id in pop:
            employees_dict.pop(_id, None)


    return dict_to_json_format(tree)


def team(request):
    #fix to match new departments
    departments_list = Department.objects.all()
    teams_list = Team.objects.all()

    out = []

    for team in teams_list:

        out.append([team.abbr, json.dumps(team_dict(team)[0]), team.name])

    dep_out = []
    for dep in departments_list:
        dep_out.append([dep.abbr, '', dep.name])    

    template = loader.get_template('charts/index.html')
    context = { 'departments_tree':dep_out, 'teams_tree' : out}
    team = request.GET.get('t', '')
    if (team):
        context['team']=str(team)
    return render(request, 'charts/team.html', context)


def index(request):
    try:
        country = request.GET.get('country','')

        if not country:
            country = 'USA'

        country_group = Group.objects.get(name=' - '.join(['Country',country]))
    except:
        country_group = Group.objects.get(name='Country - USA')

    departments_list = Department.objects.filter(director_of__country=country_group)

    print(departments_list)
    teams_list = Team.objects.all()

    out = []

    for department in departments_list:

        out.append([department.abbr, json.dumps(department_dict(department,country_group)[0]), department.name])

    teams_out = []
    for team in teams_list:
        teams_out.append([team.abbr, '', team.name])

    template = loader.get_template('charts/index.html')
    context = { 'departments_tree':out, 'teams_tree' : teams_out}
    department = request.GET.get('dep', '')
    if (department):
        context['department']=str(department)

    print(context)
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



# def team(request):
#     t = request.GET.get('team', '')
#     team = list(Team.objects.filter(name=t))[0]


#     manager = {"name": team.manager.name, "title": title, "className": "", "manager" : manager_id, "collapsed": employee.collapse, "sub" : {}, "department": department.name}

#     for member in team.members.all():
#         if member.name != direct


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
