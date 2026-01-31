from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta

from django.db.models import Count, Sum, Value, F
from ..models import course, course_event, user_group,category_program_permission,user_detail,notifications
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




@csrf_exempt
def fetch_notification(request):
    # data = json.loads(request.body)
    user_id = request.user.id
  
    # ev_id = data.get("ev_id")

    content = user_detail.objects.get(user_id=user_id)
    
    # regbyev = notifications.objects.select_related("cm").filter()
    # print(regbyev.cm)
    # total_rq_quta = 0
    
    # for aaa in regbyev:
        
    #     try:
    #         bbbb = register_payment.objects.filter(register_id=aaa.register_id).first()
    #         if bbbb:
    #          total_rq_quta += bbbb.rp_quota
    #     except register_payment.DoesNotExist:  
    #         bbbb = 0

    datas = notifications.objects.select_related("cm").filter(
        # ใส่ Filter ตามที่ต้องการ
    ).annotate(
        # ดึง cm_name จากตาราง category_program มาไว้ในชื่อใหม่
        category_label=F('cm__cm_name') 
    ).values(
        'notifications_id',
        'notification_type',
        'title',
        'message',
        'is_read',
        'category_label', # ใช้ชื่อที่ตั้งใหม่จาก annotate
        'crt_date'
    ).order_by('-crt_date')


    data = list(datas)
    return JsonResponse(data, status=200, safe=False)  

    