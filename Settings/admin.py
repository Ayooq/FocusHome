from django.contrib import admin
from Settings.models import Settings, Groups, Types
# Register your models here.

admin.site.register(Groups)
admin.site.register(Types)
admin.site.register(Settings)