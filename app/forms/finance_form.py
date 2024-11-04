from django import forms
from ..models import billing_cycle_setting
from ..constant import dayChoices

class billing_cycle_setting_form(forms.ModelForm):
    bcs_start_day = forms.ChoiceField(
        choices=dayChoices,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'วันเริ่มต้น', 'required': 'required'}),
        label='วันเริ่มต้น'
    )
    bcs_end_day = forms.ChoiceField(
        choices=dayChoices,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'วันเริ่มสิ้นสุด', 'required': 'required'}),
        label='วันเริ่มสิ้นสุด'
    )
    module = forms.CharField(max_length=128,label="", widget=forms.TextInput(attrs={'class': 'form-control','type':'hidden'}))
    class Meta:
        model = billing_cycle_setting
        fields = ('__all__')
        