from django.db import models

# Create your models here.

class Employee(models.Model):
	employee_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	title = models.CharField(max_length=100)
	manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return self.name