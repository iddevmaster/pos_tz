from datetime import date
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Value
from django.db.models.functions import TruncMonth
from ..models import category_program_permission, course, course_event, teacher_income_setting, billing_cycle_setting, user_group, user_detail, desciption_bill,tax_setting,bill_setting,certificate_setting,commissionstages,location_thai,pay_item,register_main,customers,register_payment,register_payment_items,fact_commission,commissionstages,User,fact_customer,com_head,notifications,training
from ..constant import defaultTitle, thai_months,unitPayChoices
from ..functions import dateTimeNow, last_day_of_month,checkpermi
from ..forms.finance_form import billing_cycle_setting_form
from ..forms.teacher_form import teacherIncomeSettingForm
from django.http import JsonResponse
import json
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Coalesce


@login_required(login_url='/login')
def setting_form_create(request):
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
       
        name = request.POST['name']
        last_entry = desciption_bill.objects.order_by('-seq').first()
        
        content = desciption_bill(
        name=name,
        seq=last_entry.seq + 1,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow())
        content.save()
        messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/description/setting/form/create")

    desciption = desciption_bill.objects.all().order_by('seq')
    context = {'title': defaultTitle,  'data': desciption, 'listMenuPermission': objMenu}
            
    return render(request, 'settingdes/setting_form_create.html', context)




def setting_form_bill(request):
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
 
    bill = bill_setting.objects.get(bill_id=1)



    context = {'title': defaultTitle, 'listMenuPermission': objMenu,'bill_id':bill.bill_id,'is_show_signature':bill.is_show_signature}
            
    return render(request, 'settingdes/bill_form_create.html', context)


@login_required(login_url='/login')
def setting_form_certificate(request):
    user_id = request.user.id
    try:
        cm_id = user_detail.objects.get(user_id=user_id).cm_id
    except user_detail.DoesNotExist:
        cm_id = 0

    cleaned_path = request.path.strip('/')
    if checkpermi(cleaned_path, cm_id) == 0:
        return render(request, '403.html', status=403)

    list_menu_permission = category_program_permission.objects.filter(
        cm_id=cm_id
    ).values('group_value', 'group_label').annotate(
        dcount=Count('group_value')
    ).order_by('group_label')
    obj_menu = []
    for menu_group in list_menu_permission:
        children = category_program_permission.objects.filter(
            cm_id=cm_id,
            group_value=menu_group['group_value'],
        ).order_by('page_label')
        obj_menu.append({
            'group_label': menu_group['group_label'],
            'group_value': menu_group['group_value'],
            'children': children,
        })

    setting, _ = certificate_setting.objects.get_or_create(
        certificate_setting_id=1,
        defaults={'template_type': 1},
    )

    if request.method == 'POST':
        for field in ('template_type', 'template_type_eng'):
            try:
                value = int(request.POST.get(field, 1))
            except (TypeError, ValueError):
                value = 1
            setattr(setting, field, value if value in (1, 2) else 1)
        setting.save(update_fields=['template_type', 'template_type_eng'])
        messages.success(request, 'บันทึกการตั้งค่าใบเซอร์เรียบร้อยแล้ว')
        return redirect('certificate_setting_form')

    context = {
        'title': defaultTitle,
        'template_type': setting.template_type,
        'template_type_eng': setting.template_type_eng,
        'listMenuPermission': obj_menu,
    }
    return render(request, 'settingdes/certificate_form_create.html', context)


def setting_form_tax(request):
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
 
    tax = tax_setting.objects.get(tax_id=1)

    

    context = {'title': defaultTitle, 'listMenuPermission': objMenu,'tax_id':tax.tax_id,'tax':tax.tax,'tax_com':tax.tax_com}
            
    return render(request, 'settingdes/tax_form_create.html', context)


@csrf_exempt
def savetax(request):
    data = json.loads(request.body)
    tax_id = data.get("tax_id")
    taxu = data.get("tax")
    tax_com = data.get("tax_com")

    fields = {'tax': taxu}
    if tax_com not in (None, ''):
        fields['tax_com'] = tax_com
    tax_setting.objects.filter(tax_id=tax_id).update(**fields)
    datas = {'status':'200'}
    return JsonResponse(data,safe=False)

