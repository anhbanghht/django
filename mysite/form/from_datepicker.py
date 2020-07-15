from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput
from django import forms

class DatePickerForm(forms.Form):
    dateStart = forms.DateField(
        widget=DatePickerInput(format='%m/%d/%Y')
    )
    dateEnd = forms.DateField(
        widget=DatePickerInput(format='%m/%d/%Y')
    )
    timeStart = forms.DateField(
        widget=TimePickerInput(format='%H:%M')
    )
    timeEnd = forms.DateField(
        widget=TimePickerInput(format='%H:%M')
    )