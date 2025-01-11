from datetime import date
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Value
from django.db.models.functions import TruncMonth
from ..models import category_program_permission, course, course_event, teacher_income_setting, billing_cycle_setting, user_group, user_detail, teacher,pay_item,compensation
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
    result = course_event.objects.select_related("course").filter(
        cancelled=1, ev_date_start__month=month_current, ev_date_start__year=year_current, module=m.module).order_by("-ev_id")
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
        ev__module=m.module, tis_end_date__year=year_current).annotate(month=TruncMonth('tis_start_date'))
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

        
        # print(thai_months[i-1])
        # เช็คและตัดรอบบิล

        for r2 in b:
            day_start = r2.bcs_start_day
            day_end = r2.bcs_end_day
            # ถ้าเดือนสุดท้ายน้อยกว่าค่า day_end ที่ตั้งไว้ ให้เอาเดือนสุดท้ายมาตั้งใหม่
            if last_day <= day_end:
                day_end = last_day
            instance = teacher_income_setting.objects.filter(
                ev__module=m.module,
                active=0,
                tis_start_date__day__gte=day_start,
                tis_end_date__day__lte=day_end,
                tis_end_date__month=month,
                tis_end_date__year=year_current
            )
            if teacher_current != None and teacher_current != '':
                instance = instance.filter(teacher=teacher_current)
            tis_group = f"{day_start} - {day_end}"
            if day_current >= day_end and instance.count() >= 1:
                instance.update(active=1, tis_group=tis_group,
                                upd_date=dateTimeNow())
        obj2 = []
        content = teacher_income_setting.objects.filter(
            ev__module=m.module, active=1, tis_end_date__month=month, tis_end_date__year=year_current)
        if teacher_current != None and teacher_current != '':
            content = content.filter(teacher=teacher_current)
        group_content = content.values('tis_group').annotate(
            order_count=Count('id'), order_sum=Sum('tis_sum')).order_by('tis_group')

        for r3 in group_content:
            # print(r['tis_group']  + ' ' +  thai_months[month-1])
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
        instance = course_event.objects.get(pk=ev_id)
        
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
            status='W'
        )
        content.save()
        x = course_event.objects.get(pk=ev_id)
        x.status = "W"
        x.save()

        messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/course/event/teachers/form/create/" + str(ev_id))
    # print(instance.ev_date_start.month)
    teacher_data = teacher_income_setting.objects.filter(ev=ev_id)
    ids = [1, 2]
    count_hour_wi = teacher_income_setting.objects.filter(ev=ev_id,pi__in=ids).aggregate(Sum('tis_quantity'))['tis_quantity__sum'] or 0
    count_hour_pi = teacher_income_setting.objects.filter(ev=ev_id,pi=3).aggregate(Sum('tis_quantity'))['tis_quantity__sum'] or 0
    listposition = pay_item.objects.filter(
            cancelled=1, active=1)
    list_teacher = teacher.objects.filter(
        module=m.module, cancelled=1, active=1)
    
    
    context = {'title': title, 'main_data': instance,  'data': teacher_data,
               'form': teacherIncomeSettingForm(module), 'listMenuPermission': objMenu,'teacher':list_teacher,'unit':unitPayChoices,'listposition':listposition,'hour_wi':count_hour_wi,'hour_pi':count_hour_pi}
    return render(request, 'finance/course_teacher_event_set_income.html', context)


@login_required(login_url='/login')
def course_teacher_event_set_income_form_delete(request):
    id = request.POST['id']
    ev_id = request.POST['ev_id']
    try:
        instance = teacher_income_setting.objects.get(pk=id)
    except teacher_income_setting.DoesNotExist:
        instance = None
        return redirect("/course/event/teachers/form/create/" + str(ev_id))
    instance.delete()

    x = course_event.objects.get(pk=ev_id)

   
    if teacher_income_setting.objects.filter(ev_id=ev_id).count() == 0:
         x.status = "N"
         x.save()
   
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
            print(teacher_id)
            data['status_hour'] = True
            data['status_people'] = True
            data['status_teacher'] = True
            if pi == '1' :
               
                hour = instance['ev_hour'] or 0
                people = instance['ev_people'] or 0
            elif  pi == '2' :
              
                hour = instance['ev_hour_two'] or 0
                people = instance['ev_people_two'] or 0
            elif  pi == '3' :
             
                hour = instance['ev_hour_three'] or 0
                people = instance['ev_people_three'] or 0

            st =['Y','W']
      
            content = teacher_income_setting.objects.filter(ev_id=ev_id,status__in=st,pi=pi).aggregate(total=Coalesce(Sum('tis_quantity'), Value(0)))
            tttt = teacher_income_setting.objects.filter(ev_id=ev_id,status__in=st,pi=pi).values('pi').annotate(total=Count('pi')) 
            teacher = teacher_income_setting.objects.filter(ev_id=ev_id,status__in=st,pi=pi,teacher_id=teacher_id).count() or 0
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
            print(instance.ev_date_start)

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
                status='W'
                )
            content.save()

            instance.status = 'W'
            instance.save()
            
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
           

            instance = teacher_income_setting.objects.filter(id=ev_id).count()
            
         

    
            datas = {'status':200,'s':instance}
            return JsonResponse(datas, status=200,safe=False)

        except json.JSONDecodeError:
            datas = {'status':400}
            return JsonResponse(datas, status=400,safe=False)

        return JsonResponse({"error": "Only POST method is allowed"}, status=405) 



