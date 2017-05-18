from django.db import models

# Create your models here.
color_choices = (
	("navy", 'Navy'),
	("blue", 'Blue'),
	("aqua", 'Aqua'),
	("teal", 'Teal'),
	("olive", 'Olive'),
)

class Employee(models.Model):
	employee_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	title = models.CharField(max_length=100)
	displayclass = models.CharField(max_length=200, blank=True)
	manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
	departments = models.ManyToManyField('Department', blank=True)
	collapse = models.BooleanField()
	DepManager = models.BooleanField()

	color = models.CharField(max_length=20, choices=color_choices,null=True,blank=True)

	def __str__(self):
		return self.name


class Department(models.Model):
	name = models.CharField(max_length=100)
	abbr = models.CharField(max_length=10)
	director = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
	parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
	color = models.CharField(max_length=20, choices=color_choices,null=True,blank=True)

	def __str__(self):
		return self.name