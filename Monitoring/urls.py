from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    re_path('^', views.api),

]