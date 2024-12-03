from django import forms
from .models import Appointment, Prescription, MedicalTest
from accounts.models import Doctor
from datetime import datetime, timedelta
from .utils import is_time_slot_available
import os

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.all()
        
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        doctor = cleaned_data.get('doctor')
        
        if date and time and doctor:
            # Check if date is in the past
            if date < date.today():
                raise forms.ValidationError("Cannot schedule appointments in the past")

            # Check if date is too far in the future (e.g., more than 3 months)
            max_date = date.today() + timedelta(days=90)
            if date > max_date:
                raise forms.ValidationError("Cannot schedule appointments more than 3 months in advance")

            # Check doctor availability
            if not is_time_slot_available(doctor, date, time):
                raise forms.ValidationError(
                    "This time slot is not available. Please select another time."
                )
        
        return cleaned_data

class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'notes'] 

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medicine_name', 'dosage', 'frequency', 'duration', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 3}),
        }

class MedicalTestForm(forms.ModelForm):
    class Meta:
        model = MedicalTest
        fields = ['test_name', 'description', 'test_date', 'results', 'report_file']
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'results': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_report_file(self):
        file = self.cleaned_data.get('report_file')
        if file:
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be under 5MB")
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            ext = os.path.splitext(file.name)[1]
            if ext.lower() not in valid_extensions:
                raise forms.ValidationError("Only PDF and image files are allowed")
        return file