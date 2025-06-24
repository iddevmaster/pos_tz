from datetime import date
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Value
from django.db.models.functions import TruncMonth
from ..models import category_program_permission, course, course_event, teacher_income_setting, billing_cycle_setting, user_group, user_detail, teacher,pay_item,compensation,event_register,salesorder,register_main,location_thai,document,fact_teacher_user,register_payment,condition,conhead,tax_setting
from ..constant import defaultTitle, thai_months,unitPayChoices
from ..functions import dateTimeNow, last_day_of_month
from ..forms.finance_form import billing_cycle_setting_form
from ..forms.teacher_form import teacherIncomeSettingForm
from django.http import JsonResponse
import json
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Coalesce


@login_required(login_url='/login')
def course_event_list(request):
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
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    month_current = request.GET.get('qmonths', date.today().month)
    year_current = request.GET.get('qyear', date.today().year)
    course_list = course.objects.filter(
        cancelled=1, active=1).order_by("-course_id")
    status = ['W','Y','I']    
    result = course_event.objects.select_related("course").filter(
        cancelled=1, ev_date_start__month=month_current, ev_date_start__year=year_current, module=m.module,status__in=status).order_by("-ev_id")

    te = []

    # result = event_register.objects.select_related("ev").filter(ev__cancelled=1, status__in=status, ev__ev_date_start__month=month_current, ev__ev_date_start__year=year_current, ev__module=m.module)
    # for r in result:  
    #  content = course.objects.get(pk=r.ev.course_id)
    #  saf = register_main.objects.get(pk=r.register_id)
     
     
    #  fs = {'register_id':r.register_id,'course_code':content.course_code,'course_name':content.course_name,'ev_id':r.ev.ev_id,'ev_price':r.ev.ev_price,'ev_date_start':r.ev.ev_date_start,'ev_date_end':r.ev.ev_date_end,'ev_generation':r.ev.ev_generation,'ev_expired_cer_date':r.ev.ev_expired_cer_date,'ev_expired_cer_quantity':r.ev.ev_expired_cer_quantity,'bill':saf.register_number}
        
    #  te.append(fs)  
    
    context = {'title': defaultTitle,  'data': result,
               'course_list': course_list, 'listMenuPermission': objMenu}
            
    return render(request, 'finance/course_event_list.html', context)


@login_required(login_url='/login')
def billing_cycle_setting_form_create(request):
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
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    if request.method == 'POST':
        form = billing_cycle_setting_form(request.POST)
        if not form.is_valid():
            messages.error(
                request, "ไม่สามารถทำรายการได้ !  ,กรุณาทำรายการใหม่อีกครั้ง ")
        if form.is_valid():
            form.save()
            messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/billing/setting/form/create")
    data = billing_cycle_setting.objects.filter(module=m.module)
    context = {'title': defaultTitle, 'form': billing_cycle_setting_form(
        initial={'module': m.module}), 'data': data, 'listMenuPermission': objMenu}
    return render(request, 'finance/billing_cycle_setting_form_create.html', context)


@login_required(login_url='/login')
def billing_cycle_setting_form_delete(request):
    id = request.POST['id']
    try:
        instance = billing_cycle_setting.objects.get(pk=id)
    except billing_cycle_setting.DoesNotExist:
        instance = None
        return redirect("/billing/setting/form/create")
    instance.delete()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/billing/setting/form/create")


