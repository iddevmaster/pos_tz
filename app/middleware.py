import time


LAST_ACTIVITY_KEY = 'last_activity'
LAST_ACTIVITY_INTERVAL = 60  # บันทึกซ้ำทุก 60 วินาที เพื่อลดการเขียน session ทุก request


class LastActivityMiddleware:
    """บันทึกเวลาใช้งานล่าสุดของ User ลงใน session ใช้สำหรับหน้า User ที่ออนไลน์"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            now = int(time.time())
            last = request.session.get(LAST_ACTIVITY_KEY, 0)
            if now - last >= LAST_ACTIVITY_INTERVAL:
                forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
                request.session[LAST_ACTIVITY_KEY] = now
                request.session['last_ip'] = forwarded.split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')
                request.session['last_agent'] = request.META.get('HTTP_USER_AGENT', '')[:200]
        return self.get_response(request)


COM_LOCK_URL = '/com-lock/'
COM_LOCK_ALLOW = (
    COM_LOCK_URL, '/finance/sale/commission', '/api/', '/static/', '/media/',
    '/login', '/logout', '/authen_check', '/admin',
    # หลังเปิดบิล ระบบพาไปหน้าประวัติบิล/พิมพ์ใบเสร็จ -> ให้ใช้ได้
    '/register/payment/history/', '/salesnotevent/payment/history/',
    '/register/print/', '/salesnotevent/print/',
)
COM_LOCK_OK_KEY = 'com_lock_ok_until'
COM_LOCK_OK_TTL = 30  # ไม่ติดล็อค -> ไม่ต้องเช็คซ้ำ 30 วินาที


class ComLockMiddleware:
    """ล็อคเว็บ: คนเปิดบิลเงินสด (user_create) ที่ยังกำหนดค่าคอมไม่ครบ (บิลเดือนนี้)
    จะเข้าได้แค่หน้า /com-lock/ หน้ากำหนดค่าคอม และหน้าพิมพ์บิล จนกว่าจะกำหนดครบ
    เช็คเฉพาะการเปิดหน้าเว็บ (GET) ไม่ยุ่งกับ API / AJAX"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if (user is not None and user.is_authenticated and request.method == 'GET'
                and not request.path.startswith(COM_LOCK_ALLOW)
                and request.headers.get('x-requested-with') != 'XMLHttpRequest'):
            now = int(time.time())
            if request.session.get(COM_LOCK_OK_KEY, 0) < now:
                from .functions import creator_missing_com_bills
                if creator_missing_com_bills(user.id):
                    from django.shortcuts import redirect
                    return redirect(COM_LOCK_URL)
                request.session[COM_LOCK_OK_KEY] = now + COM_LOCK_OK_TTL
        return self.get_response(request)
