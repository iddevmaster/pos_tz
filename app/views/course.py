from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.db.models import Count
from ..models import course, course_event, user_group,category_program_permission,user_detail,teacher_income_setting,location_thai,pay_item,teacher,project_code
from ..constant import defaultTitle
from ..functions import addDay, addYear, dateTimeNow, dmytoymd
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
import json


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
            status='Y')      
    
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

    context = {'title': defaultTitle, 'listMenuPermission': objMenu, 'data': result, 'course_list': course_list,'location': _location,'project_list':project_list}
    
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
    ev_hour_three = request.POST['ev_hour_three']
    ev_people = request.POST['ev_people']
    ev_people_two = request.POST['ev_people_two']
    ev_people_three = request.POST['ev_people_three']

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
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow(),
        ev_hour=ev_hour,
        ev_hour_two=ev_hour_two,
        ev_hour_three=ev_hour_three,
        ev_people=ev_people,
        ev_people_two=ev_people_two,
        ev_people_three=ev_people_three,
        status='N',
        module=m.module,
    )
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/course/event")


@login_required(login_url='/login')
def course_event_update(request):
    
    ev_id = request.POST['ev_id']
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
    ev_hour_three = request.POST['ev_hour_three']
    ev_people = request.POST['ev_people_update']
    ev_people_two = request.POST['ev_people_two_update']
    ev_people_three = request.POST['ev_people_three_update']
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
    content.course_id = course_id
    content.project_id = project_id
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/course/event")


@login_required(login_url='/login')
def course_event_delete(request):
    ev_id = request.POST['ev_id']
    content = course_event.objects.get(pk=ev_id)
    content.cancelled = 0
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/course/event")


@login_required(login_url='/login')
def calendar_event(request):
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
    context = {'title': title,'listMenuPermission': objMenu}
    return render(request, 'course/calendar_event.html', context)

    


def calendar_event_api(request):
    user_id = request.user.id
    print (request.GET)
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
        sobj = _date + timedelta(days=-30)
        eobj = _date + timedelta(days=30)
    content = course_event.objects.select_related(
        "course").filter(active=1, cancelled=1, ev_date_start__gte=sobj, ev_date_end__lte=eobj ,module=m.module)
    # print(len(content))

    obj = []

    for r in content:
        end = str(r.ev_date_end)
        y, m, d = end.split("-")
        nextdayend = addDay(1, int(y), int(m), int(d))

        col = r.status
        if col == 'W' :
         t = '#e0ce1b'
        elif col == 'N': 
         t = '#eb2509'   
        else:
         t = '#4be01b'
        
        res = {'backgroundColor':t,'borderColor':'#1e7e34','textColor':'#ffffff','title': str(r.course.course_name) + " (รุ่นที่ " + str(r.ev_generation)+")",
               'start': r.ev_date_start, 'end': dmytoymd(nextdayend)}
        obj.append(res)
    return JsonResponse(obj, safe=False)


def calendar_event_api2(request,id):
    user_id = request.user.id
    sss = id
    
    content = teacher_income_setting.objects.select_related('ev').filter(teacher_id=id,tis_start_date__gt=datetime.date.today())
  
    obj = []
    
    for r in content:  
       print(r)
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
       
        fs = {'fname':a.teacher_firstname_th,'lname':a.teacher_lastname_th,'status':x.status,'position':x.pi_id,'pay_name':str(pa)}
        
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
            dt = "-"
     

       col = r.status
       if col == 'W' :
        t = '#e0ce1b'
       else:
        t = '#4be01b'

       res = {'teach':te,'daynum':dD,'day':dt,'evs_status':r.status,'start': r.ev.ev_date_start,'end':dmytoymd(nextdayend),'course_id':(r.ev.course_id),'evs_id':(r.id),'title': str(result.course_name) + " (รุ่นที่ " + str(r.ev.ev_generation)+") ตำแหน่ง"+ str(pay),'backgroundColor':t,'borderColor':'#1e7e34','textColor':'#ffffff','show':evte.is_show}

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
            content.status = 'Y'
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