@login_required(login_url='/login')
def billing_cycle_result(request):
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
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    # month_current = date.today().month
    year_current = request.GET.get('qyear', date.today().year)
    teacher_current = request.GET.get('qteacher', None)
    day_current = date.today().day

   
    # day_current = 10
    b = billing_cycle_setting.objects.filter(module=m.module)

    start_content = teacher_income_setting.objects.filter(
        ev__module=m.module, tis_end_date__year=year_current,status='I').annotate(month=TruncMonth('tis_start_date'))
    
    start_content = start_content.values('month').annotate(
        order_count=Count('id'), order_sum=Sum('tis_sum')).order_by('-month')
    
    if teacher_current != None and teacher_current != '':
        start_content = start_content.filter(teacher=teacher_current)
    # print(content)
    list_teacher = teacher.objects.filter(
        module=m.module, cancelled=1, active=1)
    obj = []
  
   
  
    for r1 in start_content:
        
        total_month_sum = r1['order_sum']
        defaultdata = r1['month']  # y-m-d
        month = defaultdata.month
        
        get_last_day = last_day_of_month(
            datetime.date(int(year_current), month, 1))
        last_day = get_last_day.day
        
   
        for r2 in b:
            day_start = r2.bcs_start_day
            day_end = r2.bcs_end_day
            tis_group = f"{day_start} - {day_end}"
         
     
            # ถ้าเดือนสุดท้ายน้อยกว่าค่า day_end ที่ตั้งไว้ ให้เอาเดือนสุดท้ายมาตั้งใหม่
            if last_day <= day_end:
                
                day_end = last_day
        
            instance = teacher_income_setting.objects.filter(
                ev__module=m.module,
                active=0,
                tis_start_date__day__gte=day_start,
                tis_end_date__day__lte=day_end,
                tis_end_date__month=month,
                tis_end_date__year=year_current,
                status="S"
            )
            # for a in instance:
            #      print(a.ev_id)
           
            if teacher_current != None and teacher_current != '':
                instance = instance.filter(teacher=teacher_current)
          
            if day_current >= day_end and instance.count() >= 1:
                instance.update(tis_group=tis_group,status='S',
                                upd_date=dateTimeNow())
        obj2 = []
        content = teacher_income_setting.objects.filter(
            ev__module=m.module, active=1, tis_end_date__month=month, tis_end_date__year=year_current,status='S')
        if teacher_current != None and teacher_current != '':
            content = content.filter(teacher=teacher_current)
        group_content = content.values('tis_group').annotate(
            order_count=Count('id'), order_sum=Sum('tis_sum')).order_by('tis_group')

        for r3 in group_content:
            order_sum = r3['order_sum']
            tis_group = r3['tis_group']
            teachers = content.filter(tis_group=tis_group)
            new_data = {'tis_group': tis_group,
                        'order_sum': order_sum, 'teachers': teachers}
            
            obj2.append(new_data)
        final = {'month': thai_months[month-1],
                 'total_month_sum': total_month_sum, 'content': obj2}

        obj.append(final)

    context = {'title': defaultTitle, 'data': obj,
               'listMenuPermission': objMenu, 'list_teacher': list_teacher}
    return render(request, 'finance/billing_cycle_result.html', context)


