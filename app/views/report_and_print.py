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
from ..forms.form_month import MyFormWithThai
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum, F

from ..forms.student_form import studentForm
from ..constant import defaultTitle, api_id_card
from ..models import category_program_permission, course, course_event, customers, location_thai, register_main, register_payment, register_payment_items, student, pos_machine, register_ref, register_applove,user_group,user_detail,factbilldes,desciption_bill,teacher_income_setting,course_event,teacher,document,signature,add_on,billing_cycle_setting,conhead,condition,pay_item,fact_teacher_user,training,bill_setting,com_income_setting,fact_customer,fact_signature,signature
from ..functions import dateTimeIntNow, dateTimeNow, dmytoymd, month_fomat, lastDateOfmonth, treeDigit, twoDigit, format_daterange, ymdtodmy,format_daterange_new,ymdtodmy_new,checkpermi


THAI_MONTH_NAMES = [
    (1, 'มกราคม'),
    (2, 'กุมภาพันธ์'),
    (3, 'มีนาคม'),
    (4, 'เมษายน'),
    (5, 'พฤษภาคม'),
    (6, 'มิถุนายน'),
    (7, 'กรกฎาคม'),
    (8, 'สิงหาคม'),
    (9, 'กันยายน'),
    (10, 'ตุลาคม'),
    (11, 'พฤศจิกายน'),
    (12, 'ธันวาคม'),
]

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
    
    bill = bill_setting.objects.get(bill_id=1)
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
    
    factcustomer = fact_customer.objects.get(register_id=content.register_id)
    customer = customers.objects.get(pk=factcustomer.customer_id)
    if content_regist.ev.ev_vat == 1:
        rpi_price_default = float(
            items.rpi_price_total) + float(items.rpi_price_vat)
    else:
        rpi_price_default = items.rpi_price_total

    
    t = 0
    if items.type_payment == 'FullPayment':
       t = 0
    elif items.type_payment == 'Deposit':
       t = items.rpi_price - items.rpi_price_pay
    else:   
       t = 0

    print(t)   
    
 
    context = {'title': defaultTitle,  'data': content,'etc':obj2,'add_on':dataadd,'is_show_signature':bill.is_show_signature,'total':t,
               'items': items, "content_regist": content_regist, 'rpi_price_default': rpi_price_default, 'machine': machine, 'customer': customer,'user':users,'signa':signa,'manger':mange,'time':content.crt_date,'signama':signama}
    if content_regist.pay_type == 1:
        # ถ้าเป็นใบเสร็จอย่างย่อ
        if short == "yes":
            return render(request, 'print/register_print_bill_short.html', context)
        return render(request, 'print/register_print_bill.html', context)
    return render(request, 'print/register_print_sale_quotation.html', context)

@login_required(login_url='/login')
def register_print_witdraw(request, teacher_id, start, end):

    start_new = ymdtodmy_new(start)
    end_new = ymdtodmy_new(end)

    
    obj = []
    list_teacher = teacher.objects.get(teacher_id=teacher_id,cancelled=1, active=1)

    content = teacher_income_setting.objects.select_related('ev').filter(status='S',teacher=teacher_id,ev__ev_date_start__gte=start,ev__ev_date_end__lte=end)
    uuid_without_dashes = str(teacher_id).replace('-', '')
    factuser = fact_teacher_user.objects.get(teacher_id=uuid_without_dashes)
    getdatauser = User.objects.get(pk=factuser.user_id)
    requirements = 'ไม่มี'
    name_con = '-'
    totalp = 0
    sumtax = 0
    for rs in content:
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

             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,status='I',pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)

            totalp += price
         
            taxall = price * (rs.tax / 100)
            sumtax += taxall
           
            r = {'pay_name':pay.pi_name,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation,'tax':taxall}
        
            obj.append(r)



    context = {'title': defaultTitle, 'data': obj,'list_teacher':list_teacher,'cou':content.count(),'totalp':totalp,'getdatauser':getdatauser,
             'start_new':start_new,'end_new':end_new,'sumtax':sumtax}
    return render(request, 'print/register_print_witdraw.html',context)


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
    bill = bill_setting.objects.get(bill_id=1)
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
    cus = fact_customer.objects.get(register_id=content.register_id)
 
    customer = customers.objects.get(customer_id=cus.customer_id)
    rpi_price_rpi_pri = items.rpi_price * items.rpi_quantity 
    # ราคารวม  rpi_price  สินค้า
    if items.vat == '1':
        rpi_total = items.rpi_price_total + items.rpi_price_vat
    else:
        rpi_total = items.rpi_price_total
    # ราคารวม  ช่องแนวนอน
   
  
    # ราคาก่อนvat
    rpi_price_default = items.rpi_price_total  

    context = {'title': defaultTitle,  'data': content,'etc':obj2,'add_on':dataadd,'rpi_total':rpi_total,'is_show_signature':bill.is_show_signature,
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

    path = request.path
    cleaned_path = path.strip('/')    
    checkpa = checkpermi(cleaned_path,cm_id)
    if checkpa == 0:
        return render(request, '403.html')     
    
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
def register_selller_report_event(request):
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

    path = request.path
    cleaned_path = path.strip('/')    
    checkpa = checkpermi(cleaned_path,cm_id)
    if checkpa == 0:
        return render(request, '403.html')     
    
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
    return render(request, 'report/register_selller_report_event.html', context)

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
    type_payment = request.POST.get('type_payment', 'FullPayment')

   
    content = fact_customer.objects.select_related(
            "register","customer").filter(register__module=m.module)
    
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
        content = content.filter(Q(customer__customer_name__icontains=customer_name))
    if event == 1:
        content = content.filter(register__ev__ev_id__isnull=False)
    if event == 2:
        content = content.filter(register__ev__ev_id__isnull=True)
    if type_payment == 'FullPayment':
        content = content.filter(Q(register__orderstatus='FullPayment') | Q(register__orderstatus='Completed'))
    if type_payment == 'Deposit':
        content = content.filter(Q(register__orderstatus='Deposit'))     

    
    
    obj = []
    total_sum = 0
    
    for r in content:
        
        payment_list = register_payment_items.objects.select_related('rp','register').filter(
            register_id=r.register,register__status='Y').order_by("-rp__rp_id")
        course_list = []
        for rs in payment_list:
            
            if rs.register is not None:
                rpi_price_result = rs.rpi_price_result
                if rs.register.is_event == 'Y':
                    course_list = course_event.objects.select_related('course').filter(ev_id=rs.register.ev_id).first()
                else:
                    course_list = course.objects.filter(course_id=rs.register.course.course_id).first() 
            else:
                rpi_price_result = 0
            total_sum += rpi_price_result
            
            cs = fact_customer.objects.select_related("register","customer").filter(register_id=rs.register.register_id).first()
            
            res = {'customer_list': cs,
               'course_list': course_list, 'payment_list': rs}
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
         cus = fact_customer.objects.get(register_id=r.register_id)
         custo = customers.objects.get(customer_id=cus.customer_id)
         nmscr = ''
      
         if r.pay_type == 1:
             total_payment += item.rpi_price_total
         else:
             total_credit += item.rpi_price_total

         if payment.number_receipt != None:    
            nmscr = payment.number_receipt
          
         fs = {'number_receipt':nmscr,'rp_doc_number':payment.rp_doc_number,'pay_type':r.pay_type,'customer':custo.customer_name,'tax':custo.customer_tax,'tel':custo.customer_phone,'rpi_price':item.rpi_price_total}
         obj.append(fs) 
           
    total = total_payment + total_credit
    status = ['N','Y']
    count_payment = register_main.objects.filter(ev_id=tincome.ev_id,status__in=status,pay_type=1).count()
    count_credit = register_main.objects.filter(ev_id=tincome.ev_id,status__in=status,pay_type=2).count()
    totaldata = document.objects.filter().count()
    payment = register_payment.objects.get(register_id=r.register_id)
   
    month_current = date.today().month
    year_current = date.today().year
    day_current = date.today().today
    
    

    totalhours = cou_ev.ev_hour + cou_ev.ev_hour_two
    running_number = treeDigit(totaldata + 1)
    student_code = "TOP" + str(twoDigit(month_current)) + \
            str(running_number) + "/" + str(year_current)
 
   
    context = {'title': defaultTitle,'data':obj,'teacher_income_setting':tincome,'course_ev':cou_ev,'tax_number':tincome.teacher.tax_number,'fname':tincome.teacher.teacher_firstname_th,'lname':tincome.teacher.teacher_lastname_th,'status':tincome.status,'pi':tincome.pi_id,'day':day_current,'month_current':month_fomat(month_current),'year_current':year_current,'today':date.today(),
               'course_code':cou_ev.course.course_code,'course_name':cou_ev.course.course_name,'total_payment':total_payment,'total_credit':total_credit,'total':total,'total_bill_payment':count_payment,'total_bill_credit':count_credit,'totalhours':totalhours,'doc':student_code,'teach_in_come':ev_id,'tis_compensation':tincome.tis_compensation}
    return render(request, 'print/register_excel_seller_accept.html', context)


@login_required(login_url='/login')
def register_excel_seller_view(request,doc_id):
    user_id = request.user.id
   
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
         cus = fact_customer.objects.get(register_id=r.register_id)
         custo = customers.objects.get(customer_id=cus.customer_id)
      
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

    totalhours = cou_ev.ev_hour + cou_ev.ev_hour_two
    totalprice = int(getdoc.price) / totalhours 


    users = User.objects.get(id=payment.user_create)
    signa = signature.objects.filter(user_id=payment.user_create).first()
  
    mange = User.objects.get(id=payment.user_manage)
    signaMange = signature.objects.filter(user_id=payment.user_manage).first()
  
    
    ddx = getdoc.created_at.day
    mmx = getdoc.created_at.month
    yyx = getdoc.created_at.year
    yyy = str(int(yyx) + 543)

    running_number = treeDigit(totaldata + 1)
    student_code = "TOP" + str(twoDigit(month_current)) + \
            str(running_number) + "/" + str(year_current)
    _date = date.today()
    context = {'ddx': ddx,'mmx': mmx,'yyy': yyy,'title': defaultTitle,'data':obj,'teacher_income_setting':tincome,'course_ev':cou_ev,'tax_number':tincome.teacher.tax_number,'fname':tincome.teacher.teacher_firstname_th,'lname':tincome.teacher.teacher_lastname_th,'status':tincome.status,'users':users,'signa':signa,'mange':mange,'signaMange':signaMange,'date':_date,'doc_in_hrc':getdoc,
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

    path = request.path
    cleaned_path = path.strip('/')    
    checkpa = checkpermi(cleaned_path,cm_id)
    if checkpa == 0:
        return render(request, '403.html')    
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

    path = request.path
    cleaned_path = path.strip('/')    
    checkpa = checkpermi(cleaned_path,cm_id)
    if checkpa == 0:
        return render(request, '403.html')    
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
    date_range = request.POST.get('date_range', None)
    teacher_id = request.POST.get('teacher_id', None)

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

    teacher_income = teacher_income_setting.objects.filter(status='I',teacher=teacher_id)
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

             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,status='I',pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)

            totalp += price
            r = {'pay_name':pay.pi_name,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation}
        
            obj.append(r)



    context = {'title': defaultTitle, 'data': obj, 'list_user': result,'daterange': daterange,
               'listMenuPermission': objMenu, 'list_teacher': list_teacher}
    return render(request, 'report/billing_cycle_result.html', context)



@login_required(login_url='/login')
def register_report_compensation_withdraw_onemore(request):
    user_id = request.user.id
    date_range = request.POST.get('date_range', None)
    teacher_id = request.POST.get('teacher_id', None)
    teac = fact_teacher_user.objects.get(user_id=user_id)
    uuid_without_dashes = str(teac.teacher_id).replace('-', '')

    
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
        ev__module=m.module,status='S')

    list_teacher = teacher.objects.filter(
        module=m.module, cancelled=1, active=1)
    obj = []
   
    teacher_one = teacher.objects.get(teacher_id=teac.teacher_id,cancelled=1)


    context = {'title': defaultTitle, 'data': obj, 'list_user': result,'daterange': daterange,'teacher_one':teacher_one,
               'listMenuPermission': objMenu}
    return render(request, 'report/billing_cycle_result_one.html', context)


