"""กติกาการติดตามลูกค้าเก่า / ลูกค้าตกค้าง

- ครบกำหนดต่ออายุ = วันที่กรอกเลข SQ / SO / PO (salesorder.crt_date) + 2 ปี
- เตือน Sale เจ้าของเมื่อเหลือ 90 / 60 / 30 วัน
- สิทธิ์ของ Sale เจ้าของ (protect_until)
    ไม่เคยติดตาม      : เตือนครั้งแรก + 3 เดือน
    ติดตาม 1-2 ครั้ง   : เตือนครั้งล่าสุด + 3 เดือน
    ติดตาม 3 ครั้งขึ้นไป : max(เตือนครั้งล่าสุด, ติดตามครั้งล่าสุด) + 3 เดือน
- หมดสิทธิ์แล้วย้ายไปลูกค้าตกค้างอัตโนมัติ Sale คนใดก็รับเรื่องได้ ล็อก 90 วัน
- ออกใบเสนอราคาใหม่แล้ว (quoted) หยุดนับ ถ้าปิดการขายได้ (มี salesorder) = won
"""
from collections import Counter
from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db import connection, transaction

from .functions import dateTimeNow
from .models import (
    customer_followup,
    customer_followup_owner_log,
    event_register,
    fact_commission,
    fact_customer,
    notifications,
    register_main,
    register_payment,
    salesorder,
    user_detail,
)

ALERT_LEVELS = (90, 60, 30)
RENEW_YEARS = 2
PROTECT_MONTHS = 3
MIN_FOLLOWUPS = 3
CLAIM_DAYS = 90

SALE_CATEGORIES = (6, 11, 15)
MANAGER_CATEGORIES = (1, 9, 10, 12, 13, 16)
REGISTRY_ROUTE = 'customer-followup/registry'

ACTIVE_STATUSES = (
    customer_followup.STATUS_WAITING,
    customer_followup.STATUS_ALERTING,
    customer_followup.STATUS_FOLLOWING,
)


def today():
    return date.today()


def compute_protect_until(followup):
    if not followup.first_alert_date:
        return None
    if followup.followup_count == 0:
        return followup.first_alert_date + relativedelta(months=PROTECT_MONTHS)
    end = followup.last_alert_date + relativedelta(months=PROTECT_MONTHS)
    if followup.followup_count >= MIN_FOLLOWUPS and followup.last_followup_date:
        end = max(end, followup.last_followup_date + relativedelta(months=PROTECT_MONTHS))
    return end


def can_manage(user):
    """ผู้ที่มีเมนูทะเบียนติดตามลูกค้า = ผจก. / ผบห. / Sale Desk เห็นและจัดการได้ทุกรายการ"""
    from .functions import checkpermi
    if user.is_superuser:
        return True
    try:
        cm_id = user_detail.objects.get(user_id=user.id).cm_id
    except user_detail.DoesNotExist:
        return False
    return checkpermi(REGISTRY_ROUTE, cm_id) == 1


def can_work_on(user, followup):
    """คนที่ติดตาม / ออกใบเสนอราคาได้: เจ้าของที่ยังมีสิทธิ์ หรือคนที่รับเรื่องจากลูกค้าตกค้าง"""
    if followup.status in ACTIVE_STATUSES:
        return followup.owner_sale_id == user.id
    if followup.status == customer_followup.STATUS_POOL:
        return followup.claimed_by_id == user.id
    return False


def _notify(user_ids, message, url, cm_id=6):
    now = dateTimeNow()
    notifications.objects.bulk_create([
        notifications(
            notification_type='app',
            title='ติดตามลูกค้า',
            message=message[:255],
            reference_id='followup',
            reference_type='followup',
            is_read='false',
            read_at=now,
            action_url=url,
            priority='easy',
            user_id=user_id,
            created_by=1,
            cm_id=cm_id,
            crt_date=now,
            upd_date=now,
        )
        for user_id in set(user_ids) if user_id
    ])


def _users_in(categories):
    return list(
        user_detail.objects.filter(
            cm_id__in=categories, user__is_active=True
        ).values_list('user_id', flat=True)
    )


def _renewal_sale_order(register_id):
    er_ids = event_register.objects.filter(register_id=register_id).values_list('er_id', flat=True)
    return salesorder.objects.filter(er_id__in=list(er_ids)).order_by('-crt_date').first()


