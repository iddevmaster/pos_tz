from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
# from django.http import HttpResponse, response
from datetime import date, timedelta
from dateutil import rrule
import json
from datetime import datetime
from ..forms.student_form import studentForm
from ..constant import defaultTitle, api_id_card
from ..models import category_program_permission, course_event, customers, location_thai, register_main, register_payment, register_payment_items, student,register_ref, register_applove, user_group, user_detail
from ..functions import dateTimeIntNow, dateTimeNow, dmytoymd, month_fomat,treeDigit, twoDigit

api_id_card = api_id_card

# https://docs.djangoproject.com/en/1.11/ref/models/querysets/#gt


@login_required(login_url='/login')
def customer_read_idcard(request):
    result = request.POST['data']
    if result is None or result == '':
        messages.error(request, "ไม่สามารถทำรายการได้ !")
        return redirect("/")
    json_data = json.loads(result)
    if json_data is None:
        messages.error(request, "ไม่สามารถทำรายการได้ !")
        return redirect("/")
    request.session['idcard_data'] = json_data
    return redirect("/")


@login_required(login_url='/login')
def register_home(request):
    title = defaultTitle
    user_id = request.user.id
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)


    try:
        idcard_data = request.session['idcard_data']
        Province = idcard_data['Province']
        Amphur = idcard_data['Amphur']
        Tumbol = idcard_data['Tumbol']
        HomeNo = idcard_data['HomeNo']
        Road = idcard_data['Road']
        Moo = idcard_data['Moo']
        Soi = idcard_data['Soi']
        Trok = idcard_data['Trok']
        address = str(HomeNo)

        if Moo != '':
            address += " " + str(Moo)
        if Road != '':
            address += " ถ." + str(Road)
        if Soi != '':
            address += " ซ." + str(Soi)

        if Trok != '':
            address += " " + str(Trok)

    except KeyError:
        idcard_data = None
        Province = None
        Amphur = None
        Tumbol = None
        address = ""
    if idcard_data is not None:
        try:
            _location = location_thai.objects.get(
                province_name__icontains=Province, amphur_name__icontains=Amphur, district_name__icontains=Tumbol)
        except location_thai.DoesNotExist:
            _location = None
    else:
        _location = None
    try:
        register_id = request.session['register_id']
        content_regist = register_main.objects.get(register_id=register_id)
    except KeyError:
        content_regist = None
    # print(register_id)
    _date = date.today()
    hundredDaysLater = _date + timedelta(days=90)
    obj = []
    for dt in rrule.rrule(rrule.MONTHLY, dtstart=datetime(2024, 10, 30), until=hundredDaysLater):
        _newdate = str(dt).split(" ")[0]
        yearstart = _newdate.split("-")[0]
        monthstart = _newdate.split("-")[1]
        label = month_fomat(monthstart) + " " + yearstart
        # print(label)
        result = course_event.objects.select_related("course").filter(
            cancelled=1, active=1, ev_date_start__month=int(monthstart), ev_date_start__year=int(yearstart), module=m.module).order_by("ev_date_start")
        content = {"label": label, "data": result}
        obj.append(content)
    # print(idcard_data)
    context = {'title': title,  'data': obj, 'listMenuPermission': objMenu,'content_regist1': _newdate,
               'content_regist': content_regist, 'idcard_data': idcard_data, 'location': _location, 'address': address, 'api_id_card': api_id_card}
    return render(request, 'register/register.html', context)


@login_required(login_url='/login')
def register_reset(request):
    try:
        del request.session['register_id']
    except KeyError:
        pass

    try:
        del request.session['idcard_data']
    except KeyError:
        pass
    return redirect("/")


