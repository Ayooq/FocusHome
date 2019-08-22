from django.contrib import admin
from django.urls import path

from . import views

app_name = 'profiles'
urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add, name='add'),
    path('edit/<int:pk>', views.edit, name='edit'),
    path('delete/<int:pk>', views.delete, name='delete'),
    path('permit/<int:pk>', views.permit, name='permit'),
]
