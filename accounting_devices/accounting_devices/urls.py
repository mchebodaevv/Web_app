from django.urls import path
from django.contrib import admin
from inventory_devices import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),  # Главная страница
    path('suppliers/', views.suppliers, name='suppliers'),
    path('devices/', views.devices, name='devices'), #Страница поставщиков
    path('departments/', views.departments, name='departments'),
    path('employees/', views.employees, name='employees'),
    path('devices_responsible/', views.devices_responsible, name='devices_responsible'),
]
