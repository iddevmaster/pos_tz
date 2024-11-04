from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from ..models import user_group, category_program,category_program_permission ,user_detail
from ..constant import defaultTitle, listMenu
from ..forms.user_form import category_program_form


@login_required(login_url='/login')
def category_program_form_create(request):
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
        form = category_program_form(request.POST)
        if not form.is_valid():
            messages.error(
                request, "ไม่สามารถทำรายการได้ !  ,กรุณาทำรายการใหม่อีกครั้ง ")
        if form.is_valid():
            form.save()
            messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/user/category/list")
    data = category_program.objects.filter(cancelled=1, module=m.module)
    context = {'title': defaultTitle, 'form': category_program_form(
        initial={'module': m.module}), 'data': data,'listMenuPermission': objMenu,}
    return render(request, 'user/category_program_form_create.html', context)


@login_required(login_url='/login')
def category_program_form_delete(request):
    id = request.POST['id']
    try:
        instance = category_program.objects.get(pk=id)
    except category_program.DoesNotExist:
        instance = None
        return redirect("/user/category/list")
    instance.cancelled = 0
    instance.save()
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/user/category/list")


@login_required(login_url='/login')
def category_program_form_permission(request, pk):
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id_main = u.cm
    except user_detail.DoesNotExist:
        cm_id_main = 0
    
    instance = get_object_or_404(category_program, pk=pk)
    cm_id = instance.pk
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id_main).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    if request.method == 'POST':
        category_program_permission.objects.filter(cm=cm_id).delete()
        objCreate = []
        for value in request.POST.getlist("page_route"):
            filtered_menu = [
                item for item in listMenu if item['value'] == value]
            if len(filtered_menu) > 0:
                content = category_program_permission(page_route=value, page_label=filtered_menu[0]['label'], group_value=filtered_menu[0]['group_value'],
                                              group_label=filtered_menu[0]['group_label'], cm_id=cm_id)
                objCreate.append(content)
        category_program_permission.objects.bulk_create(objCreate)
        messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/user/category/list")
    obj = []
    for rs in listMenu:
        
        try:
            category_program_permission.objects.get(page_route=rs['value'], cm_id=cm_id)
            selectMenu = True
        except category_program_permission.DoesNotExist:
            selectMenu = False
        newMenu = {'value': rs['value'], 'label': rs['label'], 'group_value': rs['group_value'],
                   'group_label': rs['group_label'], 'selectMenu': selectMenu}
        obj.append(newMenu)
    context = {'title': defaultTitle,'data': instance, 'listMenu': obj, 'listMenuPermission': objMenu}
    return render(request, 'user/category_program_form_permission.html', context)
