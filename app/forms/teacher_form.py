from django import forms
from ..constant import prefixEng,prefixThai,activeChoices,teacherTypeChoices,unitPayChoices,Levelchoices
from ..models import teacher,pay_item
class teacherForm(forms.Form):
    teacher_cover = forms.ImageField(label="รูประจำตัวครู / วิทยากร")
    teacher_identification_number = forms.CharField(
        label="รหัสบัตร ปชช./ Passport", max_length=64, widget=forms.TextInput(attrs={'class': 'form-control'}))
    teacher_prefix_th = forms.ChoiceField(label="คำนำหน้าภาษาไทย", required=False,
                                          choices=prefixThai, widget=forms.Select(attrs={'class': 'form-control'}))
    teacher_firstname_th = forms.CharField(label="ชื่อภาษาไทย",max_length=128,   widget=forms.TextInput(attrs={'class': 'form-control'}))
    teacher_lastname_th = forms.CharField(
        label="นามสกุลภาษาไทย", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    teacher_prefix_eng = forms.ChoiceField(
        label="คำนำหน้าภาษาอังกฤษ", required=False, choices=prefixEng, widget=forms.Select(attrs={'class': 'form-control'}))
    teacher_firstname_eng = forms.CharField(label="ชื่อภาษาอังกฤษ", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    teacher_lastname_eng = forms.CharField(
        label="นามสกุลภาษาอังกฤษ", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    teacher_type = forms.ChoiceField(label="ประเภท", choices=teacherTypeChoices, widget=forms.Select(attrs={'class': 'form-control'}))
    active = forms.ChoiceField(label="Active", choices=activeChoices, widget=forms.Select(attrs={'class': 'form-control'}))
    level = forms.ChoiceField(label="Level", choices=Levelchoices, widget=forms.Select(attrs={'class': 'form-control'}))


class teacherIncomeSettingForm(forms.Form):
    pi = forms.ModelChoiceField(
        queryset=pay_item.objects.filter(
            cancelled=1, active=1), to_field_name='pk', label="ตำแหน่ง / หน้าที่ / รายการ", empty_label=None, widget=forms.Select(attrs={'class': 'select2'}))
    tis_compensation = forms.CharField(label="ค่าตอบแทน", widget=forms.TextInput(attrs={'class': 'form-control'}))
    # tis_unit = forms.CharField(label="หน่วย (เช่น ชั่วโมง,วัน,สัปดาห์ ,เดือน)",max_length=128,  widget=forms.TextInput(attrs={'class': 'form-control'}))
    tis_unit = forms.ChoiceField(label="หน่วย", choices=unitPayChoices, widget=forms.Select(attrs={'class': 'form-control'}))
    tis_quantity = forms.CharField(label="จำนวนต่อหน่วย",  widget=forms.TextInput(attrs={'class': 'form-control'}))
    tis_sum = forms.CharField(label="รวม",  widget=forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}))
    teacher = forms.ModelChoiceField(
        queryset=teacher.objects.filter(
            cancelled=1, active=1), to_field_name='pk', label="ครู - วิทยากร", empty_label=None, widget=forms.Select(attrs={'class': 'select2'}))
    # active = forms.ChoiceField(label="Active", choices=activeChoices, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self,  module, *args, **kwargs):
        super(teacherIncomeSettingForm, self).__init__(*args, **kwargs)
        # print(categor_value)
        if module is not None:
            self.fields['teacher'].queryset = teacher.objects.filter(
                module=module, cancelled=1, active=1)
