import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Case, Count, F, FloatField, Max, Sum, When
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .. import ecount
from ..constant import defaultTitle
from ..functions import checkpermi, dateTimeNow
from ..models import (
    category_program_permission,
    ecount_api_setting,
    register_payment_items,
    transfer_data_log,
    user_detail,
    user_group,
)

DAILY_SALES_ROUTE = 'transfer-data/daily-sales'
ECOUNT_SETTING_ROUTE = 'settings/ecount-api'
ECOUNT_LOGIN_FIELDS = ('login_url', 'com_code', 'user_id', 'lan_type', 'zone')
# ลูกค้า พนักงาน คลัง และโปรเจกต์ใน Ecount ที่ใช้กับเอกสารขายเงินสดรายวัน
ECOUNT_SALE_DEFAULTS = {
    'CUST': 'C1826',
    'EMP_CD': '00012',
    'WH_CD': '00018',
    'PJT_CD': 'TZ260001',
}
# รายการขายตัวอย่างสำหรับปุ่มทดสอบส่ง API
ECOUNT_TEST_SALE = {
    'UPLOAD_SER_NO': '1',
    **ECOUNT_SALE_DEFAULTS,
    'PROD_CD': '1100052',
    'QTY': '1',
    'PRICE': '100',
    'USER_PRICE_VAT': '',
    'SUPPLY_AMT': '100',
    'SUPPLY_AMT_F': '',
    'VAT_AMT': '7',
    'REMARKS': 'ทดสอบ',
}


def _get_cm_id(request):
    try:
        return user_detail.objects.get(user_id=request.user.id).cm_id
    except user_detail.DoesNotExist:
        return 0


def _base_context(cm_id):
    groups = category_program_permission.objects.filter(cm_id=cm_id).values(
        'group_value', 'group_label'
    ).annotate(dcount=Count('group_value')).order_by('group_label')
    menu = []
    for group in groups:
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=group['group_value']
        ).order_by('page_label')
        menu.append({**group, 'children': children})
    return {'title': defaultTitle, 'listMenuPermission': menu}


def _parse_date(value):
    try:
        return datetime.strptime(value or '', '%Y-%m-%d').date()
    except ValueError:
        return date.today()


def _date_range(request):
    start = _parse_date(request.GET.get('start'))
    end = _parse_date(request.GET.get('end'))
    return (end, start) if start > end else (start, end)


def _daily_sales(module, start, end):
    """ยอดเงินสดที่รับจริงต่อวัน แยกตาม Item code ใช้เกณฑ์เดียวกับรายงานใบเสร็จ (เฉพาะบิลเงินสดที่ไม่ถูกยกเลิก นับตามวันที่ออกใบเสร็จ)"""
    # Deposit เก็บราคาเต็มไว้ใน rpi_price_result เงินที่รับจริงอยู่ใน rpi_price_pay ส่วนประเภทอื่นอยู่ใน rpi_pay
    received = Case(
        When(type_payment='Deposit', then=F('rpi_price_pay')),
        default=F('rpi_pay'),
        output_field=FloatField(),
    )
    rows = list(
        register_payment_items.objects.filter(
            rp__active=1,
            rp__status_bill='Y',
            rp__register__pay_type=1,
            rp__register__module=module,
            rp__crt_date__date__gte=start,
            rp__crt_date__date__lte=end,
        )
        .annotate(sale_date=TruncDate('rp__crt_date'))
        .values('sale_date', 'rpi_code')
        .annotate(
            rpi_name=Max('rpi_name'),
            total_bill=Count('rp_id', distinct=True),
            dis=Sum('rpi_price_discount'),
            vat=Sum('rpi_price_vat'),
            result=Sum(received),
        )
        .order_by('sale_date', 'rpi_code')
    )
    for row in rows:
        row['total'] = (row['result'] or 0) - (row['vat'] or 0)
    return rows


def _day_total(rows):
    return round(sum(row['result'] or 0 for row in rows), 2)


def _with_transfer_status(day, log):
    day['log'] = log
    # ยอดเปลี่ยนหลังส่ง เช่น มีใบเสร็จเพิ่มหรือยกเลิกบิล ต้องส่งใหม่
    day['changed'] = log is not None and log.amount != day['subtotal']
    return day


def _group_by_day(module, rows):
    days = []
    for row in rows:
        if not days or days[-1]['sale_date'] != row['sale_date']:
            days.append({'sale_date': row['sale_date'], 'rows': []})
        days[-1]['rows'].append(row)
    logs = {
        log.sale_date: log
        for log in transfer_data_log.objects.filter(
            module=module, sale_date__in=[day['sale_date'] for day in days]
        ).select_related('sent_by')
    }
    for day in days:
        day['subtotal'] = _day_total(day['rows'])
        _with_transfer_status(day, logs.get(day['sale_date']))
    return days


