from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from ..models import teacher,user_group,category_program_permission,user_detail
from ..constant import defaultTitle
from ..forms.teacher_form import  teacherForm
from ..functions import  dateTimeNow
@login_required(login_url='/login')
def teacher_list(request):
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
    result = teacher.objects.filter(cancelled=1,module=m.module).order_by("-crt_date")
    context = {'title': title,  'data': result,'listMenuPermission': objMenu}
    return render(request, 'teacher/teachers.html', context)

@login_required(login_url='/login')
def teacher_form_create(request):
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
    if request.method == 'POST':
        try:
            teacher_cover = request.FILES['teacher_cover']
        except KeyError:
            teacher_cover = None
        teacher_identification_number = request.POST['teacher_identification_number']
        teacher_prefix_th = request.POST['teacher_prefix_th']
        teacher_firstname_th = request.POST['teacher_firstname_th']
        teacher_lastname_th = request.POST['teacher_lastname_th']
        teacher_prefix_eng = request.POST['teacher_prefix_eng']
        teacher_firstname_eng = request.POST['teacher_firstname_eng']
        teacher_lastname_eng = request.POST['teacher_lastname_eng']
        teacher_type =  request.POST['teacher_type']
        active = request.POST['active']
        t = teacher.objects.filter(teacher_identification_number=teacher_identification_number).count()
        if t > 0:
            messages.error(request, "รหัสครูท่านนี้ได้ถูกบันทึกไว้แล้ว กรุณาทำรายการใหม่!")
            return redirect("/teacher/form/create")
        content = teacher(
            teacher_identification_number = teacher_identification_number,
            teacher_prefix_th = teacher_prefix_th,
            teacher_firstname_th = teacher_firstname_th,
            teacher_lastname_th = teacher_lastname_th,
            teacher_prefix_eng = teacher_prefix_eng,
            teacher_firstname_eng = teacher_firstname_eng,
            teacher_lastname_eng = teacher_lastname_eng,
            teacher_cover = teacher_cover,
            teacher_type = teacher_type,
            active = active,
            crt_date=dateTimeNow(),
            upd_date=dateTimeNow(),
            module=m.module
        )
        content.save()
        messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/teachers")
    title = defaultTitle
    context = {'title': title, 'form':teacherForm(),'listMenuPermission': objMenu}
    return render(request, 'teacher/teacher_form_create.html', context)

@login_required(login_url='/login')
def teacher_form_update(request,teacher_id):
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
        instance = teacher.objects.get(teacher_id=teacher_id)
    except (teacher.DoesNotExist,AttributeError, ValueError,ValidationError):
        instance = None
        return redirect("/teachers")
    if request.method == 'POST':
        try:
            instance.teacher_cover = request.FILES['teacher_cover']
        except KeyError:
            instance.teacher_cover = instance.teacher_cover
        instance.teacher_identification_number = request.POST['teacher_identification_number']
        instance.teacher_prefix_th = request.POST['teacher_prefix_th']
        instance.teacher_firstname_th = request.POST['teacher_firstname_th']
        instance.teacher_lastname_th = request.POST['teacher_lastname_th']
        instance.teacher_prefix_eng = request.POST['teacher_prefix_eng']
        instance.teacher_firstname_eng = request.POST['teacher_firstname_eng']
        instance.teacher_lastname_eng = request.POST['teacher_lastname_eng']
        instance.teacher_type =  request.POST['teacher_type']
        instance.active = request.POST['active']
        t = teacher.objects.filter(teacher_identification_number=request.POST['teacher_identification_number']).exclude(teacher_id=teacher_id).count()
        if t > 0:
            messages.error(request, "รหัสครูท่านนี้ได้ถูกบันทึกไว้แล้ว กรุณาทำรายการใหม่!")
            return redirect("/teacher/form/create")
        instance.save()
        messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/teachers")
    initial = {'teacher_identification_number':instance.teacher_identification_number,'teacher_prefix_th':instance.teacher_prefix_th,'teacher_firstname_th': instance.teacher_firstname_th,
               'teacher_lastname_th':instance.teacher_lastname_th,'teacher_prefix_eng':instance.teacher_prefix_eng,'teacher_firstname_eng': instance.teacher_firstname_eng,
               'teacher_lastname_eng':instance.teacher_lastname_eng,'teacher_cover':instance.teacher_cover,'teacher_type':instance.teacher_type,'active':instance.active}
    title = defaultTitle
    context = {'title': title,'image_path':instance.teacher_cover, 'form':teacherForm(initial=initial),'id':instance.teacher_id,'listMenuPermission': objMenu}
    return render(request, 'teacher/teacher_form_update.html', context)

@login_required(login_url='/login')
def teacher_form_delete(request):
    id = request.POST['id']
    try:
        instance = teacher.objects.get(pk=id)
    except teacher.DoesNotExist:
        instance = None
        return redirect("/teachers")
    instance.cancelled = 0
    instance.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/teachers")

@login_required(login_url='/login')
def teacher_manage_income(request,teacher_id):
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
        instance = teacher.objects.get(teacher_id=teacher_id)
    except (teacher.DoesNotExist,AttributeError, ValueError,ValidationError):
        instance = None
        return redirect("/teachers")
    title = defaultTitle
    # result = teacher.objects.filter(cancelled=1).order_by("-crt_date")
    context = {'title': title,  'main_data': instance,'listMenuPermission': objMenu}
    return render(request, 'teacher/teacher_manage_income.html', context)