@login_required(login_url='/login')
def course_teacher_event_set_income_form_create(request, ev_id):
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
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    module = m.module
    title = defaultTitle
    try:
    
        instance = course_event.objects.get(ev_id=ev_id)
    except course_event.DoesNotExist:
        instance = None
        return redirect("/finance/billing/setting")
    if request.method == 'POST':
        
        pi = request.POST['pi']
        tis_compensation = request.POST['tis_compensation']
        tis_unit = request.POST['tis_unit']
        tis_quantity = request.POST['tis_quantity']
        tis_sum = request.POST['tis_sum']
        teacher_id = request.POST['teacher']
        
        # register = str(request.POST['register_id']).replace('-', '')
        
        if pi == '1' or pi == '2':
         content = teacher_income_setting(
            tis_compensation=tis_compensation,
            tis_unit=tis_unit,
            tis_quantity=tis_quantity,
            tis_sum=tis_sum,
            tis_start_date=instance.ev_date_start,
            tis_end_date=instance.ev_date_end,
            ev_id=ev_id,
            teacher_id=teacher_id,
            pi_id=pi,
            crt_date=dateTimeNow(),
            upd_date=dateTimeNow(),
            status='W',
            register_id='-',
        )
         content.save()
         x = course_event.objects.get(ev_id=ev_id)
         x.status = "W"
         x.save()

        if pi == '3':
         contentx = teacher_income_setting(
            tis_compensation=tis_compensation,
            tis_unit=tis_unit,
            tis_quantity=tis_quantity,
            tis_sum=tis_sum,
            tis_start_date=instance.ev_date_start,
            tis_end_date=instance.ev_date_end,
            ev_id=ev_id,
            teacher_id=teacher_id,
            pi_id=pi,
            crt_date=dateTimeNow(),
            upd_date=dateTimeNow(),
            status='W',
            register_id='-',
            
         )
         contentx.save()
        #  x = event_register.objects.get(register_id=register)
        #  x.status = "W"
        #  x.save()
         tot = 0
         x = course_event.objects.get(ev_id=ev_id)
         x.status = "W"
         x.save()
         totalpeol = teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=pi).count()
    
        if pi == '4':
         contentx = teacher_income_setting(
            tis_compensation=tis_compensation,
            tis_unit=tis_unit,
            tis_quantity=tis_quantity,
            tis_sum=tis_sum,
            tis_start_date=instance.ev_date_start,
            tis_end_date=instance.ev_date_end,
            ev_id=ev_id,
            teacher_id=teacher_id,
            pi_id=pi,
            crt_date=dateTimeNow(),
            upd_date=dateTimeNow(),
            status='W',
            register_id='-',
            
         )
         contentx.save()
        #  x = event_register.objects.get(register_id=register)
        #  x.status = "W"
        #  x.save()
         tot = 0
         x = course_event.objects.get(ev_id=ev_id)
         x.status = "W"
         x.save()
         totalpeol = teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=pi).count()

        if pi == '5':
        
         contentx = teacher_income_setting(
            tis_compensation=tis_compensation,
            tis_unit=tis_unit,
            tis_quantity=tis_quantity,
            tis_sum=tis_sum,
            tis_start_date=instance.ev_date_start,
            tis_end_date=instance.ev_date_end,
            ev_id=ev_id,
            teacher_id=teacher_id,
            pi_id=pi,
            crt_date=dateTimeNow(),
            upd_date=dateTimeNow(),
            status='W',
            register_id='-',
            
         )
         contentx.save()

         tot = 0
         x = course_event.objects.get(ev_id=ev_id)
         x.status = "W"
         x.save()
         totalpeol = teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=pi).count()
           
    
         if totalpeol > 0 :
            bb = 1000 / totalpeol
            teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=pi).update(tis_sum=0,tis_compensation=0)  
        if pi == '6':
         contentx = teacher_income_setting(
            tis_compensation=0,
            tis_unit=tis_unit,
            tis_quantity=tis_quantity,
            tis_sum=0,
            tis_start_date=instance.ev_date_start,
            tis_end_date=instance.ev_date_end,
            ev_id=ev_id,
            teacher_id=teacher_id,
            pi_id=pi,
            crt_date=dateTimeNow(),
            upd_date=dateTimeNow(),
            status='W',
            register_id='-',
         )
         contentx.save()
  
         x = course_event.objects.get(ev_id=ev_id)
         x.status = "W"
         x.save()
         totalpeol = teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=pi).count()
         if totalpeol > 0 :
           bb = 300 / totalpeol
           teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=pi).update(tis_sum=bb,tis_compensation=bb) 





        if pi == '7' or pi == '8':
         content = teacher_income_setting(
            tis_compensation=0,
            tis_unit=tis_unit,
            tis_quantity=tis_quantity,
            tis_sum=0,
            tis_start_date=instance.ev_date_start,
            tis_end_date=instance.ev_date_end,
            ev_id=ev_id,
            teacher_id=teacher_id,
            pi_id=pi,
            crt_date=dateTimeNow(),
            upd_date=dateTimeNow(),
            status='Y',
            register_id='-',
        )
         content.save()
         x = course_event.objects.get(ev_id=ev_id)
         x.status = "W"
         x.save()



        messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/course/event/teachers/form/create/" + str(ev_id))
    # print(instance.ev_date_start.month)
    # regis_i = event_register.objects.get(register_id=register_id)
    
    teacher_data = teacher_income_setting.objects.filter(ev=ev_id)
  
    ids = [1, 2]



    delta = instance.ev_date_end - instance.ev_date_start
    days_difference = delta.days + 1

        
    count_hour_wi = teacher_income_setting.objects.filter(ev=ev_id,pi__in=ids).aggregate(Sum('tis_quantity'))['tis_quantity__sum'] or 0
    count_hour_pi = teacher_income_setting.objects.filter(ev=ev_id,pi=3).aggregate(Sum('tis_quantity'))['tis_quantity__sum'] or 0
    dis_limit = teacher_income_setting.objects.filter(ev=ev_id,pi=3).aggregate(Sum('tis_sum'))['tis_sum__sum'] or 0
    total = instance.limit_price - dis_limit
    listposition = pay_item.objects.filter(
            cancelled=1, active=1)
    list_teacher = teacher.objects.filter(
        module=m.module, cancelled=1, active=1)
    location = location_thai.objects.get(location_id=instance.location_id)

    
    context = {'title': title, 'main_data': instance,  'data': teacher_data,'dis_limit': total,'address':location,
               'form': teacherIncomeSettingForm(module), 'listMenuPermission': objMenu,'teacher':list_teacher,'unit':unitPayChoices,'listposition':listposition,'hour_wi':count_hour_wi,'hour_pi':count_hour_pi,'count_day':days_difference}
    return render(request, 'finance/course_teacher_event_set_income.html', context)


@login_required(login_url='/login')
def course_teacher_event_set_income_form_delete(request):
    id = request.POST['id']
    ev_id = request.POST['ev_id']
    py_id = request.POST['py_id_delete']
    
    try:
        instance = teacher_income_setting.objects.get(pk=id)
    except teacher_income_setting.DoesNotExist:
        instance = None
        return redirect("/course/event/teachers/form/create/" + str(ev_id))
    instance.delete()

    c_event = course_event.objects.get(pk=ev_id)
   
    if py_id == '5':
       data_tac = teacher_income_setting.objects.filter(ev_id=ev_id,active=0,pi_id=py_id).count()
       
       if data_tac > 0 :
         bb = 1000 / data_tac
         teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=py_id).update(tis_sum=bb,tis_compensation=bb)

    if py_id == '6':
        data_tac = teacher_income_setting.objects.filter(ev_id=ev_id,active=0,pi_id=py_id).count()
        if data_tac > 0 :
            bb = 300 / data_tac
            teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=py_id).update(tis_sum=bb,tis_compensation=bb)



    if teacher_income_setting.objects.filter(ev_id=ev_id).count() == 0:
        c_event = course_event.objects.get(pk=ev_id)
        c_event.status = "N"
        c_event.save()

    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/course/event/teachers/form/create/" + str(ev_id))



