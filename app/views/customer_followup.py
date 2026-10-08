from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .. import customer_followup as rules
from ..constant import defaultTitle
from ..functions import dateTimeNow, treeDigit, twoDigit
from ..models import (
    category_program_permission,
    course,
    course_event,
    customer_followup,
    customer_followup_log,
    customer_followup_owner_log,
    customers,
    fact_customer,
    register_main,
    register_payment,
    register_payment_items,
    student,
    user_detail,
    user_group,
)


def _base_context(request):
    try:
        cm_id = user_detail.objects.get(user_id=request.user.id).cm_id
    except user_detail.DoesNotExist:
        cm_id = 0

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


def _base_queryset():
    return customer_followup.objects.select_related(
        'course', 'owner_sale', 'original_sale', 'claimed_by', 'new_register'
    )


def _filter(request, queryset):
    status = request.GET.get('status', '').strip()
    keyword = request.GET.get('q', '').strip()
    sale_id = request.GET.get('sale', '').strip()
    due_from = request.GET.get('due_from', '').strip()
    due_to = request.GET.get('due_to', '').strip()
    if status:
        queryset = queryset.filter(status=status)
    if keyword:
        queryset = queryset.filter(
            Q(customer_name__icontains=keyword)
            | Q(customer_tax__icontains=keyword)
            | Q(source_doc_no__icontains=keyword)
            | Q(new_doc_no__icontains=keyword)
            | Q(course__course_name__icontains=keyword)
        )
    if sale_id:
        queryset = queryset.filter(
            Q(owner_sale_id=sale_id) | Q(original_sale_id=sale_id) | Q(claimed_by_id=sale_id)
        )
    if due_from:
        queryset = queryset.filter(due_date__gte=due_from)
    if due_to:
        queryset = queryset.filter(due_date__lte=due_to)
    return queryset


def _decorate(followups):
    today = rules.today()
    for followup in followups:
        followup.days_left = (followup.due_date - today).days
        followup.protect_days_left = (
            (followup.protect_until - today).days if followup.protect_until else None
        )
    return followups


def _render_list(request, mode, queryset, heading, subtitle):
    followups = _decorate(list(_filter(request, queryset)[:500]))
    context = _base_context(request)
    context.update({
        'mode': mode,
        'heading': heading,
        'subtitle': subtitle,
        'followups': followups,
        'status_choices': customer_followup.STATUS_CHOICES,
        'sales': rules.sale_users() if mode == 'registry' else [],
        'can_manage': rules.can_manage(request.user),
    })
    return render(request, 'customer_followup/list.html', context)


@login_required(login_url='/login')
def followup_list(request):
    queryset = _base_queryset().filter(
        Q(owner_sale=request.user) | Q(claimed_by=request.user)
    ).exclude(status=customer_followup.STATUS_WAITING)
    if not request.GET.get('status'):
        queryset = queryset.exclude(status=customer_followup.STATUS_WON)
    return _render_list(
        request, 'mine', queryset, 'ติดตามลูกค้า',
        'ลูกค้าที่ใกล้ครบกำหนดต่ออายุ 2 ปี และลูกค้าตกค้างที่คุณรับเรื่องไว้',
    )


@login_required(login_url='/login')
def followup_pool(request):
    queryset = _base_queryset().filter(status=customer_followup.STATUS_POOL)
    return _render_list(
        request, 'pool', queryset, 'ลูกค้าตกค้าง',
        f'Sale ทุกคนรับเรื่องได้ เมื่อรับแล้วรายการจะถูกล็อกไว้ {rules.CLAIM_DAYS} วัน',
    )


@login_required(login_url='/login')
def followup_registry(request):
    if not rules.can_manage(request.user):
        raise Http404
    queryset = _base_queryset()
    if not request.GET.get('status'):
        queryset = queryset.exclude(status=customer_followup.STATUS_WAITING)
    return _render_list(
        request, 'registry', queryset, 'ทะเบียนติดตามลูกค้า',
        'ภาพรวมการติดตามลูกค้าเก่าของ Sale ทุกคน',
    )


def _visible_followup_or_404(request, pk):
    followup = get_object_or_404(_base_queryset(), pk=pk)
    user_id = request.user.id
    can_view = (
        followup.status == customer_followup.STATUS_POOL
        or user_id in (followup.owner_sale_id, followup.original_sale_id, followup.claimed_by_id)
        or rules.can_manage(request.user)
    )
    if not can_view:
        raise Http404
    return followup


def _last_item(register_id):
    return register_payment_items.objects.filter(
        register_id=register_id
    ).order_by('-rpi_id').first()


