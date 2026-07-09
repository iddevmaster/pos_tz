import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from ..constant import defaultTitle
from ..functions import dateTimeNow, checkpermi
from django.db.models import Sum

from ..models import (
    User,
    category_program_permission,
    user_detail,
    course,
    teacher,
    course_event,
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
    commission_event_rule,
    commission_event_allocation,
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


def _users_json():
    import json as _json
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    return _json.dumps(
        [{'id': u.id, 'name': (f'{u.first_name} {u.last_name}'.strip() or u.username)} for u in users],
        ensure_ascii=False)


def _get_or_create_payee_for_user(user_id):
    """หา/สร้าง commission_payee ที่ผูกกับ auth_user คนนี้ (ผู้รับประเภท STAFF)"""
    user = User.objects.get(id=user_id)
    full_name = f'{user.first_name} {user.last_name}'.strip() or user.username
    payee, _created = commission_payee.objects.get_or_create(
        user_id=user_id,
        defaults={'payee_type': 'STAFF', 'payee_name': full_name,
                  'bank_name': '', 'bank_account': '',
                  'active': 1, 'crt_date': dateTimeNow(), 'upd_date': dateTimeNow()})
    return payee


# ยอดฐานคำนวณค่าคอม = ยอดบิลหลังหัก vat ออก (สูตรเดียวกับที่ใช้อยู่เดิมใน finance.withdraw_list_one_com)
def _base_amount(rpi):
    price = rpi.rpi_price_result or 0
    after_vat = (price * 7) / 107
    return price - after_vat


def _allowed_policy_codes(course_obj):
    """
    เลือกนโยบายที่จะแสดงตาม flag ของสินค้า (course):
    is_commission -> นโยบาย 1 (ค่า Commission IDC 3%)
    is_consultant -> นโยบาย 2 (จ่ายบุคคลภายนอก)
    is_operation  -> นโยบาย 3 (จ่ายค่าตอบแทนผู้ปฏิบัติงาน)
    ถ้าไม่ได้เลือกอันไหนเลย -> นโยบาย 4 (ค่า Commission IDC) เท่านั้น
    """
    if course_obj is None:
        return None
    codes = []
    if course_obj.is_commission:
        codes.append('1')
    if course_obj.is_consultant:
        codes.append('2')
    if course_obj.is_operation:
        codes.append('3')
    if not codes:
        codes = ['4']
    return codes


def _policy_tree(rows_by_condition, course_obj=None):
    """
    rows_by_condition: dict condition_id -> extra dict to merge into the condition's json
    course_obj: ถ้าระบุ จะกรองเฉพาะนโยบายที่เกี่ยวข้องกับสินค้านี้ตาม is_commission/is_operation/is_consultant
    คืนค่าเป็น list ของนโยบายเรียงตาม seq พร้อมเงื่อนไขย่อยเรียงตาม seq
    """
    tree = []
    policies = commission_policy.objects.filter(active=1).order_by('seq').prefetch_related('conditions')
    allowed_codes = _allowed_policy_codes(course_obj)
    if allowed_codes is not None:
        policies = policies.filter(policy_code__in=allowed_codes)
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
    context = {'title': defaultTitle, 'listMenuPermission': objMenu, 'courses': courses, 'users_json': _users_json()}
    return render(request, 'commission/rules.html', context)


@csrf_exempt
def api_rules_list(request):
    data = json.loads(request.body)
    course_id = data.get('course_id')
    course_obj = course.objects.filter(pk=course_id).first()

    rows_by_condition = {}
    rules = commission_rule.objects.filter(course_id=course_id).prefetch_related('allocations__payee')
    for r in rules:
        allocations = [{'alloc_id': a.alloc_id, 'payee_id': a.payee_id,
                         'payee_name': a.payee.payee_name, 'percent': a.percent} for a in r.allocations.all()]
        rows_by_condition[r.condition_id] = {
            'rule_id': r.rule_id, 'rate': r.rate, 'active': bool(r.active), 'allocations': allocations,
        }

    return JsonResponse({'policies': _policy_tree(rows_by_condition, course_obj)}, safe=False)


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
    user_id = data.get('user_id')
    percent = data.get('percent')

    payee = _get_or_create_payee_for_user(user_id)
    alloc = commission_rule_allocation.objects.create(
        rule_id=rule_id, payee=payee, percent=percent or 0)
    return JsonResponse({'status': 200, 'alloc_id': alloc.alloc_id, 'payee_name': payee.payee_name})


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
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    context = {'title': defaultTitle, 'listMenuPermission': objMenu, 'payees': payees, 'users': users}
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
    context = {'title': defaultTitle, 'listMenuPermission': objMenu, 'rows': rows, 'users_json': _users_json()}
    return render(request, 'commission/bills.html', context)


@login_required(login_url='/login')
def bills_list_all(request):
    cm_id, objMenu = _menu_context(request)
    rows_ev = []
    rows_noev = []
    items = register_payment_items.objects.select_related('register', 'register__course', 'rp').filter(
        register__status='Y').order_by('-rpi_id')[:500]
    for rpi in items:
        sold = _bill_is_sold(rpi)
        plan = commission_plan.objects.filter(rpi=rpi).first() if sold else None
        if not sold:
            status = 'OPEN'
        elif not plan:
            status = 'SOLD_NOPLAN'
        elif not plan.is_locked:
            status = 'SOLD_EDITING'
        else:
            status = 'SOLD_LOCKED'
        row = {
            'rpi_id': rpi.rpi_id,
            'rp_doc_number': rpi.rp.rp_doc_number if rpi.rp else '-',
            'register_number': rpi.register.register_number if rpi.register else '-',
            'customer_name': rpi.rp.rp_name_customer if rpi.rp else '-',
            'course_name': rpi.register.course.course_name if rpi.register and rpi.register.course else '-',
            'amount': rpi.rpi_price_result,
            'crt_date': rpi.rp.crt_date if rpi.rp else None,
            'status': status,
            'sold': sold,
        }
        if rpi.register and rpi.register.is_event == 'Y':
            rows_ev.append(row)
        else:
            rows_noev.append(row)
    context = {'title': defaultTitle, 'listMenuPermission': objMenu, 'rows_ev': rows_ev, 'rows_noev': rows_noev}
    return render(request, 'commission/listall.html', context)


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
    plan = commission_plan.objects.select_related('register', 'register__course').get(plan_id=plan_id)
    course_obj = plan.register.course if plan.register else None

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
        'policies': _policy_tree(rows_by_condition, course_obj),
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

    payee = _get_or_create_payee_for_user(data.get('user_id'))
    alloc = commission_plan_allocation.objects.create(
        line=line, payee=payee, percent=data.get('percent') or 0)
    return JsonResponse({'status': 200, 'alloc_id': alloc.alloc_id, 'payee_name': payee.payee_name})


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


# =====================================================================
# หน้า: ค่าตอบแทนผู้ปฏิบัติงาน ต่อ course_event (ev_id)
# =====================================================================

@login_required(login_url='/login')
def event_commission_page(request, ev_id):
    cm_id, objMenu = _menu_context(request)
    ev = course_event.objects.select_related('course').get(ev_id=ev_id)

    ev_user_name = ''
    if ev.ev_user:
        try:
            u = User.objects.get(id=ev.ev_user)
            ev_user_name = f'{u.first_name} {u.last_name}'.strip()
        except User.DoesNotExist:
            pass

    bills_qs = register_payment_items.objects.filter(register__ev=ev)
    bill_count = bills_qs.count()
    total_revenue = bills_qs.aggregate(s=Sum('rpi_price_result'))['s'] or 0

    policies = commission_policy.objects.filter(active=1, policy_code='3').order_by('seq').prefetch_related(
        'conditions')
    rules_by_cond = {
        r.condition_id: r
        for r in commission_event_rule.objects.filter(event=ev).prefetch_related('allocations__payee')
    }
    payees = commission_payee.objects.filter(active=1).order_by('payee_type', 'payee_name')

    policy_data = []
    for p in policies:
        conds = []
        for c in p.conditions.filter(active=1).order_by('seq'):
            rule = rules_by_cond.get(c.condition_id)
            allocs = []
            if rule:
                for a in rule.allocations.all():
                    allocs.append({
                        'ev_alloc_id': a.ev_alloc_id,
                        'payee_id': a.payee_id,
                        'payee_name': a.payee.payee_name,
                        'percent': a.percent,
                        'amount': a.amount,
                        'status': a.status,
                    })
            conds.append({
                'condition_id': c.condition_id,
                'condition_code': c.condition_code,
                'condition_name': c.condition_name,
                'calc_type': c.calc_type,
                'ev_rule_id': rule.ev_rule_id if rule else None,
                'rate': rule.rate if rule else 0,
                'active': bool(rule.active) if rule else False,
                'allocations': allocs,
            })
        policy_data.append({
            'policy_id': p.policy_id,
            'policy_code': p.policy_code,
            'policy_name': p.policy_name,
            'conditions': conds,
        })

    users = User.objects.filter(is_active=1).order_by('first_name', 'last_name')

    import json as _json
    context = {
        'title': defaultTitle,
        'listMenuPermission': objMenu,
        'ev': ev,
        'ev_user_name': ev_user_name,
        'bill_count': bill_count,
        'total_revenue': total_revenue,
        'policy_data_json': _json.dumps(policy_data, ensure_ascii=False),
        'users_json': _json.dumps(
            [{'id': u.id, 'name': f'{u.first_name} {u.last_name}'.strip() or u.username}
             for u in users],
            ensure_ascii=False),
        'payees_json': _json.dumps(
            [{'payee_id': px.payee_id, 'payee_name': px.payee_name, 'payee_type': px.payee_type}
             for px in payees],
            ensure_ascii=False),
    }
    return render(request, 'commission/event_commission.html', context)


@csrf_exempt
def api_ev_rule_save(request):
    data = json.loads(request.body)
    ev_id = data.get('ev_id')
    condition_id = data.get('condition_id')
    rate = data.get('rate')
    active = data.get('active')

    rule, _created = commission_event_rule.objects.get_or_create(
        event_id=ev_id, condition_id=condition_id,
        defaults={'rate': rate or 0, 'active': 1 if active else 0,
                  'crt_date': dateTimeNow(), 'upd_date': dateTimeNow()})
    if not _created:
        if rate is not None:
            rule.rate = rate
        if active is not None:
            rule.active = 1 if active else 0
        rule.upd_date = dateTimeNow()
        rule.save()

    return JsonResponse({'status': 200, 'ev_rule_id': rule.ev_rule_id})


@csrf_exempt
def api_ev_alloc_add(request):
    data = json.loads(request.body)
    ev_rule_id = data.get('ev_rule_id')
    user_id = data.get('user_id')
    percent = float(data.get('percent') or 0)

    payee = _get_or_create_payee_for_user(user_id)

    rule = commission_event_rule.objects.get(ev_rule_id=ev_rule_id)
    total_revenue = (
        register_payment_items.objects
        .filter(register__ev=rule.event)
        .aggregate(s=Sum('rpi_price_result'))['s'] or 0
    )
    base = total_revenue * rule.rate / 100
    amount = base * percent / 100

    alloc = commission_event_allocation.objects.create(
        ev_rule=rule, payee=payee, percent=percent,
        amount=round(amount, 2), status='PENDING',
        crt_date=dateTimeNow(), upd_date=dateTimeNow())

    return JsonResponse({
        'status': 200,
        'ev_alloc_id': alloc.ev_alloc_id,
        'amount': alloc.amount,
        'payee_name': payee.payee_name,
    })


@csrf_exempt
def api_ev_alloc_delete(request):
    data = json.loads(request.body)
    commission_event_allocation.objects.filter(ev_alloc_id=data.get('ev_alloc_id')).delete()
    return JsonResponse({'status': 200})


@csrf_exempt
def api_ev_alloc_status(request):
    data = json.loads(request.body)
    alloc = commission_event_allocation.objects.get(ev_alloc_id=data.get('ev_alloc_id'))
    next_status = data.get('status')
    if next_status not in ('PENDING', 'APPROVED', 'PAID'):
        return JsonResponse({'status': 400, 'message': 'สถานะไม่ถูกต้อง'}, status=400)
    alloc.status = next_status
    if next_status == 'APPROVED':
        alloc.approved_by = request.user if request.user.is_authenticated else None
        alloc.approved_at = dateTimeNow()
    if next_status == 'PAID':
        alloc.paid_by = request.user if request.user.is_authenticated else None
        alloc.paid_at = dateTimeNow()
    alloc.upd_date = dateTimeNow()
    alloc.save()
    return JsonResponse({'status': 200})
