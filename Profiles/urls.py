from django.contrib import admin
from django.urls import path, re_path
from Profiles import views as profile_view


urlpatterns = [
    re_path(r'^/$', profile_view.index),
    re_path(r'^/edit/$', profile_view.edit),
    re_path(r'^/update/$', profile_view.update),
    re_path(r'^/create/$', profile_view.create),
    re_path(r'^/perm/$', profile_view.perm),
]