from django.urls import path

from . import views

app_name = 'clients'
urlpatterns = [
    path('', views.index, name='index'),
    path('api', views.api, name='api'),
    path('add', views.add, name='add'),
    path('edit/<int:pk>', views.edit, name='edit'),
    path('delete/<int:pk>', views.delete, name='delete'),
]