@csrf_exempt
def savesettingbill(request):
    data = json.loads(request.body)
    bill_id = data.get("bill_id")
    sign = data.get("is_show_signature")

  
    bill_setting.objects.filter(bill_id=bill_id).update(is_show_signature=sign)
    datas = {'status':'200'}
    return JsonResponse(data,safe=False)


def setting_form_delete(request):

    id = request.POST['id']     
   
    instance = desciption_bill.objects.get(seq=id)
    instance.delete()
    desciption = desciption_bill.objects.all().order_by('seq')  
    t = 0
    for desciptions in desciption:
        t += 1
        desciptions.seq = t
        desciptions.save()
        
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/description/setting/form/create")




def setting_form_update(request):


    des_id = request.POST['des_id']
    name = request.POST['name']
    content = desciption_bill.objects.get(des_id=des_id)
    content.name = name
    content.save()

    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/description/setting/form/create")


@csrf_exempt
def up(request):
    data = json.loads(request.body)
    ids = int(data.get("id"))
    x = int(data.get("id")) - 1

    a = desciption_bill.objects.get(seq=ids)
    b = desciption_bill.objects.get(seq=x)
   
    a.seq = a.seq - 1
    a.save()


    b.seq = b.seq + 1
    b.save()


    datas = {'status':'200'}
    return JsonResponse(datas,safe=False)

@csrf_exempt
def down(request):    
    data = json.loads(request.body)
    ids = int(data.get("id"))
    x = int(data.get("id")) + 1

    a = desciption_bill.objects.get(seq=ids)
    b = desciption_bill.objects.get(seq=x)
   
    a.seq = a.seq + 1
    a.save()


    b.seq = b.seq - 1
    b.save()


    datas = {'status':'200'}
    return JsonResponse(datas,safe=False)


@login_required(login_url='/login')
def setting_form_commissionstages(request):
    user_id = request.user.id
    id = request.GET.get('com_id')

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
 

    ciom = commissionstages.objects.filter(com_head_id=id).order_by('seq') 
    head = com_head.objects.all()

  

    context = {'title': defaultTitle, 'listMenuPermission': objMenu,'data':ciom,'head':head}
            
    return render(request, 'settingdes/setting_com_form_create.html', context)
    

@login_required(login_url='/login')
def setting_form_commissionstages_create(request):
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
       
        name = request.POST['stage_name']
        description = request.POST['stage_description']
        
     
        commission_ra = request.POST.get('commission_rate')
        com_ids = request.POST.get('com_ids')
        cu = commissionstages.objects.filter(com_head_id=com_ids).count()
       
        if cu == 0:
            se = 1
        else :  
            last_entry = commissionstages.objects.filter(com_head_id=com_ids).order_by('-seq').first()  
            se = last_entry.seq + 1
   
        


        
        content = commissionstages(
        stage_name=name,
        commission_rate=commission_ra,
        seq=se,
        stage_description=description,
        com_head_id=com_ids,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow())
        content.save()
        messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/commissionstages/setting/form")

    desciption = commissionstages.objects.all().order_by('seq')
    context = {'title': defaultTitle,  'data': desciption, 'listMenuPermission': objMenu}
            
    return render(request, 'settingdes/setting_com_form_create.html', context)



@login_required(login_url='/login')

def setting_form_commissionstages_update(request):


    stage_id = request.POST['stage_id']
    stage_name = request.POST['stage_name']
    commission_rate = request.POST['commission_rate_update']
    stage_description = request.POST['stage_description_update']


   
    content = commissionstages.objects.get(stage_id=stage_id)
    content.stage_name = stage_name
    content.commission_rate = commission_rate
    content.stage_description = stage_description
    content.save()

    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/commissionstages/setting/form")

def setting_form_commissionstages_delete(request):

    id = request.POST['id']     
   
    instance = commissionstages.objects.get(seq=id)
    instance.delete()
    desciption = commissionstages.objects.all().order_by('seq')  
    t = 0
    for desciptions in desciption:
        t += 1
        desciptions.seq = t
        desciptions.save()
        
    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/commissionstages/setting/form/create")



@csrf_exempt
def findbillevid(request):
    data = json.loads(request.body)
    ev_id = data.get("ev_id")


    


  

    datas = {'status':'200'}
    return JsonResponse(data,safe=False)


