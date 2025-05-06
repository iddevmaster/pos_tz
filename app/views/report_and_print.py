from django.shortcuts import render, redirect
from datetime import date
import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import messages
from ..functions import dateTimeNow, last_day_of_month
from django.contrib.auth.decorators import login_required 
from django.db.models import Q, Count
# from django.http import HttpResponse, response
from datetime import date, timedelta
from dateutil import rrule 
import json
from ..constant import defaultTitle, thai_months,unitPayChoices
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum, F
from ..forms.student_form import studentForm
from ..constant import defaultTitle, api_id_card
from ..models import category_program_permission, course, course_event, customers, location_thai, register_main, register_payment, register_payment_items, student, pos_machine, register_ref, register_applove,user_group,user_detail,factbilldes,desciption_bill,teacher_income_setting,course_event,teacher,document,signature,add_on,billing_cycle_setting,conhead,condition,pay_item
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
   
    # users = User.objects.get(id=content.user_create)
    
    items = register_payment_items.objects.filter(rp_id=content.rp_id).first()
    uuid_without_dashes = str(content.register_id).replace('-', '')
    billdess = factbilldes.objects.filter(register_id=uuid_without_dashes)
    obj2 = []
    if billdess:
        for rsx in billdess:    
            
            x = desciption_bill.objects.get(des_id=rsx.des_id)
            v = {'des_id': x.des_id,  'name': x.name}
            obj2.append(v)

    content_regist = register_main.objects.select_related(
        "ev").get(register_id=content.register_id)
    
    users = User.objects.get(id=content.user_create)
    signa = signature.objects.filter(user_id=content.user_create).first()
    signama = signature.objects.filter(user_id=content.user_manage).first()
    try:
        mange = User.objects.get(id=content.user_manage)
    except User.DoesNotExist:
        mange = None
    dataadd = add_on.objects.filter(register_id=uuid_without_dashes,status='Y').values()
    
    customer = customers.objects.get(register_id=content.register_id)
    if content_regist.ev.ev_vat == 1:
        rpi_price_default = float(
            items.rpi_price_total) + float(items.rpi_price_vat)
    else:
        rpi_price_default = items.rpi_price_total

    context = {'title': defaultTitle,  'data': content,'etc':obj2,'add_on':dataadd,
               'items': items, "content_regist": content_regist, 'rpi_price_default': rpi_price_default, 'machine': machine, 'customer': customer,'user':users,'signa':signa,'manger':mange,'time':content.crt_date,'signama':signama}
    if content_regist.pay_type == 1:
        # ถ้าเป็นใบเสร็จอย่างย่อ
        if short == "yes":
            return render(request, 'print/register_print_bill_short.html', context)
        return render(request, 'print/register_print_bill.html', context)
    return render(request, 'print/register_print_sale_quotation.html', context)


