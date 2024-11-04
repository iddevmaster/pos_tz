from django import forms
from ..constant import prefixEng,prefixThai

class studentForm(forms.Form):
    student_identification_number = forms.CharField(label="รหัสบัตร ปชช./ Passport", max_length=64,
                                                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    student_prefix_th = forms.ChoiceField(label="คำนำหน้าภาษาไทย", required=False,
                                          choices=prefixThai, widget=forms.Select(attrs={'class': 'form-control'}))
    student_firstname_th = forms.CharField(label="ชื่อภาษาไทย", max_length=128,
                                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    student_lastname_th = forms.CharField(label="นามสกุลภาษาไทย", max_length=128,
                                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    student_prefix_eng = forms.ChoiceField(label="คำนำหน้าภาษาอังกฤษ", required=False,
                                           choices=prefixEng, widget=forms.Select(attrs={'class': 'form-control'}))
    student_firstname_eng = forms.CharField(label="ชื่อภาษาอังกฤษ", max_length=128,
                                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    student_lastname_eng = forms.CharField(label="นามสกุลภาษาอังกฤษ", max_length=128,
                                           widget=forms.TextInput(attrs={'class': 'form-control'}))
