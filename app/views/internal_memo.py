import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..constant import defaultTitle
from ..models import (
    InternalMemo,
    InternalMemoAttachment,
    InternalMemoWorkImage,
    InternalMemoWorkLog,
    category_program_permission,
    user_detail,
)


ALLOWED_ATTACHMENTS = {'.pdf', '.jpg', '.jpeg', '.png'}
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024
MAX_ATTACHMENTS = 5
ALLOWED_WORK_IMAGES = {'.jpg', '.jpeg', '.png'}


ADMIN_GROUP_NAME = 'ผู้ดูแลระบบ'


def _can_view_all_memos(user):
    return user.is_staff or user_detail.objects.filter(
        user_id=user.id, cm__cm_name=ADMIN_GROUP_NAME
    ).exists()


def _submitted_status(require_review):
    if require_review:
        return InternalMemo.STATUS_PENDING_REVIEW
    return InternalMemo.STATUS_PENDING_APPROVAL


def _submitted_message(require_review):
    if require_review:
        return 'ส่งบันทึกให้ผู้ตรวจสอบ ชั้น 1 แล้ว'
    return 'ส่งบันทึกให้ผู้อนุมัติแล้ว'


def _validate_workflow(request, reviewers, approvers, errors):
    require_review = request.POST.get('workflow', 'review') != 'direct'
    reviewer = None
    if require_review:
        try:
            reviewer = reviewers.get(pk=request.POST.get('reviewer', '').strip())
        except (User.DoesNotExist, ValueError):
            errors.append('กรุณาเลือกผู้ตรวจสอบ ชั้น 1')
    try:
        approver = approvers.get(pk=request.POST.get('approver', '').strip())
    except (User.DoesNotExist, ValueError):
        approver = None
        errors.append('กรุณาเลือกผู้อนุมัติ')
    if reviewer and approver and reviewer.pk == approver.pk:
        errors.append('ผู้ตรวจสอบ ชั้น 1 และผู้อนุมัติ ชั้น 2 ต้องเป็นคนละคนกัน')
    return require_review, reviewer, approver


def _can_update_work_status(user, memo, is_admin=None):
    """Only admins (is_staff or the ผู้ดูแลระบบ group) may update work status."""
    if memo.status != InternalMemo.STATUS_APPROVED:
        return False
    if is_admin is None:
        is_admin = _can_view_all_memos(user)
    return is_admin


def _save_work_update(request, memo):
    """Validate and record a work-status update. Returns a list of errors."""
    work_status = request.POST.get('work_status', '').strip()
    note = request.POST.get('note', '').strip()
    images = request.FILES.getlist('images')
    errors = []
    if work_status not in dict(InternalMemo.WORK_STATUS_CHOICES):
        errors.append('กรุณาเลือกสถานะการดำเนินงาน')
    if len(images) > MAX_ATTACHMENTS:
        errors.append('แนบรูปภาพได้สูงสุด 5 รูป')
    for image in images:
        if os.path.splitext(image.name)[1].lower() not in ALLOWED_WORK_IMAGES:
            errors.append('รองรับเฉพาะรูปภาพ JPG และ PNG')
            break
        if image.size > MAX_ATTACHMENT_SIZE:
            errors.append('รูปภาพแต่ละรูปต้องไม่เกิน 10 MB')
            break
    if errors:
        return errors

    with transaction.atomic():
        now = timezone.now()
        log = InternalMemoWorkLog.objects.create(
            memo=memo,
            work_status=work_status,
            note=note,
            updated_by=request.user,
        )
        for image in images:
            InternalMemoWorkImage.objects.create(
                log=log, file=image, original_name=image.name
            )
        memo.work_status = work_status
        memo.work_status_updated_at = now
        memo.work_status_updated_by = request.user
        memo.save(update_fields=[
            'work_status', 'work_status_updated_at',
            'work_status_updated_by', 'updated_at',
        ])
    return []


def _memo_user_display(memo, field_name):
    try:
        person = getattr(memo, field_name)
    except User.DoesNotExist:
        return '-'
    if person is None:
        return '-'
    return person.get_full_name() or person.username or '-'


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


