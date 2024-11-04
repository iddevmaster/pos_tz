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
        if path.strip('/') == item['value']:
            group_value = item['group_value']
            break
    print(group_value)
    # ส่งค่า group_value ไปยัง template
    return group_value