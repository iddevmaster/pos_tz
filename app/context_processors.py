def sale_permission(request):
    """ส่งสิทธิ์เปิดการขายให้ทุก template (ใช้ซ่อน/แสดงเมนูใน base.html)"""
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {}
    from .functions import user_sale_perms, SALE_PERM_EVENT, SALE_PERM_NOEVENT
    perms = user_sale_perms(request)
    return {
        'can_sale_event': SALE_PERM_EVENT in perms,
        'can_sale_noevent': SALE_PERM_NOEVENT in perms,
    }
