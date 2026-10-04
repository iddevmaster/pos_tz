from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from ..models import user_group, category_program,category_program_permission,user_detail,teacher,compensation,fact_teacher_user
from ..constant import defaultTitle, listMenu
from ..forms.user_form import category_program_form
from ..functions import dateTimeNow


def _menu_context(user_id):
    try:
        cm_id = user_detail.objects.get(user_id=user_id).cm_id
    except user_detail.DoesNotExist:
        cm_id = 0
    groups = category_program_permission.objects.filter(cm_id=cm_id).values(
        'group_value', 'group_label'
    ).annotate(dcount=Count('group_value')).order_by('group_label')
    menu = []
    for group in groups:
        menu.append({
            **group,
            'children': category_program_permission.objects.filter(
                cm_id=cm_id, group_value=group['group_value']
            ).order_by('page_label'),
        })
    return menu


@login_required(login_url='/login')
def profile_edit(request):
    profile_user = request.user
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        new_password_confirm = request.POST.get('new_password_confirm', '')
        errors = []

        if not first_name:
            errors.append('กรุณาระบุชื่อ')
        if not last_name:
            errors.append('กรุณาระบุนามสกุล')
        if email and User.objects.filter(
            email__iexact=email
        ).exclude(pk=profile_user.pk).exists():
            errors.append('Email นี้ถูกใช้งานแล้ว')
        wants_password_change = bool(
            current_password or new_password or new_password_confirm
        )
        if wants_password_change:
            if not profile_user.check_password(current_password):
                errors.append('รหัสผ่านปัจจุบันไม่ถูกต้อง')
            if not new_password:
                errors.append('กรุณาระบุรหัสผ่านใหม่')
            elif new_password != new_password_confirm:
                errors.append('รหัสผ่านใหม่และการยืนยันไม่ตรงกัน')
            else:
                try:
                    validate_password(new_password, profile_user)
                except ValidationError as error:
                    errors.extend(error.messages)

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            profile_user.first_name = first_name
            profile_user.last_name = last_name
            profile_user.email = email
            profile_user.save(update_fields=[
                'first_name', 'last_name', 'email'
            ])
            if wants_password_change:
                profile_user.set_password(new_password)
                profile_user.save(update_fields=['password'])
                update_session_auth_hash(request, profile_user)
            messages.success(request, 'แก้ไขโปรไฟล์เรียบร้อยแล้ว')
            return redirect('profile_edit')

    return render(request, 'user/profile_edit.html', {
        'title': defaultTitle,
        'listMenuPermission': _menu_context(request.user.id),
        'profile_user': profile_user,
    })


@login_required(login_url='/login')
@user_passes_test(lambda current_user: current_user.is_staff, login_url='/403')
def user_teacher_create(request):
    categories = category_program.objects.filter(
        active=1, cancelled=1
    ).order_by('cm_name')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        category_id = request.POST.get('category', '')
        is_teacher = request.POST.get('is_teacher') == '1'

        errors = []
        if not username:
            errors.append('กรุณาระบุ Username')
        elif User.objects.filter(username__iexact=username).exists():
            errors.append('Username นี้ถูกใช้งานแล้ว')
        if email and User.objects.filter(email__iexact=email).exists():
            errors.append('Email นี้ถูกใช้งานแล้ว')
        if not first_name or not last_name:
            errors.append('กรุณาระบุชื่อและนามสกุล')
        if len(password) < 8:
            errors.append('รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร')
        if password != password_confirm:
            errors.append('รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน')
        try:
            category = categories.get(pk=category_id)
        except (category_program.DoesNotExist, ValueError):
            category = None
            errors.append('กรุณาเลือกกลุ่มผู้ใช้งาน')

        identification_number = request.POST.get(
            'teacher_identification_number', ''
        ).strip()
        if is_teacher:
            if not identification_number:
                errors.append('กรุณาระบุเลขบัตรประชาชน/Passport ของครูฝึก')
            elif teacher.objects.filter(
                teacher_identification_number=identification_number,
                cancelled=1,
            ).exists():
                errors.append('เลขบัตรประชาชน/Passport นี้มีข้อมูลครูฝึกแล้ว')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            with transaction.atomic():
                new_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=request.POST.get('is_active') == '1',
                )
                user_group.objects.create(
                    user=new_user,
                    module=category.module,
                )
                user_detail.objects.create(user=new_user, cm=category)

                if is_teacher:
                    teacher_record = teacher.objects.create(
                        teacher_identification_number=identification_number,
                        tax_number=request.POST.get('tax_number', '').strip(),
                        teacher_prefix_th=request.POST.get('teacher_prefix_th', ''),
                        teacher_firstname_th=first_name,
                        teacher_lastname_th=last_name,
                        teacher_prefix_eng=request.POST.get('teacher_prefix_eng', ''),
                        teacher_firstname_eng=request.POST.get(
                            'teacher_firstname_eng', ''
                        ).strip(),
                        teacher_lastname_eng=request.POST.get(
                            'teacher_lastname_eng', ''
                        ).strip(),
                        teacher_cover=request.FILES.get('teacher_cover'),
                        teacher_type=request.POST.get('teacher_type', '1'),
                        active=1,
                        cancelled=1,
                        crt_date=dateTimeNow(),
                        upd_date=dateTimeNow(),
                        module=category.module,
                        level='4',
                    )
                    teacher_key = str(teacher_record.teacher_id).replace('-', '')
                    fact_teacher_user.objects.create(
                        user_id=new_user.id,
                        teacher_id=teacher_key,
                    )
                    for py_id, field_name in (
                        ('1', 'compensation_wi'),
                        ('2', 'compensation_pi'),
                        ('3', 'compensation_help'),
                    ):
                        compensation.objects.create(
                            compensation=request.POST.get(field_name) or 0,
                            teacher_id=teacher_key,
                            status='Y',
                            note='',
                            compensation_group_id='1',
                            py_id=py_id,
                        )
            messages.success(request, 'เพิ่มผู้ใช้งานเรียบร้อยแล้ว')
            return redirect('user_manage_list')

    context = {
        'title': defaultTitle,
        'categories': categories,
        'listMenuPermission': _menu_context(request.user.id),
    }
    return render(request, 'user/user_teacher_create.html', context)


