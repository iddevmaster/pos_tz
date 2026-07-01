import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from ..constant import defaultTitle
from ..functions import dateTimeNow, checkpermi
from ..models import (
    User,
    category_program_permission,
    user_detail,
    course,
    teacher,
    register_main,
    register_payment,
    register_payment_items,
    commission_policy,
    commission_condition,
    commission_payee,
    commission_rule,
    commission_rule_allocation,
    commission_plan,
    commission_plan_line,
    commission_plan_allocation,
    commission_payout,
)


def _menu_context(request):
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
        objMenu.append({'group_label': rs['group_label'],
                         'group_value': rs['group_value'], 'children': children})
    return cm_id, objMenu


# ยอดฐานคำนวณค่าคอม = ยอดบิลหลังหัก vat ออก (สูตรเดียวกับที่ใช้อยู่เดิมใน finance.withdraw_list_one_com)
def _base_amount(rpi):
    price = rpi.rpi_price_result or 0
    after_vat = (price * 7) / 107
    return price - after_vat


def _policy_tree(rows_by_condition):
    """
    rows_by_condition: dict condition_id -> extra dict to merge into the condition's json
    คืนค่าเป็น list ของนโยบายเรียงตาม seq พร้อมเงื่อนไขย่อยเรียงตาม seq
    """
    tree = []
    policies = commission_policy.objects.filter(active=1).order_by('seq').prefetch_related('conditions')
    for p in policies:
        conditions = []
        for c in p.conditions.filter(active=1).order_by('seq'):
            row = {
                'condition_id': c.condition_id,
                'condition_code': c.condition_code,
                'condition_name': c.condition_name,
                'calc_type': c.calc_type,
            }
            row.update(rows_by_condition.get(c.condition_id, {}))
            conditions.append(row)
        tree.append({
            'policy_id': p.policy_id,
            'policy_code': p.policy_code,
            'policy_name': p.policy_name,
            'conditions': conditions,
        })
    return tree


# =====================================================================
# หน้า: ตั้งค่าค่าคอมตามสินค้า (อัตราเริ่มต้น per course x condition)
# =====================================================================
@login_required(login_url='/login')
def rules_page(request):
    cm_id, objMenu = _menu_context(request)
    courses = course.objects.filter(cancelled=1, active=1).order_by('course_code')
    payees = commission_payee.objects.filter(active=1).order_by('payee_type', 'payee_name')
    context = {'title': defaultTitle, 'listMenuPermission': objMenu, 'courses': courses, 'payees': payees}
    return render(request, 'commission/rules.html', context)


@csrf_exempt
def api_rules_list(request):
    data = json.loads(request.body)
    course_id = data.get('course_id')

    rows_by_condition = {}
    rules = commission_rule.objects.filter(course_id=course_id).prefetch_related('allocations__payee')
    for r in rules:
        allocations = [{'alloc_id': a.alloc_id, 'payee_id': a.payee_id,
                         'payee_name': a.payee.payee_name, 'percent': a.percent} for a in r.allocations.all()]
        rows_by_condition[r.condition_id] = {
            'rule_id': r.rule_id, 'rate': r.rate, 'active': bool(r.active), 'allocations': allocations,
        }

    return JsonResponse({'policies': _policy_tree(rows_by_condition)}, safe=False)


@csrf_exempt
def api_rules_save(request):
    data = json.loads(request.body)
    course_id = data.get('course_id')
    condition_id = data.get('condition_id')
    rate = data.get('rate')
    active = data.get('active')

    rule, _created = commission_rule.objects.get_or_create(
        course_id=course_id, condition_id=condition_id,
        defaults={'rate': rate or 0, 'active': 1 if active else 0, 'crt_date': dateTimeNow(), 'upd_date': dateTimeNow()})
    if not _created:
        if rate is not None:
            rule.rate = rate
        if active is not None:
            rule.active = 1 if active else 0
        rule.upd_date = dateTimeNow()
        rule.save()

    return JsonResponse({'status': 200, 'rule_id': rule.rule_id})


@csrf_exempt
def api_rules_allocation_add(request):
    data = json.loads(request.body)
    rule_id = data.get('rule_id')
    payee_id = data.get('payee_id')
    percent = data.get('percent')

    alloc = commission_rule_allocation.objects.create(
        rule_id=rule_id, payee_id=payee_id, percent=percent or 0)
    return JsonResponse({'status': 200, 'alloc_id': alloc.alloc_id})


@csrf_exempt
def api_rules_allocation_delete(request):
    data = json.loads(request.body)
    alloc_id = data.get('alloc_id')
    commission_rule_allocation.objects.filter(alloc_id=alloc_id).delete()
    return JsonResponse({'status': 200})


# =====================================================================
# หน้า: ผู้รับเงิน (payee master)
# =====================================================================
@login_required(login_url='/login')
def payees_page(request):
    cm_id, objMenu = _menu_context(request)
    payees = commission_payee.objects.filter(active=1).order_by('payee_type', 'payee_name')
    context = {'title': defaultTitle, 'listMenuPermission': objMenu, 'payees': payees}
    return render(request, 'commission/payees.html', context)