@login_required(login_url='/login')
def register_printnoev(request, rp_id):
    
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
   
    # users = User.objects.get(id=content.user_create)
    
    items = register_payment_items.objects.filter(rp_id=content.rp_id).first()
    uuid_without_dashes = str(content.register_id).replace('-', '')
 

    billdess = factbilldes.objects.filter(register_id=uuid_without_dashes)
    obj2 = []
    if billdess:
        for rsx in billdess:    
            
            x = desciption_bill.objects.get(des_id=rsx.des_id)
            v = {'des_id': x.des_id,  'name': x.name}
            obj2.append(v)

    
    content_regist = register_main.objects.get(register_id=content.register_id)
    
    users = User.objects.get(id=content.user_create)
    signa = signature.objects.filter(user_id=content.user_create).first()
    signama = signature.objects.filter(user_id=content.user_manage).first()
    try:
        mange = User.objects.get(id=content.user_manage)
    except User.DoesNotExist:
        mange = None
    dataadd = add_on.objects.filter(register_id=uuid_without_dashes,status='Y').values()
    
    customer = customers.objects.get(register_id=content.register_id)
    rpi_price_rpi_pri = items.rpi_price * items.rpi_quantity 
    # ราคารวม  rpi_price  สินค้า
    if items.vat == '1':
        rpi_total = items.rpi_price_total + items.rpi_price_vat
    else:
        rpi_total = items.rpi_price_total
    # ราคารวม  ช่องแนวนอน
   
    print(rpi_total)
    # ราคาก่อนvat
    rpi_price_default = items.rpi_price_total  

    context = {'title': defaultTitle,  'data': content,'etc':obj2,'add_on':dataadd,'rpi_total':rpi_total,
               'items': items, "content_regist": content_regist,'rpi_price_rpi_pri':rpi_price_rpi_pri, 'rpi_price_default': rpi_price_default, 'machine': machine, 'customer': customer,'user':users,'signa':signa,'manger':mange,'time':content.crt_date,'signama':signama}
    if content_regist.pay_type == 1:
        # ถ้าเป็นใบเสร็จอย่างย่อ
        if short == "yes":
            return render(request, 'print/register_print_bill_short.html', context)
        return render(request, 'print/register_print_billno.html', context)
    return render(request, 'print/register_print_sale_quotationno.html', context)



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
    event = int(request.POST.get('event', 0))
 
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
    if event == 1:
        content = content.filter(register__ev__ev_id__isnull=False)
    if event == 2:
        content = content.filter(register__ev__ev_id__isnull=True)

    
    obj = []
    total_sum = 0
    for r in content:
        
        
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
def register_excel_seller_accept(request,ev_id):
    user_id = request.user.id
    
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    content = teacher_income_setting.objects.select_related('ev').filter(pk=ev_id)
    tincome = teacher_income_setting.objects.select_related('teacher').get(pk=ev_id)
    cou_ev = course_event.objects.select_related('course').get(pk=tincome.ev_id)
    # teach = teacher.objects.get(teacher_id=tincome.teacher)
    status = ['N','Y']
    content_regist = register_main.objects.select_related(
        "seller", "ev").filter(ev_id=tincome.ev_id,status__in=status).order_by("pay_type")
    obj = []  
    total_payment = 0
    total_credit = 0
    for r in content_regist:  
       
         
         payment = register_payment.objects.get(register_id=r.register_id)
         item = register_payment_items.objects.get(register_id=r.register_id)
         custo = customers.objects.get(register_id=r.register_id)
      
         if r.pay_type == 1:
             total_payment += item.rpi_price_total
         else:
             total_credit += item.rpi_price_total
                 
          
         fs = {'rp_doc_number':payment.rp_doc_number,'pay_type':r.pay_type,'customer':custo.customer_name,'tax':custo.customer_tax,'tel':custo.customer_phone,'rpi_price':item.rpi_price_total}
         obj.append(fs) 
           
    total = total_payment + total_credit
    status = ['N','Y']
    count_payment = register_main.objects.filter(ev_id=tincome.ev_id,status__in=status,pay_type=1).count()
    count_credit = register_main.objects.filter(ev_id=tincome.ev_id,status__in=status,pay_type=2).count()
    totaldata = document.objects.filter().count()
    payment = register_payment.objects.get(register_id=r.register_id)
   
    month_current = date.today().month
    year_current = date.today().year
    year_current_f = str(int(date.today().year) + 543)
    current_time = datetime.now().time()
    totalhours = cou_ev.ev_hour + cou_ev.ev_hour_two
    running_number = treeDigit(totaldata + 1)
    student_code = "TOP" + str(twoDigit(month_current)) + \
            str(running_number) + "/" + str(year_current)
 
    
    context = {'title': defaultTitle,'data':obj,'teacher_income_setting':tincome,'course_ev':cou_ev,'tax_number':tincome.teacher.tax_number,'fname':tincome.teacher.teacher_firstname_th,'lname':tincome.teacher.teacher_lastname_th,'status':tincome.status,'pi':tincome.pi_id,
               'course_code':cou_ev.course.course_code,'course_name':cou_ev.course.course_name,'total_payment':total_payment,'total_credit':total_credit,'total':total,'total_bill_payment':count_payment,'total_bill_credit':count_credit,'totalhours':totalhours,'doc':student_code,'teach_in_come':ev_id}
    return render(request, 'print/register_excel_seller_accept.html', context)


