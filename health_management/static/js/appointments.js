document.addEventListener('DOMContentLoaded', function() {
    // Time slot selection
    const timeSlots = document.querySelectorAll('.time-slot');
    timeSlots.forEach(slot => {
        slot.addEventListener('click', function() {
            if (!this.classList.contains('booked')) {
                timeSlots.forEach(s => s.classList.remove('selected'));
                this.classList.add('selected');
                document.getElementById('selected_time').value = this.dataset.time;
            }
        });
    });

    // Date picker initialization and validation
    const datePicker = document.getElementById('appointment_date');
    if (datePicker) {
        const today = new Date();
        const maxDate = new Date();
        maxDate.setDate(today.getDate() + 90); // 3 months ahead
        
        datePicker.min = today.toISOString().split('T')[0];
        datePicker.max = maxDate.toISOString().split('T')[0];
        
        datePicker.addEventListener('change', function() {
            updateAvailableTimeSlots(this.value);
        });
    }
});

// Function to update available time slots based on selected date
async function updateAvailableTimeSlots(date) {
    try {
        const response = await fetch(`/api/available-slots/${date}/`);
        const data = await response.json();
        
        const timeSlotsContainer = document.getElementById('time_slots');
        timeSlotsContainer.innerHTML = '';
        
        data.slots.forEach(slot => {
            const slotElement = document.createElement('div');
            slotElement.className = `time-slot ${slot.available ? 'available' : 'booked'}`;
            slotElement.dataset.time = slot.time;
            slotElement.textContent = slot.time;
            timeSlotsContainer.appendChild(slotElement);
        });
    } catch (error) {
        console.error('Error fetching time slots:', error);
    }
} 