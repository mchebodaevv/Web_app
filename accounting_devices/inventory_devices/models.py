from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
class Supplier(models.Model):
    supp_name = models.CharField(max_length=100, verbose_name="Имя поставщика")
    supp_phone = models.CharField(max_length=25, verbose_name="Телефон поставщика")
    supp_address = models.TextField(verbose_name="Адрес поставщика")

    def __str__(self):
        return self.supp_name
class Devices(models.Model):
    DEVICE_TYPES = [
        ("Мышь", "Мышь"),
        ("Клавиатура", "Клавиатура"),
        ("Монитор", "Монитор"),
        ("Принтер", "Принтер"),
        ("Другое", "Другое"),
    ]

    STATUS_CHOICES = [
        ("На складе", "На складе"),
        ("В эксплуатации", "В эксплуатации"),
        ("В ремонте", "В ремонте"),
        ("Списано", "Списано"),
    ]

    dev_manufact = models.CharField(max_length=100, verbose_name="Производитель")
    dev_model = models.CharField(max_length=100, verbose_name="Модель")
    dev_type = models.CharField(max_length=45, choices=DEVICE_TYPES, verbose_name="Тип")
    inv_num = models.CharField(max_length=50, unique=True, verbose_name="Инвентарный номер")
    dev_number = models.CharField(max_length=50, unique=True, verbose_name="Серийный номер")
    dev_buydate = models.DateField(verbose_name="Дата покупки")
    dev_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Поставщик")
    dev_status = models.CharField(max_length=45, choices=STATUS_CHOICES, verbose_name="Статус")
    def __str__(self):
        return f"{self.dev_manufact} {self.dev_model}"
class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название отдела")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес")
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"
class Employee(models.Model):
    ROLE_CHOICES = (
        ("admin", "Администратор"),
        ("user", "Пользователь"),
    )
    name = models.CharField(max_length=100, verbose_name="ФИО")
    email = models.EmailField(max_length=100, verbose_name="Электронная почта")
    phone = models.CharField(max_length=50, unique=True, verbose_name="Номер телефона")
    post = models.CharField(max_length=50, verbose_name="Должность")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Отдел")
    login = models.CharField(max_length=50, unique=True, null=True, verbose_name="Логин")
    us_password = models.CharField(max_length=50, null=True, verbose_name="Пароль")  # Удалите после миграции
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user", verbose_name="Роль")

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Связь с User
    def __str__(self):
        return self.name
@receiver(pre_save, sender=Employee)
def check_login_change(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Employee.objects.get(pk=instance.pk)
        if old_instance.login and old_instance.login != instance.login:
            try:
                User.objects.get(username=old_instance.login).delete()
            except User.DoesNotExist:
                pass
@receiver(post_save, sender=Employee)
def create_or_update_user(sender, instance, created, **kwargs):
    if instance.login:
        user, created = User.objects.get_or_create(username=instance.login)

        user.email = instance.email
        user.is_active = True

        if instance.us_password:
            user.set_password(instance.us_password)

        user.save()

        # Назначаем роли через группы
        admin_group, _ = Group.objects.get_or_create(name="Администратор")
        user_group, _ = Group.objects.get_or_create(name="Пользователь")

        user.groups.clear()  # Удаляем из всех групп перед добавлением в нужную

        if instance.role == "admin":
            user.groups.add(admin_group)
            user.is_staff = True
        else:
            user.groups.add(user_group)
            user.is_staff = False

        user.save()

        # Привязываем пользователя к сотруднику
        if instance.user != user:
            instance.user = user
            instance.save(update_fields=["user"])  # Обновляем поле без лишних изменений
@receiver(post_delete, sender=Employee)
def delete_user_when_employee_deleted(sender, instance, **kwargs):
    """Удаляем пользователя при удалении сотрудника"""
    if instance.user:
        instance.user.delete()
class Responsible(models.Model):
    STATUS_CHOICES = [
        ("Выдано","Выдано"),
        ("Возвращено", "Возвращено"),
    ]
    device = models.ForeignKey(Devices, on_delete=models.CASCADE, verbose_name="Устройство")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    date_assigned = models.DateField(verbose_name="Дата выдачи")
    date_returned = models.DateField(null=True, blank=True, verbose_name="Дата возврата")
    status = models.CharField(max_length=45, choices=STATUS_CHOICES,default="Выдано", verbose_name="Статус")
    class Meta:
        unique_together = ('device', 'date_returned')  # Уникальность по устройству и дате возврата
        constraints = [
            models.UniqueConstraint(fields=['device', 'date_assigned'], name='unique_device_assignment')
        ]

    def __str__(self):
        return f"{self.device} выдано {self.employee} на {self.date_assigned}"
class Applications(models.Model):
    device = models.ForeignKey('Devices', on_delete=models.CASCADE, related_name="service_requests")
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name="requests")
    description = models.TextField()
    status = models.CharField(max_length=20, default='Новая')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Заявка {self.id} – {self.device.dev_model}"
class Performer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=25, verbose_name="Телефон ")
    address = models.TextField(verbose_name="Адрес ")

    def __str__(self):
        return f"{self.name}"
class Service(models.Model):
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, verbose_name="Заявка")
    performer = models.ForeignKey(Performer, on_delete=models.CASCADE, verbose_name="Исполнитель")
    description = models.TextField()
    dev_buydate = models.DateField(verbose_name="Дата обслуживания")
    def __str__(self):
        return f"Обслуживание №{self.id}"
class DeviceOperationLog(models.Model):
    OPERATION_CHOICES = (
        ('Создание', 'Создание устройства'),
        ('Редактирование', 'Изменение устройства'),
        ('Удаление', 'Удаление устройства'),
        ('Передача', 'Передача устройства'),
        ('Возврат', 'Возврат устройства'),
    )

    device = models.ForeignKey(Devices, on_delete=models.CASCADE, related_name='operation_logs')
    operation_type = models.CharField(max_length=40, choices=OPERATION_CHOICES)
    description = models.TextField(null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.operation_type} - {self.device} - {self.timestamp}"