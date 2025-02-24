from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Supplier,Devices
def index(request):
    return render(request,"inventory_devices/html/index.html")

def suppliers(request):
    success = False
    if request.method == 'POST' and 'delete_id' in request.POST:
        supplier_id = request.POST.get('delete_id')
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            supplier.delete()
            success = True
        except Supplier.DoesNotExist:
            pass
        return redirect('suppliers')
    # Обработка редактирования
    if request.method == 'POST' and 'edit_mode' in request.POST:
        supplier_id = request.POST.get('supplier_id')
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            supplier.supp_name = request.POST.get('supp_name')
            supplier.supp_phone = request.POST.get('supp_phone')
            supplier.supp_address = request.POST.get('supp_address')
            supplier.save()
            success = True
        except Supplier.DoesNotExist:
            pass
        return redirect('suppliers')

    # Обработка создания нового поставщика
    if request.method == 'POST':
        supp_name = request.POST.get('supp_name')
        supp_phone = request.POST.get('supp_phone')
        supp_address = request.POST.get('supp_address')

        if supp_name and supp_phone and supp_address:
            Supplier.objects.create(
                supp_name=supp_name,
                supp_phone=supp_phone,
                supp_address=supp_address
            )
            success = True
        return redirect('suppliers')

    suppliers_list = Supplier.objects.all()
    return render(request, "inventory_devices/html/suppliers.html", {
        'suppliers': suppliers_list,
        'success': success,
    })
def devices(request):
    devices_list = Devices.objects.all()
    device_types = Devices.DEVICE_TYPES
    suppliers_list = Supplier.objects.all()
    device_status = Devices.STATUS_CHOICES
    if request.method == 'POST' and 'delete_id' in request.POST:
        device_id = request.POST.get('delete_id')
        try:
            print(device_id)
            device = Devices.objects.get(id=device_id)
            device.delete()
            success = True
        except Devices.DoesNotExist:
            pass
        return redirect('devices')
    if request.method == "POST" and "edit_dev_mode" in request.POST:
        device_id = request.POST.get("edit_dev_id")
        dev_supplier_id = request.POST.get("edit_dev_supplier")

        try:
            device = Devices.objects.get(id=device_id)
            supplier = Supplier.objects.get(id=dev_supplier_id)

            device.dev_manufact = request.POST.get("edit_dev_manufact")
            device.dev_model = request.POST.get("edit_dev_model")
            device.dev_type = request.POST.get("dev_type")
            device.dev_number = request.POST.get("edit_dev_number")
            device.dev_buydate = request.POST.get("edit_dev_buydate")
            device.dev_supplier = supplier  # Передаем объект, а не id
            device.dev_status = request.POST.get("edit_dev_status")

            device.save()
        except Devices.DoesNotExist:
            pass
        return redirect('devices')
    if request.method == 'POST':
        dev_manufact = request.POST.get('dev_manufact')
        dev_model = request.POST.get('dev_model')
        dev_type = request.POST.get('dev_type')
        dev_number = request.POST.get('dev_number')
        dev_buydate = request.POST.get('dev_buydate')
        dev_supplier = request.POST.get('dev_supplier')
        dev_status = request.POST.get('dev_status')
        supplier = Supplier.objects.get(id=dev_supplier)
        if dev_manufact  and dev_model and dev_type and dev_number and dev_buydate and supplier and dev_status:
            Devices.objects.create(
            dev_manufact=dev_manufact,
            dev_model=dev_model,
            dev_type=dev_type,
            dev_number=dev_number,
            dev_buydate=dev_buydate,
            dev_supplier=supplier,
            dev_status=dev_status,
        )
        return redirect('devices')


        return redirect("device_list")
    return render(request,"inventory_devices/html/devices.html",{'devices':devices_list,'device_types': device_types,'suppliers':suppliers_list,'device_status':device_status })