@csrf_exempt
def course_teacher_event_get_income_form_compo(request):
 if request.method == "POST":
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            
            teacher = data.get("teacher_id")
            py = data.get("py")
            
            data = compensation.objects.filter(
            py_id=py, teacher_id=teacher).values().first()
           
            # x = compensation.objects.all()
          
            # Simulate saving the item (replace with database save later)
            if data:
                return JsonResponse(data, status=201,safe=False)
            else:
                data = []
                return JsonResponse(data, status=200,safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": data}, status=400,safe=False)

        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

@csrf_exempt
def checkhours(request):
 if request.method == "POST":
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
       
            pi = data.get("pi")
            tis_quantity = data.get("tis_quantity")
            ev_id = data.get("ev_id")
            teacher_id = data.get("teacher_id")
            instance = course_event.objects.filter(pk=ev_id).values().first()
            st =['Y','W']
            content = teacher_income_setting.objects.filter(ev_id=ev_id,status__in=st,pi=pi).aggregate(total=Coalesce(Sum('tis_quantity'), Value(0)))
            tttt = teacher_income_setting.objects.filter(ev_id=ev_id,status__in=st,pi=pi).values('pi').annotate(total=Count('pi')) 
            teacher = teacher_income_setting.objects.filter(ev_id=ev_id,status__in=st,pi=pi,teacher_id=teacher_id).count() or 0
         
            data['status_hour'] = True
            data['status_people'] = True
            data['status_teacher'] = True
            if pi == '1' : 
                hour = instance['ev_hour'] or 0
                people = instance['ev_people'] or 0   
                
            # เช็คว่า มีครูฝึกคนนี้รึยัง
            
                totalp = 0
                total = content['total'] + tis_quantity
                for author in tttt:
                    totalp = author['total']
                if hour < total :
                    data['status_hour'] = False
                if people <= totalp:
                    data['status_people'] = False    
                if teacher > 0:
                    data['status_teacher'] = False

            elif  pi == '2' :
              
                hour = instance['ev_hour_two'] or 0
                people = instance['ev_people_two'] or 0

                totalp = 0
                total = content['total'] + tis_quantity
                for author in tttt:
                    totalp = author['total']
                if hour < total :
                    data['status_hour'] = False
                if people <= totalp:
                    data['status_people'] = False    
                if teacher > 0:
                    data['status_teacher'] = False
            elif  pi == '3' :
             
              

                teacher = teacher_income_setting.objects.filter(ev_id=ev_id,status__in=st,pi=pi,teacher_id=teacher_id).count() or 0
                if teacher > 0:
                    data['status_hour'] = True
                    data['status_people'] = True
                    data['status_teacher'] = False
      
            elif  pi == '4' :
             
                 if teacher > 0:
                    data['status_hour'] = True
                    data['status_people'] = True
                    data['status_teacher'] = False
            elif  pi == '4' or pi == '5'or pi == '6'or pi == '7'or pi == '8':
             
                 if teacher > 0:
                    data['status_hour'] = True
                    data['status_people'] = True
                    data['status_teacher'] = False        
       
         
            if data:
                datas = {'status_hour': data['status_hour'],'status_people': data['status_people'],'status_teacher': data['status_teacher']}
      
              
                return JsonResponse(datas, status=201,safe=False)
            else:
                datas = {'status_hour': data['status_hour'],'status_people': data['status_people'],'status_teacher': data['status_teacher']}
         
                return JsonResponse(datas, status=200,safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": instance}, status=400,safe=False)

        return JsonResponse({"error": "Only POST method is allowed"}, status=405)        

@csrf_exempt
def saveeventadmin(request):
 if request.method == "POST":
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            ev_id = data.get("ev_id")
            pi = data.get("pi")
            teacher_id = data.get("teacher_id")
            tis_compensation = data.get("tis_compensation")
            tis_quantity = data.get("tis_quantity")
            tis_sum = data.get("tis_sum")
            tis_unit = data.get("tis_unit")
            
                 
       
          
            instance = course_event.objects.filter(pk=ev_id).first()
      
            if pi == '1' or pi == '2':
              content = teacher_income_setting(
                tis_compensation=tis_compensation,
                tis_unit=tis_unit,
                tis_quantity=tis_quantity,
                tis_sum=tis_sum,
                tis_start_date=instance.ev_date_start,
                tis_end_date=instance.ev_date_end,
                ev_id=ev_id,
                teacher_id=teacher_id,
                pi_id=pi,
                crt_date=dateTimeNow(),
                upd_date=dateTimeNow(),
                status='W',
                register_id='-',
                )
              content.save()
              x = course_event.objects.get(ev_id=ev_id)
        
              x.status = 'W'
              x.save()
            datas = {'status':200} 
            if pi == '3':

              content = teacher_income_setting(
                tis_compensation=tis_compensation,
                tis_unit=tis_unit,
                tis_quantity=tis_quantity,
                tis_sum=tis_sum,
                tis_start_date=instance.ev_date_start,
                tis_end_date=instance.ev_date_end,
                ev_id=ev_id,
                teacher_id=teacher_id,
                pi_id=pi,
                crt_date=dateTimeNow(),
                upd_date=dateTimeNow(),
                status='W',
                register_id='-',
            )
              content.save()
  
              x = course_event.objects.get(ev_id=ev_id)
        
              x.status = 'W'
              x.save()
             
   
            if pi == '4':

              content = teacher_income_setting(
                tis_compensation=tis_compensation,
                tis_unit=tis_unit,
                tis_quantity=tis_quantity,
                tis_sum=tis_sum,
                tis_start_date=instance.ev_date_start,
                tis_end_date=instance.ev_date_end,
                ev_id=ev_id,
                teacher_id=teacher_id,
                pi_id=pi,
                crt_date=dateTimeNow(),
                upd_date=dateTimeNow(),
                status='W',
                register_id='-',
            )
              content.save()
  
              x = course_event.objects.get(ev_id=ev_id)
        
              x.status = 'W'
              x.save()
             


            datas = {'status':200}


            if pi == '5':    
              content = teacher_income_setting(
                tis_compensation=tis_compensation,
                tis_unit=tis_unit,
                tis_quantity=tis_quantity,
                tis_sum=tis_sum,
                tis_start_date=instance.ev_date_start,
                tis_end_date=instance.ev_date_end,
                ev_id=ev_id,
                teacher_id=teacher_id,
                pi_id=pi,
                crt_date=dateTimeNow(),
                upd_date=dateTimeNow(),
                status='W',
                register_id='-',
            )
              content.save()
              x = course_event.objects.get(ev_id=ev_id)
              x.status = 'W'
              x.save()
              tot = 0
              totalpeol = teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=pi).count()
              if totalpeol > 0 :
                  bb = 1000 / totalpeol
                  teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=pi).update(tis_sum=bb,tis_compensation=bb)
            
            datas = {'status':200}


            if pi == '6':    
              content = teacher_income_setting(
                tis_compensation=300,
                tis_unit=tis_unit,
                tis_quantity=tis_quantity,
                tis_sum=300,
                tis_start_date=instance.ev_date_start,
                tis_end_date=instance.ev_date_end,
                ev_id=ev_id,
                teacher_id=teacher_id,
                pi_id=pi,
                crt_date=dateTimeNow(),
                upd_date=dateTimeNow(),
                status='W',
                register_id='-',
            )
              content.save()
              x = course_event.objects.get(ev_id=ev_id)
              x.status = 'W'
              x.save()
              tot = 0
            #   totalpeol = teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=pi).count()
            #   if totalpeol > 0 :
            #       bb = 300 / totalpeol
            #       teacher_income_setting.objects.filter(ev_id=ev_id, active=0,pi_id=pi).update(tis_sum=0,tis_compensation=0)
            

            if pi == '7':    
              content = teacher_income_setting(
                tis_compensation=0,
                tis_unit=tis_unit,
                tis_quantity=tis_quantity,
                tis_sum=0,
                tis_start_date=instance.ev_date_start,
                tis_end_date=instance.ev_date_end,
                ev_id=ev_id,
                teacher_id=teacher_id,
                pi_id=pi,
                crt_date=dateTimeNow(),
                upd_date=dateTimeNow(),
                status='W',
                register_id='-',
            )
              content.save()
              x = course_event.objects.get(ev_id=ev_id)
              x.status = 'W'
              x.save()

            if pi == '8':    
              content = teacher_income_setting(
                tis_compensation=0,
                tis_unit=tis_unit,
                tis_quantity=tis_quantity,
                tis_sum=0,
                tis_start_date=instance.ev_date_start,
                tis_end_date=instance.ev_date_end,
                ev_id=ev_id,
                teacher_id=teacher_id,
                pi_id=pi,
                crt_date=dateTimeNow(),
                upd_date=dateTimeNow(),
                status='Y',
                register_id='-',
            )
              content.save()
              x = course_event.objects.get(ev_id=ev_id)
              x.status = 'W'
              x.save()  
         
            
            datas = {'status':200}
            return JsonResponse(datas, status=200,safe=False)

        except json.JSONDecodeError:
            datas = {'status':400}
            return JsonResponse(datas, status=400,safe=False)

        return JsonResponse({"error": "Only POST method is allowed"}, status=405)  



