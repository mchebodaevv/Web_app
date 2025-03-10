from inventory_devices.models import Responsible, Devices, Employee
from datetime import date

# Замените на существующие экземпляры
device = Devices.objects.first()  # Получите первый экземпляр устройства
employee = Employee.objects.first()  # Получите первого сотрудника

responsible = Responsible(
    device=device,
    employee=employee,
    date_assigned=date.today(),
    date_returned=None  # Или укажите дату возврата, если необходимо
)

responsible.save()  # Попробуйте сохранить