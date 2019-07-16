from django.contrib import admin
from DeviceUnits.models import Units, Family, ClientUnits

# Register your models here.
admin.site.register(Units)
admin.site.register(Family)
admin.site.register(ClientUnits)
