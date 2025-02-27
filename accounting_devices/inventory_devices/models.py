from django.db import models


class Supplier(models.Model):
    supp_name = models.CharField(max_length=100, verbose_name="Имя поставщика")
    supp_phone = models.CharField(max_length=15, verbose_name="Телефон поставщика")
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
    dev_type = models.CharField(max_length=15, choices=DEVICE_TYPES, verbose_name="Тип")
    dev_number = models.CharField(max_length=50, unique=True, verbose_name="Серийный номер")
    dev_buydate = models.DateField(verbose_name="Дата покупки")
    dev_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Поставщик")
    dev_status = models.CharField(max_length=15, choices=STATUS_CHOICES, verbose_name="Статус")
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
    name = models.CharField(max_length=100, verbose_name="ФИО")
    email = models.CharField(max_length=100, verbose_name="Электронная почта")
    phone = models.CharField(max_length=50, unique=True, verbose_name="Номер телефона")
    post = models. CharField(max_length=50,verbose_name="Должность")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Отдел")
    def __str__(self):
        return f"{self.name}"