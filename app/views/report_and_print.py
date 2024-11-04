from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
# from django.http import HttpResponse, response
from datetime import date, timedelta
from dateutil import rrule
import json
from ..forms.student_form import studentForm
from ..constant import defaultTitle, api_id_card
from ..models import category_program_permission, course, course_event, customers, location_thai, register_main, register_payment, register_payment_items, student, pos_machine, register_ref, register_applove,user_group,user_detail
from ..functions import dateTimeIntNow, dateTimeNow, dmytoymd, month_fomat, lastDateOfmonth, treeDigit, twoDigit, format_daterange, ymdtodmy


@login_required(login_url='/login')
def register_print(request, rp_id):
    
    short = request.GET.get('short', 'no')
    current_user = request.user
    user_id_authen = current_user.id
    try:
        content = register_payment.objects.get(pk=rp_id)
    except register_payment.DoesNotExist:
        content = None
        return render(request, '404.html')
    try:
        machine = pos_machine.objects.filter(user=user_id_authen).last()
    except pos_machine.DoesNotExist:
        machine = None
   

    items = register_payment_items.objects.filter(rp_id=content.rp_id).first()

    content_regist = register_main.objects.select_related(
        "ev").get(register_id=content.register_id)
    customer = customers.objects.get(register_id=content.register_id)
    if content_regist.ev.ev_vat == 1:
        rpi_price_default = float(
            items.rpi_price_total) + float(items.rpi_price_vat)
    else:
        rpi_price_default = items.rpi_price_total
    context = {'title': defaultTitle,  'data': content,
               'items': items, "content_regist": content_regist, 'rpi_price_default': rpi_price_default, 'machine': machine, 'customer': customer}
    if content_regist.pay_type == 1:
        # ถ้าเป็นใบเสร็จอย่างย่อ
        if short == "yes":
            return render(request, 'print/register_print_bill_short.html', context)
        return render(request, 'print/register_print_bill.html', context)
    return render(request, 'print/register_print_sale_quotation.html', context)


@login_required(login_url='/login')
def register_selller_report(request):
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
    
    list_user = User.objects.filter(is_staff=0, is_active=1,user_group_ref__module=m.module).prefetch_related('user_group_ref')
    course_list = course.objects.filter(
        cancelled=1, active=1).order_by("-course_id")
    
    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = "01" + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    default_end = str(lastday) + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    daterange = str(default_start) + " - " + str(default_end)
    try:
        province_list = location_thai.objects.all().values(
            'province_code', 'province_name').annotate(total=Count('province_code'))
    except location_thai.DoesNotExist:
        province_list = None
    context = {'title': defaultTitle,  'province_list': province_list, 'listMenuPermission': objMenu,
               'list_user': list_user, 'course_list': course_list, 'daterange': daterange}
    return render(request, 'report/register_selller_report.html', context)

