from django.db.models import F, Q
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from .models import Supplier, Devices, Department, Employee, Responsible
from django.utils import timezone
from datetime import datetime
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
            device.inv_num = request.POST.get("edit_inv_num")
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
        inv_num = request.POST.get('inv_num')
        supplier = Supplier.objects.get(id=dev_supplier)
        if dev_manufact  and dev_model and dev_type and inv_num and dev_number and dev_buydate and supplier and dev_status:
            Devices.objects.create(
            dev_manufact=dev_manufact,
            dev_model=dev_model,
            dev_type=dev_type,
            inv_num = inv_num,
            dev_number=dev_number,
            dev_buydate=dev_buydate,
            dev_supplier=supplier,
            dev_status=dev_status,
        )
        return redirect('devices')


        return redirect("device_list")
    return render(request,"inventory_devices/html/devices.html",{'devices':devices_list,'device_types': device_types,'suppliers':suppliers_list,'device_status':device_status })
def departments(request):
    if request.method == 'POST' and 'delete_id' in request.POST:
        department_id = request.POST.get('delete_id')
        try:
            print(department_id)
            department = Department.objects.get(id=department_id)
            department.delete()
            success = True
        except Devices.DoesNotExist:
            pass
        return redirect('departments')
    if request.method == "POST" and "edit_dep_mode" in request.POST:
        depart_id = request.POST.get("edit_dep_id")
        try:
            department = Department.objects.get(id=depart_id)

            department.name= request.POST.get("edit_dep_name")
            department.phone = request.POST.get("edit_dep_phone")
            department.address = request.POST.get("edit_dep_address")

            department.save()
        except Department.DoesNotExist:
            pass
        return redirect('departments')
    if request.method == 'POST':
        dep_name = request.POST.get('dep_name')
        dep_phone = request.POST.get('dep_phone')
        dep_address = request.POST.get('dep_address')

        if dep_name and dep_phone and dep_address:
            Department.objects.create(
                name=dep_name,
                phone=dep_phone,
                address=dep_address
            )
        return redirect('departments')
    departments = Department.objects.all()
    return render(request,"inventory_devices/html/departments.html",{'departments':departments})
def employees(request):
    employees = Employee.objects.all()
    departments = Department.objects.all()
    if request.method == 'POST' and 'delete_id' in request.POST:
        employee_id = request.POST.get('delete_id')
        try:
            employee = Employee.objects.get(id=employee_id)
            employee.delete()
            success = True
        except Employee.DoesNotExist:
            pass
        return redirect('employees')
    if request.method == "POST" and "edit_emp_mode" in request.POST:
        employee_id = request.POST.get("edit_emp_id")
        department_id = request.POST.get("edit_emp_department")
        try:
            employee = Employee.objects.get(id=employee_id)
            department = Department.objects.get(id=department_id)

            employee.name = request.POST.get("edit_emp_name")
            employee.email = request.POST.get("edit_emp_email")
            employee.phone = request.POST.get("edit_emp_phone")
            employee.post = request.POST.get("edit_emp_post")
            employee.department = department

            employee.save()
        except Employee.DoesNotExist:
            pass
        return redirect('employees')
    if request.method == 'POST':
        emp_name = request.POST.get('emp_name')
        emp_email = request.POST.get('emp_email')
        emp_phone = request.POST.get('emp_phone')
        emp_post = request.POST.get('emp_post')
        emp_department = request.POST.get('emp_department')
        department = Department.objects.get(id=emp_department)
        if emp_name  and emp_email and emp_phone and emp_post and department:
            Employee.objects.create(
            name=emp_name,
            email=emp_email,
            phone=emp_phone,
            post=emp_post,
            department=department,
        )
        return redirect('employees')

    return render(request,"inventory_devices/html/employees.html",{'employees':employees,'departments':departments})
