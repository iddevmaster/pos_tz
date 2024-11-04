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

class course(models.Model):
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



# ev_vat  0  =ไม่รวม Vat,1 = รวม Vat


@cleanup.select
class course_event(models.Model):
    ev_id = models.AutoField(primary_key=True)
    ev_date_start = models.DateField(blank=True, null=True)
    ev_date_end = models.DateField(blank=True, null=True)
    ev_generation = models.IntegerField(default=0, blank=False)
    ev_remark = models.CharField(max_length=256, blank=True, default=None)
    ev_price = models.FloatField(default=0, blank=False)
    ev_vat = models.IntegerField(default=0, blank=False)
    ev_expired_cer_quantity = models.IntegerField(default=0, blank=False)
    ev_expired_cer_date = models.DateField(blank=True, null=True)
    ev_logo = models.ImageField(
        upload_to=generate_unique_name('images/logo'), default=None)
    active = models.IntegerField(default=1, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    cancelled = models.IntegerField(default=1, blank=False)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    module = models.CharField(max_length=12, blank=True, default=defaultModule)
   
    
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
    ev = models.ForeignKey(course_event, on_delete=models.CASCADE)
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_create")
    user_update = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_update")
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
    rp = models.ForeignKey(
        register_payment, on_delete=models.CASCADE)
    register = models.ForeignKey(register_main, on_delete=models.CASCADE)


class customers(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_code = models.CharField(max_length=128, blank=True, default=None)
    customer_name = models.CharField(max_length=256, blank=True, default=None)
    customer_tax = models.CharField(max_length=64, blank=True, default=None)
    customer_phone = models.CharField(max_length=64, blank=True, default=None)
    customer_email = models.CharField(max_length=64, blank=True, default=None)
    customer_address = models.CharField(
        max_length=512, blank=True, default=None)
    location = models.ForeignKey(
        location_thai, on_delete=models.CASCADE)
    register = models.ForeignKey(register_main, on_delete=models.CASCADE)

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
    teacher_cover = models.ImageField(
        upload_to=generate_unique_name('images/teacher'), default=None)
    teacher_type = models.IntegerField(default=1, blank=False)
    active = models.IntegerField(default=1, blank=False)
    crt_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    cancelled = models.IntegerField(default=1, blank=False)
    module = models.CharField(max_length=12, blank=True, default=defaultModule)
    def __str__(self):
        name = str(self.teacher_firstname_th) + " - " + str(self.teacher_lastname_th)
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
    ev = models.ForeignKey(course_event, on_delete=models.CASCADE)
    teacher = models.ForeignKey(teacher, on_delete=models.CASCADE)
    pi = models.ForeignKey(pay_item, on_delete=models.CASCADE)

class billing_cycle_setting(models.Model):
    bcs_start_day = models.IntegerField(default=0, blank=False)
    bcs_end_day  = models.IntegerField(default=0, blank=False)
    module = models.CharField(max_length=12, blank=True, default=defaultModule)
    
# student_learning_status  0 = ยังไม่จบหลักสูตร , 1  = จบหลักสูตรแล้ว
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