@login_required(login_url='/login')
def register_create(request):
    current_user = request.user
    seller_id = current_user.id
    ev_id = request.POST['ev_id']
    customer_type = request.POST['customer_type']
    pay_type = request.POST['pay_type']
    try:
        m = user_group.objects.get(user=seller_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    if int(pay_type) == 1:
        close_the_sale = 1
    else:
        close_the_sale = 0
    object = register_main.objects.create(
        register_number="-",
        customer_type=customer_type,
        customer_status=0,
        pay_type=pay_type,
        pay_status=1,
        close_the_sale=close_the_sale,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow(),
        ev_id=ev_id,
        seller_id=seller_id,
        user_update_id=seller_id,
        module=m.module
    )
    object.refresh_from_db()
    register_id = object.register_id
    # print(register_id)
    request.session['register_id'] = str(register_id)
    return redirect("/")


@login_required(login_url='/login')
def customer_create(request):

    try:
        register_id = request.session['register_id']
        content_regist = register_main.objects.get(register_id=register_id)
        if not content_regist:
            return redirect("/")
    except KeyError:
        register_id = None
        content_regist = None
        return redirect("/")
    chkcustomer = customers.objects.filter(register_id=register_id).count()
    if chkcustomer > 0:
        return redirect("/register/reset")
    customer_code = "C" + str(dateTimeIntNow())
    customer_name = request.POST['customer_name']
    customer_tax = request.POST['customer_tax']
    customer_phone = request.POST['customer_phone']
    customer_email = request.POST['customer_email']
    customer_address = request.POST['customer_address']
    location_id = request.POST['location_id']
    customers.objects.create(
        customer_code=customer_code,
        customer_name=customer_name,
        customer_tax=customer_tax,
        customer_phone=customer_phone,
        customer_email=customer_email,
        customer_address=customer_address,
        location_id=location_id,
        register_id=register_id
    )

    # Update Register
    month_current = date.today().month
    year_current = date.today().year
    year_current_f = str(int(date.today().year) + 543)
    totaldata = register_main.objects.filter(
        crt_date__month=month_current, crt_date__year=year_current).exclude(register_number="-").count()
    running_number = treeDigit(totaldata + 1)
    register_number = "R" + year_current_f[2:4] + "/" + \
        str(twoDigit(month_current)) + "/" + str(running_number)
    content = register_main.objects.get(pk=register_id)
    content.register_number = register_number
    content.save()

    customer_type = content_regist.customer_type
    if customer_type == 1:
        student_firstname_th = request.POST['student_firstname_th']
        student_lastname_th = request.POST['student_lastname_th']
        totaldata = student.objects.filter(
            crt_date__month=month_current, crt_date__year=year_current).count()
        running_number = treeDigit(totaldata + 1)
        student_code = "TZ" + str(twoDigit(month_current)) + \
            str(running_number) + "/" + str(year_current)
        student.objects.create(
            student_identification_number=customer_tax,
            student_prefix_th="",
            student_firstname_th=student_firstname_th,
            student_lastname_th=student_lastname_th,
            student_prefix_eng="",
            student_firstname_eng="",
            student_lastname_eng="",
            student_code=student_code,
            crt_date=dateTimeNow(),
            upd_date=dateTimeNow(),
            register_id=register_id
        )

    try:
        del request.session['register_id']
    except KeyError:
        pass
    try:
        del request.session['idcard_data']
    except KeyError:
        pass
    return redirect("/register/payment/" + str(register_id))


@login_required(login_url='/login')
def register_detail(request, register_id):
    title = defaultTitle
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        content_regist = register_main.objects.get(register_id=register_id)
    except:
        content_regist = None
        return redirect("/")
    content_customer = customers.objects.select_related("location").filter(
        register_id=register_id).first()
    content_course = course_event.objects.select_related(
        "course").get(ev_id=content_regist.ev_id)
    context = {'title': title,  'content_regist': content_regist, 'listMenuPermission': objMenu,
               'content_customer': content_customer, 'content_course': content_course}
    return render(request, 'register/register_detail.html', context)


@login_required(login_url='/login')
def payment(request, register_id):
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)

    title = defaultTitle
    try:
        content = customers.objects.select_related(
            "register", "location").get(register_id=register_id)
    except:
        content = None
        return redirect("/")
    content_regist = register_main.objects.select_related(
        "seller", "ev").prefetch_related("student_register").get(register_id=register_id)

    content_course = course_event.objects.select_related(
        "course").get(ev_id=content_regist.ev_id)
    # ถ้าเป็นบุคคลให้ส่งข้อมูลนักเรียนไปด้วย
    if content_regist.customer_type == 1:
        try:
            student_data = student.objects.filter(
                register_id=register_id).first()
        except:
            student_data = None
    else:
        student_data = None
    # print(content)
    context = {'title': title,  'data': content, 'listMenuPermission': objMenu,
               'content_regist': content_regist, 'content_course': content_course, 'student_data': student_data}
    return render(request, 'register/register_payment.html', context)


