from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout

class UserTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Exclude these paths from the redirect logic
            excluded_paths = [
                '/logout/',
                '/login/',
                '/admin/',
                '/portal/dashboard/',
                '/portal/patient/dashboard/',
                '/portal/doctor/dashboard/',
                '/static/',
                '/media/',
            ]
            
            current_path = request.path
            if not any(current_path.startswith(path) for path in excluded_paths):
                if request.user.is_patient and current_path != '/portal/patient/dashboard/':
                    return redirect('portal:patient_dashboard')
                elif request.user.is_doctor and current_path != '/portal/doctor/dashboard/':
                    return redirect('portal:doctor_dashboard')

        response = self.get_response(request)
        return response 