@csrf_exempt
def data_event(request):
    data = json.loads(request.body)
    ev_id = data.get("evid")
    
    teacher_data = teacher_income_setting.objects.filter(ev_id=ev_id)
    
    sff = []
    obj = []
    if teacher_data.count() > 0:
        
        for x in teacher_data:
            sff = {
                "teacher_prefix_th": x.teacher.teacher_prefix_th,
                "teacher_firstname_th": x.teacher.teacher_firstname_th,
                "teacher_lastname_th": x.teacher.teacher_lastname_th,
                "pi_id":x.pi_id,
                "pi_name":pay_item.objects.filter(id=x.pi_id).values_list('pi_name').first(),
                "tis_quantity": x.tis_quantity,
                "tis_unit": x.tis_unit,
                "compensation":x.tis_compensation,
                "id":x.id,
                "status":x.status,
                "teacher_id": x.teacher_id,
                "tis_sum": x.tis_sum,
                "tis_expenses": x.tis_expenses
            }
            obj.append(sff)
            
         
        else :
            sff = []

    return JsonResponse(obj,safe=False)



@csrf_exempt
def data_event_label(request):
    data = json.loads(request.body)
    ev_id = data.get("evid")
    mains  = training.objects.filter(ev=ev_id)
    mains = list(training.objects.filter(ev=ev_id).values('student_prefix_th', 'student_firstname_th', 'student_lastname_th'))


    
    teacher_data = teacher_income_setting.objects.filter(ev_id=ev_id)
    datas = {
       'obj':''
    }
    sff = []
    obj = []
    if teacher_data.count() > 0:
        
        for x in teacher_data:
            sff = {
                "teacher_prefix_th": x.teacher.teacher_prefix_th,
                "teacher_firstname_th": x.teacher.teacher_firstname_th,
                "teacher_lastname_th": x.teacher.teacher_lastname_th,
                "pi_id":x.pi_id,
                "pi_name":pay_item.objects.filter(id=x.pi_id).values_list('pi_name').first(),
                "tis_quantity": x.tis_quantity,
                "tis_unit": x.tis_unit,
                "compensation":x.tis_compensation,
                "id":x.id,
                "status":x.status,
                "teacher_id": x.teacher_id,
                "tis_sum": x.tis_sum,
                "tis_expenses": x.tis_expenses
            }
            obj.append(sff)
            
         
        else :
            sff = []


    datas = {
    'name':'ss','data':obj,'teacher':mains
    }    

    return JsonResponse(datas,safe=False)


@csrf_exempt
def data_bill(request):
    data = json.loads(request.body)
    ev_id = data.get("evid")
    month_current = request.GET.get('qmonths', date.today().month)
    year_current = request.GET.get('qyear', date.today().year)

    
    obj = []

      
    content = register_main.objects.filter(ev_id=ev_id,orderstatus='Deposit')
    for r in content:
        
       
        customer_list = customers.objects.select_related('register').filter(
            register_id=r.register_id).first()
        
        payment = register_payment.objects.filter(register=r.register_id).first()
        payment_i = register_payment_items.objects.filter(register=r.register_id).first()
        
        # customer_list = customers.objects.select_related('register').filter(
        #     register_id=r.register_id).first()
        
        # total_payment = register_payment.objects.filter(
        #     register_id=r.register_id).count()
        # course_list = course_event.objects.select_related(
        #     'course').filter(ev_id=r.ev_id).first()
        ct = '-'
        if r.customer_type == '1':
            ct = 'เครดิต'
        else:
            ct = 'เงินสด'

        cus_type = '-'
        if r.customer_type == '1':
            cus_type = 'บริษัท'
        else:
            cus_type = 'บุคคล'    


        uuid_without_dashes = str(r.register_id).replace('-', '')
      

        res = {'register_id':uuid_without_dashes,'ev_id':ev_id,'register_number': r.register_number,'pay_type':ct,'rp_name_seller':payment.rp_name_seller,'rp_name_customer':payment.rp_name_customer,'rpi_code':payment_i.rpi_code,'rpi_name':payment_i.rpi_name,'customer_type':cus_type,'rp_doc_number':payment.rp_doc_number}
        obj.append(res)


    return JsonResponse(obj,safe=False)



