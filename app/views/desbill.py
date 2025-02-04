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
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Coalesce


@login_required(login_url='/login')
def listdesc(request):
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
        cancelled=1, ev_date_start__month=month_current, ev_date_start__year=year_current, module=m.module,status='Y').order_by("-ev_id")

    te = []
    status = ['N','W','Y']
    # result = event_register.objects.select_related("ev").filter(ev__cancelled=1, status__in=status, ev__ev_date_start__month=month_current, ev__ev_date_start__year=year_current, ev__module=m.module)
    # for r in result:  
    #  content = course.objects.get(pk=r.ev.course_id)
    #  saf = register_main.objects.get(pk=r.register_id)
     
     
    #  fs = {'register_id':r.register_id,'course_code':content.course_code,'course_name':content.course_name,'ev_id':r.ev.ev_id,'ev_price':r.ev.ev_price,'ev_date_start':r.ev.ev_date_start,'ev_date_end':r.ev.ev_date_end,'ev_generation':r.ev.ev_generation,'ev_expired_cer_date':r.ev.ev_expired_cer_date,'ev_expired_cer_quantity':r.ev.ev_expired_cer_quantity,'bill':saf.register_number}
        
    #  te.append(fs)  
    
    context = {'title': defaultTitle,  'data': result,
               'course_list': course_list, 'listMenuPermission': objMenu}
            
    return render(request, 'settingdes/setting_form_create.html', context)