@login_required(login_url='/login')
def register_excel_seller(request):
    user_id = request.user.id
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    
    date_range = request.POST.get('date_range', None)
    # year_current = int(request.POST.get('qyear', date.today().year))
    # month_current = int(request.POST.get('qmonths', date.today().month))
    province_code = int(request.POST.get('qprovince', 0))
    customer_type = int(request.POST.get('qcustomer_type', 0))
    pay_type = int(request.POST.get('qpay_type', 0))
    close_the_sale = int(request.POST.get('qclose_the_sale', -1))
    course_id = int(request.POST.get('qcourse', 0))
    generation = request.POST.get('qgeneration', 0)
    seller = int(request.POST.get('qseller', 0))
    customer_name = request.POST.get('qcustomer_name', None)
    content = customers.objects.select_related(
        'register', 'location').filter(register__module=m.module)
    lastday = lastDateOfmonth(
        date.today().year,  date.today().month, date.today().day)
    default_start = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + "01"
    default_end = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + str(lastday)

    if date_range is not None:
        start, end = format_daterange(date_range)
        if start == end:
            content = content.filter(
                register__crt_date__date=start)
        else:
            content = content.filter(
                register__crt_date__date__gte=start, register__crt_date__date__lte=end)
        range_param = date_range
    else:
        # content = content.filter(
        #     register__crt_date__month=month_current, register__crt_date__year=year_current)
        content = content.filter(
            register__crt_date__date__gte=default_start, register__crt_date__date__lte=default_end)
        range_param = str(ymdtodmy(default_start)) + \
            " - " + str(ymdtodmy(default_end))
    province_name = "ทุกจังหวัด"
    if province_code != 0:
        content = content.filter(location__province_code=province_code)
        p = location_thai.objects.filter(
            province_code=province_code).values_list("province_name").first()
        province_name = p[0]
    customer_type_param = "ทุกประเภท"
    if customer_type != 0:
        content = content.filter(register__customer_type=customer_type)
        if customer_type == 1:
            customer_type_param = "บุคคล"
        else:
            customer_type_param = "บริษัท"
    pay_type_param = "ทุกประเภท"
    if pay_type != 0:
        content = content.filter(register__pay_type=pay_type)
        if pay_type == 1:
            pay_type_param = "เงินสด"
        else:
            pay_type_param = "เครดิต"
    close_the_sale_param = "ทุกประเภท"
    if close_the_sale != -1:
        content = content.filter(register__close_the_sale=close_the_sale)
        if close_the_sale == 0:
            close_the_sale_param = "กำลังขาย"
        elif close_the_sale == 1:
            close_the_sale_param = "ปิดการขาย - ขายสำเร็จ"
        elif close_the_sale == 2:
            close_the_sale_param = "ปิดการขาย - ขายไม่สำเร็จ"
    course_param = "ทุกหลักสูตร"
    if course_id != 0:
        content = content.filter(register__ev__course_id=course_id)
        c = course.objects.get(course_id=course_id)
        course_param = str(c.course_code) + " " + str(c.course_name)
    generation_param = "ทุกรุ่น"
    if generation:
        content = content.filter(register__ev__ev_generation=generation)
        generation_param = generation
    seller_param = "ทุกคน"
    if seller != 0:
        content = content.filter(register__seller_id=seller)
        u = User.objects.get(id=seller)
        seller_param = str(u.first_name) + " " + str(u.last_name)
    if customer_name != None:
        content = content.filter(Q(customer_name__icontains=customer_name))
    obj = []
    total_sum = 0
    for r in content:
        # print(r.register_id)
        payment_list = register_payment_items.objects.select_related('rp').filter(
            register_id=r.register).order_by("-rp__rp_id").first()

        if payment_list is not None:
            rpi_price_result = payment_list.rpi_price_result
        else:
            rpi_price_result = 0
        total_sum += rpi_price_result
        course_list = course_event.objects.select_related(
            'course').filter(ev_id=r.register.ev_id).first()
        res = {'customer_list': r,
               'course_list': course_list, 'payment_list': payment_list}
        obj.append(res)

    param = {'total_data': len(content), 'range_param': range_param, 'province_name': province_name, 'customer_type_param': customer_type_param,
             'pay_type_param': pay_type_param, 'close_the_sale_param': close_the_sale_param, 'course_param': course_param, 'generation_param': generation_param, 'seller_param': seller_param}
    context = {'title': defaultTitle, 'data': obj,
               'param': param, 'total_sum': total_sum}
    return render(request, 'print/register_excel_seller.html', context)


@login_required(login_url='/login')
def register_report_quotation(request):
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
    
    list_user = User.objects.filter(is_staff=0, is_active=1,user_group_ref__module=m.module).prefetch_related('user_group_ref')
    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = "01" + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    default_end = str(lastday) + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    daterange = str(default_start) + " - " + str(default_end)
    course_list = course.objects.filter(
        cancelled=1, active=1).order_by("-course_id")
    try:
        province_list = location_thai.objects.all().values(
            'province_code', 'province_name').annotate(total=Count('province_code'))
    except location_thai.DoesNotExist:
        province_list = None
    context = {'title': defaultTitle,  'province_list': province_list,
               'list_user': list_user, 'course_list': course_list, 'daterange': daterange,'listMenuPermission': objMenu}
    return render(request, 'report/register_report_quotation.html', context)