@login_required(login_url='/login')
def payment_create(request):
    now = date.today()
    # Main
    register_id = request.POST['register_id']
    rp_code_customer = request.POST['rp_code_customer']
    rp_name_customer = request.POST['rp_name_customer']
    rp_tax = request.POST['rp_tax']
    rp_name_seller = request.POST['rp_name_seller']
    rp_name_contact = request.POST['rp_name_contact']
    rp_branch = request.POST['rp_branch']
    rp_address = request.POST['rp_address']
    rp_phone = request.POST['rp_phone']
    rp_email = request.POST['rp_email']
    rp_confirm_date_price = dmytoymd(
        request.POST.get("rp_confirm_date_price", now.strftime("%d/%m/%Y")))
    rp_date_delivery = dmytoymd(
        request.POST.get("rp_date_delivery", now.strftime("%d/%m/%Y")))

    try:
        rp_quota = request.POST['rp_quota']
    except KeyError:
        rp_quota = 1

    rp_ref1 = request.POST['rp_ref1']
    rp_ref2 = request.POST['rp_ref2']
    content_main = register_main.objects.get(register_id=register_id)
    pay_type = content_main.pay_type
    customer_type = content_main.customer_type
    if pay_type == 1:
        active = 1
    else:
        active = 0
    month_current = date.today().month
    year_current = date.today().year
    year_current_f = str(int(date.today().year) + 543)
    totaldata = register_payment.objects.filter(
        crt_date__month=month_current, crt_date__year=year_current).count()
    running_number = treeDigit(totaldata + 1)
    rp_doc_number = "TZ" + year_current_f[2:4] + "/" + \
        str(twoDigit(month_current)) + "/" + str(running_number)
    # Item
    rpi_code = request.POST['rpi_code']
    rpi_name = request.POST['rpi_name']
    rpi_quantity = request.POST['rpi_quantity']
    rpi_unit = request.POST['rpi_unit']
    rpi_price = request.POST['rpi_price']
    rpi_price_discount = request.POST['rpi_price_discount']
    rpi_price_total = request.POST['rpi_price_total']
    rpi_price_vat = request.POST['rpi_price_vat']
    rpi_price_result = request.POST['rpi_price_result']

    # Crate Main
    object = register_payment.objects.create(
        rp_doc_number=rp_doc_number,
        rp_code_customer=rp_code_customer,
        rp_name_customer=rp_name_customer,
        rp_tax=rp_tax,
        rp_name_seller=rp_name_seller,
        rp_name_contact=rp_name_contact,
        rp_branch=rp_branch,
        rp_address=rp_address,
        rp_phone=rp_phone,
        rp_email=rp_email,
        rp_confirm_date_price=rp_confirm_date_price,
        rp_date_delivery=rp_date_delivery,
        rp_quota=rp_quota,
        rp_ref1=rp_ref1,
        rp_ref2=rp_ref2,
        active=active,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow(),
        register_id=register_id
    )
    object.refresh_from_db()
    rp_id = object.rp_id
    # Create Item
    content_regist = register_main.objects.select_related(
        "ev").get(register_id=register_id)
    ev_vat = content_regist.ev.ev_vat
    # print(ev_vat)

    if ev_vat == 0:
        new_total = rpi_price_total
    else:
        new_total = float(rpi_price_total) - float(rpi_price_vat)
    register_payment_items.objects.create(
        rpi_code=rpi_code,
        rpi_name=rpi_name,
        rpi_quantity=rpi_quantity,
        rpi_unit=rpi_unit,
        rpi_price=rpi_price,
        rpi_price_discount=rpi_price_discount,
        rpi_price_total=new_total,
        rpi_price_vat=rpi_price_vat,
        rpi_price_result=rpi_price_result,
        rpi_pay=rpi_price_result,
        rp_id=rp_id,
        register_id=register_id
    )

    # ถ้ามีการแก้ไขใบเสร็จ / ใบเสนอราคา ให้ทำการเปลี่ยนสถานะเป็นค่าเริ่มต้นทั้งหมด
    check_bill = register_payment.objects.filter(
        register_id=register_id).exclude(rp_id=rp_id)
    if check_bill.count() >= 1 and pay_type == 2:
        check_bill.update(active=0)

    # ตรวจสอบว่ามีการอนุมัติให้แก้ไขหรือยัง จากนั้นให้ทำการเปลี่ยน complete เป็น 1 ทันที
    content_approve = register_applove.objects.filter(
        register_id=register_id, doc_type=1, status=1, complete=0)
    if content_approve.count() > 0:
        content_approve.update(complete=1)
        if pay_type == 2:
            content_main.close_the_sale = 0
            content_main.save()

    # ถ้าเป็นประเภทนักเรียน ให้ นำข้อมูลการสมัครมาบันทึกที่ฐานข้อมูลนักเรียนทันที
    if customer_type == 1:
        # Delete ข้อมูลนักเรียนเก่าทิ้ง
        content = student.objects.get(register_id=register_id)
        content.delete()

        student_firstname_th = request.POST['student_firstname_th']
        student_lastname_th = request.POST['student_lastname_th']
        totaldata = student.objects.filter(
            crt_date__month=month_current, crt_date__year=year_current).count()
        running_number = treeDigit(totaldata + 1)
        student_code = "TZ" + str(twoDigit(month_current)) + \
            str(running_number) + "/" + str(year_current)
        student.objects.create(
            student_identification_number=rp_tax,
            student_prefix_th="",
            student_firstname_th=student_firstname_th,
            student_lastname_th=student_lastname_th,
            student_prefix_eng="",
            student_firstname_eng="",
            student_lastname_eng="",
            student_code=student_code,
            crt_date=dateTimeNow(),
            upd_date=dateTimeNow(),
            register_id=register_id
        )

    messages.success(request, "ทำรายการสำเร็จ !")
    # return redirect("/register/management")
    return redirect("/register/payment/history/" + str(register_id))


