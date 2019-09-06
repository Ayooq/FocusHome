from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(url='login', permanent=False)),
    path('/', RedirectView.as_view(url='login', permanent=False)),

    path('login', views.log_in),
    path('logout', views.log_out),

    re_path(r'^api/devices', include('Devices.urls')),
    re_path(r'^api/clients', include('Clients.urls')),
    re_path(r'^api/users', include('Profiles.urls')),
    re_path(r'^api/monitoring', include('Monitoring.urls')),
    re_path(r'^api/notifications', include('Monitoring.urls')),

    re_path(r'^api/settings', views.settings),

    re_path(r'^', views.react_view),

]
