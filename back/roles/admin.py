from django.contrib import admin

from .models import Group, Role

admin.site.register(Group)
admin.site.register(Role)
