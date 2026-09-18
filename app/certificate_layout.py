"""Shared A4 landscape layout and strictly validated editor properties (millimetres)."""
import math
import re
from urllib.parse import quote

from django.core.exceptions import ValidationError
from django.templatetags.static import static
from django.utils import formats, translation

from .templatetags.ex_functions import thai_date


def certificate_elements(language, student=None, event=None):
    elements = []

    def add(key, label, kind, value, x, y, w, h, size=18, bold=False, opacity=1):
        elements.append(dict(id=key, label=label, kind=kind, value=value,
                             x=x, y=y, w=w, h=h, size=size, bold=bold,
                             opacity=opacity, align='center', color='#000000', font='Sarabun',
                             visible=True, locked=False, z=len(elements)))

    # Match the Thai print template's 40%-wide corner artwork, preserving its ratio.
    corner_w, corner_h = (118.8, 72.62) if language == 'th' else (106, 40)
    add('header', 'รูปตกแต่งด้านบน', 'image', static('images/cer_head_rm.png'), 0, 0, corner_w, corner_h)
    add('footer', 'รูปตกแต่งด้านล่าง', 'image', static('images/cer_footer_rm.png'), 297 - corner_w, 210 - corner_h, corner_w, corner_h)
    add('watermark', 'ลายน้ำ', 'image', static('images/newlogo_resize.png'), 85, 50, 127, 93, opacity=.15)
    add('customer_logo', 'โลโก้ลูกค้า', 'image', event.ev_logo.url if event and event.ev_logo else '', 5, 5, 27, 27)
    add('system_logo', 'โลโก้ Training', 'image', static('images/newlogo_resize.png'), 263, 5, 29, 25)
    add('company_logo', 'โลโก้บริษัท', 'image', static('images/id.png'), 261, 178, 25, 25)
    add('title', 'หัวข้อใบประกาศ', 'text', 'Certificate of Achievement', 40, 9, 217, 15, 30, True)
    add('intro', 'ข้อความรับรอง', 'text', 'This is to certify that', 40, 26, 217, 12, 21, True)
    name = 'นาย ตัวอย่าง นามสกุล' if language == 'th' else 'Mr. Example Student'
    if student:
        name = ' '.join(str(getattr(student, 'student_' + part + '_' + language) or '') for part in ('prefix', 'firstname', 'lastname'))
    add('student_name', 'ชื่อผู้เรียน (อัตโนมัติ)', 'dynamic', name, 30, 42, 237, 15, 26, True)
    add('completion', 'ข้อความผ่านการอบรม', 'text', 'has successfully complete', 40, 60, 217, 10, 18)
    course_name = (event.course.course_name if language == 'th' else event.course.course_name_eng) if event else ('หลักสูตรตัวอย่าง' if language == 'th' else 'Example Training Course')
    add('course_name', 'ชื่อหลักสูตร (อัตโนมัติ)', 'dynamic', course_name or '', 25, 73, 247, 24, 26, True)
    date_text = '18 กันยายน 2569' if language == 'th' else '18 September 2026'
    if event:
        if language == 'th':
            date_text = thai_date(event.ev_date_end) or ''
        else:
            with translation.override('en'):
                date_text = formats.date_format(event.ev_date_start, 'd F Y') if event.ev_date_start else ''
    add('date', 'วันที่อบรม (อัตโนมัติ)', 'dynamic', date_text, 40, 98, 217, 13, 26, True)
    add('divider', 'เส้นคั่น', 'line', '', 74, 112, 149, 1)
    for key, label, value, y in [
        ('institute', 'สถาบัน', 'Conducted by : ID DRIVER INSTITUTE', 115),
        ('license_transport', 'ใบอนุญาตขนส่ง', 'Permit License NO. 4050007/2550 by Department of Land Transport', 124),
        ('license_education', 'ใบอนุญาตศึกษา', 'Permit License no. ขก.08/2550 by Ministry of Educatinon', 133),
        ('contact', 'ข้อมูลติดต่อ', 'Line : @idtz Email : id.trainingcenter@iddrives.co.th', 142),
    ]:
        add(key, label, 'text', value, 25, y, 247, 9, 16)
    add('signature', 'ลายเซ็น', 'image', static('images/signature.png'), 116, 152, 65, 23)
    add('signer', 'ชื่อผู้ลงนาม', 'text', 'Mr. Chalermchai Hoonnakarinthon', 45, 176, 207, 10, 21, True)
    add('position', 'ตำแหน่งผู้ลงนาม', 'text', 'Vice President', 45, 187, 207, 10, 21, True)
    add('logos', 'โลโก้ท้ายใบประกาศ', 'image', static('images/all-logo-04.PNG'), 79, 199, 139, 10)
    code = str(student.student_code) if student else 'TZ-EXAMPLE-001'
    add('qr', 'QR Code', 'image', 'https://quickchart.io/qr?text=' + quote(code, safe='') + '&size=200', 5, 174, 21, 21)
    add('number', 'เลขใบประกาศ (อัตโนมัติ)', 'dynamic', 'Certificate No. ' + code, 3, 196, 70, 5, 9)
    expiry = event.ev_expired_cer_date.strftime('%d/%m/%Y') if event and event.ev_expired_cer_date else ''
    add('expiry', 'วันหมดอายุ (อัตโนมัติ)', 'dynamic', 'Expired Date. ' + expiry, 3, 202, 70, 5, 9)
    return elements


