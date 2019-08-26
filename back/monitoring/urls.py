from django.urls import path

from . import views

app_name = 'monitoring'
urlpatterns = [
    path('', views.index, name='index'),
    path('device/<int:id>', views.index, name='index'),
    path('api', views.api, name='api'),
]