@login_required(login_url='/login')
def register_report_compensation_withdraw(request):
    user_id = request.user.id
    
    date_range = request.POST.get('date_range', None)
    teacher_id = request.POST.get('teacher_id', None)

    start = None
    end = None
    start_new = None
    end_new = None
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

    
    list_teacher = teacher.objects.filter(
        module=m.module, cancelled=1, active=1)
    obj = []

    teacher_one = None
    getdatauser = None
   
    content = teacher_income_setting.objects.select_related('ev').filter(status='S',teacher=teacher_id)
    if teacher_id is not None:
        teacher_one = teacher.objects.get(teacher_id=teacher_id)
        uuid_without_dashes = str(teacher_id).replace('-', '')
        factuser = fact_teacher_user.objects.get(teacher_id=uuid_without_dashes)
        getdatauser = User.objects.get(pk=factuser.user_id)

       
    if date_range is not None:
        start, end = format_daterange(date_range)
        start_new ,end_new = format_daterange_new(date_range)
      
        if start == end:
            content = content.filter(ev__ev_date_start__gte=start)
        else:
            content = content.filter(ev__ev_date_start__gte=start,ev__ev_date_end__lte=end)
    print(start)
    requirements = 'ไม่มี'
    name_con = '-'
    totalp = 0
    sumtax = 0
    for rs in content:
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
             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,status='I',pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot 
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)

            totalp += price
         
            taxall = price * (rs.tax / 100)
            sumtax += taxall
           
            r = {'pay_name':pay.pi_name,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation,'tax':taxall}
        
            obj.append(r)



    context = {'title': defaultTitle, 'data': obj, 'list_user': result,'daterange': daterange,'totalp':totalp,'date_range':date_range,'teacher_id':teacher_id,'cou':content.count(),
            'list_teacher': list_teacher,'start':start,'end':end,'start_new':start_new,'end_new':end_new,'sumtax':sumtax,'teacher_one':teacher_one,'getdatauser':getdatauser}
    return render(request, 'print/report_withdraw.html', context)    

@login_required(login_url='/login')
def register_report_summary(request):
    user_id = request.user.id
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    path = request.path
    cleaned_path = path.strip('/')    
    checkpa = checkpermi(cleaned_path,cm_id)
    if checkpa == 0:
        return render(request, '403.html')    
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
    obj = []
    day_current_m = date.today().month - 1
  
    context = {'title': defaultTitle, 'data': obj,'listMenuPermission': objMenu,'thai_months': THAI_MONTH_NAMES,'current_month':day_current_m}
    return render(request, 'report/billing_cycle_result_summary_overdue.html', context) 


@login_required(login_url='/login')
def register_report_summary_teacher(request):
    user_id = request.user.id
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    path = request.path
    cleaned_path = path.strip('/')    
    checkpa = checkpermi(cleaned_path,cm_id)
    if checkpa == 0:
        return render(request, '403.html')    
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
    obj = []
    day_current_m = date.today().month
  
    context = {'title': defaultTitle, 'data': obj,'listMenuPermission': objMenu,'thai_months': THAI_MONTH_NAMES,'current_month':day_current_m}
    return render(request, 'report/billing_cycle_result_summary_withdraw.html', context) 




