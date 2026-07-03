from django.db import models
from django.contrib.auth.models import User
import uuid
from django_cleanup import cleanup
from .functions import generate_unique_name ,generateShortId

# Create your models here.
defaultModule ="tz"

# Master Data
class location_thai(models.Model):
    location_id = models.AutoField(primary_key=True)
    district_code = models.CharField(max_length=128, blank=True, default=None)
    district_name = models.CharField(max_length=128, blank=True, default=None)
    zipcode = models.CharField(max_length=128, blank=True, default=None)
    amphur_code = models.CharField(max_length=128, blank=True, default=None)
    amphur_name = models.CharField(max_length=128, blank=True, default=None)
    province_code = models.CharField(max_length=128, blank=True, default=None)
    province_name = models.CharField(max_length=128, blank=True, default=None)

class pay_item(models.Model):
    pi_name = models.CharField(max_length=128, blank=True, default=None)
    active = models.IntegerField(default=1, blank=False)
    cancelled = models.IntegerField(default=1, blank=False)
    def __str__(self):
        return self.pi_name
 # End Master Data   
class fact_teacher_user(models.Model):
    user_id = models.IntegerField(blank=True ,default=None)
    teacher_id = models.CharField(max_length=32, editable=False)
 

class user_group(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,related_name="user_group_ref")
    module = models.CharField(max_length=12, blank=True, default=defaultModule)

class category_program(models.Model):
    cm_name = models.CharField(max_length=128, blank=True, default=None)
    active = models.IntegerField(default=1, blank=False)
    cancelled = models.IntegerField(default=1, blank=False)
    module = models.CharField(max_length=12, blank=True, default=defaultModule)
    

class category_program_permission(models.Model):
    id = models.CharField(
        primary_key=True, default=generateShortId, max_length=24, unique=True)
    page_route = models.CharField(max_length=64, blank=True, default=None)
    page_label = models.CharField(max_length=64, blank=True, default=None)
    group_value = models.CharField(
        max_length=64, blank=True, default=None)
    group_label = models.CharField(max_length=64, blank=True, default=None)
    cm = models.ForeignKey(category_program, on_delete=models.CASCADE)


    
