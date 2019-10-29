from django.contrib import admin
from django.urls import path, re_path
from Clients import views as client_view

urlpatterns = [
    path('', client_view.index),
    re_path(r'^edit/$', client_view.edit),
    re_path(r'^update/$', client_view.update),
    re_path(r'^create/$', client_view.create),
]