@login_required(login_url='/login')
@user_passes_test(lambda current_user: current_user.is_staff, login_url='/403')
def user_manage_list(request):
    keyword = request.GET.get('q', '').strip()
    accounts = User.objects.all().order_by('first_name', 'last_name', 'username')
    if keyword:
        accounts = accounts.filter(
            Q(username__icontains=keyword)
            | Q(first_name__icontains=keyword)
            | Q(last_name__icontains=keyword)
            | Q(email__icontains=keyword)
        )
    accounts = list(accounts)
    details = {
        item.user_id: item.cm.cm_name
        for item in user_detail.objects.filter(
            user_id__in=[account.id for account in accounts]
        ).select_related('cm')
    }
    for account in accounts:
        account.category_name = details.get(account.id, '-')
    return render(request, 'user/user_manage_list.html', {
        'title': defaultTitle,
        'listMenuPermission': _menu_context(request.user.id),
        'accounts': accounts,
        'keyword': keyword,
    })


@login_required(login_url='/login')
@user_passes_test(lambda current_user: current_user.is_staff, login_url='/403')
def user_manage_edit(request, pk):
    account = get_object_or_404(User, pk=pk)
    categories = category_program.objects.filter(
        active=1, cancelled=1
    ).order_by('cm_name')
    try:
        current_category_id = account.user_detail.cm_id
    except user_detail.DoesNotExist:
        current_category_id = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        category_id = request.POST.get('category', '').strip()
        new_password = request.POST.get('new_password', '')
        new_password_confirm = request.POST.get('new_password_confirm', '')
        errors = []

        if not username:
            errors.append('กรุณาระบุ Username')
        elif User.objects.filter(
            username__iexact=username
        ).exclude(pk=account.pk).exists():
            errors.append('Username นี้ถูกใช้งานแล้ว')
        if not first_name or not last_name:
            errors.append('กรุณาระบุชื่อและนามสกุล')
        if email and User.objects.filter(
            email__iexact=email
        ).exclude(pk=account.pk).exists():
            errors.append('Email นี้ถูกใช้งานแล้ว')
        try:
            category = categories.get(pk=category_id)
        except (category_program.DoesNotExist, ValueError):
            category = None
            errors.append('กรุณาเลือกกลุ่มผู้ใช้งาน')
        if new_password or new_password_confirm:
            if new_password != new_password_confirm:
                errors.append('รหัสผ่านใหม่และการยืนยันไม่ตรงกัน')
            else:
                try:
                    validate_password(new_password, account)
                except ValidationError as error:
                    errors.extend(error.messages)

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            with transaction.atomic():
                account.username = username
                account.first_name = first_name
                account.last_name = last_name
                account.email = email
                is_current_account = account.pk == request.user.pk
                account.is_active = (
                    True if is_current_account
                    else request.POST.get('is_active') == '1'
                )
                account.is_staff = (
                    True if is_current_account
                    else request.POST.get('is_staff') == '1'
                )
                if new_password:
                    account.set_password(new_password)
                account.save()
                user_detail.objects.update_or_create(
                    user=account, defaults={'cm': category}
                )
                user_group.objects.update_or_create(
                    user=account, defaults={'module': category.module}
                )
            messages.success(request, 'แก้ไขผู้ใช้งานเรียบร้อยแล้ว')
            return redirect('user_manage_list')

    return render(request, 'user/user_manage_edit.html', {
        'title': defaultTitle,
        'listMenuPermission': _menu_context(request.user.id),
        'account': account,
        'categories': categories,
        'current_category_id': current_category_id,
    })


@login_required(login_url='/login')
@user_passes_test(lambda current_user: current_user.is_staff, login_url='/403')
def user_manage_delete(request, pk):
    if request.method != 'POST':
        return redirect('user_manage_list')
    account = get_object_or_404(User, pk=pk)
    if account.pk == request.user.pk:
        messages.error(request, 'ไม่สามารถลบบัญชีที่กำลังใช้งานอยู่ได้')
        return redirect('user_manage_list')
    username = account.username
    try:
        account.delete()
        messages.success(request, f'ลบผู้ใช้งาน {username} เรียบร้อยแล้ว')
    except ProtectedError:
        messages.error(
            request,
            'ไม่สามารถลบผู้ใช้งานนี้ได้ เนื่องจากมีข้อมูลเอกสารอ้างอิงอยู่',
        )
    return redirect('user_manage_list')


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