@login_required(login_url='/login')
def register_excel_quotation(request):
    user_id = request.user.id
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    
    date_range = request.POST.get('date_range', None)
    close_the_sale = int(request.POST.get('qclose_the_sale', -1))
    course_id = int(request.POST.get('qcourse', 0))
    generation = request.POST.get('qgeneration', 0)
    seller = int(request.POST.get('qseller', 0))
    customer_name = request.POST.get('qcustomer_name', None)

    content = register_payment.objects.select_related(
        'register').filter(register__pay_type=2, active=1,register__module=m.module)

    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + "01"
    default_end = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + str(lastday)
    if date_range is not None:
        start, end = format_daterange(date_range)
        if start == end:
            content = content.filter(
                register__crt_date__date=start)
        else:
            content = content.filter(
                register__crt_date__date__gte=start, register__crt_date__date__lte=end)
        range_param = date_range
    else:
        content = content.filter(
            register__crt_date__date__gte=default_start, register__crt_date__date__lte=default_end)
        range_param = str(ymdtodmy(default_start)) + \
            " - " + str(ymdtodmy(default_end))

    close_the_sale_param = "ทุกประเภท"
    if close_the_sale != -1:
        content = content.filter(register__close_the_sale=close_the_sale)
        if close_the_sale == 0:
            close_the_sale_param = "กำลังขาย"
        elif close_the_sale == 1:
            close_the_sale_param = "ปิดการขาย - ขายสำเร็จ"
        elif close_the_sale == 2:
            close_the_sale_param = "ปิดการขาย - ขายไม่สำเร็จ"
    course_param = "ทุกหลักสูตร"
    if course_id != 0:
        content = content.filter(register__ev__course_id=course_id)
        c = course.objects.get(course_id=course_id)
        course_param = str(c.course_code) + " " + str(c.course_name)
    generation_param = "ทุกรุ่น"
    if generation:
        content = content.filter(register__ev__ev_generation=generation)
        generation_param = generation
    seller_param = "ทุกคน"
    if seller != 0:
        content = content.filter(register__seller_id=seller)
        u = User.objects.get(id=seller)
        seller_param = str(u.first_name) + " " + str(u.last_name)
    if customer_name != None:
        content = content.filter(Q(rp_name_customer__icontains=customer_name))
    obj = []
    total_sum = 0
    for r in content:
        # print(r.register_id)
        customer_list = customers.objects.filter(
            register=r.register_id).select_related('location').first()
        payment_list = register_payment_items.objects.filter(
            rp_id=r.rp_id).order_by("-rp__rp_id").first()
        if payment_list is not None:
            rpi_price_result = payment_list.rpi_price_result
        else:
            rpi_price_result = 0
        total_sum += rpi_price_result

        course_list = course_event.objects.select_related(
            'course').filter(ev_id=r.register.ev_id).first()
        res = {'main': r, 'customer_list': customer_list,
               'course_list': course_list, 'payment_list': payment_list}
        obj.append(res)
    # print(total_sum)
    param = {'total_data': len(content), 'range_param': range_param, 'close_the_sale_param': close_the_sale_param,
             'course_param': course_param, 'generation_param': generation_param, 'seller_param': seller_param}
    context = {'title': defaultTitle, 'data': obj,
               'param': param, 'total_sum': total_sum}
    return render(request, 'print/register_excel_quotation.html', context)


@login_required(login_url='/login')
def register_report_bill(request):
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
    
    list_user = User.objects.filter(is_staff=0, is_active=1,user_group_ref__module=m.module).prefetch_related('user_group_ref')
    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = "01" + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    default_end = str(lastday) + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    daterange = str(default_start) + " - " + str(default_end)
    course_list = course.objects.filter(
        cancelled=1, active=1).order_by("-course_id")
    try:
        province_list = location_thai.objects.all().values(
            'province_code', 'province_name').annotate(total=Count('province_code'))
    except location_thai.DoesNotExist:
        province_list = None
    context = {'title': defaultTitle,  'province_list': province_list, 'listMenuPermission': objMenu,
               'list_user': list_user, 'course_list': course_list, 'daterange': daterange}
    return render(request, 'report/register_report_bill.html', context)