@login_required(login_url='/login')
def register_excel_seller_view(request,doc_id):
    user_id = request.user.id
    print(doc_id)
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')

    obj = []
    getdoc = document.objects.get(doc_id=doc_id)
    tincome = teacher_income_setting.objects.select_related('teacher').get(pk=getdoc.teacher_income_id)
    cou_ev = course_event.objects.select_related('course').get(pk=tincome.ev_id)
    # teach = teacher.objects.get(teacher_id=tincome.teacher)
    status = ['N','Y']
    content_regist = register_main.objects.select_related(
        "seller", "ev").filter(ev_id=tincome.ev_id,status__in=status).order_by("pay_type")
    obj = []  
    total_payment = 0
    total_credit = 0
    for r in content_regist:  
       
         
         payment = register_payment.objects.get(register_id=r.register_id)
         item = register_payment_items.objects.get(register_id=r.register_id)
         custo = customers.objects.get(register_id=r.register_id)
      
         if r.pay_type == 1:
             total_payment += item.rpi_price_total
         else:
             total_credit += item.rpi_price_total
                 
          
         fs = {'rp_doc_number':payment.rp_doc_number,'pay_type':r.pay_type,'customer':custo.customer_name,'tax':custo.customer_tax,'tel':custo.customer_phone,'rpi_price':item.rpi_price_total}
         obj.append(fs) 
    total = total_payment + total_credit
    status = ['N','Y']
    count_payment = register_main.objects.filter(ev_id=tincome.ev_id,status__in=status,pay_type=1).count()
    count_credit = register_main.objects.filter(ev_id=tincome.ev_id,status__in=status,pay_type=2).count()
    totaldata = document.objects.filter().count()
    payment = register_payment.objects.get(register_id=r.register_id)
   
    month_current = date.today().month
    year_current = date.today().year
    year_current_f = str(int(date.today().year) + 543)
    current_time = datetime.now().time()
    totalhours = cou_ev.ev_hour + cou_ev.ev_hour_two
    totalprice = int(getdoc.price) / totalhours 


    users = User.objects.get(id=payment.user_create)
    signa = signature.objects.filter(user_id=payment.user_create).first()

    mange = User.objects.get(id=payment.user_manage)
    
    running_number = treeDigit(totaldata + 1)
    student_code = "TOP" + str(twoDigit(month_current)) + \
            str(running_number) + "/" + str(year_current)
         
    context = {'title': defaultTitle,'data':obj,'teacher_income_setting':tincome,'course_ev':cou_ev,'tax_number':tincome.teacher.tax_number,'fname':tincome.teacher.teacher_firstname_th,'lname':tincome.teacher.teacher_lastname_th,'status':tincome.status,'users':users,'signa':signa,'mange':mange,
               'course_code':cou_ev.course.course_code,'course_name':cou_ev.course.course_name,'total_payment':total_payment,'total_credit':total_credit,'total':total,'total_bill_payment':count_payment,'total_bill_credit':count_credit,'totalhours':totalhours,'doc':getdoc.doc_number,'payment_policy':getdoc.doc_number,'totalprice':totalprice,'price':getdoc.price}
    return render(request, 'print/register_excel_seller_view_frame.html', context)

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
    event = int(request.POST.get('event', 0))
    content = register_payment.objects.select_related(
        'register').filter(register__pay_type=2, active=1,register__module=m.module)
    print(content)
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
    if event == 1:
        content = content.filter(register__ev__ev_id__isnull=False)
    if event == 2:
        content = content.filter(register__ev__ev_id__isnull=True)    
    obj = []
    
    total_sum = 0
    for r in content:
        print(r.register_id)
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
def register_report_billtoday(request):
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
    return render(request, 'report/register_report_billtoday.html', context)   