@login_required(login_url='/login')
def register_report_summary_print_overdue(request, year, m):
    obj = []



    start = None
    end = None
    start_new = None
    end_new = None
    obj = []

    day_current_day = date.today().day
    
 
    bill = billing_cycle_setting.objects.get(id=2)
    start = bill.bcs_start_day
    get_last_day = last_day_of_month(
            datetime.date(int(year), int(m), 1))
    last_day = get_last_day.day


    content = teacher_income_setting.objects.select_related('ev').filter(status='S',active=0,tis_start_date__day__gte=start,
                tis_end_date__day__lte=last_day,
                tis_end_date__month=m,
                tis_end_date__year=year,).order_by('teacher_id')
    
    requirements = 'ไม่มี'
    name_con = '-'
    totalp = 0
    sumtax = 0
    totalall = 0
    for rs in content:
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
             
             if select != 0:
              
              totalselect = condition.objects.get(condition_id=select)
              price = int(rs.tis_quantity) * (totalselect.price)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              name_con = head.name
              tis_compensation = totalselect.price
              print(price)
             else:
                price = int(rs.tis_quantity) * (rs.tis_compensation)    
                tis_compensation = rs.tis_compensation
                print(price)
            else :    
        
             if int(rs.pi_id) == 2:
                
              price = int(rs.tis_quantity) * (rs.tis_compensation)  
              tis_compensation = rs.tis_compensation        
              print(price)
             elif int(rs.pi_id) == 3:
            
              price = int(rs.tis_quantity) * (rs.tis_compensation) 
              tis_compensation = rs.tis_compensation
              print(price)
             elif int(rs.pi_id) == 4:
              
              price = int(rs.tis_quantity) * (rs.tis_compensation) 
              tis_compensation = rs.tis_compensation
              print(price)
             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot
              print(price)
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)

            totalp += price
         
            taxall = price * (rs.tax / 100)
            sumtax += taxall
           
           
            r = {'teacher':rs.teacher_id,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation,'tax':taxall}
        
            obj.append(r)   

    result_dict = {}
    for item in obj:
            teacher_one = teacher.objects.get(teacher_id=item["teacher"])
            uuid_without_dashes = str(item["teacher"]).replace('-', '')
            factuser = fact_teacher_user.objects.get(teacher_id=uuid_without_dashes)
            getdatauser = User.objects.get(pk=factuser.user_id)
            item_id = item["teacher"]
            name = teacher_one
            qty = item["price"]
            ta = item["tax"]
            total = item["price"] -item["tax"]
            aaaa = total
            if item_id not in result_dict:
                result_dict[item_id] = {"Id": item_id, "price": 0, "tax": 0,"total":0,'name':name,'username':getdatauser.username}
            result_dict[item_id]["price"] += qty
            result_dict[item_id]["tax"] += ta
            result_dict[item_id]["total"] += aaaa

    result_list = list(result_dict.values())
    totalall = totalp - sumtax
      
    context = {'title': defaultTitle, 'data': obj,'result_dict':result_list,'start_new':start_new,'end_new':end_new,'start':start,'end':last_day,'sumtax':sumtax,'totalp':totalp,'totalall':totalall,'day_current_m':month_fomat(m),'year_current':year}

    return render(request, 'print/register_print_witdraw_overdue_print.html', context)    


def register_report_summary_print_overdue_one(request,teacher_id, year, m):

  
    obj = []
    list_teacher = teacher.objects.get(teacher_id=teacher_id,cancelled=1, active=1)

    end = None
    start_new = None
    end_new = None
    obj = []

    day_current_day = date.today().day
    
 
    bill = billing_cycle_setting.objects.get(id=2)
    start = bill.bcs_start_day
    get_last_day = last_day_of_month(
            datetime.date(int(year), int(m), 1))
    last_day = get_last_day.day


    content = teacher_income_setting.objects.select_related('ev').filter(status='S',active=0,tis_start_date__day__gte=start,teacher_id=teacher_id,
                tis_end_date__day__lte=last_day,
                tis_end_date__month=m,
                tis_end_date__year=year).order_by('teacher_id')
    
    uuid_without_dashes = str(teacher_id).replace('-', '')
    factuser = fact_teacher_user.objects.get(teacher_id=uuid_without_dashes)
    getdatauser = User.objects.get(pk=factuser.user_id)
    requirements = 'ไม่มี'
    name_con = '-'
    totalp = 0
    sumtax = 0
    total = 0
    totalall = 0
    for rs in content:
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
             
             if select != 0:
              
              totalselect = condition.objects.get(condition_id=select)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              checkcourse_con = course.objects.get(course_id=head.course.course_id)
              
    
              if checkcourse_con.is_type_condition == '1':
                 price = int(rs.tis_quantity) * (totalselect.price)
                 name_con = head.name
                 tis_compensation = totalselect.price
              else:   
                 
                 if totalselect.action == '1':
                    tis_quantity = int(rs.tis_quantity) + int(totalselect.hour)
                    price = int(rs.tis_compensation) * (tis_quantity)
                    tis_compensation = rs.tis_compensation
                    name_con = head.name
                 else :
                    price = int(rs.tis_quantity) * (totalselect.price)
                    name_con = head.name
                    tis_compensation = totalselect.price
             else:
                
                price = int(rs.tis_quantity) * (rs.tis_compensation)  
                name_con = '-'
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
          
             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot

            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)

            totalp += price
         
            taxall = price * (rs.tax / 100)
            sumtax += taxall
            total = price - taxall
            totalall += total
            r = {'pay_name':pay.pi_name,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation,'tax':taxall,'total':total}
        
            obj.append(r)
    today = datetime.date.today()
    us_format = today.strftime("%d/%m/%Y")


    context = {'title': defaultTitle, 'data': obj,'list_teacher':list_teacher,'cou':content.count(),'totalp':totalp,'getdatauser':getdatauser,'m':month_fomat(m),'year':year,
             'start_new':start,'end_new':last_day,'sumtax':sumtax,'totalall':totalall,'today':us_format}
    return render(request, 'print/register_print_overdue_one.html',context)


@login_required(login_url='/login')
def register_report_summary_print(request, start, end):


  
   

    start_new = None
    end_new = None
    obj = []
    #   start, end = format_daterange(date_range)
    #     start_new ,end_new = format_daterange_new(date_range)

    
    content = teacher_income_setting.objects.select_related('ev').filter(status='S',ev__ev_date_start__gte=start,ev__ev_date_end__lte=end).order_by('teacher_id')
    requirements = 'ไม่มี'
    name_con = '-'
    totalp = 0
    sumtax = 0
    totalall = 0
    for rs in content:
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
             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,status='I',pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot 
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)

            totalp += price
         
            taxall = price * (rs.tax / 100)
            sumtax += taxall
           
            r = {'teacher':rs.teacher_id,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation,'tax':taxall}
        
            obj.append(r)   


 

    result_dict = {}
    for item in obj:
            teacher_one = teacher.objects.get(teacher_id=item["teacher"])
            uuid_without_dashes = str(item["teacher"]).replace('-', '')
            factuser = fact_teacher_user.objects.get(teacher_id=uuid_without_dashes)
            getdatauser = User.objects.get(pk=factuser.user_id)
            item_id = item["teacher"]
            name = teacher_one
            qty = item["price"]
            ta = item["tax"]
         
            total = item["price"] -item["tax"]
            aaaa = total

            if item_id not in result_dict:
                result_dict[item_id] = {"Id": item_id, "price": 0, "tax": 0,"total":0,'name':name,'username':getdatauser.username}
            result_dict[item_id]["price"] += qty
            result_dict[item_id]["tax"] += ta
            result_dict[item_id]["total"] += aaaa

    result_list = list(result_dict.values())
    totalall = totalp - sumtax
    
    context = {'title': defaultTitle, 'data': obj,'result_dict':result_list,'start_new':start_new,'end_new':end_new,'start':start,'end':end,'sumtax':sumtax,'totalp':totalp,'totalall':totalall}
  
    return render(request, 'print/register_print_witdraw_summary_print.html', context)    




