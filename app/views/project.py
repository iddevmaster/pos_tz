from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.db.models import Count, Sum, Value
from ..models import course, course_event, user_group,category_program_permission,user_detail,teacher_income_setting,location_thai,pay_item,teacher,project_code
from ..constant import defaultTitle
from ..functions import addDay, addYear, dateTimeNow, dmytoymd
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
import json
from django.core import serializers

@login_required(login_url='/login')
def project_list(request):
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
    result = project_code.objects.filter(
        cancelled=1)
    print(result)    
    context = {'title': title, 'listMenuPermission': objMenu, 'data': result}
    return render(request, 'projectcode/project_list.html', context)


@login_required(login_url='/login')
def project_event_update(request):
   
    project_codes = request.POST['project_code']
    names = request.POST['name']
    
    project_id = request.POST['id']
    
    content = project_code.objects.get(project_id=project_id)
    
    # print(content)
    content.project_code = project_codes
    content.name = names
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
  
    return redirect("/projectlist")


@login_required(login_url='/login')
def project_event_delete(request):
    project_id = request.POST['id']
    content = project_code.objects.get(project_id=project_id)
    content.cancelled = 0
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/projectlist")

def project_event_create(request):
    content = project_code(
        project_code=request.POST['project_code'],
        name=request.POST['name'],
        status=1,
        crt_date=dateTimeNow(),
        cancelled=1,

    )
    content.save()

    return redirect("/projectlist")



@csrf_exempt
def updatestatus(request):
 if request.method == "POST":
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            print(data)
            project_id = data.get("project_id")
            show = data.get("status")
           
            content = project_code.objects.get(project_id=project_id)
            content.status = show
            content.save()
    
            return JsonResponse(data, status=200,safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": 'x'}, status=400,safe=False)

        return JsonResponse({"error": "Only POST method is allowed"}, status=405)    