@login_required(login_url='/login')
def payment_form_update(request, register_id):
    title = defaultTitle
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        content = customers.objects.select_related(
            "register", "location").get(register_id=register_id)
    except:
        content = None
        return redirect("/register/management")
    content_regist = register_main.objects.select_related(
        "seller", "ev").get(register_id=register_id)
    # if content_regist.close_the_sale > 0:
    #     return redirect("/register/management")
    content_course = course_event.objects.select_related(
        "course").get(ev_id=content_regist.ev_id)
    total_pay = register_payment.objects.filter(
        register_id=register_id).count()
    last_data = register_payment_items.objects.select_related(
        "rp").filter(register_id=register_id).order_by("-rp_id").first()

    if content_regist.customer_type == 1:
        student_data = student.objects.get(register_id=register_id)
    else:
        student_data = None
    # print(total_pay)
    context1 = {'title': title,  'data': content, 'listMenuPermission': objMenu,
                'content_regist': content_regist, 'content_course': content_course}
    context2 = {'title': title,  'data': last_data, 'content_regist': content_regist, 'listMenuPermission': objMenu,
                'content_course': content_course, 'student_data': student_data}
    if total_pay < 1:
        return render(request, 'register/register_payment.html', context1)
    return render(request, 'register/register_payment_update.html', context2)


