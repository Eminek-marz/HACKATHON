from django.db import models
from accounts.models import Doctor, Patient
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Schedule(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE)
    working_days = models.CharField(max_length=100, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_start = models.TimeField()
    break_end = models.TimeField()

    def __str__(self):
        return f"{self.doctor}'s Schedule"

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_records')
    date_created = models.DateTimeField(auto_now_add=True)
    diagnosis = models.TextField()
    prescription = models.TextField()
    notes = models.TextField(blank=True)
    next_appointment = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"Medical Record for {self.patient} by Dr. {self.doctor}"

class Feedback(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='feedbacks')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"Feedback for Dr. {self.doctor.user.get_full_name()} by {self.patient.user.get_full_name()}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'time']
        # Ensure no double booking for doctors
        unique_together = ['doctor', 'date', 'time']

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.user.get_full_name()} on {self.date} at {self.time}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]

    def is_past_due(self):
        from datetime import datetime, date
        today = date.today()
        return (self.date < today or 
                (self.date == today and self.time < datetime.now().time())) 