@csrf_exempt
def api_payee_create(request):
    data = json.loads(request.body)
    payee = commission_payee.objects.create(
        payee_type=data.get('payee_type'),
        payee_name=data.get('payee_name'),
        user_id=data.get('user_id') or None,
        teacher_id=data.get('teacher_id') or None,
        bank_name=data.get('bank_name'),
        bank_account=data.get('bank_account'),
        active=1,
        crt_date=dateTimeNow(),
        upd_date=dateTimeNow(),
    )
    return JsonResponse({'status': 200, 'payee_id': payee.payee_id})


@csrf_exempt
def api_payee_delete(request):
    data = json.loads(request.body)
    commission_payee.objects.filter(payee_id=data.get('payee_id')).update(active=0)
    return JsonResponse({'status': 200})


# =====================================================================
# หน้า: บิลขาย -> กำหนดแผนค่าคอม (กำหนดได้ก็ต่อเมื่อบิลปิดการขาย-ขายสำเร็จแล้วเท่านั้น)
# =====================================================================
def _bill_is_sold(rpi):
    """บิลถือว่า 'ขายสำเร็จ' เมื่อออกใบเสร็จแล้ว (status_bill='Y') และปิดการขายแล้ว (close_the_sale=1)"""
    rp = register_payment.objects.filter(rp_id=rpi.rp_id).first()
    reg = rpi.register
    return bool(rp and rp.status_bill == 'Y' and reg and reg.close_the_sale == 1)


@login_required(login_url='/login')
def bills_page(request):
    cm_id, objMenu = _menu_context(request)
    rows = []
    items = register_payment_items.objects.select_related('register', 'register__course', 'rp').order_by('-rpi_id')[:200]
    for rpi in items:
        if not _bill_is_sold(rpi):
            continue
        plan = commission_plan.objects.filter(rpi=rpi).first()
        rows.append({
            'rpi_id': rpi.rpi_id,
            'rp_doc_number': rpi.rp.rp_doc_number if rpi.rp else '-',
            'register_number': rpi.register.register_number,
            'course_name': rpi.register.course.course_name if rpi.register.course else '-',
            'amount': rpi.rpi_price_result,
            'plan_id': plan.plan_id if plan else None,
            'is_locked': bool(plan.is_locked) if plan else False,
        })
    payees_all = commission_payee.objects.filter(active=1).order_by('payee_type', 'payee_name')
    context = {'title': defaultTitle, 'listMenuPermission': objMenu, 'rows': rows, 'payees_all': payees_all}
    return render(request, 'commission/bills.html', context)


@csrf_exempt
def api_plan_open(request):
    data = json.loads(request.body)
    rpi_id = data.get('rpi_id')
    rpi = register_payment_items.objects.select_related('register', 'register__course').get(rpi_id=rpi_id)

    if not _bill_is_sold(rpi):
        return JsonResponse({'status': 400, 'message': 'บิลนี้ยังไม่ปิดการขาย-ขายสำเร็จ ไม่สามารถกำหนดค่าคอมได้'}, status=400)

    plan, created = commission_plan.objects.get_or_create(
        rpi=rpi, defaults={'register': rpi.register, 'crt_date': dateTimeNow(), 'upd_date': dateTimeNow()})

    if created and rpi.register.course_id:
        # seed แผนค่าคอมจากอัตรากลางของสินค้า ณ เวลาที่เปิดแผน (แก้ไขต่อได้อิสระ ไม่กระทบอัตรากลาง)
        rules = commission_rule.objects.filter(course_id=rpi.register.course_id).prefetch_related('allocations')
        for r in rules:
            line = commission_plan_line.objects.create(
                plan=plan, condition_id=r.condition_id, rate=r.rate, active=r.active, source='DEFAULT')
            for a in r.allocations.all():
                commission_plan_allocation.objects.create(
                    line=line, payee_id=a.payee_id, percent=a.percent)

    return JsonResponse({'status': 200, 'plan_id': plan.plan_id, 'is_locked': bool(plan.is_locked)})


@csrf_exempt
def api_plan_detail(request):
    data = json.loads(request.body)
    plan_id = data.get('plan_id')
    plan = commission_plan.objects.get(plan_id=plan_id)

    rows_by_condition = {}
    lines = commission_plan_line.objects.filter(plan=plan).prefetch_related('allocations__payee')
    for l in lines:
        allocations = [{'alloc_id': a.alloc_id, 'payee_id': a.payee_id,
                         'payee_name': a.payee.payee_name, 'percent': a.percent} for a in l.allocations.all()]
        rows_by_condition[l.condition_id] = {
            'line_id': l.line_id, 'rate': l.rate, 'active': bool(l.active),
            'source': l.source, 'allocations': allocations,
        }

    payouts = []
    for po in commission_payout.objects.filter(plan=plan).select_related('condition', 'payee'):
        payouts.append({
            'payout_id': po.payout_id,
            'condition_code': po.condition.condition_code,
            'condition_name': po.condition.condition_name,
            'rate': po.rate,
            'payee_name': po.payee.payee_name if po.payee else None,
            'payee_percent': po.payee_percent,
            'payout_amount': po.payout_amount,
            'status': po.status,
        })

    return JsonResponse({
        'status': 200,
        'plan_id': plan.plan_id,
        'is_locked': bool(plan.is_locked),
        'policies': _policy_tree(rows_by_condition),
        'payouts': payouts,
    }, safe=False)