@login_required(login_url='/login')
def payment_history(request, register_id):
    title = defaultTitle
    user_id = request.user.id
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        main = register_main.objects.get(register_id=register_id)
    except:
        main = None
        return redirect("/")

    # ตรวจสอบว่ามีการอนุมัติยัง
    try:
        content_approve = register_applove.objects.filter(
            register_id=register_id, doc_type=1, status=1, complete=0).order_by("-crt_date").first()
    except:
        content_approve = None
    # ตรวจสอบว่ามีการร้องขออนุมัติไปล่าสุดหรือยัง
    try:
        content_approve_p = register_applove.objects.filter(
            register_id=register_id, doc_type=1, status=0, complete=0).order_by("-crt_date").first()
    except:
        content_approve_p = None

    content = register_payment.objects.filter(
        register_id=register_id).order_by("-rp_id")
    if len(content) < 1:
        return redirect("/register/payment/" + str(register_id))
    list_user = User.objects.filter(is_staff=0, is_active=1,user_group_ref__module=m.module).exclude(pk=user_id)
    obj = []
    for r in content:
        items = register_payment_items.objects.filter(rp_id=r.rp_id).first()
        res = {'main': r, 'items': items}
        obj.append(res)
    context = {'title': title,  'data': obj, 'main': main, 'list_user': list_user, 'listMenuPermission': objMenu,
               'content_approve': content_approve, 'content_approve_p': content_approve_p}
    return render(request, 'register/register_payment_history.html', context)


@login_required(login_url='/login')
def register_approve_create(request):
    current_user = request.user
    user_crt = current_user.id
    register_id = request.POST['register_id']
    user_approve_id = request.POST['user_approve_id']
    remark = request.POST['remark']
    doc_type = request.POST['doc_type']
    register_applove.objects.create(
        doc_type=doc_type,
        remark=remark,
        crt_date=dateTimeNow(),
        register_id=register_id,
        user_approve_id=user_approve_id,
        user_crt_id=user_crt,
    )
    return redirect("/register/payment/history/" + str(register_id))


@login_required(login_url='/login')
def student_list(request, register_id):
    title = defaultTitle
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        main = register_main.objects.select_related(
            "ev").get(register_id=register_id)
    except register_main.DoesNotExist:
        main = None
        return redirect("/")
    # ถ้ายังไม่ปิดการขาย
    if main.close_the_sale < 1:
        return redirect("/")

    try:
        ref_data = register_ref.objects.filter(
            register_id=register_id).order_by('-crt_date').first()
    except:
        ref_data = None

    detail = course_event.objects.select_related(
        "course").get(ev_id=main.ev_id)
    content = student.objects.filter(
        register_id=register_id).order_by('-crt_date')
    payment_data = register_payment.objects.filter(
        register_id=register_id, active=1).order_by('-crt_date').first()
    if payment_data:
        rp_quota = payment_data.rp_quota
    else:
        rp_quota = content.count()
    context = {'title': title,  'data': content, 'listMenuPermission': objMenu,
               'main': main, 'detail': detail, 'rp_quota': rp_quota, 'total_student': content.count(), 'ref_data': ref_data, 'api_id_card': api_id_card}
    # ต้องระบุเลข SQ ก่อนถึงจะให้เพิ่มนักเรียนได้
    if not ref_data and main.customer_type == 2 and main.pay_type == 2:
        return render(request, 'register/student_form_confirm.html', context)
    return render(request, 'register/student_list.html', context)


@login_required(login_url='/login')
def student_ref_create(request):
    current_user = request.user
    user_crt = current_user.id
    register_id = request.POST['register_id']
    ref = request.POST['ref']

    register_ref.objects.create(
        ref=ref,
        crt_date=dateTimeNow(),
        register_id=register_id,
        user_crt_id=user_crt,
    )
    return redirect("/register/studentlist/" + str(register_id))


