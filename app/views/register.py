from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
# from django.http import HttpResponse, response
from datetime import date, timedelta
from dateutil import rrule
import json
from datetime import datetime
from ..forms.student_form import studentForm
from ..form import ExcelUploadForm
from django.http import JsonResponse
from ..constant import defaultTitle, api_id_card
from django.shortcuts import render
import openpyxl
from django.views.decorators.csrf import csrf_exempt
from ..models import category_program_permission, course_event, customers, location_thai, course,fact_signature, register_main, register_payment, register_payment_items, student,register_ref, register_applove, user_group, user_detail, event_register,salesorder,desciption_bill,factbilldes,teacher_income_setting,User,document,teacher,signature,add_on,fact_addon,training,fact_teacher_user
from ..functions import dateTimeIntNow, dateTimeNow, dmytoymd, month_fomat,treeDigit, twoDigit
from ..constant import prefixEng,prefixThai

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
    
    _date = date.today()
    hundredDaysLater = _date + timedelta(days=365)
    obj = []
    
    for dt in rrule.rrule(rrule.MONTHLY, dtstart=datetime(2024, 12, 1), until=hundredDaysLater):
        
        _newdate = str(dt).split(" ")[0]
        yearstart = _newdate.split("-")[0]
        monthstart = _newdate.split("-")[1]
        label = month_fomat(monthstart) + " " + yearstart
        status = ['N','W','I','S','Y']
        # print(label)
        result = course_event.objects.select_related("course").filter(status__in=status,
            cancelled=1, active=1, ev_date_start__month=int(monthstart), ev_date_start__year=int(yearstart), module=m.module).order_by("ev_date_start")
        content = {"label": label, "data": result}
        obj.append(content)
    # print(idcard_data)
    context = {'title': title,  'data': obj, 'listMenuPermission': objMenu,'content_regist1': _newdate,
               'content_regist': content_regist, 'idcard_data': idcard_data, 'location': _location, 'address': address, 'api_id_card': api_id_card}
    return render(request, 'register/register.html', context)

@login_required(login_url='/login')
def register_homenotevent(request):
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
    hundredDaysLater = _date + timedelta(days=365)

  
    courses = course.objects.filter(cancelled=1, active=1,is_show_order='Y')
    obj = []
    

    # print(idcard_data)
    context = {'title': title,  'data': courses, 'listMenuPermission': objMenu,
               'content_regist': content_regist, 'idcard_data': idcard_data, 'location': _location, 'address': address, 'api_id_card': api_id_card}
    return render(request, 'register/register_noevent.html', context)


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

def register_resetnoevent(request):
    try:
        del request.session['register_id']
    except KeyError:
        pass

    try:
        del request.session['idcard_data']
    except KeyError:
        pass
    return redirect("/salesnotevent")

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

    
    event = course_event.objects.get(pk=ev_id)
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
        course_id=event.course_id,
        seller_id=seller_id,
        user_update_id=seller_id,
        is_event='Y',
        module=m.module
    )
    object.refresh_from_db()
    register_id = object.register_id
    # print(register_id)
    request.session['register_id'] = str(register_id)
    return redirect("/")

@login_required(login_url='/login')
def register_createnoevent(request):
    current_user = request.user
    seller_id = current_user.id
    course = request.POST['course_id']
    print(course)
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
        seller_id=seller_id,
        course_id=course,
        user_update_id=seller_id,
        is_event='N',
        module=m.module
    )
    object.refresh_from_db()
    register_id = object.register_id
    # print(register_id)
    request.session['register_id'] = str(register_id)
    return redirect("/salesnotevent")

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
def customer_createno(request):

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
    return redirect("/salesnotevent/payment/" + str(register_id))    


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
    
    des_bill = desciption_bill.objects.all().order_by('seq')
    regbyev = register_main.objects.filter(ev_id=content_regist.ev_id)
    total_rq_quta = 0

    signature = fact_signature.objects.select_related('user').all()
    
    
 
    
    for aaa in regbyev:
        
        try:
            bbbb = register_payment.objects.filter(register_id=aaa.register_id).first()
            if bbbb:
             total_rq_quta += bbbb.rp_quota
             
        except register_payment.DoesNotExist:  
      
            bbbb = 0
    content_course = course_event.objects.select_related(
        "course").get(ev_id=content_regist.ev_id)
    
    list_user = User.objects.filter(is_staff=0, is_active=1).prefetch_related('user_group_ref')
    # ถ้าเป็นบุคคลให้ส่งข้อมูลนักเรียนไปด้วย
    total_ca_quta = content_regist.ev.ev_training - total_rq_quta
    
    if content_regist.customer_type == 1:
        try:
            student_data = student.objects.filter(
                register_id=register_id).first()
        except:
            student_data = None
    else:
        student_data = None
    # print(content)
    course_list = course.objects.filter(is_show_order='Y',cancelled=1)
    uuid_without_dashes = str(register_id).replace('-', '')
    
    addon = add_on.objects.filter(register_id=uuid_without_dashes,status='Y')

    total_price = add_on.objects.filter(register_id=uuid_without_dashes,status='Y').aggregate(Sum('rpi_price_result'))["rpi_price_result__sum"] or 0

    context = {'title': title,  'data': content, 'listMenuPermission': objMenu,'des_bill':des_bill,'manage':signature,'course_list':course_list,'addon':addon,'total_price_add_on':total_price,
               'content_regist': content_regist, 'content_course': content_course, 'student_data': student_data,'quata':total_ca_quta,'ev_training':content_regist.ev.ev_training,'list_user':list_user}
    return render(request, 'register/register_payment.html', context)