@login_required(login_url='/login')
def register_report_compensation(request):
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
    # month_current = date.today().month


    result = teacher.objects.filter(cancelled=1).order_by("-crt_date")
    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = "01" + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    default_end = str(lastday) + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    daterange = str(default_start) + " - " + str(default_end)


    year_current = request.GET.get('qyear', date.today().year)
    teacher_current = request.GET.get('qteacher', None)
    day_current = date.today().day
    # day_current = 10
    b = billing_cycle_setting.objects.filter(module=m.module)
    start_content = teacher_income_setting.objects.filter(
        ev__module=m.module,status='I')

    list_teacher = teacher.objects.filter(
        module=m.module, cancelled=1, active=1)
    obj = []



    teacher_income = teacher_income_setting.objects.filter(status='I')
    requirements = 'ไม่มี'
    name_con = '-'
    totalp = 0
    for rs in teacher_income:
            regbyev = register_main.objects.filter(ev_id=rs.ev)
            total_rq_quta = 0
            for aaa in regbyev:
                try:
                    bbbb = register_payment.objects.filter(register_id=aaa.register_id).first()
                    if bbbb:
                        total_rq_quta += bbbb.rp_quota
                except register_payment.DoesNotExist:  
                        bbbb = 0
            
            event = course_event.objects.get(ev_id=rs.ev_id)
            select = 0
            price = 0
            tis_compensation = 0
         
            if int(event.condition_type) == 1:
                
                requirements = 'มี'
            if int(rs.pi_id) == 1:
           
             if event.condition_type == '1':  # เช็คว่า วิทยากร มีเงื่อนไขไหม
                icont = condition.objects.filter(conhead=event.condition_id)
                for iconts in icont:
        
                     typet = iconts.type
                      
                     if typet == '1':
                    
                        if total_rq_quta > iconts.student:
                            select = iconts.condition_id
                            break
                     elif typet == '2':
                    
                        if iconts.student < total_rq_quta:
                            select = iconts.condition_id
                            break
                     elif typet == '3':
                        
                        if iconts.student == total_rq_quta: 
                            select = iconts.condition_id
                            break  
             print('วิทยากร',select)
             if select != 0:
              
              totalselect = condition.objects.get(condition_id=select)
              price = int(rs.tis_quantity) * (totalselect.price)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              name_con = head.name
              tis_compensation = totalselect.price
              print('คำนวน',price)
              
             else:
                price = int(rs.tis_quantity) * (rs.tis_compensation)    
                tis_compensation = rs.tis_compensation
               
        
            else :    
        
             if int(rs.pi_id) == 2:

              price = int(rs.tis_quantity) * (rs.tis_compensation)  
              tis_compensation = rs.tis_compensation        
              
             elif int(rs.pi_id) == 3:
            
              price = int(rs.tis_quantity) * (rs.tis_compensation) 
              tis_compensation = rs.tis_compensation

             elif int(rs.pi_id) == 4:
              
              price = int(rs.tis_quantity) * (rs.tis_compensation) 
              tis_compensation = rs.tis_compensation
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)

            totalp += price
            r = {'pay_name':pay.pi_name,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation}
        
            obj.append(r)



    context = {'title': defaultTitle, 'data': obj, 'list_user': result,'daterange': daterange,
               'listMenuPermission': objMenu, 'list_teacher': list_teacher}
    return render(request, 'report/billing_cycle_result.html', context)