@login_required(login_url='/login')
def register_report_summary_teacher_all(request ,teacher_id, year, m):

    month_select_now = request.POST.get('monthss', m)
    
    m_n = month_select_now
    m_l = int(month_select_now) - 1


    obj = []

    get_last_day = last_day_of_month(
            datetime.date(int(year), int(m), 1))
    last_day = get_last_day.day
    default_start = str(year) + "-" + \
        str(m_l) + "-" + "21"
    default_end = str(year) + "-" + \
        str(m_n) + "-" + "20"
    
  
    get_last_day_m = last_day_of_month(
            datetime.date(int(year), m_l, 1))
    last_day_m = get_last_day_m.day
   
    tis_group_l = f"21 - {last_day_m}"
    tis_group_f = "1 - 20"


    day_current_day = date.today().day
    today = datetime.date.today()
    us_format = today.strftime("%d/%m/%Y")

    
    customer_order_counts = teacher_income_setting.objects.filter(status='S',tis_end_date__gte=default_start,tis_end_date__lte=default_end,teacher=teacher_id)
    price = 0
    totalp = 0
    totalp_f = 0
    sumtaxall = 0
    sumtaxl = 0
    sumtaxf = 0
    totalall = 0
    name_con = '-'
    for rs in customer_order_counts:
            
            price_te_f = 0
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
            tis_compensation = 0
            if int(event.condition_type) == 1:
                requirements = 'มี'
            if int(rs.pi_id) == 1:
             if event.condition_type == '1':  # เช็คว่า วิทยากร มีเงื่อนไขไหม
                
                checkcourse = condition.objects.filter(conhead=event.condition_id).first() 
                checkhead = conhead.objects.filter(conhead_id=checkcourse.conhead_id).first() 
                checkcourse_con = course.objects.get(course_id=checkhead.course_id)
          
                if checkcourse_con.is_type_condition == '1':
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('student')
                   for iconts in icont:
                      typet = iconts.type
                      if iconts.type_add == '1': 
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

                else : 
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('action')
                   for iconts in icont:
                     if iconts.action == '0': 
                        
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='2').order_by('student')
                     elif iconts.action == '1':  
                         
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='1').order_by('-student')
                     for checkcons in checkcon:
                        if total_rq_quta > checkcons.student:
                            select = checkcons.condition_id
                            
                            break
                        else:
                           select = 0
           
             
             if select != 0:
              totalselect = condition.objects.get(condition_id=select)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              checkcourse_con = course.objects.get(course_id=checkhead.course_id)
              if checkcourse_con.is_type_condition == '1':
                 price = int(rs.tis_quantity) * (totalselect.price)
                 name_con = head.name
                 tis_compensation = totalselect.price
              else:   
                 if totalselect.action == '1':
                    tis_quantity = int(rs.tis_quantity) + int(totalselect.hour)
                    price = int(rs.tis_compensation) * (tis_quantity)
                    tis_compensation = rs.tis_compensation
                    name_con = head.name
                 else :
                    price = int(rs.tis_quantity) * (totalselect.price)
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
              

             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot

             elif int(rs.pi_id) == 7:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=7).count()
              all = 1000 
              price = rs.tis_compensation
              tis_compensation =  rs.tis_compensation

             elif int(rs.pi_id) == 8:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=7).count()
              all = 1000 
              price = rs.tis_compensation
              tis_compensation =  rs.tis_compensation 
           
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)
            
            totalp += price
            

            taxall = price * (rs.tax / 100)
            price_te = price - taxall
            sumtaxl += taxall
            totalall = totalp - sumtaxl
           
            print(rs.ev_id)
            print(event.ev_date_start)
            print(event.ev_date_end)
           
   
            r = {'teacher':rs.teacher_id,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'name_con':name_con,'tis_compensation':tis_compensation,'tax':taxall,'totalall':price_te}
           
            obj.append(r)   

       
        
    teacher_one = teacher.objects.get(teacher_id=teacher_id)
    uuid_without_dashes = str(teacher_id).replace('-', '')
    factuser = fact_teacher_user.objects.get(teacher_id=uuid_without_dashes)
    getdatauser = User.objects.get(pk=factuser.user_id)

    
    factsignature = fact_signature.objects.select_related('user').filter(user_id=factuser.user_id).first()
    sure = signature.objects.filter(image_id=factsignature.fact_id).first()

    mage = signature.objects.filter(image_id=3).first()
    gm = signature.objects.filter(image_id=5).first()
 
    signa = ''
    if sure:
       signa = sure
    
    context = {'title': defaultTitle, 'data': obj,'tis_group_f':tis_group_f,'tis_group_l':tis_group_l,'old_m':month_fomat(m_l),'current_m':month_fomat(m_n),'year_current':year,'m':m_n,'totalp':totalp,'totalall':totalall,'sumtax':sumtaxl,'teacher':teacher_one,'code':getdatauser,'today':us_format,'signature':signa,'factsignature':factsignature,'mage':mage,'gm':gm}
    return render(request, 'print/register_print_witdrawa_one_lasted.html',context)


@login_required(login_url='/login')
def register_report_summary_teacher_all_month(request , year, m):

    month_select_now = request.POST.get('monthss', date.today().month)
    
 
    m_n = m
    m_l = int(m) - 1
 
    day_same_m = request.POST.get('monthss', date.today().month)
 
    day_current_m = request.POST.get('monthss', date.today().month - 1)

    year_current = request.GET.get('qyear', date.today().year)
    
    start = None
    end = None
    start_new = None
    end_new = None
    obj = []
    t_a_all_tax = 0
    t_a_f = 0
    t_a_l = 0
    t_a_before_tax = 0
    t_a_t_tax = 0
    get_last_day = last_day_of_month(
            datetime.date(int(year), int(m), 1))
    last_day = get_last_day.day
    default_start = str(year) + "-" + \
        str(m_l) + "-" + "21"
    default_end = str(year) + "-" + \
        str(m_n) + "-" + "20"


    get_last_day_m = last_day_of_month(
            datetime.date(int(year_current), m_l, 1))
    last_day_m = get_last_day_m.day
   
    tis_group_l = f"21 - {last_day_m}"
    tis_group_f = "1 - 20"
    


    day_current_day = date.today().day

  
    result_dict = {}
    customer_order_counts = teacher_income_setting.objects.filter(status='S',tis_end_date__gte=default_start,tis_end_date__lte=default_end).values('teacher').distinct()
    
   
    for customer_order in customer_order_counts:
        item_id = customer_order['teacher']
        teacher_one = teacher.objects.get(teacher_id=customer_order['teacher'])
        uuid_without_dashes = str(customer_order["teacher"]).replace('-', '')
        factuser = fact_teacher_user.objects.get(teacher_id=uuid_without_dashes)
        getdatauser = User.objects.get(pk=factuser.user_id)
        code = getdatauser
        name = teacher_one
        
        lassssst = teacher_income_setting.objects.filter(tis_group=tis_group_l,teacher=customer_order['teacher'],status='S',tis_end_date__gte=default_start,tis_end_date__lte=default_end)
        
        price = 0
        totalp = 0
        totalp_f = 0
        sumtaxall = 0
        sumtaxl = 0
        sumtaxf = 0
        totalall = 0
        for rs in lassssst:
            
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
            
           
            tis_compensation = 0
            if int(event.condition_type) == 1:
                requirements = 'มี'
            if int(rs.pi_id) == 1:
             if event.condition_type == '1':  # เช็คว่า วิทยากร มีเงื่อนไขไหม
                
                checkcourse = condition.objects.filter(conhead=event.condition_id).first() 
                checkhead = conhead.objects.filter(conhead_id=checkcourse.conhead_id).first() 
                checkcourse_con = course.objects.get(course_id=checkhead.course_id)
          
                if checkcourse_con.is_type_condition == '1':
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('student')
                   for iconts in icont:
                      typet = iconts.type
                      if iconts.type_add == '1': 
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

                else : 
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('action')
                   for iconts in icont:
                     if iconts.action == '0': 
                        
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='2').order_by('student')
                     elif iconts.action == '1':  
                         
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='1').order_by('-student')
                     for checkcons in checkcon:
                        if total_rq_quta > checkcons.student:
                            select = checkcons.condition_id
                            
                            break
                        else:
                           select = 0
           
             
             if select != 0:
              totalselect = condition.objects.get(condition_id=select)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              checkcourse_con = course.objects.get(course_id=checkhead.course_id)
              if checkcourse_con.is_type_condition == '1':
                 price = int(rs.tis_quantity) * (totalselect.price)
                 name_con = head.name
                 tis_compensation = totalselect.price
              else:   
                 if totalselect.action == '1':
                    tis_quantity = int(rs.tis_quantity) + int(totalselect.hour)
                    price = int(rs.tis_compensation) * (tis_quantity)
                    tis_compensation = rs.tis_compensation
                    name_con = head.name
                 else :
                    price = int(rs.tis_quantity) * (totalselect.price)
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

             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot
              
              
              price = int(rs.tis_quantity) * (rs.tis_compensation) 
              tis_compensation = rs.tis_compensation 
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)
            
            totalp += price
         
            taxall = price * (rs.tax / 100)
            sumtaxl += taxall
        first = teacher_income_setting.objects.filter(tis_group=tis_group_f,teacher=customer_order['teacher'],status='S',tis_end_date__gte=default_start,tis_end_date__lte=default_end)
       
        for rs in first:
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
                
                checkcourse = condition.objects.filter(conhead=event.condition_id).first() 
                checkhead = conhead.objects.filter(conhead_id=checkcourse.conhead_id).first() 
                checkcourse_con = course.objects.get(course_id=checkhead.course_id)
          
                if checkcourse_con.is_type_condition == '1':
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('student')
                   for iconts in icont:
                      typet = iconts.type
                      if iconts.type_add == '1': 
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

                else : 
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('action')
                   for iconts in icont:
                     if iconts.action == '0': 
                       
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='2').order_by('student')
                     elif iconts.action == '1':  
                       
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='1').order_by('-student')
                     for checkcons in checkcon:
                        if total_rq_quta > checkcons.student:
                            select = checkcons.condition_id
                            
                            break
                        else:
                           select = 0
           
             
             if select != 0:
              totalselect = condition.objects.get(condition_id=select)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              checkcourse_con = course.objects.get(course_id=checkhead.course_id)
              if checkcourse_con.is_type_condition == '1':
                 price = int(rs.tis_quantity) * (totalselect.price)
                 name_con = head.name
                 tis_compensation = totalselect.price
              else:   
                 if totalselect.action == '1':
                    tis_quantity = int(rs.tis_quantity) + int(totalselect.hour)
                    price = int(rs.tis_compensation) * (tis_quantity)
                    tis_compensation = rs.tis_compensation
                    name_con = head.name
                 else :
                    price = int(rs.tis_quantity) * (totalselect.price)
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
             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot
            
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)
            
            totalp_f += price
            taxall = price * (rs.tax / 100)
            sumtaxf += taxall

            
        if item_id not in result_dict:
                aa = totalp_f + totalp
                
                sumtaxall = sumtaxl + sumtaxf
                totalall = aa - sumtaxall
            
                t_a_all_tax += totalall
                t_a_f += totalp_f 
                t_a_l += totalp
                t_a_before_tax += aa
                t_a_t_tax += sumtaxall



                result_dict[item_id] = {"Id": item_id, "price": totalp,"price_f": totalp_f, "tax": sumtaxall,"total":aa,'username':name,'code':code,'totalall':totalall}   
            
    

    
    result_list = list(result_dict.values())
    context = {'title': defaultTitle, 'data': obj,'result_dict':result_list,'tis_group_f':tis_group_f,'tis_group_l':tis_group_l,'old_m':month_fomat(m_l),'current_m':month_fomat(m_n),'year_current':year_current,'m':m_n, 't_a_before_tax':t_a_before_tax,'t_a_all_tax':t_a_all_tax,'t_a_f':t_a_f,'t_a_l':t_a_l,'t_a_t_tax':t_a_t_tax}


    return render(request, 'print/register_print_witdraw_summary_print.html',context)
   
