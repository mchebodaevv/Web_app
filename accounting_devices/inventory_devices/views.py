from django.db.models import F, Q
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from .models import Supplier, Devices, Department, Employee, Responsible, Applications,Performer,Service, DeviceOperationLog
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout

def login_view(request):
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Проверяем, правильно ли введены данные
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Если пользователь найден, выполняем вход
            login(request, user)
            return redirect('home')  # Перенаправляем на домашнюю страницу после входа
        else:
            # Если данные неправильные, показываем ошибку
            return render(request, 'login.html', {'error': 'Неверное имя пользователя или пароль'})

    return render(request, 'login.html')
def user_logout(request):
    logout(request)  # Выход из системы
    return redirect('home')
def is_admin(user):
    return user.groups.filter(name="Администратор").exists()
def is_user(user):
    return user.groups.filter(name="Пользователь").exists()
@login_required
def index(request):
    total_count = Devices.objects.count()
    storage_count = Devices.objects.filter(dev_status="На складе").count()
    in_use_count = Devices.objects.filter(dev_status="В эксплуатации").count()
    written_off_count = Devices.objects.filter(dev_status="Списано").count()
    context = {
        'storage_count': storage_count,
        'in_use_count': in_use_count,
        'written_off_count': written_off_count,
        'total_count': total_count
    }

    return render(request, "inventory_devices/html/index.html", context)
@login_required
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
@login_required
@user_passes_test(is_admin)
def devices(request):
    devices_list = Devices.objects.all()
    device_types = Devices.DEVICE_TYPES
    suppliers_list = Supplier.objects.all()
    device_status = Devices.STATUS_CHOICES
    if request.method == 'POST' and 'delete_id' in request.POST:
        device_id = request.POST.get('delete_id')
        try:
            device = Devices.objects.get(id=device_id)
            device.delete()

            # Логирование операции удаления устройства

            success = True
        except Devices.DoesNotExist:
            pass
        return redirect('devices')
    if request.method == "POST" and "writeoff_mode" in request.POST:
        device_id = request.POST.get("writeoff_id")
        writeoff_date_str = request.POST.get("dev_writeoff")
        try:
            device = Devices.objects.get(id=device_id)
            buy_date = device.dev_buydate
            writeoff_date = datetime.strptime(writeoff_date_str, "%Y-%m-%d").date()

            if writeoff_date < buy_date:
                # Пример с messages
                return render(request, 'inventory_devices/html/devices.html', {
                    'devices': Devices.objects.all(),
                    'error_message': "Дата списания не может быть раньше даты покупки."
                })

            device.dev_status = "Списано"
            device.dev_writeoff = writeoff_date
            device.save()
            DeviceOperationLog.objects.create(
                device=device,
                operation_type='Списание',
                description=f"Списано устройство: {device.dev_manufact} {device.dev_model} (#{device.inv_num})",
            )
        except Devices.DoesNotExist:
            pass
        return redirect('devices')
    if request.method == "POST" and "edit_dev_mode" in request.POST:
        device_id = request.POST.get("edit_dev_id")
        dev_supplier_id = request.POST.get("edit_dev_supplier")
        try:
            device = Devices.objects.get(id=device_id)
            supplier = Supplier.objects.get(id=dev_supplier_id)

            # Получаем старые значения устройства для описания изменений
            old_manufact = device.dev_manufact
            old_model = device.dev_model
            old_inv_num = device.inv_num
            old_status = device.dev_status

            # Обновляем данные устройства
            device.dev_manufact = request.POST.get("edit_dev_manufact")
            device.dev_model = request.POST.get("edit_dev_model")
            device.dev_type = request.POST.get("dev_type")
            device.inv_num = request.POST.get("edit_inv_num")
            device.dev_number = request.POST.get("edit_dev_number")
            device.dev_buydate = request.POST.get("edit_dev_buydate")
            device.dev_supplier = supplier  # Передаем объект, а не id
            device.dev_status = request.POST.get("edit_dev_status")

            device.save()

            # Запись в журнал операций
            DeviceOperationLog.objects.create(
                device=device,
                operation_type='Редактирование',
                description=(
                    f"Изменены данные устройства: {old_manufact} {old_model} (#{old_inv_num}) -> "
                    f"{device.dev_manufact} {device.dev_model} (#{device.inv_num})"
                ),
            )
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
        dev_status = "На складе"
        inv_num = request.POST.get('inv_num')
        supplier = Supplier.objects.get(id=dev_supplier)
        if dev_manufact  and dev_model and dev_type and inv_num and dev_number and dev_buydate and supplier and dev_status:
            device = Devices.objects.create(
            dev_manufact=dev_manufact,
            dev_model=dev_model,
            dev_type=dev_type,
            inv_num = inv_num,
            dev_number=dev_number,
            dev_buydate=dev_buydate,
            dev_supplier=supplier,
            dev_status=dev_status,
        )
            DeviceOperationLog.objects.create(
                device=device,
                operation_type='Создание',
                description=f"Добавлено устройство: {dev_manufact} {dev_model} (#{inv_num})",
            )
        return redirect('devices')


        return redirect("device_list")
    return render(request,"inventory_devices/html/devices.html",{'devices':devices_list,'device_types': device_types,'suppliers':suppliers_list,'device_status':device_status })