@login_required(login_url='/login')
def register_excel_bill(request):
    user_id = request.user.id
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    
    date_range = request.POST.get('date_range', None)
    # close_the_sale = int(request.POST.get('qclose_the_sale', -1))
    course_id = int(request.POST.get('qcourse', 0))
    generation = request.POST.get('qgeneration', 0)
    seller = int(request.POST.get('qseller', 0))
    customer_name = request.POST.get('qcustomer_name', None)

    content = register_payment.objects.select_related(
        'register').filter(register__pay_type=1, active=1,register__module=m.module)

    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + "01"
    default_end = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + str(lastday)
    if date_range is not None:
        start, end = format_daterange(date_range)
        if start == end:
            content = content.filter(
                register__crt_date__date=start)
        else:
            content = content.filter(
                register__crt_date__date__gte=start, register__crt_date__date__lte=end)
        range_param = date_range
    else:
        content = content.filter(
            register__crt_date__date__gte=default_start, register__crt_date__date__lte=default_end)
        range_param = str(ymdtodmy(default_start)) + \
            " - " + str(ymdtodmy(default_end))

    close_the_sale_param = "ปิดการขาย - ขายสำเร็จ"
    # close_the_sale_param = "ทุกประเภท"
    # if close_the_sale != -1:
    #     content = content.filter(register__close_the_sale=close_the_sale)
    #     if close_the_sale == 0:
    #         close_the_sale_param = "กำลังขาย"
    #     elif close_the_sale == 1:
    #         close_the_sale_param = "ปิดการขาย - ขายสำเร็จ"
    #     elif close_the_sale == 2:
    #         close_the_sale_param = "ปิดการขาย - ขายไม่สำเร็จ"
    course_param = "ทุกหลักสูตร"
    if course_id != 0:
        content = content.filter(register__ev__course_id=course_id)
        c = course.objects.get(course_id=course_id)
        course_param = str(c.course_code) + " " + str(c.course_name)
    generation_param = "ทุกรุ่น"
    if generation:
        content = content.filter(register__ev__ev_generation=generation)
        generation_param = generation
    seller_param = "ทุกคน"
    if seller != 0:
        content = content.filter(register__seller_id=seller)
        u = User.objects.get(id=seller)
        seller_param = str(u.first_name) + " " + str(u.last_name)
    if customer_name != None:
        content = content.filter(Q(rp_name_customer__icontains=customer_name))
    obj = []
    total_sum = 0
    for r in content:
        # print(r.register_id)
        customer_list = customers.objects.filter(
            register=r.register_id).select_related('location').first()
        payment_list = register_payment_items.objects.filter(
            rp_id=r.rp_id).order_by("-rp__rp_id").first()
        if payment_list is not None:
            rpi_price_result = payment_list.rpi_price_result
        else:
            rpi_price_result = 0
        total_sum += rpi_price_result

        course_list = course_event.objects.select_related(
            'course').filter(ev_id=r.register.ev_id).first()
        res = {'main': r, 'customer_list': customer_list,
               'course_list': course_list, 'payment_list': payment_list}
        obj.append(res)
    # print(total_sum)
    param = {'total_data': len(content), 'range_param': range_param, 'close_the_sale_param': close_the_sale_param,
             'course_param': course_param, 'generation_param': generation_param, 'seller_param': seller_param}
    context = {'title': defaultTitle, 'data': obj,
               'param': param, 'total_sum': total_sum}
    return render(request, 'print/register_excel_bill.html', context)


@login_required(login_url='/login')
def register_report_learn_status(request):
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
    
    course_list = course.objects.filter(
        cancelled=1, active=1,module=m.module).order_by("-course_id")

    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = "01" + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    default_end = str(lastday) + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    daterange = str(default_start) + " - " + str(default_end)
    try:
        province_list = location_thai.objects.all().values(
            'province_code', 'province_name').annotate(total=Count('province_code'))
    except location_thai.DoesNotExist:
        province_list = None
    context = {'title': defaultTitle,  'province_list': province_list,'listMenuPermission': objMenu,
               'course_list': course_list, 'daterange': daterange}
    return render(request, 'report/register_report_learn_status.html', context)

