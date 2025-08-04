from datetime import date
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Value
from django.db.models.functions import TruncMonth
from ..models import category_program_permission, course, course_event, teacher_income_setting, billing_cycle_setting, user_group, user_detail, desciption_bill,tax_setting,bill_setting,commissionstages,location_thai,pay_item,register_main,customers,register_payment,register_payment_items,fact_commission,commissionstages,User,fact_customer
from ..constant import defaultTitle, thai_months,unitPayChoices
from ..functions import dateTimeNow, last_day_of_month
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

    print(objMenu)

    context = {'title': defaultTitle, 'listMenuPermission': objMenu,'tax_id':tax.tax_id,'tax':tax.tax}
            
    return render(request, 'settingdes/tax_form_create.html', context)


@csrf_exempt
def savetax(request):
    data = json.loads(request.body)
    tax_id = data.get("tax_id")
    taxu = data.get("tax")

  
    tax_setting.objects.filter(tax_id=tax_id).update(tax=taxu)
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
 

    ciom = commissionstages.objects.all().order_by('seq')  

  

    context = {'title': defaultTitle, 'listMenuPermission': objMenu,'data':ciom}
            
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
     
        commission_ra = request.POST.get('commission_ra')

  
        last_entry = commissionstages.objects.order_by('-seq').first()
        
        content = commissionstages(
        stage_name=name,
        commission_rate=commission_ra,
        seq=last_entry.seq + 1,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow())
        content.save()
        messages.success(request, "ทำรายการสำเร็จ !")
        return redirect("/commissionstages/setting/form/create")

    desciption = commissionstages.objects.all().order_by('seq')
    context = {'title': defaultTitle,  'data': desciption, 'listMenuPermission': objMenu}
            
    return render(request, 'settingdes/setting_com_form_create.html', context)



@login_required(login_url='/login')

def setting_form_commissionstages_update(request):


    stage_id = request.POST['stage_id']
    stage_name = request.POST['stage_name']
    commission_rate = request.POST['commission_rate_update']
   
    content = commissionstages.objects.get(stage_id=stage_id)
    content.stage_name = stage_name
    content.commission_rate = commission_rate
    content.save()

    messages.success(request, "ทำรายการสำเร็จ !")
    return redirect("/commissionstages/setting/form/create")

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
    print(teacher_data)
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
                "tis_sum": x.tis_sum
            }
            obj.append(sff)
            
         
        else :
            sff = []

    return JsonResponse(obj,safe=False)


@csrf_exempt
def data_bill(request):
    data = json.loads(request.body)
    ev_id = data.get("evid")
    month_current = request.GET.get('qmonths', date.today().month)
    year_current = request.GET.get('qyear', date.today().year)

    
    obj = []

      
    content = register_payment_items.objects.select_related("rp","register").filter(register__ev_id=ev_id).order_by("-rp_id")
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
      

        res = {'register_id':uuid_without_dashes,'ev_id':ev_id,'register_number': r.register.register_number,'pay_type':ct,'rp_name_seller':payment.rp_name_seller,'rp_name_customer':payment.rp_name_customer,'rpi_code':payment_i.rpi_code,'rpi_name':payment_i.rpi_name,'customer_type':cus_type,'rp_doc_number':payment.rp_doc_number}
        obj.append(res)


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

    content = fact_commission.objects.filter(register_id=register_id).order_by("stage_id")
    
    obj = []
    for r in content:
        s_name = 'ยังไม่ยืนยัน'
        stages = commissionstages.objects.filter(stage_id=r.stage_id).first()
        if r.status == 'Y':
            s_name = 'ยืนยันแล้ว'
        
        res = {'commit_id':r.commit_id,'stage_id':r.stage_id,'user_id':r.user_id,'register_id':r.register_id,'stages_name':stages.stage_name,'rates':stages.commission_rate,'s_name':s_name}
        obj.append(res)
   

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


@csrf_exempt
def update_com(request):
    data = json.loads(request.body)
    commit_id = data.get("commit_id")
    user_id = data.get("user_id")
    content = fact_commission.objects.get(commit_id=commit_id)
    content.user_id = user_id
    content.save()
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