@login_required(login_url='/login')
def followup_detail(request, pk):
    followup = _visible_followup_or_404(request, pk)
    _decorate([followup])
    source = followup.source_register
    context = _base_context(request)
    context.update({
        'followup': followup,
        'source': source,
        'payment': register_payment.objects.filter(
            register_id=source.register_id).order_by('-rp_id').first(),
        'item': _last_item(source.register_id),
        'logs': followup.logs.select_related('user'),
        'owner_logs': followup.owner_logs.select_related('from_user', 'to_user', 'user_crt'),
        'channel_choices': customer_followup_log.CHANNEL_CHOICES,
        'can_work': rules.can_work_on(request.user, followup),
        'can_claim': (
            followup.status == customer_followup.STATUS_POOL
            and followup.claimed_by_id is None
        ),
        'can_manage': rules.can_manage(request.user),
        'sales': rules.sale_users(),
        'min_followups': rules.MIN_FOLLOWUPS,
        'claim_days': rules.CLAIM_DAYS,
    })
    return render(request, 'customer_followup/detail.html', context)


@login_required(login_url='/login')
@require_POST
def followup_log_create(request, pk):
    followup = _visible_followup_or_404(request, pk)
    if not rules.can_work_on(request.user, followup):
        messages.error(request, 'คุณไม่มีสิทธิ์บันทึกการติดตามรายการนี้')
        return redirect('customer_followup_detail', pk=pk)

    data = {
        key: request.POST.get(key, '').strip()
        for key in ('contact_name', 'contact_phone', 'channel', 'result', 'note')
    }
    channels = dict(customer_followup_log.CHANNEL_CHOICES)
    if not all(data[key] for key in ('contact_name', 'contact_phone', 'result')) \
            or data['channel'] not in channels:
        messages.error(request, 'กรุณากรอกชื่อผู้ติดต่อ เบอร์โทร ช่องทาง และผลการติดต่อให้ครบ')
        return redirect('customer_followup_detail', pk=pk)

    today = rules.today()
    with transaction.atomic():
        followup = customer_followup.objects.select_for_update().get(pk=pk)
        # นับเฉพาะเจ้าของที่ยังอยู่ในช่วงสิทธิ์ และนับได้วันละ 1 ครั้ง
        counted = (
            followup.status in rules.ACTIVE_STATUSES
            and not followup.logs.filter(counted=True, crt_date__date=today).exists()
        )
        customer_followup_log.objects.create(
            followup=followup, user=request.user, counted=counted,
            contact_name=data['contact_name'][:256],
            contact_phone=data['contact_phone'][:64],
            channel=data['channel'],
            result=data['result'][:256],
            note=data['note'],
        )
        if counted:
            followup.followup_count += 1
            followup.last_followup_date = today
            if followup.status in (customer_followup.STATUS_WAITING,
                                   customer_followup.STATUS_ALERTING):
                followup.status = customer_followup.STATUS_FOLLOWING
            followup.protect_until = rules.compute_protect_until(followup)
        followup.save()
    messages.success(request, 'บันทึกการติดตามแล้ว' if counted
                     else 'บันทึกแล้ว (วันนี้นับครั้งไปแล้ว รายการนี้ไม่นับเพิ่ม)')
    return redirect('customer_followup_detail', pk=pk)


@login_required(login_url='/login')
@require_POST
def followup_claim(request, pk):
    with transaction.atomic():
        followup = get_object_or_404(customer_followup.objects.select_for_update(), pk=pk)
        if followup.status != customer_followup.STATUS_POOL or followup.claimed_by_id:
            messages.error(request, 'รายการนี้มี Sale รับเรื่องไปแล้ว')
            return redirect('customer_followup_pool')
        followup.claimed_by = request.user
        followup.owner_sale = request.user
        followup.claim_until = rules.today() + timedelta(days=rules.CLAIM_DAYS)
        followup.save()
        customer_followup_owner_log.objects.create(
            followup=followup, from_user=None, to_user=request.user,
            reason='claim', user_crt=request.user)
    messages.success(
        request, f'รับเรื่องแล้ว ล็อกไว้ถึง {followup.claim_until:%d/%m/%Y}')
    return redirect('customer_followup_detail', pk=pk)


def _next_register_number():
    today = date.today()
    year_th = str(today.year + 543)
    total = register_main.objects.filter(
        crt_date__month=today.month, crt_date__year=today.year
    ).exclude(register_number="-").count()
    return "R" + year_th[2:4] + "/" + str(twoDigit(today.month)) + "/" + str(treeDigit(total + 1))


def _next_student_code():
    today = date.today()
    total = student.objects.filter(
        crt_date__month=today.month, crt_date__year=today.year).count()
    return "TZ" + str(twoDigit(today.month)) + str(treeDigit(total + 1)) + "/" + str(today.year)


