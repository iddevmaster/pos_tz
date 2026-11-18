from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..constant import defaultTitle, thai_months
from ..models import register_main, register_payment, register_payment_items
from .user import _menu_context

THAI_MONTHS_SHORT = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.',
                     'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']


def _month_arg(value):
    """'2026-11' -> (2026, 11) ไม่ถูกต้อง -> เดือนปัจจุบัน"""
    today = date.today()
    try:
        y, m = (int(x) for x in (value or '').split('-'))
        if 2000 <= y <= 2100 and 1 <= m <= 12:
            return y, m
    except ValueError:
        pass
    return today.year, today.month


def _shift_month(y, m, delta):
    idx = y * 12 + (m - 1) + delta
    return idx // 12, idx % 12 + 1


def _bill_totals(regs):
    """ยอดสุทธิต่อบิล {register_id: {'payment': rp, 'total': float}}
    ใช้ใบเสร็จล่าสุดที่ active ของแต่ละบิล (บิลเครดิตที่แก้ไขจะมีใบเก่าที่ active=0)
    ยอดสุทธิ = rpi_price_total + rpi_price_vat (เหมือนหน้าพิมพ์บิล)"""
    latest = {}
    for rp in register_payment.objects.filter(register__in=regs, active=1).order_by('rp_id'):
        latest[rp.register_id] = rp
    totals = {rid: {'payment': rp, 'total': 0.0} for rid, rp in latest.items()}
    rp_to_reg = {rp.rp_id: rid for rid, rp in latest.items()}
    for it in register_payment_items.objects.filter(rp_id__in=rp_to_reg.keys()).values(
            'rp_id', 'rpi_price_total', 'rpi_price_vat'):
        totals[rp_to_reg[it['rp_id']]]['total'] += float(it['rpi_price_total'] or 0) + float(it['rpi_price_vat'] or 0)
    return totals


