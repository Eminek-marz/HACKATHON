from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Specialization, User, Patient, Doctor

class PatientSignUpForm(UserCreationForm):
    date_of_birth = forms.DateField()
    blood_group = forms.CharField(max_length=5)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number', 'address', 
                 'date_of_birth', 'blood_group')

    def save(self):
        user = super().save(commit=False)
        user.is_patient = True
        user.save()
        patient = Patient.objects.create(
            user=user,
            date_of_birth=self.cleaned_data.get('date_of_birth'),
            blood_group=self.cleaned_data.get('blood_group')
        )
        return user

class DoctorSignUpForm(forms.ModelForm):
    specialization = forms.ModelChoiceField(
        queryset=Specialization.objects.all(),
        empty_label="Select Specialization"
    )
    license_number = forms.CharField(max_length=50)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'address', 'password1', 'password2', 'license_number']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'DOCTOR'
        if commit:
            user.save()
            Doctor.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                license_number=self.cleaned_data['license_number']
            )
        return user

class DoctorScheduleForm(forms.ModelForm):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    working_days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    break_start = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=False
    )
    break_end = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=False
    )

    class Meta:
        model = Doctor
        fields = ['working_days', 'start_time', 'end_time', 'break_start', 'break_end']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        break_start = cleaned_data.get('break_start')
        break_end = cleaned_data.get('break_end')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time")

        if break_start and break_end and break_start >= break_end:
            raise forms.ValidationError("Break end time must be after break start time")

        return cleaned_data

    def save(self, commit=True):
        doctor = super().save(commit=False)
        schedule = {
            'working_days': self.cleaned_data['working_days'],
            'hours': {
                'start': self.cleaned_data['start_time'].strftime('%H:%M'),
                'end': self.cleaned_data['end_time'].strftime('%H:%M'),
            }
        }
        
        if self.cleaned_data['break_start'] and self.cleaned_data['break_end']:
            schedule['break'] = {
                'start': self.cleaned_data['break_start'].strftime('%H:%M'),
                'end': self.cleaned_data['break_end'].strftime('%H:%M'),
            }
            
        doctor.availability = schedule
        if commit:
            doctor.save()
        return doctor 

class PatientMedicalRecordForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'blood_group', 'allergies', 'chronic_conditions',
            'current_medications', 'medical_history',
            'emergency_contact_name', 'emergency_contact_phone',
            'weight', 'height'
        ]
        widgets = {
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 3}),
            'current_medications': forms.Textarea(attrs={'rows': 3}),
            'medical_history': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})