@login_required
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
@login_required
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
@login_required
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

                        DeviceOperationLog.objects.create(
                            device=responsible.device,
                            employee=responsible.employee,
                            operation_type='Возврат',
                            description=f"Устройство {device.dev_manufact} {device.dev_model} (#{device.inv_num}) возвращено сотрудником {responsible.employee}: ",
                        )
                        print(123)
                        device.dev_status = "На складе"
                        device.save()
                        responsible.save()

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
                            DeviceOperationLog.objects.create(
                                device=device,
                                employee=employee,
                                operation_type='Выдача',
                                description=f"Устройство {device.dev_manufact} {device.dev_model} (#{device.inv_num}) выдано сотруднику {employee}: ",
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
@login_required
def employee_devices(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        devices = Responsible.objects.filter(employee=employee,date_returned__isnull=True)  # Только не возвращенные устройства
    except Employee.DoesNotExist:
        devices = None

    return render(request, "inventory_devices/html/employee_devices.html", {
        "employee": employee,
        "devices": devices
    })
@login_required
def applications(request):
    applications = Applications.objects.all()
    devices = Devices.objects.all()
    employees = Employee.objects.all()
    if request.method == 'POST':
        device_id = request.POST.get('app_dev')
        employee_id = request.POST.get('app_emp')
        description = request.POST.get('app_desc')
        device = Devices.objects.get(id=device_id)
        employee = Employee.objects.get(id=employee_id)
        if description  and device and employee:
            Applications.objects.create(
            device=device,
            employee=employee,
            description=description,
        )
        return redirect('applications')
    return render(request,"inventory_devices/html/applications.html",{'applications':applications,'devices':devices,'employees':employees})
@login_required
def my_devices(request):
    try:
        employee = Employee.objects.get(user=request.user)  # Находим сотрудника, привязанного к пользователю
        devices = Responsible.objects.filter(employee=employee,
                                             date_returned__isnull=True)  # Только активные устройства
    except Employee.DoesNotExist:
        devices = None

    return render(request, "inventory_devices/html/my_devices.html", {
        "devices": devices
    })
@login_required
def my_applications(request):
    try:
        employee = Employee.objects.get(user=request.user)  # Находим сотрудника, привязанного к пользователю
        devices = Responsible.objects.filter(employee=employee,
                                             date_returned__isnull=True)  # Только активные устройства
        applications = Applications.objects.filter(employee=employee)
    except Employee.DoesNotExist:
        devices = None
    if request.method == 'POST' and 'delete_id' in request.POST:
        device_id = request.POST.get('delete_id')
        try:
            print(device_id)
            device = Applications.objects.get(id=device_id)
            device.delete()
            success = True
        except Devices.DoesNotExist:
            pass
        return redirect('devices')
    if request.method == 'POST' and 'edit_mode' in request.POST:
        emp_id = request.POST.get('edit_id')
        descript = request.POST.get('edit_description')
        try:
            my_app = Applications.objects.get(id=emp_id)
            my_app.description =  descript
            my_app.save()
        except Employee.DoesNotExist:
            pass
        return redirect('my_applications')
    elif request.method == 'POST':

        emp_id = request.POST.get('emp_id')
        dev = request.POST.get('dev')
        app_desc = request.POST.get('app_desc')
        device = Devices.objects.get(id=dev)
        employee = Employee.objects.get(id=emp_id)
        if app_desc and device and employee:
            Applications.objects.create(
                device=device,
                employee=employee,
                description=app_desc,
            )
        return redirect('my_applications')
    return render(request, "inventory_devices/html/my_applications.html", {
        "devices": devices,
        "applications": applications,

    })
def performers(request):
    performers = Performer.objects.all()
    if request.method == 'POST' and 'delete_id' in request.POST:
        supplier_id = request.POST.get('delete_id')
        try:
            supplier = Performer.objects.get(id=supplier_id)
            supplier.delete()
        except Supplier.DoesNotExist:
            pass
        return redirect('performers')
    if request.method == "POST" and "edit_mode" in request.POST:
        performer_id = request.POST.get("edit_id")
        try:
            performer = Performer.objects.get(id=performer_id)
            performer.name = request.POST.get("edit_name")
            performer.phone = request.POST.get("edit_phone")
            performer.address = request.POST.get("edit_address")
            performer.save()
        except Employee.DoesNotExist:
            pass
        return redirect('performers')
    if request.method == 'POST':
        p_name = request.POST.get('p_name')
        p_phone = request.POST.get('p_phone')
        p_address = request.POST.get('p_address')
        if p_name  and p_phone and p_address :
            Performer.objects.create(
            name=p_name,
            phone=p_phone,
            address=p_address,
        )
    return render(request, "inventory_devices/html/performers.html", {
        "performers": performers,
    })
@login_required
def service(request):
    services = Service.objects.all()
    performers = Performer.objects.all()
    applications = Applications.objects.filter(status='Новая')
    error_message = None
    if request.method == 'POST':
        # Удаление услуги
        if 'delete_id' in request.POST:
            service_id = request.POST.get('delete_id')
            try:
                service = Service.objects.get(id=service_id)
                service.delete()
            except Service.DoesNotExist:  # Исправлено с Supplier на Service
                error_message = "Услуга не найдена."
            return redirect('service')

        # Редактирование услуги
        if "edit_mode" in request.POST:
            service_id = request.POST.get("edit_id")
            try:
                service = Service.objects.get(id=service_id)
                performer_id = request.POST.get("edit_performer")
                application_id = request.POST.get("edit_ap_id")
                description = request.POST.get("edit_description")
                date_str = request.POST.get("edit_date")  # Получаем дату в виде строки
                print(date_str)
                service.performer = Performer.objects.get(id=performer_id)
                service.description = description

                if date_str:  # Проверяем, что дата была передана
                    date_service = datetime.strptime(date_str, '%Y-%m-%d').date()
                    application = Applications.objects.get(id=application_id)

                    if date_service < application.created_at.date():
                        error_message = "Дата обслуживания не может быть раньше даты заявки."
                    else:
                        service.dev_buydate = date_service  # Обновляем дату
                        service.save()  # Сохраняем изменения

            except Service.DoesNotExist:
                error_message = "Услуга не найдена."
            except Performer.DoesNotExist:
                error_message = "Исполнитель не найден."
            except Applications.DoesNotExist:
                error_message = "Заявка не найдена."
            except ValueError:
                error_message = "Некорректный формат даты."


        # Добавление новой услуги
        else:
            application_id = request.POST.get('applications')
            performer_id = request.POST.get('performer')
            date_ser = request.POST.get('edit_date')  # Исправлен параметр
            descript = request.POST.get('desc')

            try:
                application = Applications.objects.get(id=application_id)
                performer = Performer.objects.get(id=performer_id)

                if date_ser:
                    date_service = datetime.strptime(date_ser, '%Y-%m-%d').date()
                    if date_service < application.created_at.date():
                        error_message = "Дата обслуживания не может быть раньше даты заявки."
                    else:
                        Service.objects.create(
                            application=application,
                            performer=performer,
                            description=descript,
                            date=date_service  # Исправленное поле
                        )
                        application.status = 'Закрыта'
                        application.save()
            except Applications.DoesNotExist:
                error_message = "Заявка не найдена."
            except Performer.DoesNotExist:
                error_message = "Исполнитель не найден."
            except ValueError:
                error_message = "Некорректный формат даты."

    return render(request, "inventory_devices/html/service.html", {
        'services': services,
        'applications': applications,
        'performers': performers,
        'error_message': error_message  # Теперь error_message передаётся в шаблон
    })
@login_required
def operation_log(request):
    operation_log = DeviceOperationLog.objects.all()
    return render(request, "inventory_devices/html/operation_log.html",{'operation_log':operation_log})
def device_history(request, device_id):
    device = get_object_or_404(Devices, id=device_id)
    history = DeviceOperationLog.objects.filter(device=device).order_by('-timestamp')
    return render(request, 'inventory_devices/html/device_history.html', {'device': device, 'history': history})