def _visible_memo_or_404(request, pk):
    memo = get_object_or_404(
        InternalMemo.objects.select_related(
            'creator', 'reviewer', 'approver'
        ).prefetch_related(
            'cc_users', 'attachments'
        ),
        pk=pk,
    )
    can_view = (
        _can_view_all_memos(request.user)
        or memo.creator_id == request.user.id
        or memo.reviewer_id == request.user.id
        or memo.approver_id == request.user.id
        or (
            memo.status != InternalMemo.STATUS_DRAFT
            and memo.cc_users.filter(pk=request.user.id).exists()
        )
    )
    if not can_view:
        raise Http404
    return memo


def _render_memo_list(request, memos, extra_context):
    branches = memos.order_by().values_list('branch', flat=True).distinct()

    status = request.GET.get('status', '').strip()
    branch = request.GET.get('branch', '').strip()
    keyword = request.GET.get('q', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    work_status = request.GET.get('work_status', '').strip()
    if status:
        memos = memos.filter(status=status)
    if work_status == 'NONE':
        memos = memos.filter(work_status='')
    elif work_status:
        memos = memos.filter(work_status=work_status)
    if branch:
        memos = memos.filter(branch=branch)
    if keyword:
        memos = memos.filter(
            Q(memo_number__icontains=keyword) | Q(subject__icontains=keyword)
        )
    if date_from:
        memos = memos.filter(created_at__date__gte=date_from)
    if date_to:
        memos = memos.filter(created_at__date__lte=date_to)

    memos = list(memos)
    is_admin = _can_view_all_memos(request.user)
    for memo in memos:
        memo.creator_display = _memo_user_display(memo, 'creator')
        memo.reviewer_display = _memo_user_display(memo, 'reviewer')
        memo.approver_display = _memo_user_display(memo, 'approver')
        memo.can_update_work = _can_update_work_status(
            request.user, memo, is_admin
        )

    context = _base_context(request)
    context.update({
        'memos': memos,
        'branches': branches,
        'status_choices': InternalMemo.STATUS_CHOICES,
        'work_status_choices': InternalMemo.WORK_STATUS_CHOICES,
        **extra_context,
    })
    return render(request, 'internal_memo/list.html', context)


@login_required(login_url='/login')
def memo_list(request):
    memos = InternalMemo.objects.select_related('creator', 'reviewer', 'approver')
    if not _can_view_all_memos(request.user):
        memos = memos.filter(creator=request.user)
    return _render_memo_list(request, memos, {
        'page_title': 'ทะเบียนบันทึกภายใน',
        'page_subtitle': 'ติดตามฉบับร่าง เอกสารที่ส่ง และสถานะการอนุมัติ',
        'is_cc_page': False,
    })


@login_required(login_url='/login')
def memo_cc_list(request):
    memos = InternalMemo.objects.select_related(
        'creator', 'reviewer', 'approver'
    ).filter(cc_users=request.user).exclude(
        status=InternalMemo.STATUS_DRAFT
    ).distinct()
    return _render_memo_list(request, memos, {
        'page_title': 'สำเนาถึง',
        'page_subtitle': 'บันทึกภายในที่ส่งสำเนาถึงคุณ',
        'is_cc_page': True,
    })


@login_required(login_url='/login')
def memo_create(request):
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
    reviewers = users.filter(
        groups__name='Internal Memo Reviewer'
    ).distinct()
    approvers = users.filter(
        groups__name='Internal Memo Approver'
    ).distinct()
    if request.method == 'POST':
        recipient = request.POST.get('recipient', '').strip()
        subject = request.POST.get('subject', '').strip()
        branch = request.POST.get('branch', '').strip() or 'สำนักงานใหญ่'
        detail = request.POST.get('detail', '').strip()
        action = request.POST.get('action', 'draft')
        attachments = request.FILES.getlist('attachments')

        errors = []
        if not recipient:
            errors.append('กรุณาระบุผู้รับ')
        if not subject:
            errors.append('กรุณาระบุเรื่อง')
        if not detail:
            errors.append('กรุณาระบุรายละเอียด')
        require_review, reviewer, approver = _validate_workflow(
            request, reviewers, approvers, errors
        )
        if len(attachments) > MAX_ATTACHMENTS:
            errors.append('แนบไฟล์ได้สูงสุด 5 ไฟล์')
        for attachment in attachments:
            if os.path.splitext(attachment.name)[1].lower() not in ALLOWED_ATTACHMENTS:
                errors.append('รองรับเฉพาะไฟล์ PDF, JPG และ PNG')
                break
            if attachment.size > MAX_ATTACHMENT_SIZE:
                errors.append('ไฟล์แนบแต่ละไฟล์ต้องไม่เกิน 10 MB')
                break

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            with transaction.atomic():
                now = timezone.now()
                memo = InternalMemo.objects.create(
                    recipient=recipient,
                    subject=subject,
                    branch=branch,
                    detail=detail,
                    creator=request.user,
                    reviewer=reviewer,
                    require_review=require_review,
                    approver=approver,
                    status=(_submitted_status(require_review) if action == 'submit' else InternalMemo.STATUS_DRAFT),
                    submitted_at=(now if action == 'submit' else None),
                )
                memo.memo_number = 'MEMO-{0}-{1:05d}'.format(now.year, memo.pk)
                memo.save(update_fields=['memo_number'])
                cc_ids = request.POST.getlist('cc_users')
                memo.cc_users.set(users.filter(pk__in=cc_ids))
                for item in attachments:
                    InternalMemoAttachment.objects.create(
                        memo=memo, file=item, original_name=item.name
                    )
            messages.success(
                request,
                _submitted_message(require_review) if action == 'submit' else 'บันทึกฉบับร่างแล้ว',
            )
            return redirect('internal_memo_detail', pk=memo.pk)

    context = _base_context(request)
    context.update({
        'users': users,
        'reviewers': reviewers,
        'approvers': approvers,
    })
    return render(request, 'internal_memo/form.html', context)


@login_required(login_url='/login')
@user_passes_test(lambda user: user.is_staff, login_url='/403')
def memo_edit(request, pk):
    memo = get_object_or_404(
        InternalMemo.objects.prefetch_related('cc_users'), pk=pk
    )
    users = User.objects.filter(is_active=True).order_by(
        'first_name', 'last_name', 'username'
    )
    reviewers = users.filter(
        groups__name='Internal Memo Reviewer'
    ).distinct()
    approvers = users.filter(
        groups__name='Internal Memo Approver'
    ).distinct()

    if request.method == 'POST':
        recipient = request.POST.get('recipient', '').strip()
        subject = request.POST.get('subject', '').strip()
        branch = request.POST.get('branch', '').strip()
        detail = request.POST.get('detail', '').strip()
        errors = []

        if not recipient:
            errors.append('กรุณาระบุผู้รับ')
        if not subject:
            errors.append('กรุณาระบุเรื่อง')
        if not branch:
            errors.append('กรุณาระบุสาขา')
        if not detail:
            errors.append('กรุณาระบุรายละเอียด')
        require_review, reviewer, approver = _validate_workflow(
            request, reviewers, approvers, errors
        )

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            memo.recipient = recipient
            memo.subject = subject
            memo.branch = branch
            memo.detail = detail
            memo.reviewer = reviewer
            memo.require_review = require_review
            memo.approver = approver
            # Move an in-flight memo to the step that matches the new workflow.
            if not require_review and memo.status == InternalMemo.STATUS_PENDING_REVIEW:
                memo.status = InternalMemo.STATUS_PENDING_APPROVAL
            elif (
                require_review
                and memo.status == InternalMemo.STATUS_PENDING_APPROVAL
                and memo.reviewed_at is None
            ):
                memo.status = InternalMemo.STATUS_PENDING_REVIEW
            memo.save(update_fields=[
                'recipient', 'subject', 'branch', 'detail', 'reviewer',
                'require_review', 'approver', 'status', 'updated_at',
            ])
            memo.cc_users.set(users.filter(pk__in=request.POST.getlist('cc_users')))
            messages.success(request, 'แก้ไขบันทึกภายในเรียบร้อยแล้ว')
            return redirect('internal_memo_detail', pk=memo.pk)

    context = _base_context(request)
    selected_cc_ids = (
        {int(value) for value in request.POST.getlist('cc_users') if value.isdigit()}
        if request.method == 'POST'
        else set(memo.cc_users.values_list('id', flat=True))
    )
    context.update({
        'memo': memo,
        'users': users,
        'reviewers': reviewers,
        'approvers': approvers,
        'selected_cc_ids': selected_cc_ids,
    })
    return render(request, 'internal_memo/edit.html', context)


@login_required(login_url='/login')
@user_passes_test(lambda user: user.is_staff, login_url='/403')
def memo_delete(request, pk):
    if request.method != 'POST':
        raise Http404
    memo = get_object_or_404(InternalMemo, pk=pk)
    memo_number = memo.memo_number
    memo.delete()
    messages.success(request, f'ลบบันทึก {memo_number} เรียบร้อยแล้ว')
    return redirect('internal_memo_list')


@login_required(login_url='/login')
@user_passes_test(lambda user: user.is_staff, login_url='/403')
def memo_approver_setting(request):
    reviewer_group, _ = Group.objects.get_or_create(
        name='Internal Memo Reviewer'
    )
    approver_group, _ = Group.objects.get_or_create(
        name='Internal Memo Approver'
    )
    users = User.objects.filter(is_active=True).order_by(
        'first_name', 'last_name', 'username'
    )
    if request.method == 'POST':
        selected_reviewer_ids = request.POST.getlist('reviewers')
        selected_approver_ids = request.POST.getlist('approvers')
        reviewer_group.user_set.set(users.filter(pk__in=selected_reviewer_ids))
        approver_group.user_set.set(users.filter(pk__in=selected_approver_ids))
        messages.success(request, 'บันทึกผู้ตรวจสอบและผู้อนุมัติเรียบร้อยแล้ว')
        return redirect('internal_memo_approver_setting')

    context = _base_context(request)
    context.update({
        'users': users,
        'selected_reviewer_ids': set(
            reviewer_group.user_set.values_list('id', flat=True)
        ),
        'selected_approver_ids': set(
            approver_group.user_set.values_list('id', flat=True)
        ),
    })
    return render(request, 'internal_memo/approver_setting.html', context)


@login_required(login_url='/login')
def memo_detail(request, pk):
    memo = _visible_memo_or_404(request, pk)
    memo.creator_display = _memo_user_display(memo, 'creator')
    memo.reviewer_display = _memo_user_display(memo, 'reviewer')
    memo.approver_display = _memo_user_display(memo, 'approver')
    memo.can_update_work = _can_update_work_status(request.user, memo)
    context = _base_context(request)
    context['memo'] = memo
    context['work_logs'] = memo.work_logs.select_related(
        'updated_by'
    ).prefetch_related('images')
    return render(request, 'internal_memo/detail.html', context)


@login_required(login_url='/login')
def memo_tracking_list(request):
    is_admin = _can_view_all_memos(request.user)
    memos = InternalMemo.objects.select_related(
        'creator', 'work_status_updated_by'
    ).filter(status=InternalMemo.STATUS_APPROVED)
    if not is_admin:
        memos = memos.filter(creator=request.user)

    work_status = request.GET.get('work_status', '').strip()
    keyword = request.GET.get('q', '').strip()
    if work_status == 'NONE':
        memos = memos.filter(work_status='')
    elif work_status:
        memos = memos.filter(work_status=work_status)
    if keyword:
        memos = memos.filter(
            Q(memo_number__icontains=keyword) | Q(subject__icontains=keyword)
        )

    memos = list(memos.order_by('-decided_at'))
    for memo in memos:
        memo.creator_display = _memo_user_display(memo, 'creator')
        memo.work_updated_by_display = _memo_user_display(
            memo, 'work_status_updated_by'
        )

    context = _base_context(request)
    context.update({
        'memos': memos,
        'work_status_choices': InternalMemo.WORK_STATUS_CHOICES,
    })
    return render(request, 'internal_memo/tracking_list.html', context)


@login_required(login_url='/login')
def memo_tracking(request, pk):
    memo = _visible_memo_or_404(request, pk)
    can_update = _can_update_work_status(request.user, memo)
    if request.method == 'POST':
        if not can_update:
            raise Http404
        errors = _save_work_update(request, memo)
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            messages.success(
                request,
                f'อัปเดตการดำเนินงาน {memo.memo_number} เป็น "{memo.get_work_status_display()}" แล้ว',
            )
            return redirect('internal_memo_tracking', pk=pk)

    memo.creator_display = _memo_user_display(memo, 'creator')
    context = _base_context(request)
    context.update({
        'memo': memo,
        'can_update': can_update,
        'work_logs': memo.work_logs.select_related(
            'updated_by'
        ).prefetch_related('images'),
        'work_status_choices': InternalMemo.WORK_STATUS_CHOICES,
    })
    return render(request, 'internal_memo/tracking.html', context)


@login_required(login_url='/login')
def memo_work_status(request, pk):
    if request.method != 'POST':
        raise Http404
    memo = get_object_or_404(InternalMemo, pk=pk)
    if not _can_update_work_status(request.user, memo):
        raise Http404
    errors = _save_work_update(request, memo)
    if errors:
        for error in errors:
            messages.error(request, error)
    else:
        messages.success(
            request,
            f'อัปเดตการดำเนินงาน {memo.memo_number} เป็น "{memo.get_work_status_display()}" แล้ว',
        )
    next_url = request.POST.get('next', '')
    if next_url.startswith('/') and not next_url.startswith('//'):
        return redirect(next_url)
    return redirect('internal_memo_detail', pk=pk)


@login_required(login_url='/login')
def memo_submit(request, pk):
    if request.method != 'POST':
        raise Http404
    memo = get_object_or_404(
        InternalMemo,
        pk=pk,
        creator=request.user,
        status=InternalMemo.STATUS_DRAFT,
    )
    if memo.require_review and memo.reviewer_id is None:
        messages.error(request, 'กรุณาเลือกผู้ตรวจสอบ ชั้น 1 ก่อนส่ง')
        return redirect('internal_memo_detail', pk=pk)
    memo.status = _submitted_status(memo.require_review)
    memo.submitted_at = timezone.now()
    memo.save(update_fields=['status', 'submitted_at', 'updated_at'])
    messages.success(request, _submitted_message(memo.require_review))
    return redirect('internal_memo_detail', pk=pk)


@login_required(login_url='/login')
def memo_approval(request):
    pending = InternalMemo.objects.select_related(
        'creator', 'reviewer', 'approver'
    ).filter(
        Q(reviewer=request.user, status=InternalMemo.STATUS_PENDING_REVIEW)
        | Q(approver=request.user, status=InternalMemo.STATUS_PENDING_APPROVAL)
    )
    history = InternalMemo.objects.select_related(
        'creator', 'reviewer', 'approver'
    ).filter(
        Q(reviewer=request.user, reviewed_at__isnull=False)
        | Q(
            approver=request.user,
            status__in=[InternalMemo.STATUS_APPROVED, InternalMemo.STATUS_REJECTED],
        )
    ).distinct()[:50]
    context = _base_context(request)
    context.update({'pending_memos': pending, 'history_memos': history})
    return render(request, 'internal_memo/approval.html', context)


@login_required(login_url='/login')
@transaction.atomic
def memo_decide(request, pk):
    if request.method != 'POST':
        raise Http404
    memo = get_object_or_404(InternalMemo.objects.select_for_update(), pk=pk)
    is_reviewer_step = (
        memo.status == InternalMemo.STATUS_PENDING_REVIEW
        and memo.reviewer_id == request.user.id
    )
    is_approver_step = (
        memo.status == InternalMemo.STATUS_PENDING_APPROVAL
        and memo.approver_id == request.user.id
    )
    if not (is_reviewer_step or is_approver_step):
        raise Http404
    decision = request.POST.get('decision')
    if decision not in ('approve', 'reject'):
        messages.error(request, 'สถานะการอนุมัติไม่ถูกต้อง')
        return redirect('internal_memo_detail', pk=pk)
    now = timezone.now()
    note = request.POST.get('decision_note', '').strip()
    if is_reviewer_step:
        memo.status = (
            InternalMemo.STATUS_PENDING_APPROVAL
            if decision == 'approve'
            else InternalMemo.STATUS_REJECTED
        )
        memo.reviewer_note = note
        memo.reviewed_at = now
        update_fields = ['status', 'reviewer_note', 'reviewed_at', 'updated_at']
        if decision == 'reject':
            memo.decided_at = now
            update_fields.append('decided_at')
    else:
        memo.status = (
            InternalMemo.STATUS_APPROVED
            if decision == 'approve'
            else InternalMemo.STATUS_REJECTED
        )
        memo.decision_note = note
        memo.decided_at = now
        update_fields = ['status', 'decision_note', 'decided_at', 'updated_at']
    memo.save(update_fields=update_fields)
    messages.success(request, 'บันทึกผลการตรวจสอบ/อนุมัติแล้ว')
    return redirect('internal_memo_approval')
