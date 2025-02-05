from django.db import models

# Create your models here.
class Supplier(models.Model):
    supp_name = models.CharField(max_length=100, verbose_name="Имя поставщика")
    supp_phone = models.CharField(max_length=15, verbose_name="Телефон поставщика")
    supp_address = models.TextField(verbose_name="Адрес поставщика")

    def __str__(self):
        return self.supp_name