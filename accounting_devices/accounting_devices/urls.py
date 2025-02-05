from django.urls import path
from django.contrib import admin
from inventory_devices import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),  # Главная страница
    path('suppliers/', views.suppliers, name='suppliers'),  # Страница поставщиков

]
