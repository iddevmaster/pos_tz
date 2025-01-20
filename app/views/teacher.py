from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from ..models import teacher,user_group,category_program_permission,user_detail,compensation,user_lic,fact_teacher_user,teacher_income_setting
from ..constant import defaultTitle
from ..forms.teacher_form import  teacherForm
import uuid

from ..functions import addDay, addYear, dateTimeNow, dmytoymd
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
    return render(request, 'teacher/teachersoutsource.html', context)

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

        
        count_hour_wi = request.POST['count_hour_wi']
        count_hour_pi = request.POST['count_hour_pi']
        count_hour_help = request.POST['count_hour_help']

        note_wi = request.POST['note_wi']
        note_pi = request.POST['note_pi']
        note_help = request.POST['note_help']

        py_wi = request.POST['py_wi']
        py_pi = request.POST['py_pi']
        py_help = request.POST['py_help']


       
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
            module=m.module,
            level = '4',
            )
        content.save()
      
        t1 = teacher.objects.filter(teacher_identification_number=teacher_identification_number).first()
        uuid_with_dashes = t1.teacher_id  # This is a UUID object
        uuid_without_dashes = str(uuid_with_dashes).replace('-', '')
       
    
        x1 = compensation(
            compensation = count_hour_wi,
            teacher_id = uuid_without_dashes,
            status = 'Y',
            note = note_wi,
            compensation_group_id = py_wi,
            py_id = 1
        )
        x2 = compensation(
            compensation = count_hour_pi,
            teacher_id = uuid_without_dashes,
            status = 'Y',
            note = note_pi,
            compensation_group_id = py_pi,
            py_id = 2
        )

        x3 = compensation(
            compensation = 0,
            teacher_id = uuid_without_dashes,
            status = 'Y',
            note = note_help,
            compensation_group_id = py_help,
            py_id = 3
        )

        x1.save()
        x2.save()
        x3.save()
    
      
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
        
        old_uuid = str(teacher_id)
        new_uuid_str = old_uuid.replace("-", "")
        data1 = compensation.objects.filter(teacher_id=new_uuid_str,py_id=1).first()
        data2 = compensation.objects.filter(teacher_id=new_uuid_str,py_id=2).first()
        data3 = compensation.objects.filter(teacher_id=new_uuid_str,py_id=3).first()
      
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
        data1.compensation_group_id = request.POST['py_wi']
        data1.compensation = request.POST['count_hour_wi']
        data1.note = request.POST['note_wi']

        data2.compensation_group_id = request.POST['py_pi']
        data2.compensation = request.POST['count_hour_pi']
        data2.note = request.POST['note_pi']

        data3.compensation_group_id = request.POST['py_help']
        data3.compensation = request.POST['count_hour_help']
        data3.note = request.POST['note_help']


        t = teacher.objects.filter(teacher_identification_number=request.POST['teacher_identification_number']).exclude(teacher_id=teacher_id).count()
        if t > 0:
            messages.error(request, "รหัสครูท่านนี้ได้ถูกบันทึกไว้แล้ว กรุณาทำรายการใหม่!")
            return redirect("/teacher/form/create")
        instance.save()
        data1.save()
        data2.save()
        data3.save()
        messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/teachers")
    initial = {'teacher_identification_number':instance.teacher_identification_number,'teacher_prefix_th':instance.teacher_prefix_th,'teacher_firstname_th': instance.teacher_firstname_th,
               'teacher_lastname_th':instance.teacher_lastname_th,'teacher_prefix_eng':instance.teacher_prefix_eng,'teacher_firstname_eng': instance.teacher_firstname_eng,
               'teacher_lastname_eng':instance.teacher_lastname_eng,'teacher_cover':instance.teacher_cover,'teacher_type':instance.teacher_type,'active':instance.active}

    compo1 = {'id':data1.id,'compensation':data1.compensation,'teacher_id': data1.teacher_id,'py_id':data1.py_id,'note':data1.note,'compensation_group_id':data1.compensation_group_id}
    compo2 = {'id':data2.id,'compensation':data2.compensation,'teacher_id': data2.teacher_id,'py_id':data2.py_id,'note':data2.note,'compensation_group_id':data2.compensation_group_id}
    compo3 = {'id':data3.id,'compensation':data3.compensation,'teacher_id': data3.teacher_id,'py_id':data3.py_id,'note':data3.note,'compensation_group_id':data3.compensation_group_id}


    title = defaultTitle
    context = {'title': title,'image_path':instance.teacher_cover, 'form':teacherForm(initial=initial),'id':instance.teacher_id,'listMenuPermission': objMenu,'data1':compo1,'data2':compo2,'data3':compo3}
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
def teacher_list_cale(request):
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

    try:
        a = fact_teacher_user.objects.get(user_id=user_id)
        
        
    except fact_teacher_user.DoesNotExist:
        a = None    
    title = defaultTitle
    result = teacher.objects.filter(cancelled=1,module=m.module).order_by("-crt_date")
  



    teacher_data = teacher_income_setting.objects.select_related('ev').filter(status='Y',teacher_id=a.teacher_id)
    
    context = {'title': title,  'data': result,'listMenuPermission': objMenu,'teacher_id':a.teacher_id,'datas':teacher_data}
    return render(request, 'teacher/teachers_cale.html', context)
        

