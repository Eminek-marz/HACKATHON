from django.urls import path
from portal import views

app_name = 'portal'

urlpatterns = [
    # Dashboard URLs
    path('portal/doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    
    # Other portal-specific URLs
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('feedback/add/<int:patient_id>/', views.add_feedback, name='add_feedback'),
    path('appointment/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointment/<int:pk>/update-status/', views.update_appointment_status, name='update_appointment_status'),
    path('doctor/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    # ... other URLs ...
] 