@csrf_exempt
def evenetdel(request):
 if request.method == "POST":
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            ev_id = data.get("id")
           


            instance = teacher_income_setting.objects.get(pk=ev_id)

            register = instance.register_id
            pi_id = instance.pi_id
            evs_id = instance.ev_id
            insevent = course_event.objects.get(pk=instance.ev_id)
            instancexx = teacher_income_setting.objects.filter(ev_id=instance.ev_id,pi_id=pi_id).count()

            
            if instancexx >= 1 :
                if pi_id == 1 or pi_id == 2 or pi_id == 3 or pi_id == 4:
                  instancex = teacher_income_setting.objects.get(pk=ev_id)
                  instancex.delete()
                if pi_id == 7 or pi_id == 8:        
                  instancex = teacher_income_setting.objects.get(pk=ev_id)
                  instancex.delete()  
                # if pi_id == 3:
                #   instancex = teacher_income_setting.objects.get(pk=ev_id)
                #   instancex.delete()
                #   insevent = course_event.objects.get(pk=instance.ev_id)
                #   delta = insevent.ev_date_end - insevent.ev_date_start
                #   days_difference = delta.days + 1
                #   tot = 0
                #   totalpeol = teacher_income_setting.objects.filter(ev_id=evs_id, active=0,pi_id=pi_id,register_id=register).count()
                #   if totalpeol > 0 :
                #    tt_event = insevent.limit_price / totalpeol  # ค่าตอบแทนรายบุคคล
                #    bb = (insevent.limit_price * days_difference) / totalpeol
                #    teacher_income_setting.objects.filter(ev_id=evs_id, active=0,pi_id=pi_id,register_id=register).update(tis_sum=bb,tis_compensation=tt_event)
                #   datas = {'status':200}
                # if pi_id == 4:        
                #   instancex = teacher_income_setting.objects.get(pk=ev_id)
                #   instancex.delete()
                #   insevent = course_event.objects.get(pk=instance.ev_id)
                #   delta = insevent.ev_date_end - insevent.ev_date_start
                #   days_difference = delta.days + 1
                #   tot = 0
                #   totalpeol = teacher_income_setting.objects.filter(ev_id=evs_id, active=0,pi_id=pi_id,register_id=register).count()
                #   if totalpeol > 0 :
                #    tt_event = insevent.limit_price_workhelp / totalpeol  # ค่าตอบแทนรายบุคคล
                #    bb = insevent.limit_price_workhelp / totalpeol
                #    teacher_income_setting.objects.filter(ev_id=evs_id, active=0,pi_id=pi_id,register_id=register).update(tis_sum=bb,tis_compensation=tt_event)
                #   datas = {'status':200}

                if pi_id == 6:        
                  instancex = teacher_income_setting.objects.get(pk=ev_id)
                  instancex.delete()

                  totalpeol = teacher_income_setting.objects.filter(ev_id=evs_id, active=0,pi_id=pi_id,register_id=register).count()
                  if totalpeol > 0:
                   bb = 300 / totalpeol
                   teacher_income_setting.objects.filter(ev_id=evs_id, active=0,pi_id=pi_id,register_id=register).update(tis_sum=bb,tis_compensation=bb)
                  datas = {'status':200}  


                if pi_id == 5:        
                  instancex = teacher_income_setting.objects.get(pk=ev_id)
                  instancex.delete()

                  totalpeol = teacher_income_setting.objects.filter(ev_id=evs_id, active=0,pi_id=pi_id,register_id=register).count()
                  if totalpeol > 0:
                   xx = 1000 / totalpeol
                   teacher_income_setting.objects.filter(ev_id=evs_id, active=0,pi_id=pi_id,register_id=register).update(tis_sum=xx,tis_compensation=xx)
                  datas = {'status':200}    
                # ลบก่อน

         
                aaaa = teacher_income_setting.objects.filter(ev_id=instance.ev_id).count()
                if aaaa == 0 :
                    xx = course_event.objects.get(pk=instance.ev_id)
                    xx.status = 'Y'
                    xx.save()   
                datas = {'status':200}
                return JsonResponse(datas, status=200,safe=False)

            else:   
                # instancex = teacher_income_setting.objects.get(pk=ev_id)
                # instancex.delete()
       
                datas = {'status':200,'s':instancexx}
                return JsonResponse(datas, status=200,safe=False)
            
         
           
          
            datas = {'status':200}

            return JsonResponse(datas, status=200,safe=False)
           

        except json.JSONDecodeError:
            datas = {'status':400}
            return JsonResponse(datas, status=400,safe=False)

        return JsonResponse({"error": "Only POST method is allowed"}, status=405) 

