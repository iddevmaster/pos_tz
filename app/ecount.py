import json

import requests

LOGIN_TIMEOUT = 30
SAVE_TIMEOUT = 60
SESSION_EXPIRED_CODE = 'EXP00001'


class EcountError(Exception):
    def __init__(self, message, payload=None):
        super().__init__(message)
        # response ดิบจาก Ecount (ถ้ามี) ไว้แสดงให้ผู้ตั้งค่าตรวจสอบ
        self.payload = payload


def _decode_json(content):
    # Ecount ระบุ charset เป็น utf-8 แต่ข้อความภาษาไทยบางส่วนส่งมาเป็น TIS-620
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        text = content.decode('cp874', errors='replace')
    return json.loads(text)


def _post(url, body, timeout):
    """POST JSON ไป Ecount คืนค่า response ที่ decode แล้ว หรือ raise EcountError"""
    try:
        response = requests.post(url, json=body, timeout=timeout)
        return _decode_json(response.content)
    except requests.RequestException as error:
        raise EcountError('เชื่อมต่อ Ecount ไม่สำเร็จ', str(error))
    except ValueError:
        raise EcountError('Ecount ตอบกลับในรูปแบบที่ไม่รู้จัก', response.content.decode('utf-8', errors='replace'))


def login(setting):
    """ขอ SESSION_ID ใหม่จาก OAPILogin คืนค่า (session, response) หรือ raise EcountError"""
    required = (setting.login_url, setting.com_code, setting.user_id, setting.api_cert_key, setting.zone)
    if not all(required):
        raise EcountError('กรุณาตั้งค่าข้อมูลล็อกอิน Ecount ให้ครบก่อน')
    payload = _post(setting.login_url, {
        'COM_CODE': setting.com_code,
        'USER_ID': setting.user_id,
        'API_CERT_KEY': setting.api_cert_key,
        'LAN_TYPE': setting.lan_type,
        'ZONE': setting.zone,
    }, LOGIN_TIMEOUT)

    data = payload.get('Data') if isinstance(payload, dict) else None
    data = data if isinstance(data, dict) else {}
    datas = data.get('Datas')
    session_id = datas.get('SESSION_ID') if isinstance(datas, dict) else None
    if not session_id:
        raise EcountError(f"Ecount ปฏิเสธการล็อกอิน (Code {data.get('Code')}): {data.get('Message')}", payload)
    return session_id, payload


def _needs_login(payload):
    """Ecount ตอบ EXP00001 (Please login.) เมื่อ SESSION_ID หมดอายุหรือใช้ไม่ได้"""
    errors = payload.get('Errors') if isinstance(payload, dict) else None
    return isinstance(errors, list) and any(
        isinstance(error, dict) and error.get('Code') == SESSION_EXPIRED_CODE for error in errors
    )


def _relogin(setting):
    setting.token, _ = login(setting)
    setting.save(update_fields=['token'])


def save_sale(setting, sale_list):
    """ส่งรายการขายไป SaveSale คืนค่า (response, relogged)
    ถ้ายังไม่มี SESSION_ID หรือหมดอายุ จะขอ session ใหม่ บันทึกไว้ แล้วส่งซ้ำ 1 ครั้ง"""
    if not setting.api_url:
        raise EcountError('กรุณาตั้งค่า URL ของ API Ecount ก่อน')
    relogged = False
    if not setting.token:
        _relogin(setting)
        relogged = True
    body = {'SaleList': sale_list}
    # ต่อ SESSION_ID ตรงๆ แบบเดียวกับ Postman ไม่ encode ตัว $ และ :
    payload = _post(f"{setting.api_url}?SESSION_ID={setting.token}", body, SAVE_TIMEOUT)
    if _needs_login(payload) and not relogged:
        _relogin(setting)
        relogged = True
        payload = _post(f"{setting.api_url}?SESSION_ID={setting.token}", body, SAVE_TIMEOUT)
    return payload, relogged
