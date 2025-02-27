from django.contrib import admin
from .models import Supplier, Devices, Department, Employee

admin.site.register(Supplier)
admin.site.register(Devices)
admin.site.register(Department)
admin.site.register(Employee)