@csrf_exempt
def data_bill_com(request):
    data = json.loads(request.body)
    ev_id = data.get("evid")
    month_current = request.GET.get('qmonths', date.today().month)
    year_current = request.GET.get('qyear', date.today().year)
    obj = []

   
 
    # content = register_payment.objects.select_related('register').filter(register__ev_id=ev_id,active=1)
    content = register_payment.objects.select_related('register').filter(active=1,register__status='Y',status_bill='Y')
    doc = (data.get("doc") or '').strip()
    if doc:
        # ค้นหาด้วยเลขบิล TZ / เลขใบสมัคร R (พิมพ์มี / หรือไม่มีก็ได้ เช่น TZ69/09/002 หรือ TZ6909002)
        from django.db.models import Q
        from django.db.models.functions import Replace
        key = doc.replace('/', '').replace(' ', '')
        content = content.annotate(
            doc_plain=Replace('rp_doc_number', Value('/'), Value('')),
            reg_plain=Replace('register__register_number', Value('/'), Value('')),
        ).filter(Q(doc_plain__icontains=key) | Q(reg_plain__icontains=key)).order_by('-crt_date')[:50]
    else:
        content = content.filter(register__ev_id=ev_id)

    for r in content:
        
       
        customer_list = customers.objects.select_related('register').filter(
            register_id=r.register_id).first()
        
        payment = register_payment.objects.filter(register=r.register.register_id).first()
        payment_i = register_payment_items.objects.filter(register=r.register.register_id).first()
        
        # customer_list = customers.objects.select_related('register').filter(
        #     register_id=r.register_id).first()
        
        # total_payment = register_payment.objects.filter(
        #     register_id=r.register_id).count()
        # course_list = course_event.objects.select_related(
        #     'course').filter(ev_id=r.ev_id).first()
        ct = '-'
        if r.register.pay_type == 1:
            ct = 'เงินสด'
        else:
            ct = 'เครดิต'

        cus_type = '-'
        if r.register.customer_type == 1:
            cus_type = 'บุคคล'
        else:
            cus_type = 'บริษัท'    
    

        uuid_without_dashes = str(r.register.register_id).replace('-', '')
        
         
        seller = User.objects.filter(pk=r.register.seller_id).first()

        namessell = (seller.first_name + '-' + seller.last_name) if seller else '-'

        # หลักสูตรที่ตั้งว่าไม่มีค่าคอม -> หน้า finance/sale/commission ไม่แสดงปุ่มประเภทการจ่าย / กำหนด
        # เช็คจาก register_main.course (บิลไม่มีรอบอบรม ev จะเป็น NULL)
        bill_course = r.register.course if r.register.course_id else None
        has_commission = bill_course.has_commission if bill_course else 1

        res = {'has_commission':has_commission,'register_id':uuid_without_dashes,'ev_id':r.register.ev_id if doc else ev_id,'register_number': r.register.register_number,'pay_type':ct,'rp_name_seller':payment.rp_name_seller,'rp_name_customer':payment.rp_name_customer,'rpi_code':payment_i.rpi_code if payment_i else '-','rpi_name':payment_i.rpi_name if payment_i else '-','customer_type':cus_type,'rp_doc_number':payment.rp_doc_number,'seller':namessell,'rp_id':r.rp_id,'commit_head':payment.commit_head}
        obj.append(res)


    return JsonResponse(obj,safe=False)





@csrf_exempt
def type_bill_com(request):
 
    obj = []
    data = json.loads(request.body)
    register_id = data.get("register_id")
    commit_headdaa= data.get("commit_head")
    rps_id= data.get("rp_id")

    # บิลเงินสด ของหลักสูตรที่ตั้งว่าไม่มีค่าคอม (course.has_commission = 0) -> ไม่สร้างค่าคอม
    if register_main.objects.filter(
        register_id=register_id, pay_type=1, course__has_commission=0,
    ).exists():
        return JsonResponse({'status': 'no_commission',
                             'message': 'หลักสูตรนี้ตั้งว่าไม่มีค่าคอม ไม่สามารถกำหนดค่าคอมได้'}, status=400)

    content_approve = register_payment.objects.filter(register_id=register_id)
    content_approve.update(commit_head=commit_headdaa)

    last_entry = commissionstages.objects.filter(com_head_id=commit_headdaa)
    for r in last_entry:
        ontent = fact_commission(
        register_id=register_id,
        stage_id=r.stage_id,
        rpi_id=rps_id,
        status='N',
        com_head_id=r.com_head_id,
        )
        ontent.save()
 

    return JsonResponse(obj,safe=False)