@login_required(login_url='/login')
def paymentnoevent(request, register_id):
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
        "seller").prefetch_related("student_register").get(register_id=register_id)
    
    des_bill = desciption_bill.objects.all().order_by('seq')
    regbyev = register_main.objects.filter(register_id=register_id)
    total_rq_quta = 0

    signature = fact_signature.objects.select_related('user').all()
    
    
 
    
    for aaa in regbyev:
        
        try:
            bbbb = register_payment.objects.filter(register_id=aaa.register_id).first()
             
        except register_payment.DoesNotExist:  
            bbbb = 0

    
    list_user = User.objects.filter(is_staff=0, is_active=1).prefetch_related('user_group_ref')
    # ถ้าเป็นบุคคลให้ส่งข้อมูลนักเรียนไปด้วย
    print(content_regist.course_id)
    
    if content_regist.customer_type == 1:
        try:
            student_data = student.objects.filter(
                register_id=register_id).first()
        except:
            student_data = None
    else:
        student_data = None
    # print(content)
    course_list = course.objects.filter(is_show_order='Y',cancelled=1)
    uuid_without_dashes = str(register_id).replace('-', '')
    addon = add_on.objects.filter(register_id=uuid_without_dashes,status='Y')
    course_c = course.objects.get(is_show_order='Y',cancelled=1,course_id=content_regist.course_id)
    total_price = add_on.objects.filter(register_id=uuid_without_dashes,status='Y').aggregate(Sum('rpi_price_result'))["rpi_price_result__sum"] or 0
    
    context = {'title': title,  'data': content, 'listMenuPermission': objMenu,'des_bill':des_bill,'manage':signature,'course_list':course_list,'addon':addon,'total_price_add_on':total_price,'course':course_c,
               'content_regist': content_regist, 'student_data': student_data,'ev_training':content_regist,'list_user':list_user}
    return render(request, 'register/register_noeventpayment.html', context)    


@login_required(login_url='/login')
def payment_create(request):
    now = date.today()
    # Main
    user_id = request.user.id
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
    stmda = request.POST.get('stmdate')
    etc= request.POST.get('stmetc')
    bills = request.POST.getlist("selected_bills", [])
    rp_confirm_date_price = dmytoymd(
        request.POST.get("rp_confirm_date_price", now.strftime("%d/%m/%Y")))
    rp_date_delivery = dmytoymd(
        request.POST.get("rp_date_delivery", now.strftime("%d/%m/%Y")))
    uuid_without_dashes = str(register_id).replace('-', '')
    factbilldes.objects.filter(register_id=uuid_without_dashes).delete()  # Keeps the record with id=1
    
    user_man = request.POST.get('user_manage')  # ใช้ .get() เพื่อตรวจสอบ
    if not user_man:  # ตรวจสอบว่าคีย์ 'name' ไม่มีค่า
        user_man = 0
    
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

    if pay_type == 1:
        instecent = register_main.objects.get(register_id=register_id)
        instecent.status = 'Y'
        instecent.save()
       

    if pay_type == 2:
        instecent = register_main.objects.get(register_id=register_id)
        instecent.status = 'N'
        instecent.save()
        dtaf = event_register.objects.create(
        ev_id=instecent.ev_id,
        register_id=register_id,
        status='D'
         )
    
    u = User.objects.get(id=rp_name_seller)

    content_regist = register_main.objects.get(register_id=register_id)
    content_regist.seller_id = rp_name_seller
    content_regist.save()
    # Crate Main
    object = register_payment.objects.create(
        rp_doc_number=rp_doc_number,
        rp_code_customer=rp_code_customer,
        rp_name_customer=rp_name_customer,
        rp_tax=rp_tax,
        rp_name_seller=u.first_name+' '+u.last_name,
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
        register_id=register_id,
        user_create=user_id,
        user_manage=user_man
    )
    object.refresh_from_db()
    rp_id = object.rp_id
    getaddon = add_on.objects.filter(status="Y",register_id=uuid_without_dashes)
    for add in getaddon:
        fact_addon.objects.create(
        rp_id=rp_id,
        addon_id=add.addon_id,
    )
        
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
        register_id=register_id,
        stmdate=stmda,
        stmetc=etc,

        
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
    for bill in bills:
        dtaf = factbilldes.objects.create(
        register_id=uuid_without_dashes,
        des_id=bill
    )    

    messages.success(request, "ทำรายการสำเร็จ !")
    # return redirect("/register/management")
    return redirect("/register/payment/history/" + str(register_id))