@login_required(login_url='/login')
def followup_quote(request, pk):
    """นำข้อมูลลูกค้าเดิมไปเปิดใบเสนอราคาใหม่ (เปลี่ยนหลักสูตร จำนวนคน ราคาได้)"""
    followup = _visible_followup_or_404(request, pk)
    if not rules.can_work_on(request.user, followup):
        messages.error(request, 'คุณไม่มีสิทธิ์ออกใบเสนอราคาจากรายการนี้')
        return redirect('customer_followup_detail', pk=pk)
    try:
        module = user_group.objects.get(user=request.user.id).module
    except user_group.DoesNotExist:
        return render(request, '404.html')

    source = followup.source_register
    source_fact = fact_customer.objects.filter(register_id=source.register_id).first()
    if source_fact is None:
        messages.error(request, 'ไม่พบข้อมูลลูกค้าของบิลเดิม')
        return redirect('customer_followup_detail', pk=pk)
    item = _last_item(source.register_id)

    if request.method == 'POST':
        mode = request.POST.get('mode')
        pay_type = int(request.POST.get('pay_type') or source.pay_type or 1)
        try:
            quantity = max(int(request.POST.get('rpi_quantity') or 1), 1)
            price = float(request.POST.get('rpi_price') or 0)
        except ValueError:
            messages.error(request, 'จำนวนคนหรือราคาไม่ถูกต้อง')
            return redirect('customer_followup_quote', pk=pk)

        event = None
        if mode == 'event':
            event = get_object_or_404(course_event, pk=request.POST.get('ev_id'))
            course_id = event.course_id
        else:
            course_id = get_object_or_404(course, pk=request.POST.get('course_id')).course_id

        with transaction.atomic():
            new_register = register_main.objects.create(
                register_number="-",
                customer_type=source.customer_type,
                customer_status=0,
                pay_type=pay_type,
                pay_status=1,
                close_the_sale=1 if pay_type == 1 else 0,
                crt_date=dateTimeNow(),
                upd_date=dateTimeNow(),
                ev_id=event.ev_id if event else None,
                course_id=course_id,
                seller_id=request.user.id,
                user_update_id=request.user.id,
                is_event='Y' if event else 'N',
                module=module,
            )
            fact_customer.objects.create(
                customer_id=source_fact.customer_id, register_id=new_register.register_id)
            new_register.register_number = _next_register_number()
            new_register.save(update_fields=['register_number'])
            if new_register.customer_type == 1:
                customer = customers.objects.get(customer_id=source_fact.customer_id)
                student.objects.create(
                    student_identification_number=customer.customer_tax,
                    student_prefix_th="",
                    student_firstname_th=customer.customer_fisrt,
                    student_lastname_th=customer.customer_last,
                    student_prefix_eng="",
                    student_firstname_eng="",
                    student_lastname_eng="",
                    student_code=_next_student_code(),
                    crt_date=dateTimeNow(),
                    upd_date=dateTimeNow(),
                    register_id=new_register.register_id,
                )
            followup.new_register = new_register
            followup.new_doc_no = ''
            followup.status = customer_followup.STATUS_QUOTED
            followup.save()

        request.session['followup_prefill'] = {
            'register_id': str(new_register.register_id),
            'quantity': quantity,
            'price': price,
        }
        if event:
            return redirect('/register/payment/' + str(new_register.register_id))
        return redirect('/salesnotevent/payment/' + str(new_register.register_id))

    events = course_event.objects.select_related('course').filter(
        status__in=['W', 'I', 'S', 'Y'], cancelled=1, active=1,
        ev_date_start__gte=date.today(), module=module,
    ).order_by('ev_date_start')
    context = _base_context(request)
    context.update({
        'followup': followup,
        'source': source,
        'item': item,
        'events': events,
        'courses': course.objects.filter(is_show_order='Y', cancelled=1).order_by('course_name'),
    })
    return render(request, 'customer_followup/quote.html', context)


@login_required(login_url='/login')
@require_POST
def followup_assign(request, pk):
    """Sale Desk บันทึกชื่อผู้ขาย และเลขที่ใบเสนอราคาใหม่"""
    if not rules.can_manage(request.user):
        raise Http404
    followup = get_object_or_404(customer_followup, pk=pk)
    doc_no = request.POST.get('doc_no', '').strip()
    seller = rules.sale_users().filter(pk=request.POST.get('seller_id')).first()
    payment = register_payment.objects.select_related('register').filter(
        rp_doc_number=doc_no).order_by('-rp_id').first() if doc_no else None
    if seller is None or payment is None:
        messages.error(request, 'ไม่พบผู้ขาย หรือไม่พบเลขที่ใบเสนอราคานี้ในระบบ')
        return redirect('customer_followup_detail', pk=pk)
    if payment.register_id == followup.source_register_id:
        messages.error(request, 'เลขที่นี้เป็นบิลเดิม กรุณาระบุใบเสนอราคาใหม่')
        return redirect('customer_followup_detail', pk=pk)
    rules.assign_by_sale_desk(followup, seller, payment.register, doc_no, request.user)
    messages.success(request, 'บันทึกผู้ขายและเลขที่ใบเสนอราคาใหม่แล้ว')
    return redirect('customer_followup_detail', pk=pk)