def teacher_list_licen(request):
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
    result = user_lic.objects.filter(cancelled=1,status='W')
   
    teact = teacher.objects.filter(cancelled=1).order_by("-crt_date")
    obk = []
    for rs in list(teact):
        
        s = { 'teacher_id':rs.teacher_id }
        obk.append(s)
    context = {'title': title,  'data': result,'listMenuPermission': objMenu,'das':teact}
    return render(request, 'teacher/teachers_lic.html', context) 



def teacher_list_appv(request):
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
    result = user_lic.objects.filter(cancelled=1,status='W')
    
    context = {'title': title,  'data': result,'listMenuPermission': objMenu}
    return render(request, 'teacher/teachers_appv.html', context) 

    
@login_required(login_url='/login')
def teacher_appv_delete(request):
    id = request.POST['id']
    
    try:
        instance = user_lic.objects.get(pk=id)
        
    except user_lic.DoesNotExist:
        instance = None
        return redirect("/approvlicen")
  
    instance.status = 'D'
    instance.save()
    messages.success(request, "ทำรายการสำเร็จ !")

    return redirect("/approvlicen")


@login_required(login_url='/login')
def teacher_appv_de(request):
    id = request.POST['ids']
    
    try:
        instance = user_lic.objects.get(pk=id)
        
    except user_lic.DoesNotExist:
        instance = None
        return redirect("/approvlicen")
  
    instance.status = 'Y'
    instance.save()
    messages.success(request, "ทำรายการสำเร็จ !")

    return redirect("/approvlicen")
@login_required(login_url='/login')
def teacher_formlicen_create(request):
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
 
    
      
        # messages.success(request, "ทำรายการสำเร็จ !")
        # return redirect("/teachers")
    title = defaultTitle
    context = {'title': title, 'form':teacherForm(),'listMenuPermission': objMenu}
    return render(request, 'teacher/teacher_formlicen_create.html', context)    


@login_required(login_url='/login')
def teacher_formlicen_update(request):
    id = request.POST['lic_id']
    number = request.POST['number_lic']
   
    try:
        ev_logo = request.FILES['ev_logo']
    except KeyError:
        ev_logo = None
    issue = dmytoymd(request.POST['issue_date'])
    expire = dmytoymd(request.POST['expire_date'])
    content = user_lic.objects.get(lic_id=id)
    content.number_lic = number
    content.issue_date = issue
    content.expire_date = expire
    content.save()
    messages.success(request, "ทำรายการสำเร็จ !")
   
    return redirect("/licenteachers")