def validate_layout(layout, language):
    defaults = {e['id']: e for e in certificate_elements(language)}
    if not isinstance(layout, dict) or set(layout) - set(defaults):
        raise ValidationError('ข้อมูลองค์ประกอบไม่ถูกต้อง')
    bounds = {'x': (0, 297), 'y': (0, 210), 'w': (1, 297), 'h': (1, 210),
              'size': (6, 100), 'opacity': (0, 1), 'z': (0, 100)}
    clean = {}
    for key, props in layout.items():
        allowed = set(bounds) | {'align', 'color', 'visible', 'locked', 'bold', 'font'}
        if defaults[key]['kind'] == 'text':
            allowed.add('text')
        if not isinstance(props, dict) or set(props) - allowed:
            raise ValidationError('คุณสมบัติไม่ถูกต้อง')
        for prop, value in props.items():
            if prop in bounds:
                low, high = bounds[prop]
                if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
                    raise ValidationError('ค่าตำแหน่งหรือขนาดอยู่นอกช่วง')
            elif prop in ('visible', 'locked', 'bold') and type(value) is not bool:
                raise ValidationError('ค่าตัวเลือกไม่ถูกต้อง')
            elif prop == 'align' and value not in ('left', 'center', 'right'):
                raise ValidationError('การจัดแนวไม่ถูกต้อง')
            elif prop == 'font' and value not in ('Sarabun', 'Tahoma', 'Arial', 'serif'):
                raise ValidationError('ฟอนต์ไม่ถูกต้อง')
            elif prop == 'color' and (not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value)):
                raise ValidationError('สีไม่ถูกต้อง')
            elif prop == 'text' and (not isinstance(value, str) or len(value) > 2000):
                raise ValidationError('ข้อความยาวเกิน 2000 ตัวอักษร')
        merged = {**defaults[key], **props}
        if merged['x'] + merged['w'] > 297.01 or merged['y'] + merged['h'] > 210.01:
            raise ValidationError('องค์ประกอบต้องอยู่ภายในกระดาษ')
        clean[key] = props
    return clean


def render_elements(language, layout, student=None, event=None):
    elements = certificate_elements(language, student, event)
    for element in elements:
        element.update(layout.get(element['id'], {}))
        if element['kind'] == 'text' and 'text' in element:
            element['value'] = element['text']
    return elements