@login_required(login_url='/login')
def student_form_create(request, register_id):
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        main = register_main.objects.select_related(
            "ev").get(register_id=register_id)
    except register_main.DoesNotExist:
        main = None
        return redirect("/")
    detail = course_event.objects.select_related(
        "course").get(ev_id=main.ev_id)
    if request.method == 'POST':
        form = studentForm(request.POST)
        if form.is_valid():
            student_identification_number = form.cleaned_data['student_identification_number']
            student_prefix_th = form.cleaned_data['student_prefix_th']
            student_firstname_th = form.cleaned_data['student_firstname_th']
            student_lastname_th = form.cleaned_data['student_lastname_th']
            student_prefix_eng = form.cleaned_data['student_prefix_eng']
            student_firstname_eng = form.cleaned_data['student_firstname_eng']
            student_lastname_eng = form.cleaned_data['student_lastname_eng']
            # ตรวจสอบโควต้า
            payment_data = register_payment.objects.filter(
                register_id=register_id, active=1).order_by('-crt_date').first()
            total_student = student.objects.filter(
                register_id=register_id).count()
            rp_quota = payment_data.rp_quota
            if total_student >= rp_quota:
                messages.error(request, "ไม่สามารถทำรายการได้ !")
                return redirect("/register/studentlist/" + str(register_id))
            month_current = date.today().month
            year_current = date.today().year
            # year_current_f = str(int(date.today().year) + 543)
            totaldata = student.objects.filter(
                crt_date__month=month_current, crt_date__year=year_current).count()
            running_number = treeDigit(totaldata + 1)
            student_code = "TZ" + str(twoDigit(month_current)) + \
                str(running_number) + "/" + str(year_current)

            student.objects.create(
                student_identification_number=student_identification_number,
                student_prefix_th=student_prefix_th,
                student_firstname_th=student_firstname_th,
                student_lastname_th=student_lastname_th,
                student_prefix_eng=student_prefix_eng,
                student_firstname_eng=student_firstname_eng,
                student_lastname_eng=student_lastname_eng,
                student_code=student_code,
                crt_date=dateTimeNow(),
                upd_date=dateTimeNow(),
                register_id=register_id
            )
            messages.success(request, "ทำรายการสำเร็จ !")
            return redirect("/register/studentlist/" + str(register_id))
    context = {'title': defaultTitle,  'form': studentForm, 'listMenuPermission': objMenu,
               'main': main, 'detail': detail}
    return render(request, 'register/student_form_create.html', context)


@login_required(login_url='/login')
def student_form_update(request, student_id):
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        instance = student.objects.get(student_id=student_id)
        register_id = instance.register_id
    except (student.DoesNotExist, AttributeError, ValueError, ValidationError):
        instance = None
        register_id = ""
        return redirect("/")
    try:
        main = register_main.objects.select_related(
            "ev").get(register_id=instance.register_id)
    except register_main.DoesNotExist:
        main = None
        return redirect("/")
    detail = course_event.objects.select_related(
        "course").get(ev_id=main.ev_id)
    if request.method == 'POST':
        form = studentForm(request.POST)
        if form.is_valid():
            student_identification_number = form.cleaned_data['student_identification_number']
            student_prefix_th = form.cleaned_data['student_prefix_th']
            student_firstname_th = form.cleaned_data['student_firstname_th']
            student_lastname_th = form.cleaned_data['student_lastname_th']
            student_prefix_eng = form.cleaned_data['student_prefix_eng']
            student_firstname_eng = form.cleaned_data['student_firstname_eng']
            student_lastname_eng = form.cleaned_data['student_lastname_eng']
            month_current = date.today().month
            year_current = date.today().year
            # year_current_f = str(int(date.today().year) + 543)
            totaldata = student.objects.filter(
                crt_date__month=month_current, crt_date__year=year_current).count()
            # running_number = treeDigit(totaldata + 1)
            # student_code = "TZ" + str(twoDigit(month_current)) + \
            #     str(running_number) + "/" + str(year_current)
            instance.student_identification_number = student_identification_number
            instance.student_prefix_th = student_prefix_th
            instance.student_firstname_th = student_firstname_th
            instance.student_lastname_th = student_lastname_th
            instance.student_prefix_eng = student_prefix_eng
            instance.student_firstname_eng = student_firstname_eng
            instance.student_lastname_eng = student_lastname_eng
            instance.upd_date = dateTimeNow()
            instance.save()
            messages.success(request, "ทำรายการสำเร็จ !")
            return redirect("/register/studentlist/" + str(register_id))
    initial = {'student_identification_number': instance.student_identification_number, 'student_prefix_th': instance.student_prefix_th,
               'student_firstname_th': instance.student_firstname_th, 'student_lastname_th': instance.student_lastname_th, 'student_prefix_eng':
               instance.student_prefix_eng, 'student_firstname_eng': instance.student_firstname_eng, 'student_lastname_eng': instance.student_lastname_eng,
               }
    context = {'title': defaultTitle,  'form': studentForm(initial=initial),
               'main': main, 'detail': detail, 'student_id': student_id, 'listMenuPermission': objMenu }
    return render(request, 'register/student_form_update.html', context)


