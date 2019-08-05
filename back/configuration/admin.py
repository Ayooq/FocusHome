from django.contrib import admin

from .models import Configuration, Datatype, Group

admin.site.register(Group)
admin.site.register(Datatype)
admin.site.register(Configuration)
