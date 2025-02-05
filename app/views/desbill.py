from datetime import date
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Value
from django.db.models.functions import TruncMonth
from ..models import category_program_permission, course, course_event, teacher_income_setting, billing_cycle_setting, user_group, user_detail, desciption_bill
from ..constant import defaultTitle, thai_months,unitPayChoices
from ..functions import dateTimeNow, last_day_of_month
from ..forms.finance_form import billing_cycle_setting_form
from ..forms.teacher_form import teacherIncomeSettingForm
from django.http import JsonResponse
import json
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Coalesce


@login_required(login_url='/login')
def setting_form_create(request):
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
        messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/description/setting/form/create")

    desciption = desciption_bill.objects.all().order_by('seq')
    context = {'title': defaultTitle,  'data': desciption, 'listMenuPermission': objMenu}
            
    return render(request, 'settingdes/setting_form_create.html', context)



def setting_form_delete(request):

    id = request.POST['id']     
   
    instance = desciption_bill.objects.get(seq=id)
    instance.delete()
    desciption = desciption_bill.objects.all().order_by('seq')  
    t = 0
    for desciptions in desciption:
        t += 1
        desciptions.seq = t
        desciptions.save()
        print(t) 
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/description/setting/form/create")


def setting_form_update(request):
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/description/setting/form/create")


@csrf_exempt
def up(request):
    data = json.loads(request.body)
    ids = int(data.get("id"))
    x = int(data.get("id")) - 1

    a = desciption_bill.objects.get(seq=ids)
    b = desciption_bill.objects.get(seq=x)
   
    a.seq = a.seq - 1
    a.save()


    b.seq = b.seq + 1
    b.save()


    datas = {'status':'200'}
    return JsonResponse(datas,safe=False)

@csrf_exempt
def down(request):    
    data = json.loads(request.body)
    ids = int(data.get("id"))
    x = int(data.get("id")) + 1

    a = desciption_bill.objects.get(seq=ids)
    b = desciption_bill.objects.get(seq=x)
   
    a.seq = a.seq + 1
    a.save()


    b.seq = b.seq - 1
    b.save()


    datas = {'status':'200'}
    return JsonResponse(datas,safe=False)
