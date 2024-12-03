// Show/hide password functionality
document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.querySelectorAll('.toggle-password');
    
    togglePassword.forEach(button => {
        button.addEventListener('click', function() {
            const input = document.querySelector(this.getAttribute('toggle'));
            if (input.getAttribute('type') === 'password') {
                input.setAttribute('type', 'text');
                this.classList.add('showing');
            } else {
                input.setAttribute('type', 'password');
                this.classList.remove('showing');
            }
        });
    });

    // Handle alerts dismissal
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 3000);
    });
});

// Form validation
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
} 