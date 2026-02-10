from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta

from django.db.models import Count, Sum, Value, F
from ..models import course, course_event, user_group,category_program_permission,user_detail,teacher_income_setting,location_thai,pay_item,teacher,project_code,compensation,event_register,condition,conhead,fact_teacher_user,register_main,register_payment,training,register_payment_items
from ..constant import defaultTitle
from ..functions import addDay, addYear, dateTimeNow, dmytoymd,checkpermi
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
import datetime
import json
from django.core import serializers

@login_required(login_url='/login')
def course_list(request):
    user_id = request.user.id
     # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
      
        cm_id = u.cm
        
    except user_detail.DoesNotExist:
        cm_id = 0
          
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values("group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
       
    try:
        m = user_group.objects.get(user=user_id)
        
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    title = defaultTitle
    result = course.objects.filter(
        cancelled=1, module=m.module).order_by("-course_id")
    context = {'title': title, 'listMenuPermission': objMenu, 'data': result}
    return render(request, 'course/course.html', context)


@login_required(login_url='/login')
def course_create(request):
    user_id = request.user.id
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    course_code = request.POST['course_code']
    course_name = request.POST['course_name']
    course_name_eng = request.POST['course_name_eng']
    active = request.POST['active']
    content = course(
        course_code=course_code,
        course_name=course_name,
        course_name_eng=course_name_eng,
        active=active,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow(),
        module=m.module)
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/course")


@login_required(login_url='/login')
def course_update(request):
    course_id = request.POST['course_id']
    course_code = request.POST['course_code']
    course_name = request.POST['course_name']
    course_name_eng = request.POST['course_name_eng']
    active = request.POST['active']
    content = course.objects.get(pk=course_id)
    content.course_code = course_code
    content.course_name = course_name
    content.course_name_eng = course_name_eng
    content.active = active
    content.upd_date = dateTimeNow()
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/course")


@login_required(login_url='/login')
def course_delete(request):
    course_id = request.POST['course_id']
    content = course.objects.get(pk=course_id)
    content.cancelled = 0
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/course")


@login_required(login_url='/login')
def course_event_list(request):

    user_id = request.user.id
     # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:

       
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values("group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []

        
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        m = user_group.objects.get(user=user_id)
    
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    month_current = request.GET.get('qmonths', date.today().month)
    year_current = request.GET.get('qyear', date.today().year)

    

    Province = None
    Amphur = None
    Tumbol = None   
    course_list = course.objects.filter(
            cancelled=1, active=1).order_by("-course_id")
    project_list = project_code.objects.filter(
            status=1)      
    
    
    if Province is not None:
        try:
            _location = location_thai.objects.get(
                province_name__icontains=Province, amphur_name__icontains=Amphur, district_name__icontains=Tumbol)
           
        except location_thai.DoesNotExist:
            _location = None
    else:
        _location = None 
        
    result = course_event.objects.select_related("course").filter(
            cancelled=1, ev_date_start__month=month_current, ev_date_start__year=year_current, module=m.module).order_by("-ev_id")
    
    addall = location_thai.objects.all()
    context = {'title': defaultTitle, 'listMenuPermission': objMenu, 'data': result, 'course_list': course_list,'location': _location,'project_list':project_list,'addall':addall}
    
    return render(request, 'course/course_event_list.html', context)


@login_required(login_url='/login')
def course_event_create(request):
    user_id = request.user.id
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    course_id = request.POST['course_id']
    project_id = request.POST['project_id']
    ev_date_start = dmytoymd(request.POST['ev_date_start'])
    ev_date_end = dmytoymd(request.POST['ev_date_end'])
    ev_generation = request.POST['ev_generation']
    ev_remark = request.POST['ev_remark']
    ev_price = request.POST['ev_price']
    ev_vat = request.POST['ev_vat']
    ev_expired_cer_quantity = request.POST['ev_expired_cer_quantity']
    ev_expired_cer_date = addYear(ev_date_start, int(ev_expired_cer_quantity))
    active = request.POST['active']
    ev_hour = request.POST['ev_hour']
    ev_hour_two = request.POST['ev_hour_two']
    # ev_hour_three = request.POST['ev_hour_three']
    ev_people = request.POST['ev_people']
    ev_people_two = request.POST['ev_people_two']
    # ev_people_three = request.POST['ev_people_three']
    limitprice = request.POST['limit_price']
    limit_price_workhelp = request.POST['limit_price_workhelp']
    ev_training = request.POST['ev_training']
    checkevent = request.POST['checkevent']
    local = request.POST['location_id']
    address = request.POST['address']
    details = request.POST['details']
    status = ''
    now = datetime.datetime.now()
    time_string = now.strftime("%H%M%S")
    number_code = 'EV'+ ev_date_end + time_string + course_id
    
    if checkevent == '0':
        status = 'N'
 
    try:
        ev_logo = request.FILES['ev_logo']
       
    except KeyError:

        ev_logo = None
    content = course_event(
        ev_date_start=ev_date_start,
        ev_date_end=ev_date_end,
        ev_generation=ev_generation,
        ev_remark=ev_remark,
        ev_price=ev_price,
        ev_vat=ev_vat,
        ev_expired_cer_quantity=ev_expired_cer_quantity,
        ev_expired_cer_date=ev_expired_cer_date,
        ev_logo=ev_logo,
        active=active,
        course_id=course_id,
        project_id=project_id,
        is_show=1,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow(),
        ev_hour=ev_hour,
        ev_hour_two=ev_hour_two,
        ev_hour_three=0,
        ev_people=ev_people,
        ev_people_two=ev_people_two,
        ev_people_three=10,
        limit_price=limitprice,
        limit_price_workhelp=limit_price_workhelp,
        status=status,
        number_code=number_code,
        location_id=local,
        address=address,
        ev_training=ev_training,
        checkevent=checkevent,
        details=details,
        module=m.module,
     )
    content.save()

    

    conu = course.objects.get(pk=course_id)
    api_url = "http://127.0.0.1:8000/api/data"

    # Optional: Add headers or parameters
    headers = {
        "Content-Type": "application/json",
        }

    start = str(content.crt_date)
  
    params = {
        "item_code": conu.course_code,
        "course_id": course_id,
        "course_name": conu.course_name,
        "course_name_eng": conu.course_name_eng,
        "ev_generation": ev_generation,
        "create_at": start,
        "cancelled":1
      }
   


    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/course/event")







@login_required(login_url='/login')
def course_event_update(request):
    
    ev_id = request.POST['ev_id']
    limitprice = request.POST['limit_price']
    limit_price_workhelp = request.POST['limit_price_workhelp']
    project_id = request.POST['project_id']
    ev_date_start = dmytoymd(request.POST['ev_date_start'])
    ev_date_end = dmytoymd(request.POST['ev_date_end'])
    ev_generation = request.POST['ev_generation']
    ev_remark = request.POST['ev_remark']
    ev_price = request.POST['ev_price']
    ev_vat = request.POST['ev_vat']
    ev_expired_cer_quantity = request.POST['ev_expired_cer_quantity']
    ev_expired_cer_date = addYear(ev_date_start, int(ev_expired_cer_quantity))
    active = request.POST['active']
    ev_hour = request.POST['ev_hour']
    ev_hour_two = request.POST['ev_hour_two']
    ev_hour_three = 0
    ev_people = request.POST['ev_people_update']
    ev_people_two = request.POST['ev_people_two_update']
    ev_people_three = 10
    ev_training = request.POST['ev_training']
    local = request.POST['location_id']
    address = request.POST['address']
    try:
        ev_logo = request.FILES['ev_logo']
    except KeyError:
        ev_logo = None
    content = course_event.objects.get(pk=ev_id)
    content.ev_date_start = ev_date_start
    content.ev_date_end = ev_date_end
    content.ev_generation = ev_generation
    content.ev_remark = ev_remark
    content.ev_price = ev_price
    content.ev_vat = ev_vat
    content.ev_expired_cer_quantity = ev_expired_cer_quantity
    content.ev_expired_cer_date = ev_expired_cer_date
    content.ev_logo = ev_logo
    content.active = active
    content.ev_hour = ev_hour
    content.ev_hour_two = ev_hour_two
    content.ev_hour_three = ev_hour_three
    content.ev_people = ev_people
    content.ev_people_two = ev_people_two
    content.ev_people_three = ev_people_three
    content.upd_date = dateTimeNow()
    content.project_id = project_id
    content.limit_price = limitprice
    content.limit_price_workhelp = limit_price_workhelp
    content.ev_training = ev_training
    content.location_id = local
    content.address = address
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/course/event")

@login_required(login_url='/login')
def course_event_delete(request):
    ev_id = request.POST['ev_id']
    content = course_event.objects.get(pk=ev_id)
    content.cancelled = 0
    content.save()

    teact_in = teacher_income_setting.objects.filter(ev=ev_id).delete()

 

    conu = course.objects.get(pk=content.course_id)
    api_url = "http://127.0.0.1:8000/api/data"

    # Optional: Add headers or parameters
    headers = {
        "Content-Type": "application/json",
    }

    start = str(content.crt_date)
  
    params = {
        "item_code": conu.course_code,
        "course_id": content.course_id,
        "course_name": conu.course_name,
        "course_name_eng": conu.course_name_eng,
        "ev_generation": content.ev_generation,
        "create_at": start,
        "cancelled":0
    }
    # response = requests.get(api_url, headers=headers, params=params)
    
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/course/event")


def conditionlist(request):
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values("group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html') 
    title = defaultTitle

    
    resulta = course.objects.filter(
            cancelled=1, active=1,is_show_condition='Y').order_by("-course_id")
    result = conhead.objects.select_related("course").filter()
    context = {'title': title, 'listMenuPermission': objMenu, 'data': result, 'dataa': resulta}

    return render(request, 'condition/condition.html', context)    


def conditioncreate(request,conhead_id):
    
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values("group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html') 
    title = defaultTitle

   
    result = condition.objects.select_related("course").filter(conhead=conhead_id)
    conheadx = conhead.objects.select_related("course").get(conhead_id=conhead_id)
  
   
    try:
        instance = condition.objects.filter(conhead=conheadx)[:1].get()
       
        conu = course.objects.get(pk=conheadx.course_id)
        
    except condition.DoesNotExist:
        instance = []
        conu = []
        context = {'title': title, 'listMenuPermission': objMenu, 'data': result,'course_name':conu,'conhead_id':conhead_id,'coursea':conheadx}
        return render(request, 'condition/condition_id.html', context)   

    context = {'title': title, 'listMenuPermission': objMenu, 'data': result,'course_name':conu,'conhead_id':conhead_id,'coursea':conheadx}

    return render(request, 'condition/condition_id.html', context)    

def condition_form_delete(request):
    
    user_id = request.user.id

    id = request.POST['id']
    conhead_id = request.POST['conhead_id']
    instance = condition.objects.filter(condition_id=id)[:1].get()
    instance.delete()
    # Menu
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/condition/management/" + str(conhead_id))    


def condition_form_save(request):
    user_id = request.user.id


    conhead_id = request.POST['conhead_id']
    type_condition = request.POST['type_condition']
    
    
    instance = course.objects.get(course_id=conhead_id)
    print(instance)
    if type_condition == '1':
        student = request.POST['student']
        price = request.POST['price']
        type_id = request.POST['type_id']
        

        content = condition(
            student = student,
            price = price,
            type = type_id,
            course_id = instance.course_id,
            hour = 0,
            type_add = type_condition,
            conhead_id = conhead_id,
            action = 1
        )
        content.save()
    else:
        
        hour = request.POST['hour']
        student = request.POST['student']
        type_id = request.POST['type_id']
        action = request.POST['action']
    
        content = condition(
            student = student,
            price = 0,
            type = type_id,
            course_id = instance.course_id,
            hour = hour,
            type_add = type_condition,
            conhead_id = conhead_id,
            action = action
        )
        content.save()
        
 


    # Menu
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/condition/management/" + str(conhead_id))  

def condition_form_update(request):
    user_id = request.user.id


    conhead_id = request.POST['conhead_id']
    condition_id = request.POST['condition_id']
    type_condition = request.POST['type_condition']
    instance = course.objects.get(course_id=conhead_id)
    if type_condition == '1':
        student = request.POST['student']
        price = request.POST['price']
        type_id = request.POST['type_id']
        

        content = condition.objects.get(condition_id=condition_id)
        content.student = student
        content.price = price
        content.type = type_id
        content.save()
    else:
        
        hour = request.POST['hour']
        student = request.POST['student']
        type_id = request.POST['type_id']
        action = request.POST['action']
        content = condition.objects.get(condition_id=condition_id)
        content.student = student
        content.hour = hour
        content.type = type_id
        content.action = action
        content.save()
        

    # Menu
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/condition/management/" + str(conhead_id)) 
  
@login_required(login_url='/login')
def calendar_event(request):
    user_id = request.user.id

     # Menu
     
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
        
    path = request.path
    cleaned_path = path.strip('/')    
    checkpa = checkpermi(cleaned_path,cm_id)
    if checkpa == 0:
        return render(request, '403.html')     
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values("group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    title = defaultTitle
    listposition = pay_item.objects.filter(
            cancelled=1, active=1)
    list_teacher = teacher.objects.filter(cancelled=1, active=1)
    context = {'title': title,'listMenuPermission': objMenu,'teacher':list_teacher,'listposition':listposition}
    return render(request, 'course/calendar_event.html', context)

    
@login_required(login_url='/login')
def calendar_event_staff(request):
    user_id = request.user.id
     # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values("group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    title = defaultTitle
    listposition = pay_item.objects.filter(
            cancelled=1, active=1)
    list_teacher = teacher.objects.filter(cancelled=1, active=1)
    context = {'title': title,'listMenuPermission': objMenu,'teacher':list_teacher,'listposition':listposition}
    return render(request, 'course/calendar_event_staff.html', context)


def calendar_event_all(request):
    user_id = request.user.id
     # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values("group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    title = defaultTitle
    listposition = pay_item.objects.filter(
            cancelled=1, active=1)
    list_teacher = teacher.objects.filter(cancelled=1, active=1)
    context = {'title': title,'listMenuPermission': objMenu,'teacher':list_teacher,'listposition':listposition}
    return render(request, 'course/calendar_event_all.html', context)



def data_event(request):

    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    _date = date.today()
    if start is not None and end is not None:
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        sobj = str(start).split("T")[0]
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        eobj = str(end).split("T")[0]
    else:
        sobj = _date + timedelta(days=0)
        eobj = _date + timedelta(days=60)
    status = ['W','Y','I']
    content = course_event.objects.select_related(
        "course").filter(active=1, cancelled=1, ev_date_start__gte=sobj, ev_date_end__lte=eobj, status__in=status)
   
    obj = []

    sff = []
    for r in content:
        
        conditiondata = []
        if r :
            getcondition = conhead.objects.filter(course_id=r.course_id,is_active='Y')
            for cond in list(getcondition):
                 resx = {'conhead_id':cond.conhead_id,'name':cond.name}
                 conditiondata.append(resx)
        end = str(r.ev_date_end)
      
        y, m, d = end.split("-")
        nextdayend = addDay(1, int(y), int(m), int(d))
        

        col = r.status
        if col == 'W' :
         t = '#e0ce1b'
        elif col == 'Y': 
         t = '#eb2509'  
        elif col == 'I': 
         t = '#4be01b'  
        elif col == 'S': 
         t = '#4be01b'    
        else:
         t = '#4be01b'
        teacher_data = teacher_income_setting.objects.filter(ev=r.ev_id)
        location = location_thai.objects.get(location_id=r.location_id)
   
        sff = []
        
        if teacher_data.count() > 0:
            sff = [
            {
                "teacher_prefix_th": x.teacher.teacher_prefix_th,
                "teacher_firstname_th": x.teacher.teacher_firstname_th,
                "teacher_lastname_th": x.teacher.teacher_lastname_th,
                "pi_id":x.pi_id,
                "pi_name":pay_item.objects.filter(id=x.pi_id).values_list('pi_name').first(),
                "tis_quantity": x.tis_quantity,
                "tis_unit": x.tis_unit,
                "compensation":x.tis_compensation,
                "id":x.id,
                "status":x.status,
                "teacher_id": x.teacher_id,
                "tis_sum": x.tis_sum
            }
            for x in teacher_data
         ]
        else :
            sff = []
    #  uuid_with_dashes = t1.teacher_id  # This is a UUID object
    #     uuid_without_dashes = str(uuid_with_dashes).replace('-', '')
        delta = r.ev_date_end - r.ev_date_start
        days_difference = delta.days + 1


        

     
        res = {'backgroundColor':t,'borderColor':'#1e7e34','textColor':'#ffffff','title': str(r.course.course_name) + " (รุ่นที่ " + str(r.ev_generation)+")" ,'data':sff,
        'address':"สถานที่จัด จ."+str(location.province_name)+" อ."+str(location.amphur_name)+" ที่อยู่ "+str(r.address),
                'limit_price_workhelp':r.limit_price_workhelp,'limit_price':r.limit_price,'dis_limit': r.limit_price - (teacher_income_setting.objects.filter(ev=r.ev_id,pi=3).aggregate(Sum('tis_sum'))['tis_sum__sum'] or 0), 'start': r.ev_date_start, 'end': dmytoymd(nextdayend),'evs_id':r.ev_id,'ev_hour':r.ev_hour,'ev_hour_two':r.ev_hour_two,'ev_hour_three':r.ev_hour_three,'ev_people': r.ev_people,'ev_people_two': r.ev_people_two,'ev_people_three': r.ev_people_three,'count_day':days_difference,'condition_type': r.condition_type,'condition':conditiondata,'condition_id':r.condition_id}
        obj.append(res)
       
    return JsonResponse(obj, safe=False)




   
def calendar_event_api(request):
    user_id = request.user.id
  
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
 
    _date = date(2026, 1, 1)

    a = date(2026, 1, 1)
    b = date(2026, 12, 31)
  
    if start is not None and end is not None:
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        sobj = a
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        eobj = b
   
    else:
        sobj = _date + timedelta(days=0)
        eobj = _date + timedelta(days=1000)
    status = ['W','Y','I']
    # contentxxx = event_register.objects.select_related('ev').filter(status__in=status,ev__active=1, ev__cancelled=1, ev__ev_date_start__gte=sobj, ev__ev_date_end__lte=eobj ,ev__module=m.module)

    content = course_event.objects.select_related(
        "course").filter(active=1, cancelled=1, ev_date_start__gte=sobj, ev_date_end__lte=eobj ,module=m.module, status__in=status)
    
    obj = []

    sff = []
    for r in content:
        
        conditiondata = []
        if r :
            getcondition = conhead.objects.filter(course_id=r.course_id,is_active='Y')
            for cond in list(getcondition):
                 resx = {'conhead_id':cond.conhead_id,'name':cond.name}
                 conditiondata.append(resx)
        end = str(r.ev_date_end)
      
        y, m, d = end.split("-")
        nextdayend = addDay(1, int(y), int(m), int(d))
        

        col = r.status
        if col == 'W' :
         t = '#e0ce1b'
        elif col == 'Y': 
         t = '#eb2509'  
        elif col == 'I': 
         t = '#4be01b'  
        elif col == 'S': 
         t = '#4be01b'    
        else:
         t = '#4be01b'
        teacher_data = teacher_income_setting.objects.filter(ev=r.ev_id)
        location = location_thai.objects.get(location_id=r.location_id)
   
        sff = []
        
        if teacher_data.count() > 0:
            sff = [
            {
                "teacher_prefix_th": x.teacher.teacher_prefix_th,
                "teacher_firstname_th": x.teacher.teacher_firstname_th,
                "teacher_lastname_th": x.teacher.teacher_lastname_th,
                "pi_id":x.pi_id,
                "pi_name":pay_item.objects.filter(id=x.pi_id).values_list('pi_name').first(),
                "tis_quantity": x.tis_quantity,
                "tis_unit": x.tis_unit,
                "compensation":x.tis_compensation,
                "id":x.id,
                "status":x.status,
                "teacher_id": x.teacher_id,
                "tis_expenses":x.tis_expenses,
                "tis_sum": x.tis_sum
            }
            for x in teacher_data
         ]
        else :
            sff = []
    #  uuid_with_dashes = t1.teacher_id  # This is a UUID object
    #     uuid_without_dashes = str(uuid_with_dashes).replace('-', '')
        delta = r.ev_date_end - r.ev_date_start
        days_difference = delta.days + 1

        details = '-'
        
        if r.details:
            details = r.details
     
        res = {'backgroundColor':t,'borderColor':'#1e7e34','textColor':'#ffffff','title': str(r.course.course_code) +" "+ str(r.course.course_name) + " (รุ่นที่ " + str(r.ev_generation)+")" ,'data':sff,
        'address':"สถานที่จัด จ."+str(location.province_name)+" อ."+str(location.amphur_name)+" ที่อยู่ "+str(r.address),'details':str(details),
                'limit_price_workhelp':r.limit_price_workhelp,'limit_price':r.limit_price,'dis_limit': r.limit_price - (teacher_income_setting.objects.filter(ev=r.ev_id,pi=3).aggregate(Sum('tis_sum'))['tis_sum__sum'] or 0), 'start': r.ev_date_start, 'end': dmytoymd(nextdayend),'evs_id':r.ev_id,'ev_hour':r.ev_hour,'ev_hour_two':r.ev_hour_two,'ev_hour_three':r.ev_hour_three,'ev_people': r.ev_people,'ev_people_two': r.ev_people_two,'ev_people_three': r.ev_people_three,'count_day':days_difference,'condition_type': r.condition_type,'condition':conditiondata,'condition_id':r.condition_id}
        obj.append(res)
       
    return JsonResponse(obj, safe=False)


def calendar_event_apiall(request):
    user_id = request.user.id
  
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    _date = date.today()
    if start is not None and end is not None:
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        sobj = str(start).split("T")[0]
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        eobj = str(end).split("T")[0]
    else:
        sobj = _date + timedelta(days=0)
        eobj = _date + timedelta(days=60)
    status = ['W','Y','I','S']
    # contentxxx = event_register.objects.select_related('ev').filter(status__in=status,ev__active=1, ev__cancelled=1, ev__ev_date_start__gte=sobj, ev__ev_date_end__lte=eobj ,ev__module=m.module)
    
 
    content = course_event.objects.select_related(
        "course").filter(active=1, cancelled=1, ev_date_start__gte=sobj, ev_date_end__lte=eobj ,module=m.module, status__in=status)
   
    obj = []
    sff = []
    for r in content:
        
        to = 0
        
        billpa = register_payment.objects.select_related('register').filter(register__ev_id=r.ev_id)
        for bi in billpa:
               
                t = register_payment_items.objects.get(rp_id=bi.rp_id)
                to += t.rpi_quantity
        
        trcount = training.objects.filter(ev_id=r.ev_id).count()
        ev_traing = r.ev_training
        end = str(r.ev_date_end)
      
        y, m, d = end.split("-")
        nextdayend = addDay(1, int(y), int(m), int(d))
        

        col = r.status
        if col == 'W' :
         t = '#e0ce1b'
        elif col == 'Y': 
         t = '#eb2509'  
        elif col == 'I': 
         t = '#4be01b'  
        elif col == 'S': 
         t = '#4be01b'    
        else:
         t = '#4be01b'
        teacher_data = teacher_income_setting.objects.filter(ev=r.ev_id)
        location = location_thai.objects.get(location_id=r.location_id)
   
        
        
        if teacher_data.count() > 0:
            sff = [
            {
                "teacher_prefix_th": x.teacher.teacher_prefix_th,
                "teacher_firstname_th": x.teacher.teacher_firstname_th,
                "teacher_lastname_th": x.teacher.teacher_lastname_th,
                "pi_id":x.pi_id,
                "pi_name":pay_item.objects.filter(id=x.pi_id).values_list('pi_name').first(),
                "tis_quantity": x.tis_quantity,
                "tis_unit": x.tis_unit,
                "compensation":x.tis_compensation,
                "id":x.id,
                "status":x.status,
                "teacher_id": x.teacher_id,
                "tis_sum": x.tis_sum
            }
            for x in teacher_data
         ]
        else :
            sff = []
    #  uuid_with_dashes = t1.teacher_id  # This is a UUID object
    #     uuid_without_dashes = str(uuid_with_dashes).replace('-', '')
        delta = r.ev_date_end - r.ev_date_start

     
        res = {'backgroundColor':t,'borderColor':'#1e7e34','textColor':'#ffffff','title': str(r.course.course_code) + "(Rec" + str(to)+ '/' +str(ev_traing)+") "  + "(Reg" + str(trcount)+ '/' +str(ev_traing)+")" ,'data':sff,
        'address':"สถานที่จัด จ."+str(location.province_name)+" อ."+str(location.amphur_name)+" ที่อยู่ "+str(r.address),'start': r.ev_date_start, 'end': dmytoymd(nextdayend),'evs_id':r.ev_id,'ev_hour':r.ev_hour,'ev_hour_two':r.ev_hour_two,'ev_hour_three':r.ev_hour_three,'ev_people': r.ev_people,'ev_people_two': r.ev_people_two}
        obj.append(res)
       
    return JsonResponse(obj, safe=False)


def calendar_event_apiallcom(request):
    user_id = request.user.id
  
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    _date = date.today()
    if start is not None and end is not None:
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        sobj = str(start).split("T")[0]
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        eobj = str(end).split("T")[0]
    else:
        sobj = _date + timedelta(days=0)
        eobj = _date + timedelta(days=60)
    status = ['W','Y','I','S']
    # contentxxx = event_register.objects.select_related('ev').filter(status__in=status,ev__active=1, ev__cancelled=1, ev__ev_date_start__gte=sobj, ev__ev_date_end__lte=eobj ,ev__module=m.module)
    
 
    content = course_event.objects.select_related(
        "course").filter(active=1, cancelled=1, ev_date_start__gte=sobj, ev_date_end__lte=eobj ,module=m.module, status__in=status)
   
    obj = []
    sff = []
    for r in content:

        end = str(r.ev_date_end)
      
        y, m, d = end.split("-")
        nextdayend = addDay(1, int(y), int(m), int(d))
        

        col = r.status
        if col == 'W' :
         t = '#e0ce1b'
        elif col == 'Y': 
         t = '#eb2509'  
        elif col == 'I': 
         t = '#4be01b'  
        elif col == 'S': 
         t = '#4be01b'    
        else:
         t = '#4be01b'
        teacher_data = teacher_income_setting.objects.filter(ev=r.ev_id)
        location = location_thai.objects.get(location_id=r.location_id)
   
        
        sff = []
    #  uuid_with_dashes = t1.teacher_id  # This is a UUID object
    #     uuid_without_dashes = str(uuid_with_dashes).replace('-', '')
        delta = r.ev_date_end - r.ev_date_start
        days_difference = delta.days + 1
     
        res = {'backgroundColor':t,'borderColor':'#1e7e34','textColor':'#ffffff','title': str(r.course.course_name) + " (รุ่นที่ " + str(r.ev_generation)+")" ,'data':sff,
        'address':"สถานที่จัด จ."+str(location.province_name)+" อ."+str(location.amphur_name)+" ที่อยู่ "+str(r.address),
                'limit_price_workhelp':r.limit_price_workhelp,'limit_price':r.limit_price,'dis_limit': r.limit_price - (teacher_income_setting.objects.filter(ev=r.ev_id,pi=3).aggregate(Sum('tis_sum'))['tis_sum__sum'] or 0), 'start': r.ev_date_start, 'end': dmytoymd(nextdayend),'evs_id':r.ev_id,'ev_hour':r.ev_hour,'ev_hour_two':r.ev_hour_two,'ev_hour_three':r.ev_hour_three,'ev_people': r.ev_people,'ev_people_two': r.ev_people_two,'ev_people_three': r.ev_people_three,'count_day':days_difference}
        obj.append(res)
       
    return JsonResponse(obj, safe=False)

def calendar_event_apialloverdue(request):
    user_id = request.user.id
  
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    _date = date.today()
    if start is not None and end is not None:
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        sobj = str(start).split("T")[0]
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        eobj = str(end).split("T")[0]
    else:
        sobj = _date + timedelta(days=0)
        eobj = _date + timedelta(days=60)
    status = ['W','Y','I','S']
    # contentxxx = event_register.objects.select_related('ev').filter(status__in=status,ev__active=1, ev__cancelled=1, ev__ev_date_start__gte=sobj, ev__ev_date_end__lte=eobj ,ev__module=m.module)
    
 
    content = course_event.objects.select_related(
        "course").filter(active=1, cancelled=1, ev_date_start__gte=sobj, ev_date_end__lte=eobj ,module=m.module, status__in=status)
   
    obj = []
    sff = []
    for r in content:
        bill = 0
        end = str(r.ev_date_end)
      
        y, m, d = end.split("-")
        nextdayend = addDay(1, int(y), int(m), int(d))
        col = r.status
        sff = []
    #  uuid_with_dashes = t1.teacher_id  # This is a UUID object
    #     uuid_without_dashes = str(uuid_with_dashes).replace('-', '')
        delta = r.ev_date_end - r.ev_date_start
        days_difference = delta.days + 1
        
        order_dep = register_main.objects.filter(orderstatus='Deposit',ev_id=r.ev_id).count()
        print(r.ev_id)
        if order_dep > 0 :
            t = "#f13312"
        else :    
            t = '#4be01b'
        res = {'backgroundColor':t,'borderColor':'#1e7e34','textColor':'#ffffff','title': str(r.course.course_code) + " (รุ่นที่ " + str(r.ev_generation)+")" + "รายการค้างชำระ " + str(order_dep),'data':sff,
                'limit_price_workhelp':r.limit_price_workhelp,'limit_price':r.limit_price,'dis_limit': r.limit_price - (teacher_income_setting.objects.filter(ev=r.ev_id,pi=3).aggregate(Sum('tis_sum'))['tis_sum__sum'] or 0), 'start': r.ev_date_start, 'end': dmytoymd(nextdayend),'evs_id':r.ev_id,'ev_hour':r.ev_hour,'ev_hour_two':r.ev_hour_two,'ev_hour_three':r.ev_hour_three,'ev_people': r.ev_people,'ev_people_two': r.ev_people_two,'ev_people_three': r.ev_people_three,'count_day':days_difference}
        obj.append(res)
       
    return JsonResponse(obj, safe=False)

def calendar_event_apiteacher(request):
    user_id = request.user.id
    
    x = fact_teacher_user.objects.get(user_id=user_id)
  
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    _date = date.today()
    if start is not None and end is not None:
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        sobj = str(start).split("T")[0]
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        eobj = str(end).split("T")[0]
    else:
        sobj = _date + timedelta(days=0)
        eobj = _date + timedelta(days=60)
    status = ['W','Y','I','S']


    ev_group = []
    # contentxxx = event_register.objects.select_related('ev').filter(status__in=status,ev__active=1, ev__cancelled=1, ev__ev_date_start__gte=sobj, ev__ev_date_end__lte=eobj ,ev__module=m.module)
    data = teacher_income_setting.objects.filter(teacher=x.teacher_id)
    if data.count() > 0:
        for x in data:
            ev_group.append(x.ev_id)
            
    content = course_event.objects.select_related(
        "course").filter(active=1, cancelled=1, ev_date_start__gte=sobj, ev_date_end__lte=eobj ,module=m.module, status__in=status,ev_id__in=ev_group)
   
    obj = []
    sff = []
    for r in content:
        
    
     
    
        end = str(r.ev_date_end)
      
        y, m, d = end.split("-")
       
        

        col = r.status
        if col == 'W' :
         t = '#4be01b'
        elif col == 'Y': 
         t = '#4be01b'  
        elif col == 'I': 
         t = '#4be01b'  
        elif col == 'S': 
         t = '#4be01b'    
        else:
         t = '#4be01b'
        teacher_data = teacher_income_setting.objects.filter(ev=r.ev_id)
   
   
        
        
       
    #  uuid_with_dashes = t1.teacher_id  # This is a UUID object
    #     uuid_without_dashes = str(uuid_with_dashes).replace('-', '')
        delta = r.ev_date_end - r.ev_date_start
        days_difference = delta.days + 1
     
        res = {'backgroundColor':t,'borderColor':'#1e7e34','textColor':'#ffffff','title': str(r.course.course_name) + " (รุ่นที่ " + str(r.ev_generation)+")",'start': r.ev_date_start,'evs_id':r.ev_id}
        obj.append(res)
       
    return JsonResponse(obj, safe=False)



def calendar_event_api2(request,id):
    user_id = request.user.id
    sss = id
    pi = ['1','2','3','4','5','6','7','8']
    _date = date.today()
    date_60_days_ago = _date - timedelta(days=45)
    # content = teacher_income_setting.objects.select_related('ev').filter(teacher_id=id,tis_start_date__gt=datetime.date.today())
    content = teacher_income_setting.objects.select_related('ev').filter(teacher_id=id,pi__in=pi,tis_start_date__gte=date_60_days_ago).order_by(F('ev__ev_date_start').desc())
   
    obj = []
    
    for r in content:  
       
       start = str(r.ev.ev_date_start)
       end = str(r.ev.ev_date_end)
       
       y, m, d = end.split("-")
       Y, mM, dD = start.split("-")
       te = []
       
       teach = teacher_income_setting.objects.filter(ev_id=r.ev_id)
       evte = course_event.objects.get(ev_id=r.ev_id)
   

       for x in teach: 
       
        a = teacher.objects.get(teacher_id=x.teacher_id)
        pa = pay_item.objects.filter(id=x.pi_id).first()


   

       
        fs = {'fname':a.teacher_firstname_th,'lname':a.teacher_lastname_th,'status':x.status,'position':x.pi_id,'pay_name':str(pa),'register_id':r.register_id}
        
        te.append(fs)  
        
        
       nextdayend = addDay(1, int(y), int(m), int(d))
       result = course.objects.filter(course_id=r.ev.course_id).first()
       
       
       pay = pay_item.objects.filter(id=r.pi_id).first()
       
       
    
       day_of_week = r.ev.ev_date_start.weekday()
       

       if day_of_week:
            try:
                
                if day_of_week == 0:
                    dt = "จ"
                elif day_of_week == 1: 
                    dt = "อ"  
                elif day_of_week == 2:
                    dt = "พ"  
                elif day_of_week == 3: 
                    dt = "พฤ" 
                elif day_of_week == 4: 
                    dt = "ศ"
                elif day_of_week == 5:
                    dt = "ส"
                elif day_of_week == 6:   
                    dt = "อา"           
            except ValueError:
                dt = "-"
       else:
            dt = "จ"
     

       col = r.status
       if col == 'W' :
        t = '#e0ce1b'
       else:
        t = '#4be01b'
       r.ev_id
       eve = course_event.objects.get(ev_id=r.ev_id)
       loc = location_thai.objects.get(location_id=eve.location_id)
     
      
       res = {'address':eve.address,'prov':loc.province_name,'amphur_name':loc.amphur_name,'teach':te,'daynum':dD,'day':dt,'evs_status':r.status,'start': r.ev.ev_date_start,'end':dmytoymd(nextdayend),'course_id':(r.ev.course_id),'evs_id':(r.id),'title': str(result.course_name) + " (รุ่นที่ " + str(r.ev.ev_generation)+") ตำแหน่ง"+ str(pay),'backgroundColor':t,'borderColor':'#1e7e34','textColor':'#ffffff','show':evte.is_show,'end_day':r.ev.ev_date_end}
    
       obj.append(res)      
       
    return JsonResponse(obj, safe=False)

def calendar_event_apizs(request):
    user_id = request.user.id
  
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    _date = date.today()
    if start is not None and end is not None:
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        sobj = str(start).split("T")[0]
        # 2022-10-31T00:00:00+07:00 to  2022-10-31
        eobj = str(end).split("T")[0]
    else:
        sobj = _date + timedelta(days=0)
        eobj = _date + timedelta(days=60)
    status = ['','N','Y','I','S']
    # contentxxx = event_register.objects.select_related('ev').filter(status__in=status,ev__active=1, ev__cancelled=1, ev__ev_date_start__gte=sobj, ev__ev_date_end__lte=eobj ,ev__module=m.module)
    
 
    content = course_event.objects.select_related(
        "course").filter(active=1, cancelled=1, ev_date_start__gte=sobj, ev_date_end__lte=eobj ,module=m.module, status__in=status,checkevent=1)
   
    obj = []
    sff = []
    for r in content:
 
        end = str(r.ev_date_end)
      
        y, m, d = end.split("-")
        nextdayend = addDay(1, int(y), int(m), int(d))
        

        col = r.status
       
        if col == '' :
         t = '#f60a0a'
        else:
         t = '#4be01b'
 
    #  uuid_with_dashes = t1.teacher_id  # This is a UUID object
    #     uuid_without_dashes = str(uuid_with_dashes).replace('-', '')
        delta = r.ev_date_end - r.ev_date_start
        days_difference = delta.days + 1
     
        res = {'backgroundColor':t,'borderColor':'#1e7e34','textColor':'#ffffff','title': str(r.course.course_name) + " (รุ่นที่ " + str(r.ev_generation)+")",'start': r.ev_date_start, 'end': dmytoymd(nextdayend),'evs_id':r.ev_id,'ev_hour':r.ev_hour,'ev_hour_two':r.ev_hour_two,'ev_hour_three':r.ev_hour_three,'ev_people': r.ev_people,'ev_people_two': r.ev_people_two,'ev_people_three': r.ev_people_three,'count_day':days_difference,'evs_status':r.status}
        obj.append(res)
       
    return JsonResponse(obj, safe=False)


@login_required(login_url='/login')
def course_teacher_event_list(request,ev_id):
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
        instance = course_event.objects.get(pk=ev_id)
    except course_event.DoesNotExist:
        instance = None
        return redirect("/course/event")
    # print(instance.ev_date_start.month)
    teacher_data = teacher_income_setting.objects.filter(ev=ev_id)
    context = {'title': defaultTitle, 'main_data': instance,  'data': teacher_data,'listMenuPermission': objMenu}
    return render(request, 'course/course_teacher_event_list.html', context)


@login_required(login_url='/login')
def approve_listevent(request):
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


    context = {'title': defaultTitle,'listMenuPermission': objMenu}
    return render(request, 'course/approve_list_event.html', context)    



@csrf_exempt
def updateeve(request):
 if request.method == "POST":
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            evs_id = data.get("evs_id")
    
            content = teacher_income_setting.objects.get(id=evs_id)
            
            content.status = "Y"
            content.save()

          
            
        

    
          

        except json.JSONDecodeError:
            return JsonResponse({"error": 'x'}, status=400,safe=False)

        content = teacher_income_setting.objects.get(id=evs_id)
       
        teach = teacher_income_setting.objects.filter(ev_id=content.ev_id)
        all_passed = all(record.status == 'Y' for record in teach)
        if all_passed:
         
            content = course_event.objects.get(ev_id=content.ev_id)
            content.status = 'I'
            content.save()
        return JsonResponse({"status": "ok"}, status=200)       

@csrf_exempt
def updatstatusev(request):
 if request.method == "POST":
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            ev_id = data.get("ev_id")
            show = data.get("is_show")
           
            content = course_event.objects.get(ev_id=ev_id)
            content.is_show = show
            content.save()
    
            return JsonResponse(data, status=200,safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": 'x'}, status=400,safe=False)

        return JsonResponse({"error": "Only POST method is allowed"}, status=405)    

@csrf_exempt
def getgen(request):
 if request.method == "POST":

        try:
            data = json.loads(request.body)
            ev_id = data.get("ev_id")
            content = course_event.objects.filter(course_id=ev_id,cancelled=1).last()

            if content:
                    print(content.ev_generation + 1)
                    return JsonResponse(content.ev_generation + 1, status=200,safe=False)
            else:
                    print("No active product found.")
                    return JsonResponse(1, status=200,safe=False)
        except course_event.DoesNotExist:
            
            return JsonResponse({'error': 'not found'}, status=405)       




@csrf_exempt
def update_course_even(request):
    data = json.loads(request.body)
    ev_id = data.get("evs_id")

    content = course_event.objects.get(ev_id=ev_id)
    content.status = 'Y'
    content.save()

    return JsonResponse({"status": "ok"}, status=200)      



@csrf_exempt
def conditionhead(request):
    data = json.loads(request.body)
    id = data.get("id")
    content = []
    content = conhead.objects.select_related("course").filter(course=id,is_active='Y').values("conhead_id", "name","course__course_code")


    return JsonResponse(list(content), status=200, safe=False)     
@csrf_exempt
def conditionheadsave(request):
    data = json.loads(request.body)
    id = data.get("id")
    name = data.get("name")
    content = conhead.objects.get(pk=id)
    content.name = name
    content.save()

    return JsonResponse(id, status=200, safe=False)   

@csrf_exempt
def conditionheadcreate(request):
    data = json.loads(request.body)
    course_id = data.get("course_id")
    name = data.get("name")

    content = conhead(
        name=name,
        course_id=course_id,
        is_active='Y',
     )
    content.save()

    return JsonResponse(course_id, status=200, safe=False)     

@csrf_exempt
def conditionheaddel(request):
    data = json.loads(request.body)
    id = data.get("id")
    content = conhead.objects.get(pk=id)


    return JsonResponse(content, status=200, safe=False)  


@csrf_exempt
def condition_form_update_event(request):
    data = json.loads(request.body)
    ev_id = data.get("ev_id")
    condition_id = data.get("condition_id")
    condition_type = data.get("condition_type")


    content = course_event.objects.get(pk=ev_id)
    content.condition_id = condition_id
    content.condition_type = condition_type
    content.save()
  

    return JsonResponse(data, status=200, safe=False)  


@csrf_exempt
def calendar_event_api_totalbill(request):
    data = json.loads(request.body)
    user_id = request.user.id
    ev_id = data.get("ev_id")

    content = course_event.objects.get(ev_id=ev_id)
    regbyev = register_main.objects.filter(ev_id=ev_id)
    total_rq_quta = 0
    
    for aaa in regbyev:
        
        try:
            bbbb = register_payment.objects.filter(register_id=aaa.register_id).first()
            if bbbb:
             total_rq_quta += bbbb.rp_quota
        except register_payment.DoesNotExist:  
            bbbb = 0


    data = {'total_rq_quta':total_rq_quta,'condition_id':content.condition_id,'condition_type':content.condition_type}
    return JsonResponse(data, status=200, safe=False)  

    