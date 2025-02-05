from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Supplier
def index(request):
    return render(request,"inventory_devices/html/index.html")
from django.shortcuts import render, redirect
from .models import Supplier


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
