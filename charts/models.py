from django.db import models

# Create your models here.




class Department(models.Model):
	name = models.CharField(max_length=100)
	abbr = models.CharField(max_length=10)

	def __str__(self):
		return self.name


class Employee(models.Model):
	employee_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	title = models.CharField(max_length=100)
	displayclass = models.CharField(max_length=200, blank=True)
	manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
	departments = models.ManyToManyField(Department)
	collapse = models.BooleanField()
	DepManager = models.BooleanField()

	def __str__(self):
		return self.name