@login_required(login_url='/login')
def register_report_summary_teacher_withdraw(request):

    month_select_now = request.POST.get('monthss', date.today().month)
    
 
    m_n = month_select_now
    m_l = int(month_select_now) - 1
 
    day_same_m = request.POST.get('monthss', date.today().month)
 
    day_current_m = request.POST.get('monthss', date.today().month - 1)

    year_current = request.GET.get('qyear', date.today().year)
    
    start = None
    end = None
    start_new = None
    end_new = None
    obj = []

    get_last_day = last_day_of_month(
            datetime.date(int(year_current), int(day_current_m), 1))
    last_day = get_last_day.day
    default_start = str(date.today().year) + "-" + \
        str(m_l) + "-" + "21"
    default_end = str(date.today().year) + "-" + \
        str(m_n) + "-" + "20"
    

    get_last_day_m = last_day_of_month(
            datetime.date(int(year_current), m_l, 1))
    last_day_m = get_last_day_m.day
   
    tis_group_l = f"21 - {last_day_m}"
    tis_group_f = "1 - 20"
    


    day_current_day = date.today().day

  
    result_dict = {}
    customer_order_counts = teacher_income_setting.objects.filter(status='S',tis_end_date__gte=default_start,tis_end_date__lte=default_end).values('teacher').distinct()
    
    price = 0
    totalp = 0
    totalp_f = 0
    sumtaxall = 0
    sumtaxl = 0
    sumtaxf = 0
    totalall = 0

   
    for customer_order in customer_order_counts:
        item_id = customer_order['teacher']
        teacher_one = teacher.objects.get(teacher_id=customer_order['teacher'])
        uuid_without_dashes = str(customer_order["teacher"]).replace('-', '')
        factuser = fact_teacher_user.objects.get(teacher_id=uuid_without_dashes)
        getdatauser = User.objects.get(pk=factuser.user_id)
        code = getdatauser
        name = teacher_one
      
        lassssst = teacher_income_setting.objects.filter(tis_group=tis_group_l,teacher=customer_order['teacher'],status='S',tis_end_date__gte=default_start,tis_end_date__lte=default_end,active=0)
        
        price = 0
        totalp = 0
        totalp_f = 0
        sumtaxall = 0
        sumtaxl = 0
        sumtaxf = 0
        totalall = 0
        for rs in lassssst:
            print(rs)
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
            
            
            tis_compensation = 0
            if int(event.condition_type) == 1:
                requirements = 'มี'
            if int(rs.pi_id) == 1:
             if event.condition_type == '1':  # เช็คว่า วิทยากร มีเงื่อนไขไหม
                
                checkcourse = condition.objects.filter(conhead=event.condition_id).first() 
                checkhead = conhead.objects.filter(conhead_id=checkcourse.conhead_id).first() 
                checkcourse_con = course.objects.get(course_id=checkhead.course_id)
          
                if checkcourse_con.is_type_condition == '1':
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('student')
                   for iconts in icont:
                      typet = iconts.type
                      if iconts.type_add == '1': 
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

                else : 
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('action')
                   for iconts in icont:
                     if iconts.action == '0': 
                        
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='2').order_by('student')
                     elif iconts.action == '1':  
                         
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='1').order_by('-student')
                     for checkcons in checkcon:
                        if total_rq_quta > checkcons.student:
                            select = checkcons.condition_id
                            
                            break
                        else:
                           select = 0
           
             
             if select != 0:
              totalselect = condition.objects.get(condition_id=select)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              checkcourse_con = course.objects.get(course_id=checkhead.course_id)
              if checkcourse_con.is_type_condition == '1':
                 price = int(rs.tis_quantity) * (totalselect.price)
                 name_con = head.name
                 tis_compensation = totalselect.price
              else:   
                 if totalselect.action == '1':
                    tis_quantity = int(rs.tis_quantity) + int(totalselect.hour)
                    price = int(rs.tis_compensation) * (tis_quantity)
                    tis_compensation = rs.tis_compensation
                    name_con = head.name
                 else :
                    price = int(rs.tis_quantity) * (totalselect.price)
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

             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot

             elif int(rs.pi_id) == 7:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = rs.tis_compensation
              tis_compensation = rs.tis_compensation

             elif int(rs.pi_id) == 8:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = rs.tis_compensation
              tis_compensation = rs.tis_compensation
              
              
              price = int(rs.tis_quantity) * (rs.tis_compensation) 
              tis_compensation = rs.tis_compensation 
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)
            
            totalp += price

            
            
            
            taxall = price * (rs.tax / 100)
            sumtaxl += taxall
        first = teacher_income_setting.objects.filter(tis_group=tis_group_f,teacher=customer_order['teacher'],status='S',tis_end_date__gte=default_start,tis_end_date__lte=default_end,active=0)
       
        for rs in first:
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
                
                checkcourse = condition.objects.filter(conhead=event.condition_id).first() 
                checkhead = conhead.objects.filter(conhead_id=checkcourse.conhead_id).first() 
                checkcourse_con = course.objects.get(course_id=checkhead.course_id)
          
                if checkcourse_con.is_type_condition == '1':
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('student')
                   for iconts in icont:
                      typet = iconts.type
                      if iconts.type_add == '1': 
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

                else : 
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('action')
                   for iconts in icont:
                     if iconts.action == '0': 
                        print('เช็คลบก่อนน',iconts.action)
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='2').order_by('student')
                     elif iconts.action == '1':  
                        print('เช็คบวกที่หลัง',iconts.action) 
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='1').order_by('-student')
                     for checkcons in checkcon:
                        if total_rq_quta > checkcons.student:
                            select = checkcons.condition_id
                            
                            break
                        else:
                           select = 0
           
             
             if select != 0:
              totalselect = condition.objects.get(condition_id=select)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              checkcourse_con = course.objects.get(course_id=checkhead.course_id)
              if checkcourse_con.is_type_condition == '1':
                 price = int(rs.tis_quantity) * (totalselect.price)
                 name_con = head.name
                 tis_compensation = totalselect.price
              else:   
                 if totalselect.action == '1':
                    tis_quantity = int(rs.tis_quantity) + int(totalselect.hour)
                    price = int(rs.tis_compensation) * (tis_quantity)
                    tis_compensation = rs.tis_compensation
                    name_con = head.name
                 else :
                    price = int(rs.tis_quantity) * (totalselect.price)
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
             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot
             
             elif int(rs.pi_id) == 7:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = rs.tis_compensation
              tis_compensation = rs.tis_compensation

             elif int(rs.pi_id) == 8:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = rs.tis_compensation
              tis_compensation = rs.tis_compensation
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)
            
            totalp_f += price
            taxall = price * (rs.tax / 100)
            sumtaxf += taxall
        if item_id not in result_dict:
                aa = totalp_f + totalp
                sumtaxall = sumtaxl + sumtaxf
                totalall = aa - sumtaxall
                result_dict[item_id] = {"Id": item_id, "price": totalp,"price_f": totalp_f, "tax": sumtaxall,"total":aa,'username':name,'code':code,'totalall':totalall}   
            
    


    result_list = list(result_dict.values())
    context = {'title': defaultTitle, 'data': obj,'result_dict':result_list,'tis_group_f':tis_group_f,'tis_group_l':tis_group_l,'old_m':month_fomat(m_l),'current_m':month_fomat(m_n),'year_current':year_current,'m':m_n,'totalp_f':totalp_f}
  
    return render(request, 'print/report_withdraw_summary_teacher.html', context)   

