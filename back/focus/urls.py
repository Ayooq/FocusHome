"""focus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),

    path('', RedirectView.as_view(url='accounts/login', permanent=False)),
    path('help/', views.help, name='help'),
    path('accounts/', include([
        path('login/', views.login, name='login'),
        path('logout/', views.logout, name='logout'),
    ])),

    path('clients/', include('clients.urls')),
    path('devices/', include('devices.urls')),
    path('monitoring/', include('monitoring.urls')),
    path('profiles/', include('profiles.urls')),
]