@csrf_exempt
def data_bill_event(request):
    data = json.loads(request.body)
    ev_id = data.get("evid")
    month_current = request.GET.get('qmonths', date.today().month)
    year_current = request.GET.get('qyear', date.today().year)

    
    obj = []
    content = register_main.objects.filter(status='Y',ev_id=ev_id).exclude(register_number="-").order_by("crt_date")
    for r in content:
        factcustomer_list = fact_customer.objects.select_related('register').filter(
            register_id=r.register_id).first()
        
        
        customer_list = customers.objects.filter(
            pk=factcustomer_list.customer_id).first()
        payment = register_payment.objects.filter(register=r.register_id).first()
        payment_i = register_payment_items.objects.filter(register=r.register_id).first()
    
        ct = '-'
        if r.customer_type == '1':
            ct = 'เครดิต'
        else:
            ct = 'เงินสด'

        cus_type = '-'
        if r.customer_type == '1':
            cus_type = 'บริษัท'
        else:
            cus_type = 'บุคคล'    


        uuid_without_dashes = str(r.register_id).replace('-', '')
        formatted_datetime = r.crt_date.strftime("%Y-%m-%d %H:%M:%S")

        res = {'seller':r.seller.first_name + '-' + r.seller.last_name,'crt_date':formatted_datetime,'tel':customer_list.customer_phone,'register_id':uuid_without_dashes,'ev_id':ev_id,'register_number': payment.rp_doc_number,'pay_type':ct,'rp_name_seller':payment.rp_name_seller,'rp_name_customer':payment.rp_name_customer,'rpi_code':payment_i.rpi_code,'rpi_name':payment_i.rpi_name,'customer_type':cus_type}
        obj.append(res)


   

    return JsonResponse(obj,safe=False)

@csrf_exempt
def data_com(request):
    data = json.loads(request.body)
    register_id = data.get("register_id")
    rp_id = data.get("rp_id")
 
    bbbb = register_payment.objects.get(register_id=register_id,rp_id=rp_id)
    

    if bbbb.commit_head > 0:
        
        obj = []
        content = fact_commission.objects.filter(register_id=register_id).order_by("stage_id")
        for r in content:
            print(r)
            s_name = 'ยังไม่ยืนยัน'
            stages = commissionstages.objects.filter(stage_id=r.stage_id).first()
            
            if r.status == 'Y':
                s_name = 'ยืนยันแล้ว'
            res = {'commit_id':r.commit_id,'stage_id':r.stage_id,'user_id':r.user_id,'register_id':r.register_id,'stages_name':stages.stage_name,'rates':stages.commission_rate,'s_name':s_name}
            obj.append(res)
    else :  
        obj = []
 
    

   

    return JsonResponse(obj,safe=False)



@csrf_exempt
def user_com(request):
    data = json.loads(request.body)
    content = User.objects.filter()
    obj = []
    for r in content:
  
        res = {'id':r.id,'text':r.first_name +'-'+ r.last_name }
        obj.append(res)
   

    return JsonResponse(obj,safe=False)


COM_NOTI_REF_TYPE = 'com_bill'  # แจ้งเตือนยืนยันค่าคอม 1 รายการต่อ 1 บิลต่อ 1 ผู้รับ (reference_id = rp_id)


def _com_notify_message(item, user_id):
    """ข้อความแจ้งเตือนยืนยันค่าคอม: เลขใบเสร็จ / คอร์ส / จำนวนเงินบิล / รายการค่าคอม ของผู้รับคนนี้ในบิลนี้
    คืนค่า None ถ้าผู้รับไม่มีรายการค่าคอมในบิลนี้แล้ว"""
    bill_rpi_ids = list(register_payment_items.objects.filter(rp_id=item.rp_id).values_list('rpi_id', flat=True))
    stage_ids = list(fact_commission.objects.filter(rpi_id__in=bill_rpi_ids, user_id=user_id)
                     .values_list('stage_id', flat=True))
    if not stage_ids:
        return None
    bill_total = register_payment_items.objects.filter(rp_id=item.rp_id).aggregate(
        s=Sum('rpi_price_result'))['s'] or 0
    stage_names = list(commissionstages.objects.filter(stage_id__in=stage_ids)
                       .order_by('seq', 'stage_id').values_list('stage_name', flat=True))
    crs = item.register.course
    msg = (f"ยืนยันค่าคอม | เลขใบเสร็จ {item.rp.rp_doc_number or '-'}"
           f" | คอร์ส {crs.course_code} {crs.course_name}"
           f" | จำนวนเงินบิล {bill_total:,.2f} บาท"
           f" | รายการค่าคอม {', '.join(stage_names) or '-'}")
    return msg[:255]