@login_required(login_url='/login')
def my_sales(request):
    """สรุปยอดขายของตัวเอง (register_main.seller = user)
    เป็นหน้าแรกของคนที่ไม่มีสิทธิ์เปิดการขาย และเปิดดูได้ทุกคน"""
    user_id = request.user.id
    year, month = _month_arg(request.GET.get('month'))
    today = date.today()

    mine = register_main.objects.filter(seller_id=user_id)

    # ---- เดือนที่เลือก ----
    month_regs = list(mine.filter(crt_date__year=year, crt_date__month=month)
                      .select_related('course').order_by('-crt_date'))
    confirmed = [r for r in month_regs if r.status == 'Y']
    totals = _bill_totals([r.register_id for r in confirmed])

    sold = [r for r in confirmed if r.close_the_sale != 2]  # ไม่นับขายไม่สำเร็จ
    total_sales = sum(totals.get(r.register_id, {}).get('total', 0) for r in sold)
    cash_total = sum(totals.get(r.register_id, {}).get('total', 0) for r in sold if r.pay_type == 1)
    credit_total = sum(totals.get(r.register_id, {}).get('total', 0) for r in sold if r.pay_type == 2)

    status_count = {
        'success': sum(1 for r in confirmed if r.close_the_sale == 1),
        'waiting': sum(1 for r in confirmed if r.close_the_sale == 0),
        'fail': sum(1 for r in confirmed if r.close_the_sale == 2),
        'quotation': sum(1 for r in month_regs if r.pay_type == 2 and r.status == 'N'),
    }

    # ---- เทียบเดือนก่อน ----
    py, pm = _shift_month(year, month, -1)
    prev_regs = list(mine.filter(crt_date__year=py, crt_date__month=pm, status='Y')
                     .exclude(close_the_sale=2).values_list('register_id', flat=True))
    prev_total = sum(v['total'] for v in _bill_totals(prev_regs).values())
    change_pct = ((total_sales - prev_total) / prev_total * 100) if prev_total else None

    # ---- แยกตามหลักสูตร ----
    by_course = {}
    for r in sold:
        name = r.course.course_name if r.course_id else '-'
        row = by_course.setdefault(name, {'name': name, 'bills': 0, 'total': 0.0})
        row['bills'] += 1
        row['total'] += totals.get(r.register_id, {}).get('total', 0)
    by_course = sorted(by_course.values(), key=lambda x: -x['total'])
    for row in by_course:
        row['pct'] = (row['total'] / total_sales * 100) if total_sales else 0

    # ---- แนวโน้ม 12 เดือน (สิ้นสุดที่เดือนที่เลือก) ----
    sy, sm = _shift_month(year, month, -11)
    trend_regs = list(mine.filter(status='Y', crt_date__gte=date(sy, sm, 1))
                      .exclude(close_the_sale=2)
                      .filter(crt_date__lt=date(*_shift_month(year, month, 1), 1))
                      .values_list('register_id', 'crt_date'))
    trend_totals = _bill_totals([rid for rid, _ in trend_regs])
    trend_map = {}
    for rid, crt in trend_regs:
        key = (crt.year, crt.month)
        trend_map[key] = trend_map.get(key, 0) + trend_totals.get(rid, {}).get('total', 0)
    trend = []
    for i in range(12):
        ty, tm = _shift_month(sy, sm, i)
        trend.append({'label': THAI_MONTHS_SHORT[tm - 1],
                      'year': ty + 543, 'total': trend_map.get((ty, tm), 0),
                      'current': (ty, tm) == (year, month)})
    trend_max = max((t['total'] for t in trend), default=0) or 1
    for t in trend:
        t['height'] = round(t['total'] / trend_max * 100, 1)

    # ---- รายการบิล ----
    # เลขที่เอกสาร/ลูกค้า: ดึงทุกบิลในเดือน (ไม่ใช่แค่ status Y) ใช้ใบที่ active ก่อน ไม่มีค่อยใช้ใบล่าสุด
    # (ใบเสนอราคาเครดิตที่รออนุมัติ status N เก็บ register_payment ไว้แบบ active=0)
    doc_rp = {}
    for rp in register_payment.objects.filter(
            register__in=[r.register_id for r in month_regs]).order_by('active', 'rp_id'):
        doc_rp[rp.register_id] = rp
    bills = []
    for r in month_regs:
        info = totals.get(r.register_id, {})
        rp = info.get('payment') or doc_rp.get(r.register_id)
        # แสดงเฉพาะบิลที่สมบูรณ์ (ทั้งเงินสด/เครดิต): ต้องมีสถานะ และมีใบเสร็จ/เลขที่เอกสารแล้ว
        # ที่ลงทะเบียนค้างไว้แต่ยังไม่บันทึกบิล (status ว่าง ไม่มี register_payment) ไม่ต้องแสดง
        if not r.status or not rp or not rp.rp_doc_number:
            continue
        is_event = r.is_event != 'N'
        bills.append({
            'reg': r,
            'doc': rp.rp_doc_number if rp else '-',
            'customer': rp.rp_name_customer if rp else '-',
            'total': info.get('total', 0),
            'history_url': ('/register/payment/history/' if is_event else '/salesnotevent/payment/history/') + str(r.register_id),
        })

    context = {
        'title': defaultTitle,
        'listMenuPermission': _menu_context(user_id),
        'month_value': '%04d-%02d' % (year, month),
        'month_label': '%s %d' % (thai_months[month - 1], year + 543),
        'is_current_month': (year, month) == (today.year, today.month),
        'total_sales': total_sales,
        'cash_total': cash_total,
        'credit_total': credit_total,
        'bill_count': len(sold),
        'avg_bill': (total_sales / len(sold)) if sold else 0,
        'prev_total': prev_total,
        'change_pct': change_pct,
        'status_count': status_count,
        'by_course': by_course,
        'trend': trend,
        'bills': bills,
    }
    return render(request, 'dashboard/my_sales.html', context)
