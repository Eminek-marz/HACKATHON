from django import forms
from accounts.models import Patient, Doctor
from .models import Feedback, MedicalRecord, Schedule, Appointment
from datetime import datetime

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['date_of_birth', 'blood_group', 'allergies', 'chronic_conditions',
                 'emergency_contact_name', 'emergency_contact_phone']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 3}),
        }

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'education', 'experience_years', 
                 'consultation_fee', 'achievements']
        widgets = {
            'education': forms.Textarea(attrs={'rows': 3}),
            'achievements': forms.Textarea(attrs={'rows': 3}),
        }

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'prescription', 'notes', 'next_appointment']
        widgets = {
            'next_appointment': forms.DateInput(attrs={'type': 'date'}),
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'prescription': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['working_days', 'start_time', 'end_time', 'break_start', 'break_end']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'break_start': forms.TimeInput(attrs={'type': 'time'}),
            'break_end': forms.TimeInput(attrs={'type': 'time'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'message']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'rating': 'Rating (1-5 stars)',
            'message': 'Your Feedback',
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': datetime.now().date().isoformat()}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.all()
        self.fields['doctor'].empty_label = "Select a Doctor" 