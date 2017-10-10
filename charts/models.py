from django.db import models
import os
from dal import autocomplete

from django import forms

from django.contrib import admin

import orgchart.settings as settings


# Create your models here.
color_choices = (
	("navy", 'Navy'),
	("blue", 'Blue'),
	("aqua", 'Aqua'),
	("teal", 'Teal'),
	("olive", 'Olive'),
)

class Country(models.Model):
	name = models.CharField(max_length=100)
	group = models.OneToOneField('auth.Group', unique=True, null=True, blank=True, related_name='group')
	abbr = models.CharField(max_length=10, unique=True)

	class Meta:
		verbose_name_plural = "countries"
	def __str__(self):
		return self.name

class Employee(models.Model):

	is_new = models.NullBooleanField(blank=True)

	employee_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	title = models.CharField(max_length=100, null=True, blank=True)
	country = models.ForeignKey('auth.Group', on_delete=models.SET_NULL, null=True, blank=True)
	#displayclass = models.CharField(max_length=200, blank=True)
	manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
	departments = models.ManyToManyField('Department', blank=True)
	teams = models.ManyToManyField('Team', blank=True)
	collapse = models.NullBooleanField(blank=True)
	#DepManager = models.BooleanField()

	 #,limit_choices_to={'name__startswith': 'Country'})

	director_of_department = models.ManyToManyField('Department', blank=True, related_name='director_of')

	color = models.CharField(max_length=20, choices=color_choices,null=True,blank=True)

	picture = models.FileField(upload_to='charts/static/charts/employee_pictures',null=True,blank=True)


	def __str__(self):
		return self.name


class Department(models.Model):
	name = models.CharField(max_length=100)
	abbr = models.CharField(max_length=10, unique=True)
	#director = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
	parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
	color = models.CharField(max_length=20, choices=color_choices,null=True,blank=True)

	country = models.ForeignKey('auth.Group', on_delete=models.SET_NULL, null=True, blank=True)


	def __str__(self):
		return self.name

class Team(models.Model):
	name = models.CharField(max_length=100)
	abbr = models.CharField(max_length=10, unique=True)
	description = models.CharField(max_length=400)
	manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="team_members")
	permanent = models.BooleanField()
	#members = models.ManyToManyField(Employee)

	def __str__(self):
		return self.name
