from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from appointments.models import Appointment
from django.contrib import messages
from accounts.decorators import doctor_required, patient_required
from .models import MedicalRecord, Schedule, Feedback
from .forms import (
    MedicalRecordForm, ScheduleForm, FeedbackForm,
    PatientProfileForm, DoctorProfileForm, AppointmentForm
)
from accounts.models import Patient, Doctor
from datetime import date
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse  # Add this for debugging

@login_required
@doctor_required
def doctor_dashboard(request):
    # Return debug information directly in the response
    debug_info = f"""
    Username: {request.user.username}
    User Type: {request.user.user_type}
    Is Patient: {request.user.is_patient}
    Is Doctor: {request.user.is_doctor}
    Is Authenticated: {request.user.is_authenticated}
    """
    return HttpResponse(f"<pre>{debug_info}</pre>")

@login_required
@patient_required
def patient_dashboard(request):
    # Return debug information directly in the response
    debug_info = f"""
    Username: {request.user.username}
    User Type: {request.user.user_type}
    Is Patient: {request.user.is_patient}
    Is Doctor: {request.user.is_doctor}
    Is Authenticated: {request.user.is_authenticated}
    """
    return HttpResponse(f"<pre>{debug_info}</pre>")

@login_required
@doctor_required
def medical_record_detail(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    if request.user != record.doctor.user:
        messages.error(request, "You don't have permission to view this record.")
        return redirect('portal:doctor_dashboard')
    
    return render(request, 'portal/medical_record_detail.html', {
        'record': record
    })

@login_required
@doctor_required
def create_medical_record(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.doctor = request.user.doctor
            record.save()
            messages.success(request, 'Medical record created successfully.')
            return redirect('portal:medical_record_detail', pk=record.pk)
    else:
        form = MedicalRecordForm()
    
    return render(request, 'portal/medical_record_form.html', {
        'form': form,
        'patient': patient
    })

@login_required
@doctor_required
def update_schedule(request):
    schedule, created = Schedule.objects.get_or_create(doctor=request.user.doctor)
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully.')
            return redirect('portal:doctor_dashboard')
    else:
        form = ScheduleForm(instance=schedule)
    
    return render(request, 'portal/schedule_form.html', {
        'form': form
    })

@login_required
def update_profile(request):
    if request.user.is_doctor:
        profile = request.user.doctor
        form_class = DoctorProfileForm
    else:
        profile = request.user.patient
        form_class = PatientProfileForm
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('portal:doctor_dashboard' if request.user.is_doctor else 'portal:patient_dashboard')
    else:
        form = form_class(instance=profile)
    
    return render(request, 'portal/profile_form.html', {
        'form': form
    })

@login_required
@patient_required
def submit_feedback(request, doctor_id):
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.patient = request.user.patient
            feedback.doctor = doctor
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('portal:doctor_detail', pk=doctor_id)
    else:
        form = FeedbackForm()
    
    return render(request, 'portal/feedback_form.html', {
        'form': form,
        'doctor': doctor
    })

@login_required
def doctor_list(request):
    doctors = Doctor.objects.all().order_by('user__first_name')
    
    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialization__icontains=search_query)
        )
    
    # Add pagination
    paginator = Paginator(doctors, 10)  # Show 10 doctors per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'doctors': page_obj,
        'search_query': search_query,
        'title': 'Find a Doctor'
    }
    return render(request, 'portal/doctor_list.html', context)

@login_required
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    feedbacks = doctor.feedbacks.all()
    schedule = doctor.schedule if hasattr(doctor, 'schedule') else None
    
    context = {
        'doctor': doctor,
        'feedbacks': feedbacks,
        'schedule': schedule,
    }
    return render(request, 'portal/doctor_detail.html', context)

@login_required
@doctor_required
def add_feedback(request, patient_id):
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=patient_id)
        feedback = Feedback(
            doctor=request.user.doctor,
            patient=patient,
            subject=request.POST.get('subject'),
            message=request.POST.get('message')
        )
        feedback.save()
        messages.success(request, 'Feedback added successfully.')
        return redirect('portal:doctor_dashboard')
    return redirect('portal:doctor_dashboard')

@login_required
def appointment_list(request):
    if request.user.is_doctor:
        appointments = Appointment.objects.filter(
            doctor=request.user.doctor
        ).order_by('-date', 'time')
    else:
        appointments = Appointment.objects.filter(
            patient=request.user.patient
        ).order_by('-date', 'time')
    
    # Add pagination
    paginator = Paginator(appointments, 10)  # Show 10 appointments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'appointments': page_obj,
        'title': 'My Appointments'
    }
    return render(request, 'portal/appointments/appointment_list.html', context)

@login_required
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user.patient
            
            # Check if the selected time slot is available
            existing_appointment = Appointment.objects.filter(
                doctor=appointment.doctor,
                date=appointment.date,
                time=appointment.time
            ).exists()
            
            if existing_appointment:
                messages.error(request, 'This time slot is already booked. Please choose another time.')
                return render(request, 'portal/appointments/appointment_form.html', {'form': form})
            
            appointment.save()
            messages.success(request, 'Appointment scheduled successfully!')
            return redirect('portal:appointment_detail', pk=appointment.pk)
    else:
        # Pre-select doctor if provided in URL
        initial = {}
        doctor_id = request.GET.get('doctor')
        if doctor_id:
            try:
                doctor = Doctor.objects.get(pk=doctor_id)
                initial['doctor'] = doctor
            except Doctor.DoesNotExist:
                pass
        
        form = AppointmentForm(initial=initial)
    
    context = {
        'form': form,
        'title': 'Schedule Appointment'
    }
    return render(request, 'portal/appointments/appointment_form.html', context)

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check if the user has permission to view this appointment
    if not (request.user.is_doctor and request.user.doctor == appointment.doctor) and \
       not (request.user.is_patient and request.user.patient == appointment.patient):
        messages.error(request, "You don't have permission to view this appointment.")
        return redirect('portal:appointment_list')
    
    context = {
        'appointment': appointment,
        'title': f'Appointment Details - {appointment.date}',
        'can_modify': not appointment.is_past_due() and appointment.status == 'SCHEDULED'
    }
    
    if request.user.is_doctor:
        # Add any doctor-specific context
        context['medical_records'] = appointment.patient.medical_records.all()
    
    return render(request, 'portal/appointments/appointment_detail.html', context)

@login_required
def update_appointment_status(request, pk):
    if not request.user.is_doctor:
        messages.error(request, "Only doctors can update appointment status.")
        return redirect('portal:appointment_list')
    
    appointment = get_object_or_404(Appointment, pk=pk, doctor=request.user.doctor)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Appointment status updated to {appointment.get_status_display()}')
        else:
            messages.error(request, "Invalid status provided.")
    
    return redirect('portal:appointment_detail', pk=pk)

def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    context = {
        'doctor': doctor,
        'title': f'Dr. {doctor.user.get_full_name()}'
    }
    return render(request, 'portal/doctor_detail.html', context)

@login_required
def dashboard(request):
    # Return debug information directly in the response
    debug_info = f"""
    Username: {request.user.username}
    User Type: {request.user.user_type}
    Is Patient: {request.user.is_patient}
    Is Doctor: {request.user.is_doctor}
    Is Authenticated: {request.user.is_authenticated}
    """
    return HttpResponse(f"<pre>{debug_info}</pre>")