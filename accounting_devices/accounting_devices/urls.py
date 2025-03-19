from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from inventory_devices import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),  # Главная страница
    path('suppliers/', views.suppliers, name='suppliers'),
    path('devices/', views.devices, name='devices'), #Страница поставщиков
    path('departments/', views.departments, name='departments'),
    path('employees/', views.employees, name='employees'),
    path('devices_responsible/', views.devices_responsible, name='devices_responsible'),
    path('applications/', views.applications, name='applications'),
    path('service/', views.service, name='service'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path("employees/<int:employee_id>/devices/", views.employee_devices, name="employee_devices"),
    path("my-devices/", views.my_devices, name="my_devices"),
    path("my-applications/", views.my_applications, name="my_applications"),
]
