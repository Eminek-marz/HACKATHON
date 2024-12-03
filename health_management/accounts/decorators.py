from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def doctor_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_doctor:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, 'You must be a doctor to access this page.')
            return redirect('portal:patient_dashboard')
    return wrap

def patient_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_patient:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, 'You must be a patient to access this page.')
            return redirect('portal:doctor_dashboard')
    return wrap 