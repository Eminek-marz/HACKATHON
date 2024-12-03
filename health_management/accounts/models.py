from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
        ('ADMIN', 'Admin'),
    )
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='PATIENT'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
    
    @property
    def is_admin(self):
        return self.user_type == 'ADMIN'
    
    def save(self, *args, **kwargs):
        # Set boolean flags based on user_type
        self.is_doctor = (self.user_type == 'DOCTOR')
        self.is_patient = (self.user_type == 'PATIENT')
        super().save(*args, **kwargs)

class Patient(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True)
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def get_age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    license_number = models.CharField(max_length=50)
    availability = models.JSONField(null=True, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    education = models.TextField(blank=True)
    achievements = models.TextField(blank=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

    def get_formatted_schedule(self):
        if not self.availability:
            return "No schedule set"
        
        schedule = []
        working_days = self.availability.get('working_days', [])
        hours = self.availability.get('hours', {})
        break_time = self.availability.get('break', {})
        
        if working_days and hours:
            schedule.append(f"Working Days: {', '.join(working_days)}")
            schedule.append(f"Hours: {hours.get('start')} - {hours.get('end')}")
            
            if break_time:
                schedule.append(
                    f"Break: {break_time.get('start')} - {break_time.get('end')}"
                )
                
        return "\n".join(schedule) 