def _sync_com_notification(item, user_id):
    """สร้าง/อัปเดตแจ้งเตือนของผู้รับ 1 คนสำหรับบิลนี้ (ไม่สร้างซ้ำ)"""
    now = dateTimeNow()
    existing = notifications.objects.filter(
        notification_type='com', reference_type=COM_NOTI_REF_TYPE,
        reference_id=str(item.rp_id), user_id=user_id).order_by('notifications_id')
    msg = _com_notify_message(item, user_id)
    if msg is None:
        # ผู้รับคนนี้ไม่มีค่าคอมในบิลนี้แล้ว (ถูกเปลี่ยนไปให้คนอื่น) -> ลบแจ้งเตือนที่ยังไม่ได้อ่าน
        existing.filter(is_read='false').delete()
        return
    noti = existing.first()
    if noti:
        noti.message = msg
        noti.is_read = 'false'
        noti.upd_date = now
        noti.save(update_fields=['message', 'is_read', 'upd_date'])
        return
    notifications.objects.create(
        notification_type='com',
        title='แจ้งเตือน',
        message=msg,
        reference_id=str(item.rp_id),
        reference_type=COM_NOTI_REF_TYPE,
        is_read='false',
        read_at=now,
        action_url='/finance/sale/com',
        priority='easy',
        user_id=user_id,
        created_by='1',
        cm_id=1,
        crt_date=now,
        upd_date=now)


@csrf_exempt
def update_com(request):

   
    data = json.loads(request.body)
    commit_id = data.get("commit_id")
    user_id = data.get("user_id")
    types = data.get("type")
    content = fact_commission.objects.get(commit_id=commit_id)
    rpi_id = content.rpi_id

    if types == 'group':
        group_qs = fact_commission.objects.filter(rpi_id=rpi_id, status='N')
        prev_users = set(group_qs.values_list('user_id', flat=True))
        group_qs.update(user_id=user_id)
    else:
        prev_users = {content.user_id}
        content.user_id = user_id
        content.save()

    # แจ้งเตือน 1 ครั้งต่อบิล: อัปเดตของผู้รับใหม่ และของผู้รับเดิม (ถ้าถูกเปลี่ยนคน)
    try:
        item = register_payment_items.objects.select_related('rp', 'register__course').get(rpi_id=rpi_id)
        for uid in {int(user_id)} | {u for u in prev_users if u}:
            _sync_com_notification(item, uid)
    except Exception:
        pass

    obj = {'status':200}
    return JsonResponse(obj,safe=False)

@csrf_exempt
def data_bill_overdue(request):
    data = json.loads(request.body)
    customers_id = data.get("customer_id")

    obj = []
  
    content = fact_customer.objects.select_related('register','customer').filter(
            customer=customers_id,register__orderstatus='Completed')
    
    
    
    for r in content:
        
    
        payment = register_payment.objects.filter(register=r.register.register_id).first()
        payment_i = register_payment_items.objects.filter(register=r.register.register_id).first()
    
 
        ct = '-'
        if r.register.customer_type == '1':
            ct = 'เครดิต'
        else:
            ct = 'เงินสด'

        cus_type = '-'
        if r.register.customer_type == '1':
            cus_type = 'บริษัท'
        else:
            cus_type = 'บุคคล'    


        uuid_without_dashes = str(r.register.register_id).replace('-', '')
      

        res = {'register_id':uuid_without_dashes,'ev_id':r.register.ev_id,'register_number': r.register.register_number,'pay_type':ct,'rp_name_seller':payment.rp_name_seller,'rp_name_customer':payment.rp_name_customer,'rpi_code':payment_i.rpi_code,'rpi_name':payment_i.rpi_name,'customer_type':cus_type}
        obj.append(res)


    return JsonResponse(obj,safe=False)
