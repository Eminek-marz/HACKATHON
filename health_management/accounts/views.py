from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from .forms import DoctorSignUpForm, PatientSignUpForm
from django.contrib.auth.decorators import login_required
from .models import User
from accounts.models import Doctor
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.user_type == 'PATIENT':
                return reverse_lazy('portal:patient_dashboard')
            elif user.user_type == 'DOCTOR':
                return reverse_lazy('portal:doctor_dashboard')
            elif user.user_type == 'ADMIN':
                return reverse_lazy('portal:admin_dashboard')
        return reverse_lazy('portal:dashboard')  # fallback

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        response = super().form_valid(form)
        user = form.get_user()
        if not user.user_type:  # If user_type is not set
            user.user_type = 'PATIENT' if user.is_patient else 'DOCTOR'
            user.save()
        return response

class DoctorSignUpView(CreateView):
    model = User
    form_class = DoctorSignUpForm
    template_name = 'accounts/doctor_signup.html'

    def get(self, request, *args, **kwargs):
        print("Doctor signup page accessed")  # Debug print
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        print("Doctor form submitted")  # Debug print
        user = form.save()
        login(self.request, user)
        return redirect('portal:doctor_dashboard')

class PatientSignUpView(CreateView):
    model = User
    form_class = PatientSignUpForm
    template_name = 'accounts/patient_signup.html'

    def get(self, request, *args, **kwargs):
        print("Patient signup page accessed")  # Debug print
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        print("Patient form submitted")  # Debug print
        user = form.save()
        login(self.request, user)
        return redirect('portal:patient_dashboard')

@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

def landing(request):
    # Landing page should be accessible to everyone
    return render(request, 'accounts/landing.html')
