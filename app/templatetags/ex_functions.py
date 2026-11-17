import datetime
from django import template
from urllib.parse import urlparse
from django.http import HttpResponse
from ..constant import listMenu

register = template.Library()
@register.filter
def thai_date(date):
    if not isinstance(date, datetime.date):
        return date

    months = [
        'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
        'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
    ]

    day = date.day
    month = months[date.month - 1]
    year = date.year + 543

    return f'{day} {month} {year}'


@register.filter
def unit_format(val):
    if val == 'hour':
        format = 'ชั่วโมง'
    elif val == 'day':
        format = 'วัน'
    elif val == 'week':
        format = 'สัปดาห์'
    elif val == 'month':
        format = 'เดือน'
    elif val == 'work':
        format = 'งาน'
    else:
        format = '-'
    return format




@register.filter
def contains(value, arg):
    """Checks if arg is in value."""
    return arg in value

@register.filter
def contains_parent(path):
    # เริ่มต้นค่า default ของ group_value เป็น None หรือค่าที่ต้องการ
    group_value = None

    # วนลูปเพื่อค้นหา request.path ใน listMenu
    for item in listMenu:
        if path.strip('/') == item['value'].strip('/'):
            group_value = item['group_value']
            break
    print(group_value)
    # ส่งค่า group_value ไปยัง template
    return group_value



@register.filter
def subtractt(value, arg):
    return value - arg

@register.filter
def can_review_memo(user):
    """เมนู 'ตรวจสอบ / อนุมัติ' บันทึกภายใน: เฉพาะ admin และผู้ที่ถูกตั้งเป็นผู้ตรวจสอบ/ผู้อนุมัติ"""
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_staff:
        return True
    if user.groups.filter(name__in=['Internal Memo Reviewer', 'Internal Memo Approver']).exists():
        return True
    from ..models import user_detail
    return user_detail.objects.filter(user_id=user.id, cm__cm_name='ผู้ดูแลระบบ').exists()