@login_required(login_url='/login')
def register_report_summary_withdraw(request):

   
   
    day_current_m = request.POST.get('monthss', date.today().month - 1)
    year_current = request.GET.get('qyear', date.today().year)

    start = None
    end = None
    start_new = None
    end_new = None
    obj = []

    day_current_day = date.today().day
    
 
    bill = billing_cycle_setting.objects.get(id=2)
    start = bill.bcs_start_day
    get_last_day = last_day_of_month(
            datetime.date(int(year_current), int(day_current_m), 1))
    last_day = get_last_day.day
    

    content = teacher_income_setting.objects.select_related('ev').filter(status='S',active=0,tis_end_date__day__gte=start,
                tis_end_date__day__lte=last_day,
                tis_end_date__month=day_current_m,
                tis_end_date__year=year_current).order_by('teacher_id')
 
    requirements = 'ไม่มี'
    name_con = '-'
    totalp = 0
    sumtax = 0
    totalall = 0
    for rs in content:
            print(rs.tis_compensation)
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
                checkcourse = condition.objects.filter(conhead=event.condition_id).first() 
                checkhead = conhead.objects.filter(conhead_id=checkcourse.conhead_id).first() 
                checkcourse_con = course.objects.get(course_id=checkhead.course_id)
          
                if checkcourse_con.is_type_condition == '1':
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('student')
                   for iconts in icont:
                      typet = iconts.type
                      if iconts.type_add == '1': 
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

                else : 
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('action')
                   for iconts in icont:
                     if iconts.action == '0': 
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='2').order_by('student')
                     elif iconts.action == '1':  
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='1').order_by('-student')
                     for checkcons in checkcon:
                        if total_rq_quta > checkcons.student:
                            select = checkcons.condition_id
                            
                            break
                        else:
                           select = 0
           
             if select != 0:
              totalselect = condition.objects.get(condition_id=select)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              checkcourse_con = course.objects.get(course_id=checkhead.course_id)
              if checkcourse_con.is_type_condition == '1':
                 price = int(rs.tis_quantity) * (totalselect.price)
                 name_con = head.name
                 tis_compensation = totalselect.price
              else:   
                 if totalselect.action == '1':
                    tis_quantity = int(rs.tis_quantity) + int(totalselect.hour)
                    price = int(rs.tis_compensation) * (tis_quantity)
                    tis_compensation = rs.tis_compensation
                    name_con = head.name
                 else :
                    price = int(rs.tis_quantity) * (totalselect.price)
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
              
             elif int(rs.pi_id) == 5:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot
              
             elif int(rs.pi_id) == 7:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = rs.tis_compensation
              tis_compensation = rs.tis_compensation
            
             elif int(rs.pi_id) == 8:
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = rs.tis_compensation
              tis_compensation = rs.tis_compensation
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)
            
            totalp += price
         
            taxall = price * (rs.tax / 100)
            sumtax += taxall
           
           
            r = {'teacher':rs.teacher_id,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation,'tax':taxall}
        
            obj.append(r)   

    result_dict = {}
    for item in obj:
            teacher_one = teacher.objects.get(teacher_id=item["teacher"])
            uuid_without_dashes = str(item["teacher"]).replace('-', '')
            factuser = fact_teacher_user.objects.get(teacher_id=uuid_without_dashes)
            getdatauser = User.objects.get(pk=factuser.user_id)
            item_id = item["teacher"]
            name = teacher_one
            qty = item["price"]
            ta = item["tax"]
            total = item["price"] -item["tax"]
            aaaa = total
            if item_id not in result_dict:
                result_dict[item_id] = {"Id": item_id, "price": 0, "tax": 0,"total":0,'name':name,'username':getdatauser.username}
            result_dict[item_id]["price"] += qty
            result_dict[item_id]["tax"] += ta
            result_dict[item_id]["total"] += aaaa

    result_list = list(result_dict.values())
    totalall = totalp - sumtax
      

    context = {'title': defaultTitle, 'data': obj,'result_dict':result_list,'start_new':start_new,'end_new':end_new,'start':start,'end':last_day,'sumtax':sumtax,'totalp':totalp,'totalall':totalall,'day_current_m':month_fomat(day_current_m),'year_current':year_current,'m':day_current_m}
  
    return render(request, 'print/report_withdraw_summary.html', context)    