@login_required(login_url='/login')
def register_report_compensation_withdraw(request):
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
    # month_current = date.today().month


    result = teacher.objects.filter(cancelled=1).order_by("-crt_date")
    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = "01" + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    default_end = str(lastday) + "/" + \
        str(date.today().month) + "/" + str(date.today().year)
    daterange = str(default_start) + " - " + str(default_end)


    year_current = request.GET.get('qyear', date.today().year)
    teacher_current = request.GET.get('qteacher', None)
    day_current = date.today().day
    # day_current = 10
    b = billing_cycle_setting.objects.filter(module=m.module)
    start_content = teacher_income_setting.objects.filter(
        ev__module=m.module,status='I')

    list_teacher = teacher.objects.filter(
        module=m.module, cancelled=1, active=1)
    obj = []



    teacher_income = teacher_income_setting.objects.filter(status='I')
    requirements = 'ไม่มี'
    name_con = '-'
    totalp = 0
    for rs in teacher_income:
            regbyev = register_main.objects.filter(ev_id=rs.ev)
            total_rq_quta = 0
            for aaa in regbyev:
                try:
                    bbbb = register_payment.objects.filter(register_id=aaa.register_id).first()
                    if bbbb:
                        total_rq_quta += bbbb.rp_quota
                except register_payment.DoesNotExist:  
                        bbbb = 0
            
            event = course_event.objects.get(ev_id=rs.ev_id)
            select = 0
            price = 0
            tis_compensation = 0
         
            if int(event.condition_type) == 1:
                requirements = 'มี'
            if int(rs.pi_id) == 1:
           
             if event.condition_type == '1':  # เช็คว่า วิทยากร มีเงื่อนไขไหม
                icont = condition.objects.filter(conhead=event.condition_id)
                for iconts in icont:
        
                     typet = iconts.type
                      
                     if typet == '1':
                    
                        if total_rq_quta > iconts.student:
                            select = iconts.condition_id
                            break
                     elif typet == '2':
                    
                        if iconts.student < total_rq_quta:
                            select = iconts.condition_id
                            break
                     elif typet == '3':
                        
                        if iconts.student == total_rq_quta: 
                            select = iconts.condition_id
                            break  
             print('วิทยากร',select)
             if select != 0:
              
              totalselect = condition.objects.get(condition_id=select)
              price = int(rs.tis_quantity) * (totalselect.price)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              name_con = head.name
              tis_compensation = totalselect.price
          
             else:
                price = int(rs.tis_quantity) * (rs.tis_compensation)    
                tis_compensation = rs.tis_compensation
               
        
            else :    
        
             if int(rs.pi_id) == 2:

              price = int(rs.tis_quantity) * (rs.tis_compensation)  
              tis_compensation = rs.tis_compensation        
              
             elif int(rs.pi_id) == 3:
            
              price = int(rs.tis_quantity) * (rs.tis_compensation) 
              tis_compensation = rs.tis_compensation

             elif int(rs.pi_id) == 4:
              
              price = int(rs.tis_quantity) * (rs.tis_compensation) 
              tis_compensation = rs.tis_compensation
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)

            totalp += price
            r = {'pay_name':pay.pi_name,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation}
        
            obj.append(r)



    context = {'title': defaultTitle, 'data': obj, 'list_user': result,'daterange': daterange,
               'listMenuPermission': objMenu, 'list_teacher': list_teacher}
    return render(request, 'print/report_withdraw.html', context)    

@login_required(login_url='/login')
def register_report_billtoday_summarize(request):
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
    return render(request, 'report/register_report_billtoday_summary.html', context)       

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
    event = int(request.POST.get('event', 0))
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
    if event == 1:
        content = content.filter(register__ev__ev_id__isnull=False)
    if event == 2:
        content = content.filter(register__ev__ev_id__isnull=True)
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
def register_excel_billtoday(request):
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
    event = int(request.POST.get('event', 0))
    content = register_payment.objects.select_related(
        'register').filter(register__pay_type=1, active=1,register__module=m.module)

    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + "01"
    default_end = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + str(lastday)
    default_today = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + str(date.today().day)

        
    if date_range is not None:
        start, end = format_daterange(date_range)
        if start == end:
            content = content.filter(
                register__crt_date__date=default_today)
        else:
            content = content.filter(
                register__crt_date__date__gte=default_today, register__crt_date__date__lte=default_today)
        range_param = date_range
    else:
        content = content.filter(
            register__crt_date__date__gte=default_today, register__crt_date__date__lte=default_today)
        range_param = str(ymdtodmy(default_today)) + \
            " - " + str(ymdtodmy(default_today))

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
    if event == 1:
        content = content.filter(register__ev__ev_id__isnull=False)
    if event == 2:
        content = content.filter(register__ev__ev_id__isnull=True)
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
    return render(request, 'print/register_excel_bill_today.html', context)


