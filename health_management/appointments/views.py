from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from functools import wraps
from .models import Appointment, MedicalTest
from appointments.forms import AppointmentForm, AppointmentUpdateForm, PrescriptionForm, MedicalTestForm
from accounts.models import Doctor
from datetime import datetime

def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_doctor:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def appointment_create(request):
    if not request.user.is_patient:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user.patient
            appointment.save()
            messages.success(request, 'Appointment scheduled successfully!')
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/appointment_form.html', {
        'form': form,
        'title': 'Schedule Appointment'
    })

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check if user has permission to view this appointment
    if not (request.user.is_patient and appointment.patient.user == request.user) and \
       not (request.user.is_doctor and appointment.doctor.user == request.user):
        raise PermissionDenied
    
    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment
    })

@login_required
def update_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Only the assigned doctor can update the appointment
    if not request.user.is_doctor or appointment.doctor.user != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = AppointmentUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('doctor_dashboard')
    else:
        form = AppointmentUpdateForm(instance=appointment)
    
    return render(request, 'appointments/appointment_form.html', {
        'form': form,
        'title': 'Update Appointment'
    })

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check if user has permission to cancel this appointment
    if not (request.user.is_patient and appointment.patient.user == request.user) and \
       not (request.user.is_doctor and appointment.doctor.user == request.user):
        raise PermissionDenied
    
    if request.method == 'POST':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully!')
        if request.user.is_patient:
            return redirect('patient_dashboard')
        return redirect('doctor_dashboard')
    
    return render(request, 'appointments/confirm_cancel.html', {
        'appointment': appointment
    })

@doctor_required
def add_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.doctor.user != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.save()
            messages.success(request, 'Prescription added successfully!')
            return redirect('appointment_detail', pk=appointment.pk)
    else:
        form = PrescriptionForm()

    return render(request, 'appointments/prescription_form.html', {
        'form': form,
        'appointment': appointment
    })

@doctor_required
def add_medical_test(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.doctor.user != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = MedicalTestForm(request.POST, request.FILES)
        if form.is_valid():
            test = form.save(commit=False)
            test.appointment = appointment
            test.save()
            messages.success(request, 'Medical test added successfully!')
            return redirect('appointment_detail', pk=appointment.pk)
    else:
        form = MedicalTestForm()

    return render(request, 'appointments/medical_test_form.html', {
        'form': form,
        'appointment': appointment
    })

@login_required
def view_medical_test(request, test_id):
    test = get_object_or_404(MedicalTest, id=test_id)
    if not (request.user.is_doctor or request.user == test.appointment.patient.user):
        raise PermissionDenied

    return render(request, 'appointments/medical_test_detail.html', {
        'test': test
    }) 