@csrf_exempt
def updateteachincom(request):

    data = json.loads(request.body)
    teach_id = data.get("ev_id")
    it = data.get("it")
    total = data.get("total")
    doc = data.get("doc")
    doc_document = data.get("doc_document")
   


    sumt = int(total) * int(it)


    teacher_income = teacher_income_setting.objects.get(id=teach_id)

    if teacher_income.pi_id == 7:
         teacher_income = teacher_income_setting.objects.get(id=teach_id)
         teacher_income.status = 'S'
         teacher_income.tis_sum = sumt
         teacher_income.tis_compensation = sumt
         teacher_income.save()
        

    else:
    
     content = document(
            doc_number=doc_document,
            title='ขอตั้งเบิกค่าจ้างเหมา ',
            teacher_income_id=teach_id,
            price=sumt,
            created_at=dateTimeNow(),
         )
     content.save()
     teacher_income = teacher_income_setting.objects.get(id=teach_id)
     teacher_income.status = 'S'
     teacher_income.tis_sum = sumt
     teacher_income.tis_compensation = sumt
     teacher_income.save()
    datas = {'status':200}

    return JsonResponse(datas, status=200,safe=False)


@csrf_exempt
def sendwithdraw(request):
    day_current = date.today().day
    data = json.loads(request.body)
    user_id = data.get("user_id")
    year_current = request.GET.get('qyear', date.today().year)
    taxs = tax_setting.objects.get(tax_id=1)

    bill = billing_cycle_setting.objects.filter()
    user = fact_teacher_user.objects.get(user_id=user_id)
    check_income = teacher_income_setting.objects.filter(teacher=user.teacher_id,status="I",active=0)

    select_bill = 0
    

    for check in check_income:
        end_date = check.tis_end_date
        tis_group = ''
        end_day = end_date.day
        end_month = end_date.month
        
        get_last_day = last_day_of_month(
            datetime.date(int(year_current), end_month, 1))
        last_day = get_last_day.day
       
        for bills in bill:
            start = bills.bcs_start_day
            end = bills.bcs_end_day
                # เช็คว่าอยู่ในรอบต้นเดือน รึ ปลายเดือน
            if start <= end_day <= end: 
                select_bill = bills.id
                break
        if select_bill == 1:
            billone = billing_cycle_setting.objects.get(id=1)
            start = billone.bcs_start_day
            end = billone.bcs_end_day
            tis_group = f"{start} - {end}"
        else :  
            billone = billing_cycle_setting.objects.get(id=2)
            start = billone.bcs_start_day
            end = last_day
            tis_group = f"{start} - {end}"
      

        teacher_income = teacher_income_setting.objects.get(id=check.id)
        teacher_income.tis_group = tis_group
        teacher_income.status = 'S'
        teacher_income.tax = taxs.tax
        teacher_income.save()
            # ถ้าเดือนสุดท้ายน้อยกว่าค่า day_end ที่ตั้งไว้ ให้เอาเดือนสุดท้ายมาตั้งใหม่
            # if last_day <= day_end:
                
            #     day_end = last_day
        
            # instance = teacher_income_setting.objects.filter(
            #     active=0,
            #     tis_start_date__day__gte=day_start,
            #     tis_end_date__day__lte=day_end,
            #     tis_end_date__month=month,
            #     tis_end_date__year=year_current,
            #     status="I"
            # )
    
    
            # day_current  วันปัจจุบัน มากกว่า รึเท่ากับ 
            # if day_current >= day_end and instance.count() >= 1:
            #     instance.update(active=1, tis_group=tis_group,status='S',
            #                     upd_date=dateTimeNow())
        # obj2 = []
     

   
 

    # user = fact_teacher_user.objects.get(user_id=user_id)
    # teacher_income = teacher_income_setting.objects.filter(teacher=user.teacher_id,status="I",active=0)
    # teacher_income = teacher_income_setting.objects.filter(
    #             active=0,
    #             tis_start_date__day__gte=day_start,
    #             tis_end_date__day__lte=day_end,
    #             tis_end_date__month=month,
    #             tis_end_date__year=year_current,
    #             status="I"
    #         )
    # for r3 in teacher_income:
    #  teacher_income = teacher_income_setting.objects.get(id=r3.id)
    #  teacher_income.status = 'S'
    #  teacher_income.active = 1
    #  teacher_income.tax = taxs.tax
    #  teacher_income.save()

    datas = {'status':200}
    return JsonResponse(datas, status=200,safe=False)