@login_required(login_url='/login')
def register_excel_billtoday_summarize(request):
    user_id = request.user.id
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    
    # date_range = request.POST.get('date_range', None)

    # course_id = int(request.POST.get('qcourse', 0))
    # generation = request.POST.get('qgeneration', 0)
    # seller = int(request.POST.get('qseller', 0))
    # customer_name = request.POST.get('qcustomer_name', None)
    # event = int(request.POST.get('event', 0))
    # content = register_payment.objects.select_related(
    #     'register').filter(register__pay_type=1, active=1,register__module=m.module)

    # lastday = lastDateOfmonth(
    #     date.today().year, date.today().month, date.today().day)
    # default_start = str(date.today().year) + "-" + \
    #     str(date.today().month) + "-" + "01"
    # default_end = str(date.today().year) + "-" + \
    #     str(date.today().month) + "-" + str(lastday)
    default_today = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + str(date.today().day)

    range_param = str(ymdtodmy(default_today)) + \
            " - " + str(ymdtodmy(default_today))

    queryset = (
        register_payment.objects
        .filter(active=1)
        .annotate(related_register_id=F('register__register_id')) 
        .filter(register__pay_type=1, register__crt_date__date=default_today)
        .values('items__rpi_code', 'items__rpi_name', 'items__rpi_code')
        .annotate(
            total_bill=Count('items__rpi_code'),
            total=Sum('items__rpi_price_total'),
            dis=Sum('items__rpi_price_discount'),
            vat=Sum('items__rpi_price_vat'),
            result=Sum('items__rpi_price_result'),
        )
    )

   
    print(queryset)
    total = 0.0  # Initialize to 0.0
    for r in queryset:
        if r['result'] is not None:
            total += r['result']
            print(total)

    context = {'sales_data': list(queryset),'total_sum':total,'today':range_param}
        
    # if date_range is not None:
    #     start, end = format_daterange(date_range)
    #     if start == end:
    #         content = content.filter(
    #             register__crt_date__date=default_today)
    #     else:
    #         content = content.filter(
    #             register__crt_date__date__gte=default_today, register__crt_date__date__lte=default_today)
    #     range_param = date_range
    # else:
    #     content = content.filter(
    #         register__crt_date__date__gte=default_today, register__crt_date__date__lte=default_today)
    #     range_param = str(ymdtodmy(default_today)) + \
    #         " - " + str(ymdtodmy(default_today))

    # close_the_sale_param = "ปิดการขาย - ขายสำเร็จ"

    # course_param = "ทุกหลักสูตร"
    # if course_id != 0:
    #     content = content.filter(register__ev__course_id=course_id)
    #     c = course.objects.get(course_id=course_id)
    #     course_param = str(c.course_code) + " " + str(c.course_name)
    # generation_param = "ทุกรุ่น"
    # if generation:
    #     content = content.filter(register__ev__ev_generation=generation)
    #     generation_param = generation
    # seller_param = "ทุกคน"
    # if seller != 0:
    #     content = content.filter(register__seller_id=seller)
    #     u = User.objects.get(id=seller)
    #     seller_param = str(u.first_name) + " " + str(u.last_name)
    # if customer_name != None:
    #     content = content.filter(Q(rp_name_customer__icontains=customer_name))
    # if event == 1:
    #     content = content.filter(register__ev__ev_id__isnull=False)
    # if event == 2:
    #     content = content.filter(register__ev__ev_id__isnull=True)
    # obj = []
    # total_sum = 0
    # for r in content:
    #     print(r.register_id)
    #     customer_list = customers.objects.filter(
    #         register=r.register_id).select_related('location').first()
    #     payment_list = register_payment_items.objects.filter(
    #         rp_id=r.rp_id).order_by("-rp__rp_id").first()
    #     if payment_list is not None:
    #         rpi_price_result = payment_list.rpi_price_result
    #     else:
    #         rpi_price_result = 0
    #     total_sum += rpi_price_result

    #     course_list = course_event.objects.select_related(
    #         'course').filter(ev_id=r.register.ev_id).first()
    #     res = {'main': r, 'customer_list': customer_list,
    #            'course_list': course_list, 'payment_list': payment_list}
    #     obj.append(res)
    # # print(total_sum)
    # param = {'total_data': len(content), 'range_param': range_param, 'close_the_sale_param': close_the_sale_param,
    #          'course_param': course_param, 'generation_param': generation_param, 'seller_param': seller_param}
    # context = {'title': defaultTitle, 'data': obj,
    #            'param': param, 'total_sum': total_sum}
    return render(request, 'print/register_excel_bill_today_summary.html', context)    


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