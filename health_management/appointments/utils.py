from datetime import datetime, timedelta
from .models import Appointment

def is_time_slot_available(doctor, date, time):
    """Check if the time slot is available for the doctor."""
    # Check if the doctor works on this day
    day_name = date.strftime('%A')
    if day_name not in doctor.availability.get('working_days', []):
        return False
    
    # Check working hours
    hours = doctor.availability.get('hours', {})
    start_time = datetime.strptime(hours.get('start', '00:00'), '%H:%M').time()
    end_time = datetime.strptime(hours.get('end', '23:59'), '%H:%M').time()
    
    if time < start_time or time > end_time:
        return False
    
    # Check break time
    break_time = doctor.availability.get('break', {})
    if break_time:
        break_start = datetime.strptime(break_time.get('start'), '%H:%M').time()
        break_end = datetime.strptime(break_time.get('end'), '%H:%M').time()
        if break_start <= time <= break_end:
            return False
    
    # Check for existing appointments
    appointment_duration = timedelta(minutes=30)  # Assuming 30-minute appointments
    appointment_end_time = (
        datetime.combine(date, time) + appointment_duration
    ).time()
    
    existing_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=date,
        status__in=['PENDING', 'CONFIRMED']
    )
    
    for existing_apt in existing_appointments:
        existing_end_time = (
            datetime.combine(date, existing_apt.time) + appointment_duration
        ).time()
        
        if (time <= existing_apt.time < appointment_end_time or
            existing_apt.time <= time < existing_end_time):
            return False
    
    return True 