@login_required(login_url='/login')
def register_report_compensation_withdraw_onemorefitter(request):
   
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



    date_range = request.POST.get('date_range', None)
    
    start = None
    end = None
    start_new = None
    end_new = None

    lastday = lastDateOfmonth(
        date.today().year, date.today().month, date.today().day)
    default_start = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + "01"
    default_end = str(date.today().year) + "-" + \
        str(date.today().month) + "-" + str(lastday)
    try:
        getteachid = fact_teacher_user.objects.get(user_id=user_id)
        obj = []
        pi = ['1','2','3','4','5']
        totalp = 0
        content = teacher_income_setting.objects.filter(teacher_id=getteachid.teacher_id,status='S',pi_id__in=pi)

        if date_range is not None:
         start, end = format_daterange(date_range)
         start_new = ymdtodmy_new(start)
         end_new = ymdtodmy_new(end)
         
         if start == end:
            content = content.filter(tis_start_date__gte=start)
         else:
            content = content.filter(tis_start_date__gte=start,tis_end_date__lte=end)     
        else:
            print('else')
            content = content.filter(tis_start_date__gte=default_start,tis_end_date__lte=default_end)
            start_new = ymdtodmy_new(default_start)
            end_new = ymdtodmy_new(default_end)
        
        name_con = '-'
        for rs in content:
            requirements = 'ไม่มี'
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
                
                checkcourse = condition.objects.filter(conhead=event.condition_id).first() 
                checkhead = conhead.objects.filter(conhead_id=checkcourse.conhead_id).first() 
                checkcourse_con = course.objects.get(course_id=checkhead.course_id)
          
                if checkcourse_con.is_type_condition == '1':
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('student')
                   for iconts in icont:
                      typet = iconts.type
                      if iconts.type_add == '1': 
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

                else : 
                   icont = condition.objects.filter(conhead=event.condition_id).order_by('action')
                   for iconts in icont:
                     if iconts.action == '0': 
                        print('เช็คลบก่อนน',iconts.action)
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='2').order_by('student')
                     elif iconts.action == '1':  
                        print('เช็คบวกที่หลัง',iconts.action) 
                        checkcon = condition.objects.filter(conhead=event.condition_id,action='1').order_by('-student')
                     for checkcons in checkcon:
                        if total_rq_quta > checkcons.student:
                            select = checkcons.condition_id
                            
                            break
                        else:
                           select = 0
                          
             if select != 0:
              
              totalselect = condition.objects.get(condition_id=select)
              head =  conhead.objects.get(conhead_id=totalselect.conhead.conhead_id)
              checkcourse_con = course.objects.get(course_id=checkhead.course_id)
              if checkcourse_con.is_type_condition == '1':
                 
                 price = int(rs.tis_quantity) * (totalselect.price)
                 name_con = head.name
                 tis_compensation = totalselect.price
              else:   
                 
                 if totalselect.action == '1':
                    tis_quantity = int(rs.tis_quantity) + int(totalselect.hour)
                    price = int(rs.tis_compensation) * (tis_quantity)
                    tis_compensation = rs.tis_compensation
                    name_con = head.name
                    
                 else :
                    price = int(rs.tis_quantity) * (totalselect.price)
                    name_con = head.name
                    tis_compensation = totalselect.price
                    


             else:
                
                price = int(rs.tis_quantity) * (rs.tis_compensation)  
                name_con = '-'
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
             elif int(rs.pi_id) == 5:
              
              tot = teacher_income_setting.objects.filter(ev_id=rs.ev,pi=5).count()
              all = 1000 
              price = all / tot
              tis_compensation = all / tot
          
              
            cours = course.objects.get(course_id=event.course_id)
            pay = pay_item.objects.get(id=rs.pi_id)
         
            
            start = str(event.ev_date_start)
          
            end = str(event.ev_date_end)
            y, m, d = end.split("-")
            Y, mM, dD = start.split("-")
            day_of_week = event.ev_date_start.weekday()
           
           
            if day_of_week:
             
             try:
                
                if day_of_week == 0:
                    dt = "จ"
                elif day_of_week == 1: 
                    dt = "อ"  
                elif day_of_week == 2:
                    dt = "พ"  
                elif day_of_week == 3: 
                    dt = "พฤ" 
                elif day_of_week == 4: 
                    dt = "ศ"
                elif day_of_week == 5:
                    dt = "ส"
                elif day_of_week == 6:   
                    dt = "อา"           
             except ValueError:
                dt = "-"
            else:
             dt = "จ"
            
            totalp += price
            
            r = {'daynum':dD,'day':dt,'pay_name':pay.pi_name,'ev_date_start':event.ev_date_start,'ev_date_end':event.ev_date_end,'ev_generation':event.ev_generation,'pi':pay.pi_name,'course_code':cours.course_code,'course_name':cours.course_name,'tis_sum':rs.tis_sum,'tis_unit':rs.tis_unit,'tis_quantity':rs.tis_quantity,'tis_compensation':rs.tis_compensation,'total_rq_quta':total_rq_quta,'price':price,'requirements':requirements,'name_con':name_con,'tis_compensation':tis_compensation}
        
            obj.append(r)

          
        context = {'title': defaultTitle, 'listMenuPermission': objMenu,'data':obj,'total_all':totalp,'user_id':user_id,'start_new':start_new,'end_new':end_new}
    except fact_teacher_user.DoesNotExist:
        getteachid = None
        return redirect("/")
    

    return render(request, 'print/report_withdraw_one.html', context)    

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
        cus = fact_customer.objects.filter(register=r.register_id).first()
        customer_list = customers.objects.filter(
            customer_id=cus.customer_id).select_related('location').first()
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

   
  
    total = 0.0  # Initialize to 0.0
    for r in queryset:
        if r['result'] is not None:
            total += r['result']
        

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


@login_required(login_url='/login')
def print_consent(request,training_id):
   
    getid = training.objects.select_related("ev").get(training_id=training_id)
  
    content = []
    context = {'title': defaultTitle,  'data': getid}
    return render(request, 'print/register_print_consent.html', context)



@login_required(login_url='/login')
def register_report_summary_com(request):
    user_id = request.user.id
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    path = request.path
    cleaned_path = path.strip('/')    
    checkpa = checkpermi(cleaned_path,cm_id)
    if checkpa == 0:
        return render(request, '403.html')     
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
    obj = []
    day_current_m = date.today().month - 1
  
    context = {'title': defaultTitle, 'data': obj,'listMenuPermission': objMenu,'thai_months': THAI_MONTH_NAMES,'current_month':day_current_m}
    return render(request, 'report/billing_cycle_result_summary_overdue_com.html', context) 


@login_required(login_url='/login')
def register_report_summary_sale_com(request):
    user_id = request.user.id
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0

    path = request.path
    cleaned_path = path.strip('/')    
    checkpa = checkpermi(cleaned_path,cm_id)
    if checkpa == 0:
        return render(request, '403.html')    
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
    obj = []
    day_current_m = date.today().month
  
    context = {'title': defaultTitle, 'data': obj,'listMenuPermission': objMenu,'thai_months': THAI_MONTH_NAMES,'current_month':day_current_m}
    return render(request, 'report/billing_cycle_result_summary_withdraw_com.html', context) 


@login_required(login_url='/login')
def register_report_summary_sale_com_one(request):
    user_id = request.user.id
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
    obj = []
    day_current_m = date.today().month
  
    context = {'title': defaultTitle, 'data': obj,'listMenuPermission': objMenu,'thai_months': THAI_MONTH_NAMES,'current_month':day_current_m}
    return render(request, 'report/billing_cycle_result_summary_withdraw_com_one.html', context) 



@login_required(login_url='/login')
def register_report_summary_user_withdraw_com(request):

    month_select_now = request.POST.get('monthss', date.today().month)
    
 
    m_n = month_select_now
    m_l = int(month_select_now) - 1
 
    day_same_m = request.POST.get('monthss', date.today().month)
 
    day_current_m = request.POST.get('monthss', date.today().month - 1)

    year_current = request.GET.get('qyear', date.today().year)
    
    start = None
    end = None
    start_new = None
    end_new = None
    obj = []

    

    get_last_day = last_day_of_month(
            datetime.date(int(year_current), int(day_current_m), 1))
    last_day = get_last_day.day
    default_start = str(date.today().year) + "-" + \
        str(m_l) + "-" + "21"
    default_end = str(date.today().year) + "-" + \
        str(m_n) + "-" + "20"
    

    get_last_day_m = last_day_of_month(
            datetime.date(int(year_current), m_l, 1))
    last_day_m = get_last_day_m.day
   
    tis_group_l = f"21 - {last_day_m}"
    tis_group_f = "1 - 20"
    


    day_current_day = date.today().day

  
    result_dict = {}
    customer_order_counts = com_income_setting.objects.filter(status='S').values('user_id').distinct()
    
    
    price = 0
    totalp = 0
    totalp_f = 0
    sumtaxall = 0
    sumtaxl = 0
    sumtaxf = 0
    totalall = 0

   
    for customer_order in customer_order_counts:
        item_id = customer_order['user_id']
    
        getdatauser = User.objects.get(pk=item_id)
        code = getdatauser
        name = getdatauser.first_name + '' + getdatauser.last_name
   
        
        lassssst = com_income_setting.objects.filter(tis_group=tis_group_l,user_id=item_id,status='S',tis_start_date__gte=default_start,tis_start_date__lte=default_end,active=0)
  
        price = 0
        totalp = 0
        totalp_f = 0
        sumtaxall = 0
        sumtaxl = 0
        sumtaxf = 0
        totalall = 0
        for rs in lassssst:
            totalp += rs.tis_com_before_tax
            sumtaxl += rs.tis_com_before_tax - rs.tis_com_after_tax
          
        first = com_income_setting.objects.filter(tis_group=tis_group_f,user_id=item_id,status='S',tis_start_date__gte=default_start,tis_start_date__lte=default_end,active=0)

        for rsf in first:
           
           totalp_f += rsf.tis_com_before_tax
           sumtaxf += rsf.tis_com_before_tax - rsf.tis_com_after_tax
           
        if item_id not in result_dict:
                aa = totalp_f + totalp
                sumtaxall = sumtaxl + sumtaxf
                
                totalall = aa - sumtaxall
                result_dict[item_id] = {"Id": item_id, "price": totalp,"price_f": totalp_f, "tax": sumtaxall,"total":aa,'username':name,'code':code,'totalall':totalall}   
            
    result_list = list(result_dict.values())
    context = {'title': defaultTitle, 'data': obj,'result_dict':result_list,'tis_group_f':tis_group_f,'tis_group_l':tis_group_l,'old_m':month_fomat(m_l),'current_m':month_fomat(m_n),'year_current':year_current,'m':m_n,'totalp_f':totalp_f}
  
    return render(request, 'print/report_withdraw_summary_commission.html', context)   