@login_required(login_url='/login')
def student_update_status(request):
    student_id = request.POST['student_id']
    register_id = request.POST['register_id']
    content = student.objects.get(pk=student_id)
    content.student_learning_status = 1
    content.upd_date = dateTimeNow()
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/register/studentlist/" + str(register_id))


@login_required(login_url='/login')
def student_update_status_all(request):
    register_id = request.POST['register_id']
    content = student.objects.filter(register_id=register_id)
    if not content:
        messages.error(request, "ไม่สามารถทำรายการได้ !")
        return redirect("/register/studentlist/" + str(register_id))
    content.update(student_learning_status=1, upd_date=dateTimeNow())
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/register/studentlist/" + str(register_id))


@login_required(login_url='/login')
def student_delete(request):
    student_id = request.POST['student_id']
    register_id = request.POST['register_id']
    content = student.objects.get(pk=student_id)
    content.delete()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/register/studentlist/" + str(register_id))


@login_required(login_url='/login')
def student_create_idcard(request):
    register_id = request.POST['register_id']
    # try:
    #     resp = requests.get(api_id_card, verify=False).text
    # except:
    #     resp = None
    #     messages.error(request, "ไม่สามารถทำรายการได้ !")
    #     return redirect("/register/studentlist/" + str(register_id))
    # data = str(resp)
    # total_string = len(data) - 1
    # result = data[13:total_string]
    result = request.POST['data']
    if result is None or result == '':
        messages.error(request, "ไม่สามารถทำรายการได้ !")
        return redirect("/register/studentlist/" + str(register_id))
    json_data = json.loads(result)
    if json_data is None:
        messages.error(request, "ไม่สามารถทำรายการได้ !")
        return redirect("/register/studentlist/" + str(register_id))
    json_data = json.loads(result)
    if json_data is None:
        messages.error(request, "ไม่สามารถทำรายการได้ !")
        return redirect("/register/studentlist/" + str(register_id))
    student_identification_number = json_data['CitizenNo']
    student_prefix_th = json_data['TitleNameTh']
    student_firstname_th = json_data['FirstNameTh']
    student_lastname_th = json_data['LastNameTh']
    student_prefix_eng = json_data['TitleNameEn']
    student_firstname_eng = json_data['FirstNameEn']
    student_lastname_eng = json_data['LastNameEn']

    # ตรวจสอบโควต้า
    payment_data = register_payment.objects.filter(
        register_id=register_id, active=1).order_by('-crt_date').first()
    total_student = student.objects.filter(register_id=register_id).count()
    rp_quota = payment_data.rp_quota
    if total_student >= rp_quota:
        messages.error(request, "ไม่สามารถทำรายการได้ !")
        return redirect("/register/studentlist/" + str(register_id))
    month_current = date.today().month
    year_current = date.today().year
    # year_current_f = str(int(date.today().year) + 543)
    totaldata = student.objects.filter(
        crt_date__month=month_current, crt_date__year=year_current).count()
    running_number = treeDigit(totaldata + 1)
    student_code = "TZ" + str(twoDigit(month_current)) + \
        str(running_number) + "/" + str(year_current)

    student.objects.create(
        student_identification_number=student_identification_number,
        student_prefix_th=student_prefix_th,
        student_firstname_th=student_firstname_th,
        student_lastname_th=student_lastname_th,
        student_prefix_eng=student_prefix_eng,
        student_firstname_eng=student_firstname_eng,
        student_lastname_eng=student_lastname_eng,
        student_code=student_code,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow(),
        register_id=register_id
    )
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/register/studentlist/" + str(register_id))