class user_detail(models.Model):
    cm = models.ForeignKey(category_program, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

@cleanup.select
class  course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_code = models.CharField(max_length=128, blank=True, default=None)
    course_name = models.CharField(max_length=128, blank=True, default=None)
    course_name_eng = models.CharField(
        max_length=128, blank=True, default=None)
    active = models.IntegerField(default=1, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    cancelled = models.IntegerField(default=1, blank=False)
    module = models.CharField(max_length=12, blank=True, default=defaultModule)
    is_show_order = models.CharField(max_length=12, blank=True, default=None)
    is_type_condition = models.CharField(max_length=12, blank=True, default=None)
    is_show_condition = models.CharField(max_length=12, blank=True, default=None)
    sale_mode = models.CharField(max_length=10, blank=True, default='all', choices=[('all','ทั้งหมด'),('event','มี Event เท่านั้น'),('noevent','ไม่มี Event เท่านั้น')])
    image_cover = models.ImageField(
        upload_to=generate_unique_name('images/course'), blank=True, null=True, default=None)

# ev_vat  0  =ไม่รวม Vat,1 = รวม Vat


@cleanup.select
class course_event(models.Model):
    ev_id = models.AutoField(primary_key=True)
    ev_date_start = models.DateField(blank=True, null=True)
    ev_date_end = models.DateField(blank=True, null=True)
    ev_generation = models.IntegerField(default=0, blank=False)
    ev_remark = models.CharField(max_length=256, blank=True, default=None)
    ev_price = models.FloatField(default=0, blank=False)
    limit_price = models.FloatField(default=0, blank=False)
    limit_price_workhelp = models.FloatField(default=0, blank=False)
    ev_vat = models.IntegerField(default=0, blank=False)
    ev_hour = models.IntegerField(default=0, blank=False)
    ev_hour_two = models.IntegerField(default=0, blank=False)
    ev_hour_three = models.IntegerField(default=0, blank=False)
    ev_people = models.IntegerField(default=0, blank=False)
    ev_people_two = models.IntegerField(default=0, blank=False)
    ev_people_three = models.IntegerField(default=0, blank=False)
    ev_expired_cer_quantity = models.IntegerField(default=0, blank=False)
    ev_training = models.IntegerField(default=1, blank=False)
    ev_expired_cer_date = models.DateField(blank=True, null=True)
    is_show = models.IntegerField(default=1, blank=False)
    ev_logo = models.ImageField(
        upload_to=generate_unique_name('images/logo'), default=None)
    active = models.IntegerField(default=1, blank=False)
    location_id = models.IntegerField(default=0, blank=False)
    address = models.CharField(max_length=512, blank=True, default=None)
    details = models.CharField(max_length=512, blank=True, default=None)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    cancelled = models.IntegerField(default=1, blank=False)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    status = models.CharField(blank=True, null=True, max_length=1)
    checkevent = models.IntegerField(default=1, blank=False)
    project = models.ForeignKey('app.project_code', on_delete=models.CASCADE)
    module = models.CharField(max_length=12, blank=True, default=defaultModule)
    condition_id = models.IntegerField(default=0, blank=False)
    condition_type = models.IntegerField(default=0, blank=False)
    number_code = models.CharField(max_length=256, blank=True, default=None)
    ev_user = models.IntegerField(default=0, blank=True, null=True)
   
    
# customer_type  1  = บุคคล ,2 = บริษัท
# customer_status  0  = เป้าหมาย , 1 = ลูกค้า
# pay_type  1  = เงินสด ,2 = เครดิต
# pay_status 1 = ยังไม่ชำระเงิน  , 2 = ชำระเงินไม่ครบ , 3 = ชำระเงินครบแล้ว
# close_the_sale 1 = ปิดการขาย - ขายสำเร็จ , 2= ปิดการขาย - ขายไม่สำเร็จ


class register_main(models.Model):
    register_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    register_number = models.CharField(max_length=64, blank=True, default=None)
    customer_type = models.IntegerField(default=0, blank=False)
    customer_status = models.IntegerField(default=0, blank=False)
    pay_type = models.IntegerField(default=0, blank=False)
    pay_status = models.IntegerField(default=0, blank=False)
    close_the_sale = models.IntegerField(default=0, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    orderstatus = models.CharField(max_length=64, blank=True, default=None)
    ev = models.ForeignKey(course_event, on_delete=models.CASCADE)
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_create")
    user_update = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_update")
    status = models.CharField(
        max_length=1, blank=True, default=None)
    number_order = models.CharField(
        max_length=64, blank=True, default=None)
    is_event = models.CharField(
        max_length=64, blank=True, default=None)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    module = models.CharField(max_length=12, blank=True, default=defaultModule)



class register_payment(models.Model):
    rp_id = models.AutoField(primary_key=True)
    rp_doc_number = models.CharField(
        max_length=128, blank=True, default=None)
    rp_code_customer = models.CharField(
        max_length=128, blank=True, default=None)
    rp_name_customer = models.CharField(
        max_length=128, blank=True, default=None)
    rp_tax = models.CharField(max_length=128, blank=True, default=None)
    rp_name_seller = models.CharField(
        max_length=128, blank=True, default=None)
    rp_name_contact = models.CharField(
        max_length=128, blank=True, default=None)
    rp_branch = models.CharField(max_length=128, blank=True, default=None)
    rp_address = models.CharField(max_length=512, blank=True, default=None)
    rp_phone = models.CharField(max_length=64, blank=True, default=None)
    rp_email = models.CharField(max_length=64, blank=True, default=None)
    rp_confirm_date_price = models.DateField(blank=True, null=True)
    rp_date_delivery = models.DateField(blank=True, null=True)
    rp_quota = models.IntegerField(default=0, blank=False)
    rp_ref1 = models.CharField(max_length=128, blank=True, default=None)
    rp_ref2 = models.CharField(max_length=128, blank=True, default=None)
    active = models.IntegerField(default=1, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    register = models.ForeignKey(register_main, on_delete=models.CASCADE)
    user_create = models.IntegerField(default=0, blank=False)
    user_manage = models.IntegerField(default=0, blank=False)
    number_receipt = models.CharField(max_length=256, blank=True, default=None)
    commit_head = models.IntegerField(default=0, blank=False)
    status_bill = models.CharField(max_length=256, blank=True, default=None)

    

class register_payment_items(models.Model):
    rpi_id = models.AutoField(primary_key=True)
    rpi_code = models.CharField(max_length=128, blank=True, default=None)
    rpi_name = models.CharField(max_length=128, blank=True, default=None)
    rpi_quantity = models.IntegerField(default=0, blank=False)
    rpi_unit = models.CharField(max_length=64, blank=True, default=None)
    rpi_price = models.FloatField(default=0, blank=False)
    rpi_price_discount = models.FloatField(default=0, blank=False)
    rpi_price_total = models.FloatField(default=0, blank=False)
    rpi_price_vat = models.FloatField(default=0, blank=False)
    rpi_price_result = models.FloatField(default=0, blank=False)
    rpi_pay = models.FloatField(default=0, blank=False)
    rpi_price_pay = models.FloatField(default=0, blank=False)
    vat = models.CharField(max_length=64, blank=True, default=None)
    rp = models.ForeignKey(
        register_payment, on_delete=models.CASCADE , related_name='items')
    register = models.ForeignKey(register_main, on_delete=models.CASCADE)
    stmdate = models.DateTimeField(blank=True, null=True)
    stmetc = models.CharField(max_length=64, blank=True, default=None)
    type_payment = models.CharField(max_length=64, blank=True, default=None)
    

class customers(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_code = models.CharField(max_length=128, blank=True, default=None)
    customer_name = models.CharField(max_length=256, blank=True, default=None)
    customer_fisrt = models.CharField(max_length=256, blank=True, default=None)
    customer_last = models.CharField(max_length=256, blank=True, default=None)
    customer_tax = models.CharField(max_length=64, blank=True, default=None)
    customer_phone = models.CharField(max_length=64, blank=True, default=None)
    customer_email = models.CharField(max_length=64, blank=True, default=None)
    customer_address = models.CharField(
        max_length=512, blank=True, default=None)
    location_id = models.IntegerField(default=0, blank=True)
    # 1=บุคคล, 2=บริษัท
    customer_type = models.IntegerField(default=1, blank=True)

class fact_customer(models.Model):
    fact_cus_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(customers, on_delete=models.CASCADE)  
    register = models.ForeignKey(register_main, on_delete=models.CASCADE) 
    status_bill = models.CharField(
        max_length=512, blank=True, default=None)
       

# status 1 = อนุมัติ , 2 = ไม่อนุมัติ
# doc_type 1 =  อนุมัติเพื่อแก้ไขใบเสร็จ / ใบเสนอราคา
# complete 0 = ยังไม่ทำรายการ , 1 = ทำรายการเสร็จสมบูรณ์แล้ว


class register_applove(models.Model):
    status = models.IntegerField(default=0, blank=False)
    doc_type = models.IntegerField(default=0, blank=False)
    complete = models.IntegerField(default=0, blank=False)
    remark = models.CharField(max_length=128, blank=True, default=None)
    crt_date = models.DateTimeField(blank=True, null=True)
    register = models.ForeignKey(register_main, on_delete=models.CASCADE)
    user_approve = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="regis_user_approve")
    user_crt = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_crt_approve", default=None)


class register_ref(models.Model):
    ref = models.CharField(max_length=128, blank=True, default=None)
    crt_date = models.DateTimeField(blank=True, null=True)
    register = models.ForeignKey(
        register_main, on_delete=models.CASCADE, related_name="ref_create")
    user_crt = models.ForeignKey(User, on_delete=models.CASCADE)

# teacher_type 1 = วิทยากรภายใน , 2 = วิทยากรภายนอก
@cleanup.select
class teacher(models.Model):
    teacher_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    teacher_identification_number = models.CharField(
        max_length=24, blank=True, default=None)
    teacher_prefix_th = models.CharField(
        max_length=48, blank=True, default=None)
    teacher_firstname_th = models.CharField(
        max_length=128, blank=True, default=None)
    teacher_lastname_th = models.CharField(
        max_length=128, blank=True, default=None)
    teacher_prefix_eng = models.CharField(
        max_length=48, blank=True, default=None)
    teacher_firstname_eng = models.CharField(
        max_length=128, blank=True, default=None)
    teacher_lastname_eng = models.CharField(
        max_length=128, blank=True, default=None)
    tax_number = models.CharField(
        max_length=24, blank=True, default=None)
    teacher_cover = models.ImageField(
        upload_to=generate_unique_name('images/teacher'), default=None)
    teacher_type = models.IntegerField(default=1, blank=False)
    active = models.IntegerField(default=1, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    cancelled = models.IntegerField(default=1, blank=False)
    module = models.CharField(max_length=12, blank=True, default=defaultModule)
    level = models.CharField(
        max_length=128, blank=True, default=None)
    def __str__(self):
        name = str(self.teacher_firstname_th) + "  - " + str(self.teacher_lastname_th)
        return name
    
# ตั้งค่ายอดที่จะจ่ายให้กับครู - วิทยากร
class teacher_income_setting(models.Model):
    tis_compensation = models.FloatField(default=0 , blank=False)
    tis_unit = models.CharField(max_length=64, blank=True, default=None)
    tis_quantity = models.IntegerField(default=0, blank=False)
    tis_sum = models.FloatField(default=0 , blank=False)
    tis_start_date = models.DateField(blank=True, null=True)
    tis_end_date  = models.DateField(blank=True, null=True)
    tis_group  = models.CharField(max_length=64, blank=True, default="-")
    active = models.IntegerField(default=0, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    ev = models.ForeignKey(course_event, on_delete=models.CASCADE )
    teacher = models.ForeignKey(teacher, on_delete=models.CASCADE)
    pi = models.ForeignKey(pay_item, on_delete=models.CASCADE)
    status = models.CharField(blank=True, null=True, max_length=1)
    register_id  = models.CharField(max_length=254, blank=True, default="-")
    tax = models.IntegerField(blank=True, default=None)
    tis_expenses = models.IntegerField(default=0 , blank=False)
    expenses_type  = models.CharField(max_length=254, blank=True, default="-")
    


class tax_setting(models.Model):
    tax_id = models.AutoField(primary_key=True)
    tax  = models.IntegerField(default=0, blank=False)
    tax_com  = models.IntegerField(default=0, blank=False)

class bill_setting(models.Model):
    bill_id = models.AutoField(primary_key=True)
    is_show_signature  = models.IntegerField(default=0, blank=False)


class billing_cycle_setting(models.Model):
    bcs_start_day = models.IntegerField(default=0, blank=False)
    bcs_end_day  = models.IntegerField(default=0, blank=False)
    module = models.CharField(max_length=12, blank=True, default=defaultModule)
    
# student_learning_status  0 = ยังไม่จบสินค้า , 1  = จบสินค้าแล้ว
class student(models.Model):
    student_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    student_identification_number = models.CharField(
        max_length=24, blank=True, default=None)
    student_prefix_th = models.CharField(
        max_length=48, blank=True, default=None)
    student_firstname_th = models.CharField(
        max_length=128, blank=True, default=None)
    student_lastname_th = models.CharField(
        max_length=128, blank=True, default=None)
    student_prefix_eng = models.CharField(
        max_length=48, blank=True, default=None)
    student_firstname_eng = models.CharField(
        max_length=128, blank=True, default=None)
    student_lastname_eng = models.CharField(
        max_length=128, blank=True, default=None)
    student_learning_status = models.IntegerField(default=0, blank=False)
    student_code = models.CharField(max_length=64, blank=True, default=None)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    register = models.ForeignKey(
        register_main, on_delete=models.CASCADE, related_name="student_register")


class pos_machine(models.Model):
    pm_id_code = models.CharField(
        max_length=64, blank=True, default=None)
    pm_id_number = models.CharField(
        max_length=64, blank=True, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
class compensation(models.Model):
    compensation = models.IntegerField(default=0 , blank=False)
    teacher_id = models.CharField(max_length=100, blank=True, default=None)
    status = models.CharField(max_length=1, blank=True ,default=None)
    note = models.CharField(max_length=128, default=0 , blank=False)
    compensation_group_id = models.CharField(max_length=1, blank=True ,default=None)
    py_id = models.CharField(max_length=1, blank=True ,default=None)

class user_lic(models.Model):
    lic_id = models.AutoField(primary_key=True)
    number_lic = models.CharField(max_length=100, blank=True, default=None)
    picture = models.CharField(max_length=128, default=0 , blank=False)
    teacher_id = models.CharField(max_length=100, blank=True, default=None)
    status = models.CharField(max_length=1, blank=True ,default=None)
    issue_date = models.DateField(blank=True, null=True)
    expire_date = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=1, default=0 , blank=False)
    cancelled = models.IntegerField(default=1, blank=False)

class project_code(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=100, blank=True, default=None)
    name = models.CharField(max_length=128, default=0 , blank=False)
    status = models.IntegerField(default=1, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    cancelled = models.IntegerField(default=1, blank=False)

class event_register(models.Model):
    er_id = models.AutoField(primary_key=True)
    ev = models.ForeignKey(course_event, on_delete=models.CASCADE ,related_name="ref_create_ev")
    register = models.ForeignKey(register_main, on_delete=models.CASCADE, related_name="ref_create_ev_reg")
    status = models.CharField(max_length=1, default=0 , blank=False)
 
    

class salesorder(models.Model):
    sale_id = models.AutoField(primary_key=True)
    er = models.ForeignKey(event_register, on_delete=models.CASCADE ,related_name="ref_er")
    type_sa = models.CharField(max_length=128, default=None , blank=True)
    po = models.CharField(max_length=64, blank=True, default=None)
    sq = models.CharField(max_length=64, blank=True, default=None)
    so = models.CharField(max_length=64, blank=True, default=None)
    invoice = models.CharField(max_length=128, blank=True, default=None)
    rv = models.CharField(max_length=128, blank=True, default=None)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    img = models.ImageField(
        upload_to=generate_unique_name('images/sales'), default=None)
    status = models.CharField(max_length=128, blank=True, default=None)
    

class desciption_bill(models.Model):
    des_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, blank=True, default=None)
    seq = models.IntegerField(default=None, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)

class factbilldes(models.Model):
    factbill_id = models.AutoField(primary_key=True)
    register_id  = models.CharField(max_length=254, blank=True, default="-")
    des_id = models.IntegerField(default=None, blank=False) 

    
       
class document(models.Model):
    doc_id = models.AutoField(primary_key=True)
    doc_number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(default=0 , blank=False)
    payment_policy = models.CharField(max_length=20, unique=True, blank=True)
    teacher_income_id = models.IntegerField(default=None, blank=False) 
    status_mange = models.CharField(max_length=1, unique=True, blank=True)
    status_gm = models.CharField(max_length=1, unique=True, blank=True)
    doc_in_hrc = models.CharField(max_length=256, unique=True, blank=True)
    
class signature(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_cover = models.ImageField(
        upload_to=generate_unique_name('images/logo'), default=None)
    user_id = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class fact_signature(models.Model):
    fact_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class add_on(models.Model):
    addon_id = models.AutoField(primary_key=True)
    course_code = models.CharField(max_length=20, unique=True, blank=True)  
    order_list = models.CharField(max_length=20, unique=True, blank=True)  
    register_id  = models.CharField(max_length=254, blank=True, default="-")
    unit = models.CharField(max_length=20, unique=True, blank=True)  
    rpi_price = models.FloatField(default=0, blank=False)
    rpi_price_discount = models.FloatField(default=0, blank=False)
    rpi_price_result = models.FloatField(default=0, blank=False)
    qty = models.IntegerField(default=0, blank=False)
    status = models.CharField(max_length=20, unique=True, blank=True)  
    rp_id = models.IntegerField(default=0, blank=False)

class fact_addon(models.Model):
    fact_id = models.AutoField(primary_key=True)
    rp_id = models.IntegerField(default=0, blank=False)
    addon_id = models.IntegerField(default=0, blank=False)

class conhead(models.Model):
    conhead_id = models.AutoField(primary_key=True) 
    name = models.CharField(max_length=20, unique=True, blank=True)
    is_active = models.CharField(max_length=20, unique=True, blank=True)
    course = models.ForeignKey(course, on_delete=models.CASCADE)

class com_head(models.Model):
    id = models.AutoField(primary_key=True) 
    name = models.CharField(max_length=20, unique=True, blank=True)
    is_active = models.CharField(max_length=20, unique=True, blank=True)

class condition(models.Model):
    condition_id = models.AutoField(primary_key=True)
    student = models.IntegerField(default=0, blank=False)
    price = models.FloatField(default=0, blank=False)
    type = models.CharField(max_length=20, unique=True, blank=True)  
    hour = models.CharField(max_length=20, unique=True, blank=True)
    type_add = models.CharField(max_length=20, unique=True, blank=True)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    conhead = models.ForeignKey(conhead, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, unique=True, blank=True)



class training(models.Model):
    training_id = models.AutoField(primary_key=True)
    student_identification_number = models.CharField(
        max_length=24, blank=True, default=None)
    student_prefix_th = models.CharField(
        max_length=48, blank=True, default=None)
    student_firstname_th = models.CharField(
        max_length=128, blank=True, default=None)
    student_lastname_th = models.CharField(
        max_length=128, blank=True, default=None)
    student_prefix_eng = models.CharField(
        max_length=100, blank=True, default=None)
    student_firstname_eng = models.CharField(
        max_length=128, blank=True, default=None)
    student_lastname_eng = models.CharField(
        max_length=128, blank=True, default=None)
    student_learning_status = models.IntegerField(default=0, blank=False)
    student_code = models.CharField(max_length=64, blank=True, default=None)
    tel = models.CharField(
        max_length=200, blank=True, default=None)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    ev = models.ForeignKey(
        course_event, on_delete=models.CASCADE)
    
class commissionstages(models.Model):
    stage_id = models.AutoField(primary_key=True)
    commission_rate = models.FloatField(default=0, blank=False)
    stage_name = models.CharField(max_length=255, unique=True, blank=True)  
    stage_description = models.CharField(max_length=255,unique=True, blank=True)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    seq = models.IntegerField(default=None, blank=False)
    types = models.CharField(max_length=1, blank=False)
    com_head_id = models.IntegerField(default=None, blank=False) 


class fact_commission(models.Model):
    commit_id = models.AutoField(primary_key=True)
    register_id = models.CharField(max_length=255, unique=True, blank=True)  
    stage_id = models.IntegerField(default=None, blank=False)   
    user_id = models.IntegerField(default=None, blank=False)   
    rpi_id = models.IntegerField(default=None, blank=False)  
    status = models.CharField(max_length=1, blank=False)
    com_head_id = models.IntegerField(default=None, blank=False) 

class com_income_setting(models.Model):
    tis_com_before_tax = models.FloatField(default=0 , blank=False)
    tis_com_after_tax = models.FloatField(default=0 , blank=False)
    tis_com_before_vat = models.FloatField(default=0 , blank=False)
    tis_com_after_vat = models.FloatField(default=0 , blank=False)
    tis_group  = models.CharField(max_length=64, blank=True, default="-")
    active = models.IntegerField(default=0, blank=False)
    status = models.CharField(max_length=1, blank=False)
    tis_start_date = models.DateField(blank=True, null=True)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    ev = models.ForeignKey(course_event, on_delete=models.CASCADE ) 
    register_id  = models.CharField(max_length=254, blank=True, default="-")
    tax = models.IntegerField(blank=True, default=None)
    com_id = models.IntegerField(blank=True, default=None)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 👈 แก้ตรงนี้
    status_pay = models.CharField(max_length=15, blank=False)
    notifications = models.CharField(max_length=1, blank=False)


class notifications(models.Model):
    notifications_id = models.AutoField(primary_key=True)
    notification_type = models.CharField(max_length=1, blank=False)
    title = models.CharField(max_length=255, blank=False)
    message = models.CharField(max_length=255, blank=False)
    reference_id = models.CharField(max_length=1, blank=False)
    reference_type = models.CharField(max_length=255, blank=False)
    is_read = models.CharField(max_length=1, blank=False)
    read_at = models.DateTimeField(blank=True, null=True)
    action_url = models.CharField(max_length=1, blank=False)
    priority = models.CharField(max_length=1, blank=False)
    created_by = models.IntegerField(blank=True, default=None)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    cm = models.ForeignKey(category_program, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


# ============================================================================
# Commission engine (นโยบายค่าคอมมิชชั่น 4 นโยบายหลัก + เงื่อนไขย่อย)
# แทนที่ com_head / commissionstages / fact_commission เดิมด้วยโครงสร้างที่รองรับ
# การแบ่งสัดส่วนผู้รับหลายคนต่อเงื่อนไข และแผนค่าคอมเฉพาะบิลที่แก้ไขได้อิสระ
# จากอัตรากลาง แต่กำหนด/ล็อกได้ก็ต่อเมื่อบิลนั้น "ปิดการขาย - ขายสำเร็จ" แล้วเท่านั้น
# ============================================================================

# calc_type  PRORATA = แบ่งสัดส่วนตามยอด , LUMPSUM = จ่ายก้อนเดียว , FIXED = จำนวนคงที่
class commission_policy(models.Model):
    policy_id = models.AutoField(primary_key=True)
    policy_code = models.CharField(max_length=8, blank=True, default=None)
    policy_name = models.CharField(max_length=255, blank=True, default=None)
    seq = models.IntegerField(default=0, blank=False)
    active = models.IntegerField(default=1, blank=False)

    def __str__(self):
        return str(self.policy_code) + " " + str(self.policy_name)


class commission_condition(models.Model):
    condition_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey(
        commission_policy, on_delete=models.CASCADE, related_name="conditions")
    condition_code = models.CharField(max_length=8, blank=True, default=None)
    condition_name = models.CharField(max_length=255, blank=True, default=None)
    calc_type = models.CharField(max_length=16, blank=True, default="PRORATA")
    seq = models.IntegerField(default=0, blank=False)
    active = models.IntegerField(default=1, blank=False)

    def __str__(self):
        return str(self.condition_code) + " " + str(self.condition_name)


# payee_type  STAFF = บุคคล(พนักงาน/ที่ปรึกษา) , DEPARTMENT = ฝ่ายงานภายใน , EXTERNAL_ORG = หน่วยงานภายนอก
class commission_payee(models.Model):
    payee_id = models.AutoField(primary_key=True)
    payee_type = models.CharField(max_length=16, blank=True, default=None)
    payee_name = models.CharField(max_length=255, blank=True, default=None)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="commission_payee_user")
    teacher = models.ForeignKey(
        teacher, on_delete=models.CASCADE, null=True, blank=True, related_name="commission_payee_teacher")
    bank_name = models.CharField(max_length=128, blank=True, default=None)
    bank_account = models.CharField(max_length=64, blank=True, default=None)
    active = models.IntegerField(default=1, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.payee_name)


# อัตรา "ค่าเริ่มต้น" ต่อสินค้า(course) x เงื่อนไข ปรับได้อิสระตลอดเวลา ไม่ผูกกับบิลใด ๆ
class commission_rule(models.Model):
    rule_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(
        course, on_delete=models.CASCADE, related_name="commission_rules")
    condition = models.ForeignKey(commission_condition, on_delete=models.CASCADE)
    rate = models.FloatField(default=0, blank=False)
    active = models.IntegerField(default=0, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("course", "condition")


# สัดส่วนผู้รับ "ค่าเริ่มต้น" ของ rule ใช้เป็น template ตอนเปิดแผนค่าคอมของบิล
class commission_rule_allocation(models.Model):
    alloc_id = models.AutoField(primary_key=True)
    rule = models.ForeignKey(
        commission_rule, on_delete=models.CASCADE, related_name="allocations")
    payee = models.ForeignKey(commission_payee, on_delete=models.CASCADE)
    percent = models.FloatField(default=0, blank=False)


# หัวแผนค่าคอมของ "บิล" หนึ่งใบ (1 รายการขาย = 1 register_payment_items)
# สร้างได้ก็ต่อเมื่อบิลนั้นปิดการขาย-ขายสำเร็จแล้วเท่านั้น (ดูเงื่อนไขที่ view เป็นผู้ตรวจสอบ)
class commission_plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    rpi = models.OneToOneField(
        register_payment_items, on_delete=models.CASCADE, related_name="commission_plan")
    register = models.ForeignKey(
        register_main, on_delete=models.CASCADE, related_name="commission_plans")
    is_locked = models.IntegerField(default=0, blank=False)
    locked_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="commission_plan_locked_by")
    locked_at = models.DateTimeField(blank=True, null=True)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)


# source  DEFAULT = ดึงจาก commission_rule ของสินค้า ณ วันที่เปิดแผน , CUSTOM = ผู้ใช้แก้ไขเฉพาะบิลนี้
class commission_plan_line(models.Model):
    line_id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(
        commission_plan, on_delete=models.CASCADE, related_name="lines")
    condition = models.ForeignKey(commission_condition, on_delete=models.CASCADE)
    rate = models.FloatField(default=0, blank=False)
    active = models.IntegerField(default=0, blank=False)
    source = models.CharField(max_length=16, blank=True, default="DEFAULT")

    class Meta:
        unique_together = ("plan", "condition")


class commission_plan_allocation(models.Model):
    alloc_id = models.AutoField(primary_key=True)
    line = models.ForeignKey(
        commission_plan_line, on_delete=models.CASCADE, related_name="allocations")
    payee = models.ForeignKey(commission_payee, on_delete=models.CASCADE)
    percent = models.FloatField(default=0, blank=False)


# ยอดค่าคอมที่ต้องจ่ายจริง เกิดขึ้นตอน "ล็อกแผน" เท่านั้น (snapshot อัตรา/ยอดฐาน ณ เวลาล็อก)
# status  PENDING = รอดำเนินการ , APPROVED = อนุมัติแล้ว , PAID = จ่ายแล้ว
class commission_payout(models.Model):
    payout_id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(
        commission_plan, on_delete=models.CASCADE, related_name="payouts")
    condition = models.ForeignKey(commission_condition, on_delete=models.CASCADE)
    payee = models.ForeignKey(
        commission_payee, on_delete=models.CASCADE, null=True, blank=True)
    rate = models.FloatField(default=0, blank=False)
    base_amount = models.FloatField(default=0, blank=False)
    payee_percent = models.FloatField(null=True, blank=True)
    payout_amount = models.FloatField(default=0, blank=False)
    status = models.CharField(max_length=16, blank=True, default="PENDING")
    approved_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="commission_payout_approved_by")
    approved_at = models.DateTimeField(blank=True, null=True)
    paid_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="commission_payout_paid_by")
    paid_at = models.DateTimeField(blank=True, null=True)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)


# ============================================================================
# Commission per course_event — ค่าตอบแทนผู้ปฏิบัติงานต่อ ev_id
# ============================================================================

class commission_event_rule(models.Model):
    """อัตราค่าตอบแทนต่อ course_event x condition"""
    ev_rule_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        course_event, on_delete=models.CASCADE, related_name="commission_ev_rules")
    condition = models.ForeignKey(commission_condition, on_delete=models.CASCADE)
    rate = models.FloatField(default=0)
    active = models.IntegerField(default=0)
    remark = models.CharField(max_length=255, blank=True, null=True)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("event", "condition")


class commission_event_allocation(models.Model):
    """สัดส่วนผู้รับค่าตอบแทนต่อ ev_rule — status PENDING/APPROVED/PAID"""
    ev_alloc_id = models.AutoField(primary_key=True)
    ev_rule = models.ForeignKey(
        commission_event_rule, on_delete=models.CASCADE, related_name="allocations")
    payee = models.ForeignKey(commission_payee, on_delete=models.CASCADE)
    percent = models.FloatField(default=100)
    amount = models.FloatField(default=0)
    status = models.CharField(max_length=16, default='PENDING')
    approved_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="ev_alloc_approved")
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="ev_alloc_paid")
    paid_at = models.DateTimeField(null=True, blank=True)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
