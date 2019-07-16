from django.contrib import admin
from Roles.models import Roles, Group
# Register your models here.

admin.site.register(Group)
admin.site.register(Roles)