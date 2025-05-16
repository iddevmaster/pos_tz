from django import forms
import calendar

THAI_MONTHS = [
    (i, calendar.month_name[i]) for i in range(1, 13)
]

class MyForm(forms.Form):
    month = forms.ChoiceField(choices=THAI_MONTHS, label='เดือน')

# หรือถ้าต้องการให้ชื่อเดือนเป็นภาษาไทยโดยเฉพาะ
THAI_MONTH_NAMES = [
    (1, 'มกราคม'),
    (2, 'กุมภาพันธ์'),
    (3, 'มีนาคม'),
    (4, 'เมษายน'),
    (5, 'พฤษภาคม'),
    (6, 'มิถุนายน'),
    (7, 'กรกฎาคม'),
    (8, 'สิงหาคม'),
    (9, 'กันยายน'),
    (10, 'ตุลาคม'),
    (11, 'พฤศจิกายน'),
    (12, 'ธันวาคม'),
]

class MyFormWithThai(forms.Form):
    month = forms.ChoiceField(choices=THAI_MONTH_NAMES, label='เดือน')