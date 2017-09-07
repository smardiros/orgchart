from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^embed/$', views.embed, name='index'),
    url(r'^update/$', views.update, name='action'),
    url(r'^$', views.index, name='index'),
]