def devices_responsible(request):
    error_message = None
    repsponsibles = Responsible.objects.all()
    devices = Devices.objects.all()
    employees = Employee.objects.all()
    if request.method == 'POST':
        if 'edit_id' in request.POST:
            responsible_id = request.POST.get('edit_id')
            device_id = request.POST.get('edit_inv_num')
            employee_id = request.POST.get('edit_employee')
            edit_date_as = request.POST.get('edit_date_assigned')
            edit_date_re = request.POST.get('edit_date_return')

            try:
                responsible = Responsible.objects.get(id=responsible_id)
                device = Devices.objects.get(id=device_id)
                employee = Employee.objects.get(id=employee_id)
                date_assigned = datetime.strptime(edit_date_as, '%Y-%m-%d').date()
                date_returned = datetime.strptime(edit_date_re, '%Y-%m-%d').date() if edit_date_re else None

                if date_returned and date_returned < date_assigned:
                    error_message = "Дата возврата не может быть раньше даты выдачи."
                else:
                    overlapping_assignments = Responsible.objects.filter(
                        device=device
                    ).filter(
                        Q(date_assigned__lte=date_assigned) &
                        (Q(date_returned__isnull=True) | Q(date_returned__gte=date_assigned))
                    ).exclude(id=responsible_id)

                    if overlapping_assignments.exists():
                        error_message = "Устройство не может быть выдано на эту дату, так как уже назначено другому сотруднику."
                    else:
                        responsible.device = device
                        responsible.employee = employee
                        responsible.date_assigned = date_assigned
                        responsible.date_returned = date_returned
                        responsible.save()
                        messages.success(request, "Запись успешно обновлена.")
                        return redirect('devices_responsible')
            except Responsible.DoesNotExist:
                error_message = "Запись не найдена."
            except Devices.DoesNotExist:
                error_message = "Устройство не найдено."
            except Employee.DoesNotExist:
                error_message = "Сотрудник не найден."
            except ValueError as e:
                error_message = str(e)
        elif 'return_mode' in request.POST:
            device_id = request.POST.get('return_device_id')
            resp_id = request.POST.get('return_id')
            date_asigned = request.POST.get('return_date_assignedd')
            date_returned = request.POST.get("date_returned")


            try:

                responsible = Responsible.objects.get(id=resp_id)
                device = Devices.objects.get(id=device_id)

                date_asigned = datetime.strptime(date_asigned, '%d-%m-%Y')
                date_returned = datetime.strptime(date_returned, '%Y-%m-%d')

                if date_returned < date_asigned:
                    error_message = "Дата возврата не может быть раньше выдачи"
                else:
                    overlapping_returns = Responsible.objects.filter(
                        device=device
                    ).filter(
                        Q(date_assigned__lte=date_returned) &
                        (Q(date_returned__isnull=True) | Q(date_returned__gte=date_returned))
                    ).exclude(id=resp_id)  # Исключаем текущую запись, чтобы не сравнивать саму с собой

                    if overlapping_returns.exists():
                        error_message = "Устройство не может быть возвращено, так как оно назначено другому сотруднику на эту дату."
                    else:
                        responsible.date_returned = date_returned
                        responsible.status = "Возвращено"
                        responsible.device = device
                        responsible.save()

                        device.dev_status = "На складе"
                        device.save()

                        messages.success(request, "Устройство успешно возвращено.")
                        return redirect('devices_responsible')

            except Responsible.DoesNotExist:
                error_message = "Ответственный не найден."
            except ValueError as e:
                error_message = str(e)
        elif request.method == 'POST' and 'delete_id' in request.POST:
            responsible_id = request.POST.get('delete_id')
            try:
                responsible = Responsible.objects.get(id=responsible_id)
                responsible.delete()
                success = True
            except Responsible.DoesNotExist:
                pass
            return redirect('devices_responsible')
        else:  # Обработка выдачи устройства
            device_id = request.POST.get('res_dev')
            employee_id = request.POST.get('res_emp')
            date_assigned = request.POST.get('date_assigned')

            try:
                device = Devices.objects.get(id=device_id)
                employee = Employee.objects.get(id=employee_id)

                if date_assigned and device and employee:
                    date_assigned = timezone.datetime.strptime(date_assigned, '%Y-%m-%d').date()

                    # Проверка, используется ли устройство в указанную дату и не было ли возвращено
                    if Responsible.objects.filter(device=device, date_returned__isnull=True).exists():
                        error_message = "Это устройство уже выдано другому сотруднику и не было возвращено."
                    else:
                        # Проверка на пересечение дат
                        overlapping_assignments = Responsible.objects.filter(
                            device=device
                        ).filter(
                            Q(date_assigned__lte=date_assigned) &
                            (Q(date_returned__isnull=True) | Q(date_returned__gte=date_assigned))
                        )

                        if overlapping_assignments.exists():
                            error_message = "Устройство не может быть выдано, так как оно уже назначено на эту дату."
                        else:
                            Responsible.objects.create(
                                date_assigned=date_assigned,
                                employee=employee,
                                device=device,
                            )
                            device.dev_status = "В эксплуатации"
                            device.save()
                            messages.success(request, "Устройство успешно выдано.")
                            return redirect('devices_responsible')  # Перенаправление без аргументов

            except Devices.DoesNotExist:
                error_message = "Устройство не найдено."
            except Employee.DoesNotExist:
                error_message = "Сотрудник не найден."
            except Exception as e:
                error_message = str(e)

    return render(request, "inventory_devices/html/devices_responsible.html", {
        'repsponsibles': repsponsibles,
        'devices': devices,
        'employees': employees,
        'error_message': error_message
    })
