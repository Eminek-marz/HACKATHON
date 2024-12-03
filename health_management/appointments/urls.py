from django.urls import path
from . import views
urlpatterns = [
    # ... existing urls ...
    path('prescription/add/<int:appointment_id>/', views.add_prescription, name='add_prescription'),
    path('medical-test/add/<int:appointment_id>/', views.add_medical_test, name='add_medical_test'),
    path('medical-test/<int:test_id>/', views.view_medical_test, name='view_medical_test'),
] 