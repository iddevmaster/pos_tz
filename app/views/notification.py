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
    
    obj = []
    # ev_id = data.get("ev_id")

    content = user_detail.objects.get(user_id=user_id)

    datas = notifications.objects.select_related("cm").filter(user_id=user_id)

    all = notifications.objects.select_related("cm").filter(user_id=user_id).count()
    unread = notifications.objects.select_related("cm").filter(user_id=user_id,is_read='false').count()
    for aaa in datas:
        res = {'notifications_id':aaa.notifications_id,'notification_type':aaa.notification_type,'title': aaa.title,'message':aaa.message,'is_read':aaa.is_read,'crt_date':aaa.crt_date}
        obj.append(res)

    s = {'total':all,'data':obj,'unread':unread}
    

    return JsonResponse(s, status=200, safe=False)  

    