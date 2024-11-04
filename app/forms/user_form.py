from django import forms
from ..models import category_program
from ..constant import activeChoices

class category_program_form(forms.ModelForm):
    cm_name = forms.CharField(label="กลุ่มผู้ใช้งาน",max_length=128,   widget=forms.TextInput(attrs={'class': 'form-control'}))
    active = forms.ChoiceField(
        choices=activeChoices,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'เปิด-ปิด', 'required': 'required'}),
        label='เปิด-ปิด'
    )
    module = forms.CharField(max_length=12,label="", widget=forms.TextInput(attrs={'class': 'form-control','type':'hidden'}))
    class Meta:
        model = category_program
        exclude = ['cancelled']
        