def _doc_label(sale, payment):
    parts = []
    for label, value in (('SQ', sale.sq), ('SO', sale.so), ('PO', sale.po)):
        if value and value.strip() not in ('', '-'):
            parts.append(f'{label} {value.strip()}')
    if payment and payment.rp_doc_number:
        parts.append(payment.rp_doc_number)
    return ' / '.join(parts)[:256]


def sync_new_followups(dry_run=False):
    """สร้างทะเบียนติดตามจาก salesorder ที่ยังไม่มีในทะเบียน (ใช้ทั้ง backfill และรายวัน)"""
    tracked = set()
    if customer_followup._meta.db_table in connection.introspection.table_names():
        tracked = set(customer_followup.objects.values_list('source_register_id', flat=True))
    latest = {}
    for sale in salesorder.objects.select_related('er__register').order_by('crt_date'):
        if not sale.crt_date:
            continue
        register = sale.er.register
        if register.register_id in tracked:
            continue
        latest[register.register_id] = sale

    created = []
    for register_id, sale in latest.items():
        register = sale.er.register
        fact = fact_customer.objects.select_related('customer').filter(register_id=register_id).first()
        payment = register_payment.objects.filter(register_id=register_id).order_by('-rp_id').first()
        customer = fact.customer if fact else None
        base_date = sale.crt_date.date()
        created.append(customer_followup(
            source_register_id=register_id,
            source_sale_id=sale.sale_id,
            source_doc_no=_doc_label(sale, payment),
            course_id=register.course_id,
            customer_name=((customer.customer_name if customer else None)
                           or (payment.rp_name_customer if payment else None) or '')[:256],
            customer_tax=((customer.customer_tax if customer else None) or '')[:64],
            customer_phone=((customer.customer_phone if customer else None)
                            or (payment.rp_phone if payment else None) or '')[:64],
            base_date=base_date,
            due_date=base_date + relativedelta(years=RENEW_YEARS),
            owner_sale_id=register.seller_id,
            original_sale_id=register.seller_id,
        ))
    if not dry_run:
        customer_followup.objects.bulk_create(created, batch_size=200)
    return created


def process_alerts(run_date, dry_run=False):
    alerted = []
    for followup in customer_followup.objects.filter(status__in=ACTIVE_STATUSES):
        days_left = (followup.due_date - run_date).days
        reached = [level for level in ALERT_LEVELS if days_left <= level]
        if not reached:
            continue
        level = min(reached)
        if followup.alert_level and level >= followup.alert_level:
            continue
        followup.alert_level = level
        followup.last_alert_date = run_date
        followup.first_alert_date = followup.first_alert_date or run_date
        if followup.status == customer_followup.STATUS_WAITING:
            followup.status = customer_followup.STATUS_ALERTING
        followup.protect_until = compute_protect_until(followup)
        alerted.append(followup)
        if not dry_run:
            followup.save()
            _notify(
                [followup.owner_sale_id],
                f'ลูกค้า {followup.customer_name} ครบกำหนดต่ออายุ {followup.due_date:%d/%m/%Y} '
                f'(เหลือ {max(days_left, 0)} วัน)',
                f'/customer-followup/{followup.followup_id}',
            )
    return alerted


def move_to_pool(run_date, dry_run=False):
    moved = []
    for followup in customer_followup.objects.filter(
        status__in=(customer_followup.STATUS_ALERTING, customer_followup.STATUS_FOLLOWING)
    ):
        followup.protect_until = compute_protect_until(followup)
        if followup.protect_until and run_date > followup.protect_until:
            moved.append(followup)
            if dry_run:
                continue
            with transaction.atomic():
                customer_followup_owner_log.objects.create(
                    followup=followup, from_user_id=followup.owner_sale_id,
                    to_user=None, reason='auto_pool')
                _notify(
                    [followup.owner_sale_id],
                    f'ลูกค้า {followup.customer_name} หมดสิทธิ์ติดตาม ย้ายไปลูกค้าตกค้างแล้ว',
                    '/customer-followup/pool',
                )
                followup.owner_sale = None
                followup.status = customer_followup.STATUS_POOL
                followup.pool_date = dateTimeNow()
                followup.save()
        elif not dry_run:
            customer_followup.objects.filter(pk=followup.pk).update(
                protect_until=followup.protect_until)
    return moved


