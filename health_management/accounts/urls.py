from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/doctor/', views.DoctorSignUpView.as_view(), name='doctor_signup'),
    path('signup/patient/', views.PatientSignUpView.as_view(), name='patient_signup'),
    
] 