@login_required(login_url='/login')
def register_report_summary_user_withdraw_com_one(request):
    user_id = request.user.id
   
    month_select_now = request.POST.get('monthss', date.today().month)
    
 
    m_n = month_select_now
    m_l = int(month_select_now) - 1
 
    day_same_m = request.POST.get('monthss', date.today().month)
 
    day_current_m = request.POST.get('monthss', date.today().month - 1)

    year_current = request.GET.get('qyear', date.today().year)
    
    start = None
    end = None
    start_new = None
    end_new = None
    obj = []

    

    get_last_day = last_day_of_month(
            datetime.date(int(year_current), int(day_current_m), 1))
    last_day = get_last_day.day
    default_start = str(date.today().year) + "-" + \
        str(m_l) + "-" + "21"
    default_end = str(date.today().year) + "-" + \
        str(m_n) + "-" + "20"
    

    get_last_day_m = last_day_of_month(
            datetime.date(int(year_current), m_l, 1))
    last_day_m = get_last_day_m.day
   
    tis_group_l = f"21 - {last_day_m}"
    tis_group_f = "1 - 20"
    


    day_current_day = date.today().day

  
    result_dict = {}
    customer_order_counts = com_income_setting.objects.filter(status='S',user_id=user_id).values('user_id')
    
    
    price = 0
    totalp = 0
    totalp_f = 0
    sumtaxall = 0
    sumtaxl = 0
    sumtaxf = 0
    totalall = 0

   
    for customer_order in customer_order_counts:
        item_id = customer_order['user_id']
    
        getdatauser = User.objects.get(pk=item_id)
        code = getdatauser
        name = getdatauser.first_name + '' + getdatauser.last_name
   
        
        lassssst = com_income_setting.objects.filter(tis_group=tis_group_l,user_id=item_id,status='S',tis_start_date__gte=default_start,tis_start_date__lte=default_end,active=0)
  
        price = 0
        totalp = 0
        totalp_f = 0
        sumtaxall = 0
        sumtaxl = 0
        sumtaxf = 0
        totalall = 0
        for rs in lassssst:
            totalp += rs.tis_com_before_tax
            sumtaxl += rs.tis_com_before_tax - rs.tis_com_after_tax
          
        first = com_income_setting.objects.filter(tis_group=tis_group_f,user_id=item_id,status='S',tis_start_date__gte=default_start,tis_start_date__lte=default_end,active=0)

        for rsf in first:
           
           totalp_f += rsf.tis_com_before_tax
           sumtaxf += rsf.tis_com_before_tax - rsf.tis_com_after_tax
           
        if item_id not in result_dict:
                aa = totalp_f + totalp
                sumtaxall = sumtaxl + sumtaxf
                
                totalall = aa - sumtaxall
                result_dict[item_id] = {"Id": item_id, "price": totalp,"price_f": totalp_f, "tax": sumtaxall,"total":aa,'username':name,'code':code,'totalall':totalall}   
            
    result_list = list(result_dict.values())
    context = {'title': defaultTitle, 'data': obj,'result_dict':result_list,'tis_group_f':tis_group_f,'tis_group_l':tis_group_l,'old_m':month_fomat(m_l),'current_m':month_fomat(m_n),'year_current':year_current,'m':m_n,'totalp_f':totalp_f}
  
    return render(request, 'print/report_withdraw_summary_commission_one.html', context)   


@login_required(login_url='/login')
def register_report_summary_user_withdraw_com_overdue(request):

   
    day_current_m = request.POST.get('monthss', date.today().month - 1)
    year_current = request.GET.get('qyear', date.today().year)

    start = None
    end = None
    start_new = None
    end_new = None
    obj = []

    day_current_day = date.today().day
    
 
    bill = billing_cycle_setting.objects.get(id=2)
    start = bill.bcs_start_day
    get_last_day = last_day_of_month(
            datetime.date(int(year_current), int(day_current_m), 1))
    last_day = get_last_day.day


    

    content = com_income_setting.objects.filter(status='S',active=0,tis_start_date__day__gte=start,
                tis_start_date__day__lte=last_day,
                tis_start_date__month=day_current_m,
                tis_start_date__year=year_current)
    
    requirements = 'ไม่มี'
    name_con = '-'
    totalp = 0
    sumtax = 0
    totalall = 0
    for rs in content:
            
    
        
            
            sumtax += rs.tis_com_before_tax - rs.tis_com_after_tax
           
           
            r = {'user_id':rs.user_id,'totalp':rs.tis_com_before_tax,'sumtax':sumtax}
          
            obj.append(r)   

    result_dict = {}
    for item in obj:
          
   
            getdatauser = User.objects.get(pk=item["user_id"])
            item_id = item["user_id"]
            name = getdatauser.first_name + ' ' + getdatauser.last_name
            qty = item["totalp"]
            ta = item["sumtax"]
            total = item["totalp"] -item["sumtax"]
            aaaa = total
            if item_id not in result_dict:
                result_dict[item_id] = {"Id": item_id, "totalp": 0, "sumtax": 0,"total":0,'name':name,'username':getdatauser.username}
            result_dict[item_id]["totalp"] += qty
            result_dict[item_id]["sumtax"] += ta
            result_dict[item_id]["total"] += aaaa
            

    result_list = list(result_dict.values())
    totalall = totalp - sumtax
      

    context = {'title': defaultTitle, 'data': obj,'result_dict':result_list,'start_new':start_new,'end_new':end_new,'start':start,'end':last_day,'sumtax':sumtax,'totalp':totalp,'totalall':totalall,'day_current_m':month_fomat(day_current_m),'year_current':year_current,'m':day_current_m}
  
    return render(request, 'print/report_withdraw_summary_overdue_com.html', context)    



@login_required(login_url='/login')
def register_excel_seller_ev(request,ev_id):
    user_id = request.user.id
    
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    



    



    status = ['FullPayment','Completed']
    content = register_main.objects.filter(status='Y',ev_id=ev_id,orderstatus__in=status).order_by("crt_date")
    
    obj = []
    total_sum = 0
    
    for r in content:
        
        payment_list = register_payment_items.objects.select_related('rp','register').filter(register__register_id=r.register_id,type_payment='FullPayment').order_by("-rp__rp_id").first()
        cus = fact_customer.objects.get(register_id=r.register_id)
        
        customer = customers.objects.get(customer_id=cus.customer_id)
        course_list = course.objects.get(course_id=r.course.course_id)
        
        res = {'payment_list':payment_list,'customer_list':customer,'course_list':course_list}
        obj.append(res)

    context = {'title': defaultTitle, 'data': obj}
    return render(request, 'print/register_excel_seller_complate.html', context)


@login_required(login_url='/login')
def register_excel_seller_evover(request,ev_id):
    user_id = request.user.id
    
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    

    status = ['Deposit']
    content = register_main.objects.filter(status='Y',ev_id=ev_id,orderstatus='Deposit').order_by("crt_date")
   
    obj = []
    total_sum = 0
    
    for r in content:
       
        payment_list = register_payment_items.objects.select_related('rp','register').filter(register__register_id=r.register_id,type_payment='Deposit').order_by("-rp__rp_id").first()
        cus = fact_customer.objects.get(register_id=r.register_id)
        customer = customers.objects.get(customer_id=cus.customer_id)
        course_list = course.objects.get(course_id=r.course.course_id)
        
        res = {'payment_list':payment_list,'customer_list':customer,'course_list':course_list}
        obj.append(res)

    context = {'title': defaultTitle, 'data': obj}
    return render(request, 'print/register_excel_seller_over.html', context)