def release_expired_claims(run_date, dry_run=False):
    expired = list(customer_followup.objects.filter(
        status=customer_followup.STATUS_POOL,
        claimed_by__isnull=False,
        claim_until__lt=run_date,
    ))
    if not dry_run:
        for followup in expired:
            customer_followup_owner_log.objects.create(
                followup=followup, from_user_id=followup.claimed_by_id,
                to_user=None, reason='claim_expired')
            followup.claimed_by = None
            followup.claim_until = None
            followup.owner_sale = None
            followup.save()
    return expired


def revert_quote(followup):
    """ใบเสนอราคาใหม่ถูกลบ / ขายไม่สำเร็จ: กลับไปติดตามต่อ หรือกลับเข้าลูกค้าตกค้าง"""
    followup.new_register = None
    followup.new_doc_no = ''
    if followup.pool_date:
        followup.status = customer_followup.STATUS_POOL
    elif followup.followup_count:
        followup.status = customer_followup.STATUS_FOLLOWING
    elif followup.alert_level:
        followup.status = customer_followup.STATUS_ALERTING
    else:
        followup.status = customer_followup.STATUS_WAITING


def update_quoted(dry_run=False):
    changes = Counter()
    for followup in customer_followup.objects.filter(
        status=customer_followup.STATUS_QUOTED
    ).select_related('new_register'):
        try:
            renewal = followup.new_register
        except register_main.DoesNotExist:
            renewal = None
        if renewal is None:
            revert_quote(followup)
            changes['reverted'] += 1
        elif renewal.close_the_sale == 2:
            revert_quote(followup)
            changes['reverted'] += 1
        else:
            if not followup.new_doc_no:
                payment = register_payment.objects.filter(
                    register_id=renewal.register_id).order_by('-rp_id').first()
                if payment and payment.rp_doc_number:
                    followup.new_doc_no = payment.rp_doc_number
            if _renewal_sale_order(renewal.register_id):
                followup.status = customer_followup.STATUS_WON
                changes['won'] += 1
        if not dry_run:
            followup.save()
    return changes


def run_daily(run_date=None, dry_run=False):
    run_date = run_date or today()
    created = sync_new_followups(dry_run=dry_run)
    quoted = update_quoted(dry_run=dry_run)
    alerted = process_alerts(run_date, dry_run=dry_run)
    moved = move_to_pool(run_date, dry_run=dry_run)
    expired = release_expired_claims(run_date, dry_run=dry_run)

    if not dry_run and (alerted or moved):
        _notify(
            _users_in(MANAGER_CATEGORIES),
            f'ติดตามลูกค้า: เข้าเกณฑ์เตือน {len(alerted)} รายการ, ย้ายไปลูกค้าตกค้าง {len(moved)} รายการ',
            '/customer-followup/registry',
            cm_id=10,
        )
    if not dry_run and moved:
        _notify(
            _users_in(SALE_CATEGORIES),
            f'มีลูกค้าตกค้างใหม่ {len(moved)} รายการ เปิดให้ Sale ทุกคนรับเรื่องได้',
            '/customer-followup/pool',
        )
    return {
        'created': len(created),
        'won': quoted['won'],
        'reverted': quoted['reverted'],
        'alerted': len(alerted),
        'moved_to_pool': len(moved),
        'claims_released': len(expired),
    }


def assign_by_sale_desk(followup, seller, renewal_register, doc_no, actor):
    """Sale Desk บันทึกชื่อผู้ขายและเลขที่ใบเสนอราคาใหม่ ผู้ขายจะได้ค่าคอมของใบใหม่"""
    with transaction.atomic():
        customer_followup_owner_log.objects.create(
            followup=followup,
            from_user_id=followup.owner_sale_id or followup.claimed_by_id,
            to_user=seller, reason='sale_desk', user_crt=actor)
        renewal_register.seller = seller
        renewal_register.user_update = actor
        renewal_register.upd_date = dateTimeNow()
        renewal_register.save(update_fields=['seller', 'user_update', 'upd_date'])
        fact_commission.objects.filter(
            register_id=str(renewal_register.register_id).replace('-', ''), status='W'
        ).update(user_id=seller.id)

        followup.owner_sale = seller
        followup.claimed_by = None
        followup.claim_until = None
        followup.new_register = renewal_register
        followup.new_doc_no = doc_no
        followup.status = (
            customer_followup.STATUS_WON
            if _renewal_sale_order(renewal_register.register_id)
            else customer_followup.STATUS_QUOTED
        )
        followup.save()


def sale_users():
    return User.objects.filter(
        is_active=True, user_detail__cm_id__in=SALE_CATEGORIES + MANAGER_CATEGORIES
    ).order_by('first_name', 'username').distinct()