def _today_status(module):
    today = date.today()
    rows = _daily_sales(module, today, today)
    log = transfer_data_log.objects.filter(
        module=module, sale_date=today
    ).select_related('sent_by').first()
    return _with_transfer_status(
        {'sale_date': today, 'has_sales': bool(rows), 'subtotal': _day_total(rows)}, log
    )


@login_required(login_url='/login')
def daily_sales(request):
    cm_id = _get_cm_id(request)
    if not checkpermi(DAILY_SALES_ROUTE, cm_id):
        return render(request, '403.html', status=403)
    try:
        module = user_group.objects.get(user=request.user.id).module
    except user_group.DoesNotExist:
        return render(request, '404.html')

    start, end = _date_range(request)
    days = _group_by_day(module, _daily_sales(module, start, end))
    context = _base_context(cm_id)
    context.update({
        'days': days,
        'today_status': _today_status(module),
        'total_sum': sum(day['subtotal'] for day in days),
        'start': start.isoformat(),
        'end': end.isoformat(),
    })
    return render(request, 'transfer_data/daily_sales.html', context)


@login_required(login_url='/login')
def daily_sales_export(request):
    if not checkpermi(DAILY_SALES_ROUTE, _get_cm_id(request)):
        return render(request, '403.html', status=403)
    try:
        module = user_group.objects.get(user=request.user.id).module
    except user_group.DoesNotExist:
        return render(request, '404.html')

    start, end = _date_range(request)
    rows = _daily_sales(module, start, end)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = (
        f'attachment; filename="daily_sales_{start:%Y%m%d}_{end:%Y%m%d}.csv"'
    )
    # BOM ให้ Excel เปิดภาษาไทยได้ถูกต้อง
    response.write('﻿')
    writer = csv.writer(response)
    writer.writerow([
        'วันที่', 'Item code', 'หลักสูตร', 'จำนวนใบเสร็จ',
        'มูลค่าก่อน VAT', 'ส่วนลด', 'ภาษีมูลค่าเพิ่ม', 'ยอดเงินสดรับ',
    ])
    for row in rows:
        writer.writerow([
            row['sale_date'].isoformat(),
            row['rpi_code'],
            row['rpi_name'],
            row['total_bill'],
            f"{row['total'] or 0:.2f}",
            f"{row['dis'] or 0:.2f}",
            f"{row['vat'] or 0:.2f}",
            f"{row['result'] or 0:.2f}",
        ])
    return response


@login_required(login_url='/login')
@require_POST
def daily_sales_mark(request):
    if not checkpermi(DAILY_SALES_ROUTE, _get_cm_id(request)):
        return render(request, '403.html', status=403)
    try:
        module = user_group.objects.get(user=request.user.id).module
    except user_group.DoesNotExist:
        return render(request, '404.html')

    sale_date = _parse_date(request.POST.get('sale_date'))
    if request.POST.get('action') == 'cancel':
        transfer_data_log.objects.filter(module=module, sale_date=sale_date).delete()
    else:
        rows = _daily_sales(module, sale_date, sale_date)
        if rows:
            transfer_data_log.objects.update_or_create(
                module=module,
                sale_date=sale_date,
                defaults={
                    'amount': _day_total(rows),
                    'sent_by': request.user,
                    'sent_at': dateTimeNow(),
                },
            )
    query = urlencode({
        'start': request.POST.get('start', ''),
        'end': request.POST.get('end', ''),
    })
    return redirect(f'/transfer-data/daily-sales?{query}')


@login_required(login_url='/login')
@require_POST
def daily_sales_test_send(request):
    """ทดสอบส่งรายการขายตัวอย่าง 1 รายการไป Ecount แสดง request/response ไม่บันทึกสถานะการส่ง"""
    if not checkpermi(DAILY_SALES_ROUTE, _get_cm_id(request)):
        return JsonResponse({'ok': False, 'message': 'ไม่มีสิทธิ์ใช้งาน'}, status=403)
    try:
        module = user_group.objects.get(user=request.user.id).module
    except user_group.DoesNotExist:
        return JsonResponse({'ok': False, 'message': 'ไม่พบ module ของผู้ใช้'}, status=404)

    sale_list = [{'BulkDatas': ECOUNT_TEST_SALE}]
    result = {'ok': False, 'request': {'SaleList': sale_list}, 'response': None}
    setting = ecount_api_setting.objects.filter(module=module).first()
    if setting is None:
        return JsonResponse({**result, 'message': 'กรุณาบันทึกการตั้งค่า API Ecount ก่อน'})
    try:
        payload, relogged = ecount.save_sale(setting, sale_list)
    except ecount.EcountError as error:
        return JsonResponse({**result, 'message': str(error), 'response': error.payload})
    data = payload.get('Data') if isinstance(payload, dict) else None
    data = data if isinstance(data, dict) else {}
    ok = bool(data.get('SuccessCnt')) and not data.get('FailCnt')
    message = (
        f"Ecount ตอบกลับ สำเร็จ {data.get('SuccessCnt', 0)} รายการ ล้มเหลว {data.get('FailCnt', 0)} รายการ"
        if data else 'Ecount ไม่รับข้อมูล ดูรายละเอียดใน response'
    )
    if relogged:
        message = 'ขอ Session ใหม่จาก Ecount แล้วส่งซ้ำ: ' + message
    return JsonResponse({**result, 'ok': ok, 'message': message, 'response': payload})