@login_required(login_url='/login')
def student_form_certificate(request, student_id):
    title = defaultTitle
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        content = student.objects.select_related(
            "register").get(pk=student_id)
    except:
        content = None
        return redirect("/")
    detail = course_event.objects.select_related(
        "course").get(ev_id=content.register.ev_id)
    context = {'title': title,  'listMenuPermission': objMenu,
               'data': content, 'detail': detail}
    return render(request, 'register/student_form_certificate.html', context)


@login_required(login_url='/login')
def register_management(request):
    title = defaultTitle
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    # month_current = date.today().month
    # year_current = date.today().year
    month_current = request.GET.get('qmonths', date.today().month)
    year_current = request.GET.get('qyear', date.today().year)

    content = register_main.objects.filter(
        crt_date__month=month_current, crt_date__year=year_current).exclude(register_number="-").order_by("-crt_date")
    obj = []
    for r in content:
        # print(r.register_id)
        # customer_list = customers.objects.select_related('register').filter(
        #     register_id=r.register_id, register__crt_date__month=1).first()
        customer_list = customers.objects.select_related('register').filter(
            register_id=r.register_id).first()
        total_payment = register_payment.objects.filter(
            register_id=r.register_id).count()
        course_list = course_event.objects.select_related(
            'course').filter(ev_id=r.ev_id).first()
        res = {'customer_list': customer_list,
               'course_list': course_list, 'total_payment': total_payment}
        obj.append(res)
    context = {'title': title,  'data': obj,'listMenuPermission': objMenu}
    return render(request, 'register/register_management.html', context)


@login_required(login_url='/login')
def update_close_the_sale(request):
    current_user = request.user
    user_id_authen = current_user.id
    register_id = request.POST['register_id']
    confirm_price = float(request.POST['confirm_price'])
    close_the_sale = int(request.POST['close_the_sale'])
    if close_the_sale == 1:
        customer_status = 1
    else:
        customer_status = 0
    try:
        content = register_main.objects.get(pk=register_id)
    except:
        content = None
        return redirect("/register/management")
    # เปรียบเทียบราคาเพื่อยืนยันการปิดการขาย
    check_payment = register_payment_items.objects.filter(
        rpi_price_result=confirm_price, register_id=register_id).order_by("-rpi_id").first()
    if check_payment:
        set_active = register_payment.objects.get(rp_id=check_payment.rp_id)
        set_active.active = 1
        set_active.upd_date = dateTimeNow()
        set_active.save()
    else:
        messages.error(request, "ไม่สามารถทำรายการได้ !")
        return redirect("/register/management")
    content.close_the_sale = close_the_sale
    content.customer_status = customer_status
    content.upd_date = dateTimeNow()
    content.user_update_id = user_id_authen
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/register/management")


@login_required(login_url='/login')
def register_cancle(request):
    register_id = request.POST['register_id']
    try:
        content = register_main.objects.get(pk=register_id)
    except:
        content = None
        return redirect("/register/management")
    content.delete()
    return redirect("/register/management")


@login_required(login_url='/login')
def approve_list(request):
    title = defaultTitle
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        content = register_applove.objects.select_related(
            'register').filter(user_approve=user_id, doc_type=1).order_by("-id")
    except:
        content = None

    context = {'title': title,  'data': content, 'listMenuPermission': objMenu}
    return render(request, 'register/approve_list.html', context)


@login_required(login_url='/login')
def approve_update_status(request):
    id = request.POST['id']
    status = request.POST['status']
    content = register_applove.objects.get(pk=id)
    content.status = status
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/approve/update/payment")
