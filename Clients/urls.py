from django.contrib import admin
from django.urls import path, re_path
from . import views


urlpatterns = [
    path('/', views.index),
    path('/add', views.add),
    path('/edit/<int:id>', views.edit),

    re_path('^/api?', views.api),
]