@login_required(login_url='/login')
def register_excel_learn_status(request):
    user_id = request.user.id
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    date_range = request.POST.get('date_range', None)
    course_id = int(request.POST.get('qcourse', 0))
    generation = request.POST.get('qgeneration', 0)
    qlearning_status = request.POST.get('qlearning_status', None)
    student_name = request.POST.get('qstudent_name', None)
    ref = request.POST.get('ref', None)

    content = student.objects.select_related(
        'register').filter(register__module=m.module)

    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + "01"
    default_end = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + str(lastday)
    if date_range is not None:
        start, end = format_daterange(date_range)
        if start == end:
            content = content.filter(
                crt_date__date=start)
        else:
            content = content.filter(
                crt_date__date__gte=start, crt_date__date__lte=end)
        range_param = date_range
    else:
        content = content.filter(
            crt_date__date__gte=default_start, crt_date__date__lte=default_end)
        range_param = str(ymdtodmy(default_start)) + \
            " - " + str(ymdtodmy(default_end))

    if course_id != 0:
        content = content.filter(register__ev__course_id=course_id)
    if student_name != None:
        content = content.filter(Q(student_firstname_th__icontains=student_name) |
                                 Q(student_lastname_th__icontains=student_name) |
                                 Q(student_firstname_eng__icontains=student_name) |
                                 Q(student_lastname_eng__icontains=student_name)
                                 )
    if qlearning_status is not None and qlearning_status != "":
        content = content.filter(student_learning_status=qlearning_status)

    if generation:
        content = content.filter(register__ev__ev_generation=generation)

    if course_id != 0:
        content = content.filter(register__ev__course_id=course_id)
    if ref != None and ref != '':
        content = content.filter(register__ref_create__ref=ref)
    obj = []
    for r in content:

        try:
            ref_data = register_ref.objects.filter(
                register=r.register).order_by("-id").first()
        except:
            ref_data = None

        res = {'main': r, 'ref_data': ref_data}
        obj.append(res)

    context = {'title': defaultTitle, 'data': obj, 'total_data': len(
        content), 'range_param': range_param}
    return render(request, 'print/register_excel_learn_status.html', context)


@login_required(login_url='/login')
def register_report_approve(request):
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
    month_current = request.GET.get('qmonths', date.today().month)
    year_current = request.GET.get('qyear', date.today().year)

    content = register_applove.objects.select_related('register', 'user_approve', 'user_crt').filter(
        crt_date__month=month_current, crt_date__year=year_current,register__module=m.module).order_by("-id")

    context = {'title': defaultTitle,  'data': content, 'listMenuPermission': objMenu}
    return render(request, 'report/register_report_approve.html', context)

def student_print_certificate(request, student_id):
    
    lang = request.GET.get('lang', 'eng')
    print = request.GET.get('print', 'true')
    try:
        content = student.objects.select_related(
            "register").get(pk=student_id)
    except:
        content = None
        return render(request, '404.html')
    detail = course_event.objects.select_related(
        "course").get(ev_id=content.register.ev_id)
    context = {'title': defaultTitle,  'data': content,
               'detail': detail, 'print': print}
    if lang == "th":
        return render(request, 'print/student_print_certificate_th.html', context)
    else:
        return render(request, 'print/student_print_certificate_eng.html', context)
    
def public_form_print(request):
    
    search = request.POST.get('search', None)
    if search == "":
        return redirect("/public/form/certificate")
    try:
        content = student.objects.filter(Q(student_firstname_th__icontains=search) |
                                         Q(student_lastname_th__icontains=search) |
                                         Q(student_firstname_eng__icontains=search) |
                                         Q(student_lastname_eng__icontains=search)
                                         ).order_by("-student_firstname_th")[0:20]
    except:
        content = []
    if search != None:
        s = search
    else:
        s = ""
    context = {'title': defaultTitle,  'data': content, 'search': s}
    return render(request, 'public/public_form_print.html', context)