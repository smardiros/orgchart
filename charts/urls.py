from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^name-autocomplete/$', views.UserAutocomplete.as_view(), name='name-autocomplete'),
	url(r'^manager-autocomplete/$', views.ManagerAutocomplete.as_view(), name='manager-autocomplete'),
	url(r'^embed/$', views.embed, name='index'),
    url(r'^update/$', views.update, name='action'),
    url(r'^$', views.index, name='index'),
]