def _clean_ecount_setting(api_url, tax, login_values):
    errors = {}
    try:
        URLValidator(schemes=['https'])(api_url)
    except ValidationError:
        errors['api_url'] = 'กรุณากรอก URL ที่ขึ้นต้นด้วย https://'
    if len(api_url) > 255:
        errors['api_url'] = 'URL ยาวเกิน 255 ตัวอักษร'
    if login_values['login_url']:
        try:
            URLValidator(schemes=['https'])(login_values['login_url'])
        except ValidationError:
            errors['login_url'] = 'กรุณากรอก URL ที่ขึ้นต้นด้วย https://'
    for field, value in login_values.items():
        if len(value) > ecount_api_setting._meta.get_field(field).max_length:
            errors[field] = 'ข้อมูลยาวเกินกำหนด'
    try:
        tax_value = round(Decimal(tax), 2)
        if not 0 <= tax_value <= 100:
            raise InvalidOperation
    except InvalidOperation:
        tax_value = None
        errors['tax'] = 'กรุณากรอกภาษีเป็นตัวเลข 0 ถึง 100'
    return tax_value, errors


@login_required(login_url='/login')
def ecount_api_setting_form(request):
    cm_id = _get_cm_id(request)
    if not request.user.is_staff or not checkpermi(ECOUNT_SETTING_ROUTE, cm_id):
        return render(request, '403.html', status=403)
    try:
        module = user_group.objects.get(user=request.user.id).module
    except user_group.DoesNotExist:
        return render(request, '404.html')

    setting = ecount_api_setting.objects.filter(module=module).first()
    api_url = setting.api_url if setting else ''
    tax = setting.tax if setting else ecount_api_setting._meta.get_field('tax').default
    cert_key = setting.api_cert_key if setting else ''
    token = setting.token if setting else ''
    login_values = {
        field: getattr(setting, field) if setting else ecount_api_setting._meta.get_field(field).default
        for field in ECOUNT_LOGIN_FIELDS
    }
    errors = {}

    if request.method == 'POST':
        api_url = request.POST.get('api_url', '').strip()
        tax = request.POST.get('tax', '').strip()
        login_values = {field: request.POST.get(field, '').strip() for field in ECOUNT_LOGIN_FIELDS}
        login_values['lan_type'] = login_values['lan_type'] or 'th-TH'
        cert_key = request.POST.get('api_cert_key', '').strip()
        token = request.POST.get('token', '').strip()
        tax_value, errors = _clean_ecount_setting(api_url, tax, login_values)
        if len(cert_key) > ecount_api_setting._meta.get_field('api_cert_key').max_length:
            errors['api_cert_key'] = 'ข้อมูลยาวเกินกำหนด'
        if not errors:
            values = {
                'api_url': api_url,
                'tax': tax_value,
                'updated_by': request.user,
                'upd_date': dateTimeNow(),
                'api_cert_key': cert_key,
                'token': token,
                **login_values,
            }
            ecount_api_setting.objects.update_or_create(module=module, defaults=values)
            messages.success(request, 'บันทึกการตั้งค่า API Ecount เรียบร้อยแล้ว')
            return redirect('ecount_api_setting_form')

    context = _base_context(cm_id)
    context.update({
        'api_url': api_url,
        'tax': tax,
        'token': token,
        'api_cert_key': cert_key,
        'setting': setting,
        'errors': errors,
        **login_values,
    })
    return render(request, 'settingdes/ecount_api_form.html', context)


@login_required(login_url='/login')
@require_POST
def ecount_api_login(request):
    if not request.user.is_staff or not checkpermi(ECOUNT_SETTING_ROUTE, _get_cm_id(request)):
        return render(request, '403.html', status=403)
    try:
        module = user_group.objects.get(user=request.user.id).module
    except user_group.DoesNotExist:
        return render(request, '404.html')

    setting = ecount_api_setting.objects.filter(module=module).first()
    if setting is None:
        return JsonResponse({'ok': False, 'message': 'กรุณาบันทึกการตั้งค่า API Ecount ก่อน', 'response': None})
    try:
        setting.token, payload = ecount.login(setting)
    except ecount.EcountError as error:
        return JsonResponse({'ok': False, 'message': str(error), 'response': error.payload})
    setting.updated_by = request.user
    setting.upd_date = dateTimeNow()
    setting.save(update_fields=['token', 'updated_by', 'upd_date'])
    return JsonResponse({'ok': True, 'message': 'ขอ Session จาก Ecount สำเร็จ', 'response': payload})