def payment_createno(request):
    now = date.today()
    # Main
    user_id = request.user.id
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
    vat = request.POST['vat']
    stmda = request.POST.get('stmdate')
    etc= request.POST.get('stmetc')
    bills = request.POST.getlist("selected_bills", [])


    rp_confirm_date_price = dmytoymd(
        request.POST.get("rp_confirm_date_price", now.strftime("%d/%m/%Y")))
    rp_date_delivery = dmytoymd(
        request.POST.get("rp_date_delivery", now.strftime("%d/%m/%Y")))
    uuid_without_dashes = str(register_id).replace('-', '')
 
    user_man = request.POST.get('user_manage')  # ใช้ .get() เพื่อตรวจสอบ
    if not user_man:  # ตรวจสอบว่าคีย์ 'name' ไม่มีค่า
        user_man = 0
    


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
    addon_total = request.POST['addon_total']

    print(addon_total)
    

    if pay_type == 1:
        instecent = register_main.objects.get(register_id=register_id)
        instecent.status = 'Y'
        instecent.save()
       

    if pay_type == 2:
        instecent = register_main.objects.get(register_id=register_id)
        instecent.status = 'Y'
        instecent.save()

    u = User.objects.get(id=rp_name_seller)

    content_regist = register_main.objects.get(register_id=register_id)
    content_regist.seller_id = rp_name_seller
    content_regist.save()
    # Crate Main
    object = register_payment.objects.create(
        rp_doc_number=rp_doc_number,
        rp_code_customer=rp_code_customer,
        rp_name_customer=rp_name_customer,
        rp_tax=rp_tax,
        rp_name_seller=u.first_name+' '+u.last_name,
        rp_name_contact=rp_name_contact,
        rp_branch=rp_branch,
        rp_address=rp_address,
        rp_phone=rp_phone,
        rp_email=rp_email,
        rp_confirm_date_price=rp_confirm_date_price,
        rp_date_delivery=rp_date_delivery,
        rp_quota=0,
        rp_ref1=rp_ref1,
        rp_ref2=rp_ref2,
        active=active,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow(),
        register_id=register_id,
        user_create=user_id,
        user_manage=user_man
    )
    object.refresh_from_db()
    rp_id = object.rp_id
    # Create Item
    content_regist = register_main.objects.get(register_id=register_id)

  
    
    if vat == '0':
       
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
        register_id=register_id,
        vat=vat,
        stmdate=stmda,
        stmetc=etc,
    )


    for bill in bills:
        dtaf = factbilldes.objects.create(
        register_id=uuid_without_dashes,
        des_id=bill
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

   

    messages.success(request, "ทำรายการสำเร็จ !")
    # return redirect("/register/management")
    return redirect("/salesnotevent/payment/history/" + str(register_id))


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
    des_bill = desciption_bill.objects.all()
    signature = fact_signature.objects.select_related('user').all()
    uuid_without_dashes = str(register_id).replace('-', '')
    course_list = course.objects.filter(is_show_order='Y',cancelled=1)
    filtered_objects = factbilldes.objects.filter(register_id=uuid_without_dashes)
    selected_bills = [obj.des_id for obj in filtered_objects]

    check_bill = register_payment.objects.filter(register_id=register_id).first()
    
    getaddon = add_on.objects.filter(register_id=uuid_without_dashes,status='Y')

    total_price = add_on.objects.filter(register_id=uuid_without_dashes,status='Y').aggregate(Sum('rpi_price_result'))["rpi_price_result__sum"] or 0

 

    context1 = {'title': title,  'data': content, 'listMenuPermission': objMenu,
                'content_regist': content_regist, 'content_course': content_course}
    context2 = {'title': title,  'data': last_data, 'content_regist': content_regist, 'listMenuPermission': objMenu,'des_bill':des_bill,'selected_bills':selected_bills,'addon':getaddon,'course_list':course_list,'total_price_add_on':total_price,'manage':signature,'select_usermanage':check_bill.user_manage,
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
def payment_historyno(request, register_id):
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
    return render(request, 'register/register_paymentno_history.html', context)


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
               'main': main, 'detail': detail, 'rp_quota': rp_quota, 'total_student': content.count(), 'ref_data': ref_data, 'api_id_card': api_id_card,'register_id':register_id}
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
def register_form_create(request, ev_id):
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
   
    content = course_event.objects.select_related(
        "course").get(active=1, cancelled=1,ev_id=ev_id)
    

    context = {'title': defaultTitle, 'listMenuPermission': objMenu,'main_data':content,'prefixEng':prefixEng,'prefixThai':prefixThai
}
    return render(request, 'register/register_form_create.html', context)


@login_required(login_url='/login')
def register_form_store(request, ev_id):
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
   
    content = course_event.objects.select_related(
        "course").get(active=1, cancelled=1,ev_id=ev_id)
    student_prefix_th = request.POST['student_prefix_th']
    student_prefix_eng = request.POST['student_prefix_eng']
    student_identification_number = request.POST['student_identification_number']
    student_firstname_th = request.POST['student_firstname_th']
    student_lastname_th = request.POST['student_lastname_th']
    student_firstname_eng = request.POST['student_firstname_eng']
    student_lastname_eng = request.POST['student_lastname_eng']

    training.objects.create(
                student_identification_number=student_identification_number,
                student_prefix_th=student_prefix_th,
                student_firstname_th=student_firstname_th,
                student_lastname_th=student_lastname_th,
                student_prefix_eng=student_prefix_eng,
                student_firstname_eng=student_firstname_eng,
                student_lastname_eng=student_lastname_eng,
                student_code='xxxxx',
                crt_date=dateTimeNow(),
                upd_date=dateTimeNow(),
                ev_id=ev_id
            )

    context = {'title': defaultTitle, 'listMenuPermission': objMenu,'main_data':content
}
    return redirect("/register/event/teacher/list/" + str(ev_id))  


@login_required(login_url='/login')
def register_form_update(request, ev_id,training_id):
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
   
    content = course_event.objects.select_related(
        "course").get(active=1, cancelled=1,ev_id=ev_id)
    student_prefix_th = request.POST['student_prefix_th']
    student_prefix_eng = request.POST['student_prefix_eng']
    student_identification_number = request.POST['student_identification_number']
    student_firstname_th = request.POST['student_firstname_th']
    student_lastname_th = request.POST['student_lastname_th']
    student_firstname_eng = request.POST['student_firstname_eng']
    student_lastname_eng = request.POST['student_lastname_eng']


    instance = training.objects.get(training_id=training_id)
    instance.student_identification_number = student_identification_number
    instance.student_prefix_th = student_prefix_th
    instance.student_firstname_th = student_firstname_th
    instance.student_lastname_th = student_lastname_th
    instance.student_prefix_eng = student_prefix_eng
    instance.student_firstname_eng = student_firstname_eng
    instance.student_lastname_eng = student_lastname_eng
    instance.upd_date = dateTimeNow()
    instance.save()
    # training.objects.create(
    #             student_identification_number=student_identification_number,
    #             student_prefix_th=student_prefix_th,
    #             student_firstname_th=student_firstname_th,
    #             student_lastname_th=student_lastname_th,
    #             student_prefix_eng=student_prefix_eng,
    #             student_firstname_eng=student_firstname_eng,
    #             student_lastname_eng=student_lastname_eng,
    #             student_code='xxxxx',
    #             crt_date=dateTimeNow(),
    #             upd_date=dateTimeNow(),
    #             ev_id=ev_id
    #         )

#     context = {'title': defaultTitle, 'listMenuPermission': objMenu,'main_data':content
# }
    return redirect("/register/event/teacher/list/" + str(ev_id))    


@login_required(login_url='/login')
def register_form_show(request, ev_id,training_id):
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

    data = training.objects.get(training_id=training_id)
    evs = course_event.objects.get(ev_id=ev_id)
    context = {'title': defaultTitle, 'listMenuPermission': objMenu,'main_data':data,'course':evs,'prefixEng':prefixEng,'prefixThai':prefixThai
}
   
    return render(request, 'register/register_form_update.html', context)


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
def register_delete(request):
    ev_id = request.POST['ev_id']
    training_id = request.POST['training_id']
    content = training.objects.get(training_id=training_id)
    content.delete()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/register/event/teacher/list/" + str(ev_id))


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


def approve_lis_event(request):
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

   
    content = event_register.objects.select_related('ev').filter(status='D').order_by('ev_id')

    obj = []
    if content:
     for r in content:
        customer_list = customers.objects.select_related('register').filter(
            register_id=r.register_id).first()
        total_payment = register_payment.objects.filter(
            register_id=r.register_id).count()
        
        payment_item = register_payment.objects.filter(
            register_id=r.register_id).first()
   
        course_list = course_event.objects.select_related(
            'course').filter(ev_id=r.ev_id).first()
        res = {'customer_list': customer_list,'register_id':r.register_id,
               'course_list': course_list, 'total_payment': total_payment,'payment_item':payment_item}
        obj.append(res)
    context = {'title': title,  'data': obj,'listMenuPermission': objMenu} 
 

    return render(request, 'register/approve_list_event.html', context)
def approve_lis_event_end(request):
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

    
    content = course_event.objects.select_related('course').filter(status='I')

    # obj = []
    # if content:
    #  for r in content:
    #     customer_list = customers.objects.select_related('register').filter(
    #         register_id=r.register_id).first()
    #     total_payment = register_payment.objects.filter(
    #         register_id=r.register_id).count()
    #     course_list = course_event.objects.select_related(
    #         'course').filter(ev_id=r.ev_id).first()
    #     res = {'customer_list': customer_list,'register_id':r.register_id,
    #            'course_list': course_list, 'total_payment': total_payment}
    #     obj.append(res)
    context = {'title': title,  'data': content,'listMenuPermission': objMenu} 
 

    return render(request, 'register/approve_list_event_end.html', context)

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
    print(check_payment)
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
def update_close_the_event(request):
    current_user = request.user
    user_id_authen = current_user.id
   
    
    register_id = request.POST['register_id']
    ev_id = request.POST['ev_id']

    pos = request.POST['po']
    sqs= request.POST['sq']
    sos = request.POST['so']
    accept_terms = request.POST.get('flexCheckDefault')

 
    try:
        ev_logo = request.FILES['ev_logo']
        
    except KeyError:
        ev_logo = None

    

    content = register_main.objects.get(pk=register_id)
    content.status = 'Y'
    content.save()

    contentev = event_register.objects.get(register_id=register_id)
    contentev.status = 'Y'
    contentev.save()
       


    savesal = salesorder.objects.create(
        er_id=contentev.er_id,
        type_sa=accept_terms,
        po=pos,
        sq=sqs,
        so=sos,
        img=ev_logo,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow()
    )

    checkev = event_register.objects.filter(ev_id=ev_id)
    all_passed = all(record.status == 'Y' for record in checkev)
    if all_passed:
            content = course_event.objects.get(ev_id=ev_id)
            content.status = 'Y'
            content.save()


    # เช็ค ev นั้นว่า มีการ ยืนยันหมดรึยัง


    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/approve/update/event")

@login_required(login_url='/login')
def update_close_the_eventend(request):
    current_user = request.user
    user_id_authen = current_user.id
   
    ev_id = request.POST['ev_id']
    content = course_event.objects.get(ev_id=ev_id)
    content.status = 'S'
    content.save()

    checkincome = teacher_income_setting.objects.filter(ev_id=ev_id)
    if checkincome:
       for r in checkincome:
           
        if r.pi_id == 1 or r.pi_id == 2 or r.pi_id == 3 or r.pi_id == 4 or r.pi_id == 5 or r.pi_id == 6:
            
            instance = teacher_income_setting.objects.get(id=r.id)
            instance.status = 'I'
            instance.save()

        if r.pi_id == 7 or r.pi_id == 8:
            instance2 = teacher_income_setting.objects.get(id=r.id)
            instance2.status = 'I'
            instance2.save()
        
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/approve/update/processevent")    

def delete_close_the_event(request):
    register_id = request.POST['register_id']
    ev_id = request.POST['ev_id']

    contentev = event_register.objects.get(ev_id=ev_id,register_id=register_id)
    contentev.status = 'C'
    contentev.save()

    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/approve/update/event")

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


@login_required(login_url='/login')
def approve_list_payment(request):

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
        obj = []
        pi_id = ['7','8']   
        
        content = teacher_income_setting.objects.select_related('ev','teacher').filter(pi_id__in=pi_id,status='I')
        
        for r in content:  
            
            ev = course_event.objects.get(ev_id=r.ev_id)
            cou = course.objects.get(pk=ev.course_id)
            res = {'pi':r.pi_id,'course_name':cou.course_name,'gen':ev.ev_generation,'ev_date_start':ev.ev_date_start,'ev_date_end':ev.ev_date_end,'tis_unit':r.tis_unit,'pi_id':r.pi_id,'item_code':cou.course_code,'teacher':r.teacher,'id':r.id,'tis_sum':r.tis_sum}

            obj.append(res)    
           
    except:
        content = None
        

    context = {'title': title,  'data': obj, 'listMenuPermission': objMenu}

    return render(request, 'register/approve_list_event_bill.html',context)


@login_required(login_url='/login')
def approve_list_payment_accept(request,pk):
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
    
    list_user = User.objects.filter(is_staff=0, is_active=1,user_group_ref__module=m.module).prefetch_related('user_group_ref')

    # try:
    #     province_list = location_thai.objects.all().values(
    #         'province_code', 'province_name').annotate(total=Count('province_code'))
    # except location_thai.DoesNotExist:
    #     province_list = None
    
    
    
    teacher_income = teacher_income_setting.objects.filter(id=pk,status='I').count()
    income = teacher_income_setting.objects.filter(id=pk,status='I').first()
    if teacher_income > 0:
        context = {'title': defaultTitle, 'listMenuPermission': objMenu,'ev_id':pk,'pi':income.pi_id }
        return render(request, 'register/register_selller_report.html',context)
    else :
        return redirect("/approvebill/update/bill")

# def upload_excel(request):
#     if request.method == 'POST':
#         form = ExcelUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             excel_file = request.FILES['file']
#             workbook = openpyxl.load_workbook(excel_file)
#             worksheet = workbook.active

#             for row in worksheet.iter_rows(min_row=2, values_only=True):
#                 if row[0]:  # Assuming the first column is not empty
#                     ExcelData.objects.create(
#                         name=row[0],
#                         age=row[1],
#                         email=row[2]
#                     )
#             return redirect('data_list')
#     else:
#         form = ExcelUploadForm()
#     return render(request, 'upload_excel.html', {'form': form})    

def approve_list_payment_update(request):
      
      tis_sum = request.POST['tis_sum']
      ids = request.POST['id']
    

      set_active = teacher_income_setting.objects.get(id=ids)
      set_active.tis_sum = tis_sum
      set_active.tis_compensation = tis_sum
      set_active.status = 'S'
      set_active.save()

      return redirect("/approvebill/update/bill")

def upload_excel(request):

  code = request.POST.get('register')  # Get text input from FormData
  
  totaldata = student.objects.filter(
        register_id=code).order_by('-crt_date')
  rp_quota = totaldata.count()  
   
  if request.method == "POST" and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            # Parse JSON data from the request body
            workbook = openpyxl.load_workbook(excel_file)
            worksheet = workbook.active

            month_current = request.GET.get('qmonths', date.today().month)
            year_current = request.GET.get('qyear', date.today().year)
            payment_data = register_payment.objects.filter(register_id=code, active=1).order_by('-crt_date').first()   # โค๊วตา
            totaldata = student.objects.filter(register_id=code).order_by('-crt_date')
            rp_quota = totaldata.count()  
       

            row_count = sum(1 for row in worksheet.iter_rows()) # count data จาก excel
            excel_data = []
          
            total = rp_quota + row_count
      
            if payment_data.rp_quota >= total:
               
                for row in worksheet.iter_rows(values_only=True):
                    if row[0]:  # Assuming the first column is not empty
                        res = {'ลำดับ':row[0],'ชื่อ':row[1],'นามสกุล':row[2]}
                        excel_data.append(res) 
               
                        totaldata = student.objects.filter(crt_date__month=month_current, crt_date__year=year_current).count()
                        running_number = treeDigit(totaldata + 1)
                        student_code = "TZ" + str(twoDigit(month_current)) + \
                        str(running_number) + "/" + str(year_current)
              
                        student.objects.create(
                        student_identification_number=row[0],
                        student_prefix_th=row[1],
                        student_firstname_th=row[2],
                        student_lastname_th=row[3],
                        student_prefix_eng=row[4],
                        student_firstname_eng=row[5],
                        student_lastname_eng=row[6],
                        student_code=student_code,
                        crt_date=dateTimeNow(),
                        upd_date=dateTimeNow(),
                        register_id=code
                    )   
                datas= {'status':'success'}
                return JsonResponse(datas, status=200,safe=False)
            else:
                datas= {'status':'fail','text':'โค๊วต้าเกินกว่ากำหนด'}
                return JsonResponse(datas, status=200,safe=False)
        except json.JSONDecodeError:
            return JsonResponse({"error": 'x'}, status=400,safe=False)

  return JsonResponse({"error": "Only POST method is allowed"}, status=405)  
@csrf_exempt
def listdata(request):

    data = json.loads(request.body)
    register_id = data.get("register_id")
    te = []
    totaldata = student.objects.filter(register_id=register_id)
    for rs in list(totaldata):
        main = register_main.objects.select_related("ev").get(register_id=register_id)
        mainev = course_event.objects.get(ev_id=main.ev_id)
        maincou = course.objects.get(course_id=mainev.course_id)  
        r = {'item_code':maincou.course_code,'course_name':maincou.course_name,'ev_generation':mainev.ev_generation,'student_identification_number':rs.student_identification_number,'student_prefix_th':rs.student_prefix_th,'student_firstname_th':rs.student_firstname_th,'student_lastname_th':rs.student_lastname_th
        }
        te.append(r)


    return JsonResponse(te, status=200,safe=False)
@csrf_exempt
def tests(request):

    data = json.loads(request.body)
    test = data.get("form")

    return JsonResponse(test, status=200,safe=False)

def testsdata(request):

    data = []
    

    return JsonResponse(data, status=20,safe=False)


@login_required(login_url='/login')
def approve_internal(request):
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

    obj = []
    content = document.objects.filter()
    for rs in content:
        try:
            teacher_income = teacher_income_setting.objects.get(id=rs.teacher_income_id)
            x = course_event.objects.get(ev_id=teacher_income.ev_id)
            courses = course.objects.get(course_id=x.course_id)
            uuid_without_dashes = str(teacher_income.teacher_id).replace('-', '')
            a = teacher.objects.get(teacher_id=uuid_without_dashes)
            r = {'doc_id':rs.doc_id,'doc_number':rs.doc_number,'title':rs.title,'price':rs.price,'ev_date_start':x.ev_date_start,'ev_date_end':x.ev_date_end,'item':courses.course_code,'course_name':courses.course_name,
        'fname':a.teacher_firstname_th,'lname':a.teacher_lastname_th,'status_mange':rs.status_mange,'status_gm':rs.status_gm}
            obj.append(r)
        except teacher_income_setting.DoesNotExist:
            teacher_income = None  # Handle the case where the object does not exist
      

        
        
  
    context = {'title': title,  'data': obj, 'listMenuPermission': objMenu}
    return render(request, 'register/approve_list_documentsinternal.html', context)


@login_required(login_url='/login')
def report_register(request):
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


      

        
        
  
    context = {'title': title, 'listMenuPermission': objMenu}
    return render(request, 'register/register_report_all.html', context)


@login_required(login_url='/login')
def report_register_re(request):
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


      

        
        
  
    context = {'title': title, 'listMenuPermission': objMenu}
    return render(request, 'register/register_report_all_re.html', context)


@login_required(login_url='/login')
def report_register_teacher(request):
    title = defaultTitle
    user_id = request.user.id


    try:
        m = fact_teacher_user.objects.get(user_id=user_id)
        
    except fact_teacher_user.DoesNotExist:
        m = None
        return redirect("/")
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

    context = {'title': title, 'listMenuPermission': objMenu}
    return render(request, 'register/register_report_all_re.html', context)


@login_required(login_url='/login')
def report_register_list(request,evs_id):
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


      
   
    c_evet = course_event.objects.select_related(
        "course").get(active=1, cancelled=1,pk=evs_id)
    print(c_evet.ev_training)
    mains  = training.objects.filter(ev=evs_id)
    obj = []
    count = 0
    for rs in list(mains):
        count += 1
        r = {'student_identification_number':rs.student_identification_number,'student_prefix_th':rs.student_prefix_th,'student_firstname_th':rs.student_firstname_th,'student_lastname_th':rs.student_lastname_th,'student_firstname_eng':rs.student_firstname_eng,'student_lastname_eng':rs.student_lastname_eng,'student_prefix_eng':rs.student_prefix_eng,'crt_date':rs.crt_date,'upd_date':rs.upd_date}
        obj.append(r)
    
    context = {'title': title, 'listMenuPermission': objMenu,'main_data': c_evet,'data':obj,'count':count}
    return render(request, 'register/register_report_all_list.html', context)



@login_required(login_url='/login')
def report_register_listteacher(request,evs_id):
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


      
   
    c_evet = course_event.objects.select_related(
        "course").get(active=1, cancelled=1,pk=evs_id)
    print(c_evet.ev_training)
    mains  = training.objects.filter(ev=evs_id)
    obj = []
    count = 0
    for rs in list(mains):
        count += 1
        r = {'training_id':rs.training_id,'student_identification_number':rs.student_identification_number,'student_prefix_th':rs.student_prefix_th,'student_firstname_th':rs.student_firstname_th,'student_lastname_th':rs.student_lastname_th,'student_firstname_eng':rs.student_firstname_eng,'student_lastname_eng':rs.student_lastname_eng,'student_prefix_eng':rs.student_prefix_eng,'crt_date':rs.crt_date,'upd_date':rs.upd_date}
        obj.append(r)
    
    context = {'title': title, 'listMenuPermission': objMenu,'main_data': c_evet,'data':obj,'count':count}
    return render(request, 'register/register_report_all_list.html', context)

@login_required(login_url='/login')
def approve_internal_doc(request,doc_id):

    
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

    obj = []



    context = {'title': title,  'data': obj, 'listMenuPermission': objMenu,'doc_id':doc_id}
    return render(request, 'print/register_excel_seller_view.html', context)



@login_required(login_url='/login')
def approve_internal_doc_print(request,doc_id):
    user_id = request.user.id
   
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')

    obj = []
    getdoc = document.objects.get(doc_id=doc_id)
    tincome = teacher_income_setting.objects.select_related('teacher').get(pk=getdoc.teacher_income_id)
    cou_ev = course_event.objects.select_related('course').get(pk=tincome.ev_id)
    # teach = teacher.objects.get(teacher_id=tincome.teacher)
    status = ['N','Y']
    content_regist = register_main.objects.select_related(
        "seller", "ev").filter(ev_id=tincome.ev_id,status__in=status).order_by("pay_type")
    obj = []  
    total_payment = 0
    total_credit = 0
    for r in content_regist:  
       
         
         payment = register_payment.objects.get(register_id=r.register_id)
         item = register_payment_items.objects.get(register_id=r.register_id)
         custo = customers.objects.get(register_id=r.register_id)
      
         if r.pay_type == 1:
             total_payment += item.rpi_price_total
         else:
             total_credit += item.rpi_price_total
                 
          
         fs = {'rp_doc_number':payment.rp_doc_number,'pay_type':r.pay_type,'customer':custo.customer_name,'tax':custo.customer_tax,'tel':custo.customer_phone,'rpi_price':item.rpi_price_total}
         obj.append(fs) 
    total = total_payment + total_credit
    status = ['N','Y']
    count_payment = register_main.objects.filter(ev_id=tincome.ev_id,status__in=status,pay_type=1).count()
    count_credit = register_main.objects.filter(ev_id=tincome.ev_id,status__in=status,pay_type=2).count()
    totaldata = document.objects.filter().count()
    payment = register_payment.objects.get(register_id=r.register_id)
   
    month_current = date.today().month
    year_current = date.today().year
    year_current_f = str(int(date.today().year) + 543)
    current_time = datetime.now().time()
    totalhours = cou_ev.ev_hour + cou_ev.ev_hour_two
    totalprice = int(getdoc.price) / totalhours 

    users = User.objects.get(id=payment.user_create)
    signa = signature.objects.filter(user_id=payment.user_create).first()

    mange = User.objects.get(id=payment.user_manage)
    
    running_number = treeDigit(totaldata + 1)
    student_code = "TOP" + str(twoDigit(month_current)) + \
            str(running_number) + "/" + str(year_current)
    context = {'title': defaultTitle,'data':obj,'teacher_income_setting':tincome,'course_ev':cou_ev,'tax_number':tincome.teacher.tax_number,'fname':tincome.teacher.teacher_firstname_th,'lname':tincome.teacher.teacher_lastname_th,'status':tincome.status,'users':users,'signa':signa,'mange':mange,
               'course_code':cou_ev.course.course_code,'course_name':cou_ev.course.course_name,'total_payment':total_payment,'total_credit':total_credit,'total':total,'total_bill_payment':count_payment,'total_bill_credit':count_credit,'totalhours':totalhours,'doc':getdoc.doc_number,'payment_policy':getdoc.doc_number,'totalprice':totalprice,'price':getdoc.price}

    return render(request, 'print/register_print_internal.html', context)    


@login_required(login_url='/login')
def approve_manage(request):

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

    obj = []
    status = ['N','']
    content = document.objects.filter(status_mange__in=status)
    for rs in content:
        
        teacher_income = teacher_income_setting.objects.get(id=rs.teacher_income_id)
        x = course_event.objects.get(ev_id=teacher_income.ev_id)
        courses = course.objects.get(course_id=x.course_id)
        uuid_without_dashes = str(teacher_income.teacher_id).replace('-', '')

        a = teacher.objects.get(teacher_id=uuid_without_dashes)
        r = {'doc_id':rs.doc_id,'doc_number':rs.doc_number,'title':rs.title,'price':rs.price,'ev_date_start':x.ev_date_start,'ev_date_end':x.ev_date_end,'item':courses.course_code,'course_name':courses.course_name,'fname':a.teacher_firstname_th,'lname':a.teacher_lastname_th,'status_mange':rs.status_mange,'status_gm':rs.status_gm}
        obj.append(r)
        
  
    context = {'title': title,  'data': obj, 'listMenuPermission': objMenu}
 
    return render(request, 'register/approve_mange.html', context)

@login_required(login_url='/login')
def approve_gm(request):

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

    obj = []
    status = ['N','']
    
    content = document.objects.filter()
    
    for rs in content:


        try:
            
            teacher_income = teacher_income_setting.objects.get(id=rs.teacher_income_id)
            x = course_event.objects.get(ev_id=teacher_income.ev_id)
            courses = course.objects.get(course_id=x.course_id)
            uuid_without_dashes = str(teacher_income.teacher_id).replace('-', '')
            a = teacher.objects.get(teacher_id=uuid_without_dashes)
            r = {'doc_id':rs.doc_id,'doc_number':rs.doc_number,'title':rs.title,'price':rs.price,'ev_date_start':x.ev_date_start,'ev_date_end':x.ev_date_end,'item':courses.course_code,'course_name':courses.course_name,'fname':a.teacher_firstname_th,'lname':a.teacher_lastname_th,'status_mange':rs.status_mange,'status_gm':rs.status_gm}
            obj.append(r)
        except teacher_income_setting.DoesNotExist:
            teacher_income = None  # Handle the case where the object does not exist
        
  
    context = {'title': title,  'data': obj, 'listMenuPermission': objMenu}
 
    return render(request, 'register/approve_gm.html', context)


@csrf_exempt
def approve_gm_save(request):

    data = json.loads(request.body)
    doc_id = data.get("doc_id")
    status = data.get("status")

    x = document.objects.get(doc_id=doc_id)
    x.status_gm = status
    x.save()  
    datas = {'status':200}

    return JsonResponse(datas, status=200,safe=False)

@csrf_exempt
def approve_mange_save(request):

    data = json.loads(request.body)
    doc_id = data.get("doc_id")
    status = data.get("status")

    x = document.objects.get(doc_id=doc_id)
    x.status_mange = status
    x.save()  
    datas = {'status':200}

    return JsonResponse(datas, status=200,safe=False)


@csrf_exempt
def addon_create(request):

    data = json.loads(request.body)
    course_id = data.get("course_id")
    qty = data.get("qty")
    rpi_price = data.get("rpi_price")
    register = data.get("register_id")
    result = data.get("addon_price_result")
    price_discount = data.get("price_discount")
    
    courses = course.objects.get(course_id=course_id)
    uuid_without_dashes = str(register).replace('-', '')
    add_on.objects.create(
        course_code=courses.course_code,
        order_list=courses.course_name,
        qty=qty,
        register_id=uuid_without_dashes,
        unit='ท่าน',
        rpi_price=rpi_price,
        rpi_price_discount=0,
        rpi_price_result=result,
        status="Y"
    )
    dataadd = add_on.objects.filter(register_id=uuid_without_dashes,status='Y').values()
    total_price = add_on.objects.filter(register_id=uuid_without_dashes,status='Y').aggregate(Sum('rpi_price_result'))["rpi_price_result__sum"] or 0
    datas = {'status':200,'data':list(dataadd),'total_price_add_on':total_price}
    return JsonResponse(datas, status=200,safe=False)

@csrf_exempt
def addon_delete(request):

    data = json.loads(request.body)
    addon_id = data.get("addon_id")
    register = data.get("register_id")
    updateeadd = add_on.objects.get(addon_id=addon_id)
    updateeadd.status = 'N'
    updateeadd.save()

    uuid_without_dashes = str(register).replace('-', '')


    dataadd = add_on.objects.filter(register_id=uuid_without_dashes,status='Y').values()
    total_price = add_on.objects.filter(register_id=uuid_without_dashes,status='Y').aggregate(Sum('rpi_price_result'))["rpi_price_result__sum"] or 0
    datas = {'status':200,'data':list(dataadd),'total_price_add_on':total_price}
    return JsonResponse(datas, status=200,safe=False)


