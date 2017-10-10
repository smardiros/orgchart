from django.conf.urls import url

from . import views

urlpatterns = [

	url(r'^name-autocomplete/$', views.UserAutocomplete.as_view(), name='name-autocomplete'),
	url(r'^employee-autocomplete/$', views.EmployeeAutocomplete.as_view(), name='employee-autocomplete'),
	url(r'^team/$', views.team, name='team'),
	url(r'^embed/$', views.embed, name='index'),
    url(r'^update/$', views.update, name='action'),
    url(r'^upload/$', views.upload_csv, name='upload'),
    url(r'^$', views.index, name='index'),
]