def withdraw_list(request):
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
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')

    
   
    try:
        getteachid = fact_teacher_user.objects.get(user_id=user_id)
        obj = []
        pi = ['1','2','3','4','5','6','7']
        teacher_income = teacher_income_setting.objects.filter(teacher_id=getteachid.teacher_id,status='I',pi_id__in=pi)
        for rs in teacher_income:
            
            event = course_event.objects.get(ev_id=rs.ev_id)
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)

            r = {'pay_name':pay.pi_name,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':rs.pi_id,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation}
        
            obj.append(r)
        
        context = {'title': defaultTitle, 'listMenuPermission': objMenu,'data':obj}
    except fact_teacher_user.DoesNotExist:
        getteachid = None
        return redirect("/")
    
    

    return render(request, 'finance/order_withdraw.html',context)



def withdraw_list_commission(request):

   
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
    return render(request, 'course/calendar_event_all_com.html', context)


def withdraw_list_one(request):
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
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')

    
   
    try:
        getteachid = fact_teacher_user.objects.get(user_id=user_id)
        obj = []
        pi = ['1','2','3','4','5']
        totalp = 0
        teacher_income = teacher_income_setting.objects.filter(teacher_id=getteachid.teacher_id,status='I',pi_id__in=pi,active=0)
        
        name_con = '-'
        for rs in teacher_income:
            requirements = 'ไม่มี'
            regbyev = register_main.objects.filter(ev_id=rs.ev)
            
            total_rq_quta = 0
            for aaa in regbyev:
                
                try:
                    bbbb = register_payment.objects.filter(register_id=aaa.register_id).first()
                    if bbbb:
                        total_rq_quta += bbbb.rp_quota
                except register_payment.DoesNotExist:  
                        bbbb = 0
            
            event = course_event.objects.get(ev_id=rs.ev_id)
            
            select = 0
            price = 0
            tis_compensation = 0
           
            

            if int(event.condition_type) == 1:
                
                requirements = 'มี'
            if int(rs.pi_id) == 1:
           
             if event.condition_type == '1':  # เช็คว่า วิทยากร มีเงื่อนไขไหม
                print('event.condition_id',event)
                checkcourse = condition.objects.filter(conhead=event.condition_id).first() 
                checkhead = conhead.objects.filter(conhead_id=checkcourse.conhead_id).first() 
                checkcourse_con = course.objects.get(course_id=checkhead.course_id)
          
                if checkcourse_con.is_type_condition == '1':
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('student')
                   for iconts in icont:
                      typet = iconts.type
                      if iconts.type_add == '1': 
                       if typet == '1':
                        if total_rq_quta > iconts.student:
                            select = iconts.condition_id
                            break
                       elif typet == '2':
                    
                        if iconts.student < total_rq_quta:
                            select = iconts.condition_id
                            break
                       elif typet == '3':
                        if iconts.student == total_rq_quta: 
                            select = iconts.condition_id
                            break   

                else : 
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('action')
                   for iconts in icont:
                     if iconts.action == '0': 
                        print('เช็คลบก่อนน',iconts.action)
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='2').order_by('student')
                     elif iconts.action == '1':  
                        print('เช็คบวกที่หลัง',iconts.action) 
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='1').order_by('-student')
                     for checkcons in checkcon:
                        if total_rq_quta > checkcons.student:
                            select = checkcons.condition_id
                            
                            break
                        else:
                           select = 0
                          
 
             if select != 0:
              
              totalselect = condition.objects.get(condition_id=select)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              checkcourse_con = course.objects.get(course_id=checkhead.course_id)
              if checkcourse_con.is_type_condition == '1':
                 print('คิดนักเรียน')
                 price = int(rs.tis_quantity) * (totalselect.price)
                 name_con = head.name
                 tis_compensation = totalselect.price
              else:   
                 
                 if totalselect.action == '1':
                    tis_quantity = int(rs.tis_quantity) + int(totalselect.hour)
                    price = int(rs.tis_compensation) * (tis_quantity)
                    tis_compensation = rs.tis_compensation
                    name_con = head.name
                    
                 else :
                    price = int(rs.tis_quantity) * (totalselect.price)
                    name_con = head.name
                    tis_compensation = totalselect.price
                    


             else:
                
                price = int(rs.tis_quantity) * (rs.tis_compensation)  
                name_con = '-'
                tis_compensation = rs.tis_compensation
               
        
            else :    
            
             if int(rs.pi_id) == 2:
              price = int(rs.tis_quantity) * (rs.tis_compensation)  
              tis_compensation = rs.tis_compensation        
              
             elif int(rs.pi_id) == 3:
            
              price = int(rs.tis_quantity) * (rs.tis_compensation) 
              tis_compensation = rs.tis_compensation

             elif int(rs.pi_id) == 4:
            
              price = int(rs.tis_quantity) * (rs.tis_compensation) 
              tis_compensation = rs.tis_compensation
             elif int(rs.pi_id) == 5:
              
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)
         
            
            start = str(event.ev_date_start)
          
            end = str(event.ev_date_end)
            y, m, d = end.split("-")
            Y, mM, dD = start.split("-")
            day_of_week = event.ev_date_start.weekday()
           
           
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
            print(price) 
            totalp += price
            
            r = {'daynum':dD,'day':dt,'pay_name':pay.pi_name,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation}
        
            obj.append(r)
        
        context = {'title': defaultTitle, 'listMenuPermission': objMenu,'data':obj,'total_all':totalp,'user_id':user_id}
    except fact_teacher_user.DoesNotExist:
        getteachid = None
        return redirect("/")
    
    

    return render(request, 'finance/teachers_withdraw.html',context)




  