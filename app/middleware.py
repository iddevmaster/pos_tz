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