@csrf_exempt
def api_plan_line_save(request):
    data = json.loads(request.body)
    plan = commission_plan.objects.get(plan_id=data.get('plan_id'))
    if plan.is_locked:
        return JsonResponse({'status': 400, 'message': 'แผนนี้ถูกล็อกแล้ว กรุณาปลดล็อกก่อนแก้ไข'}, status=400)

    line, _created = commission_plan_line.objects.get_or_create(
        plan=plan, condition_id=data.get('condition_id'),
        defaults={'rate': data.get('rate') or 0, 'active': 1 if data.get('active') else 0, 'source': 'CUSTOM'})
    if not _created:
        if data.get('rate') is not None:
            line.rate = data.get('rate')
        if data.get('active') is not None:
            line.active = 1 if data.get('active') else 0
        line.source = 'CUSTOM'
        line.save()

    return JsonResponse({'status': 200, 'line_id': line.line_id})


@csrf_exempt
def api_plan_allocation_add(request):
    data = json.loads(request.body)
    line = commission_plan_line.objects.select_related('plan').get(line_id=data.get('line_id'))
    if line.plan.is_locked:
        return JsonResponse({'status': 400, 'message': 'แผนนี้ถูกล็อกแล้ว กรุณาปลดล็อกก่อนแก้ไข'}, status=400)

    alloc = commission_plan_allocation.objects.create(
        line=line, payee_id=data.get('payee_id'), percent=data.get('percent') or 0)
    return JsonResponse({'status': 200, 'alloc_id': alloc.alloc_id})


@csrf_exempt
def api_plan_allocation_delete(request):
    data = json.loads(request.body)
    commission_plan_allocation.objects.filter(alloc_id=data.get('alloc_id')).delete()
    return JsonResponse({'status': 200})


@csrf_exempt
def api_plan_lock(request):
    data = json.loads(request.body)
    plan = commission_plan.objects.select_related('rpi').get(plan_id=data.get('plan_id'))
    if plan.is_locked:
        return JsonResponse({'status': 400, 'message': 'แผนนี้ถูกล็อกไปแล้ว'}, status=400)

    base_amount = _base_amount(plan.rpi)
    lines = commission_plan_line.objects.filter(plan=plan, active=1).prefetch_related('allocations')
    for line in lines:
        if not line.rate:
            continue
        amount = base_amount * line.rate / 100
        allocations = list(line.allocations.all())
        if allocations:
            for a in allocations:
                commission_payout.objects.create(
                    plan=plan, condition_id=line.condition_id, payee_id=a.payee_id,
                    rate=line.rate, base_amount=base_amount, payee_percent=a.percent,
                    payout_amount=amount * a.percent / 100, status='PENDING',
                    crt_date=dateTimeNow(), upd_date=dateTimeNow())
        else:
            commission_payout.objects.create(
                plan=plan, condition_id=line.condition_id, payee=None,
                rate=line.rate, base_amount=base_amount, payee_percent=None,
                payout_amount=amount, status='PENDING',
                crt_date=dateTimeNow(), upd_date=dateTimeNow())

    plan.is_locked = 1
    plan.locked_by = request.user if request.user.is_authenticated else None
    plan.locked_at = dateTimeNow()
    plan.upd_date = dateTimeNow()
    plan.save()

    return JsonResponse({'status': 200})


@csrf_exempt
def api_plan_unlock(request):
    data = json.loads(request.body)
    plan = commission_plan.objects.get(plan_id=data.get('plan_id'))

    if commission_payout.objects.filter(plan=plan).exclude(status='PENDING').exists():
        return JsonResponse({'status': 400, 'message': 'มีรายการที่อนุมัติ/จ่ายแล้ว ไม่สามารถปลดล็อกแผนนี้ได้'}, status=400)

    commission_payout.objects.filter(plan=plan).delete()
    plan.is_locked = 0
    plan.locked_by = None
    plan.locked_at = None
    plan.upd_date = dateTimeNow()
    plan.save()

    return JsonResponse({'status': 200})


@csrf_exempt
def api_payout_status(request):
    data = json.loads(request.body)
    payout = commission_payout.objects.get(payout_id=data.get('payout_id'))
    next_status = data.get('status')
    if next_status not in ('PENDING', 'APPROVED', 'PAID'):
        return JsonResponse({'status': 400, 'message': 'สถานะไม่ถูกต้อง'}, status=400)

    payout.status = next_status
    if next_status == 'APPROVED':
        payout.approved_by = request.user if request.user.is_authenticated else None
        payout.approved_at = dateTimeNow()
    if next_status == 'PAID':
        payout.paid_by = request.user if request.user.is_authenticated else None
        payout.paid_at = dateTimeNow()
    payout.upd_date = dateTimeNow()
    payout.save()

    return JsonResponse({'status': 200})
