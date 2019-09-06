from django.contrib import admin
from django.urls import path, re_path
from Devices import views as device_view


urlpatterns = [
    re_path(r'^/$', device_view.index),
    re_path(r'^/edit/$', device_view.edit),
    re_path(r'^/update/$', device_view.update),
    re_path(r'^/create/$', device_view.create),
    re_path(r'^/(\d+)/reboot/$', device_view.reboot),
    re_path(r'^/(\d+)/client_change/$', device_view.client_change),
]