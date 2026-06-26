from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from ..models import customers, location_thai,user_group,user_detail,category_program_permission
from ..constant import defaultTitle
import datetime


def _now():
    return datetime.datetime.now()


def _build_address(cus):
    """Return full address string from customer + location_thai."""
    try:
        loc = location_thai.objects.get(location_id=cus.location_id)
        return (
            f"{cus.customer_address or ''} ตำบล/แขวง {loc.district_name} "
            f"อำเภอ/เขต {loc.amphur_name} จังหวัด {loc.province_name} {loc.zipcode}"
        ).strip()
    except Exception:
        return cus.customer_address or ''


def _cus_to_dict(cus):
    return {
        'customer_id':      cus.customer_id,
        'customer_code':    cus.customer_code or '',
        'customer_name':    cus.customer_name or '',
        'customer_fisrt':   cus.customer_fisrt or '',
        'customer_last':    cus.customer_last or '',
        'customer_tax':     cus.customer_tax or '',
        'customer_phone':   cus.customer_phone or '',
        'customer_email':   cus.customer_email or '',
        'customer_address': cus.customer_address or '',
        'location_id':      cus.location_id or 0,
        'customer_type':    cus.customer_type or 1,
        'full_address':     _build_address(cus),
    }


# ─── List ────────────────────────────────────────────────────────────────────

@login_required(login_url='/login')
def customer_list(request):

    title = defaultTitle
    user_id = request.user.id
    
    try:
        m = user_group.objects.get(user=user_id)
    except user_group.DoesNotExist:
        m = None
        return render(request, '404.html')
    # Menu
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
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    context = {'title': defaultTitle,'listMenuPermission':objMenu}
    return render(request, 'customer/customer_list.html', context)


# ─── API: list (JSON) ─────────────────────────────────────────────────────────

@login_required(login_url='/login')
def customer_api_list(request):
    q = request.GET.get('q', '').strip()
    qs = customers.objects.all().order_by('-customer_id')
    if q:
        qs = qs.filter(
            Q(customer_name__icontains=q) |
            Q(customer_code__icontains=q) |
            Q(customer_phone__icontains=q) |
            Q(customer_tax__icontains=q)
        )
    data = [_cus_to_dict(c) for c in qs[:200]]
    return JsonResponse({'status': 'ok', 'data': data})


# ─── API: create ─────────────────────────────────────────────────────────────

@login_required(login_url='/login')
def customer_api_create(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)

    ctype = int(request.POST.get('customer_type', 1))
    name  = request.POST.get('customer_name', '').strip()
    first = request.POST.get('customer_fisrt', '').strip()
    last  = request.POST.get('customer_last', '').strip()

    if not name and ctype == 2:
        return JsonResponse({'status': 'error', 'message': 'กรุณากรอกชื่อบริษัท'})
    if not (first or name):
        return JsonResponse({'status': 'error', 'message': 'กรุณากรอกชื่อลูกค้า'})

    # auto code: C + timestamp
    code = 'C' + datetime.datetime.now().strftime('%y%m%d%H%M%S')

    cus = customers.objects.create(
        customer_code=code,
        customer_name=name or f'{first} {last}'.strip(),
        customer_fisrt=first,
        customer_last=last,
        customer_tax=request.POST.get('customer_tax', ''),
        customer_phone=request.POST.get('customer_phone', ''),
        customer_email=request.POST.get('customer_email', ''),
        customer_address=request.POST.get('customer_address', ''),
        location_id=int(request.POST.get('location_id') or 0),
        customer_type=ctype,
    )
    return JsonResponse({'status': 'ok', 'data': _cus_to_dict(cus)})


# ─── API: detail ─────────────────────────────────────────────────────────────

@login_required(login_url='/login')
def customer_api_detail(request, customer_id):
    try:
        cus = customers.objects.get(customer_id=customer_id)
    except customers.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'ไม่พบข้อมูล'}, status=404)
    return JsonResponse({'status': 'ok', 'data': _cus_to_dict(cus)})


# ─── API: update ─────────────────────────────────────────────────────────────

@login_required(login_url='/login')
def customer_api_update(request, customer_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)
    try:
        cus = customers.objects.get(customer_id=customer_id)
    except customers.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'ไม่พบข้อมูล'}, status=404)

    ctype = int(request.POST.get('customer_type', cus.customer_type))
    name  = request.POST.get('customer_name', '').strip()
    first = request.POST.get('customer_fisrt', '').strip()
    last  = request.POST.get('customer_last', '').strip()

    cus.customer_name    = name or f'{first} {last}'.strip()
    cus.customer_fisrt   = first
    cus.customer_last    = last
    cus.customer_tax     = request.POST.get('customer_tax', cus.customer_tax)
    cus.customer_phone   = request.POST.get('customer_phone', cus.customer_phone)
    cus.customer_email   = request.POST.get('customer_email', cus.customer_email)
    cus.customer_address = request.POST.get('customer_address', cus.customer_address)
    cus.location_id      = int(request.POST.get('location_id') or cus.location_id or 0)
    cus.customer_type    = ctype
    cus.save()
    return JsonResponse({'status': 'ok', 'data': _cus_to_dict(cus)})


# ─── API: delete ─────────────────────────────────────────────────────────────

@login_required(login_url='/login')
def customer_api_delete(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)
    customer_id = request.POST.get('customer_id')
    try:
        customers.objects.filter(customer_id=customer_id).delete()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
