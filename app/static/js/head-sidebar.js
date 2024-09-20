document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('toggle-btn');

    toggleBtn.addEventListener('click', function () {
        sidebar.classList.toggle('expand');
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const profileDropdown = document.getElementById('profileDropdown');
    const dropdownMenu = profileDropdown.nextElementSibling;

    profileDropdown.addEventListener('click', function(event) {
        event.preventDefault();
        dropdownMenu.classList.toggle('show');
    });

    document.addEventListener('click', function(event) {
        if (!profileDropdown.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.remove('show');
        }
    });
});


document.querySelector('.dropdown-item[href="#"]').addEventListener('click', function(event) {
    event.preventDefault();
    var editProfileModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
    editProfileModal.show();
});


document.getElementById('picture').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('profile-picture-preview').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const profileDropdown = document.getElementById('profileDropdown');
    const dropdownMenu = profileDropdown.nextElementSibling;

    profileDropdown.addEventListener('click', function(event) {
        event.preventDefault();
        dropdownMenu.classList.toggle('show');
    });

    document.addEventListener('click', function(event) {
        if (!profileDropdown.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.remove('show');
        }
    });
});
document.querySelector('.btn-close').addEventListener('click', function(event) {
    var editProfileModal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
    editProfileModal.hide();
    
    // Manually remove the backdrop
    document.querySelector('.modal-backdrop').remove();
});

document.querySelector('.modal').addEventListener('hidden.bs.modal', function () {
    document.querySelector('.modal-backdrop').remove();
});


// Sidebar toggle logic remains unchanged

// Function to show the loading spinner
function showSpinner() {
    const spinnerOverlay = document.querySelector('.spinner-overlay');
    spinnerOverlay.classList.add('active');
}

// Function to hide the loading spinner
function hideSpinner() {
    const spinnerOverlay = document.querySelector('.spinner-overlay');
    spinnerOverlay.classList.remove('active');
}

// Add event listener to the sidebar links (except no-loading)
document.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('click', function(event) {
        // Check if the clicked link does not have the 'no-loading' class
        if (!link.classList.contains('no-loading')) {
            showSpinner();
        }
    });
});

// Hide the spinner after page load (in case it remains visible)
window.addEventListener('load', hideSpinner);

function updateDateTime() {
    const dateTimeElement = document.getElementById('date-time');
    const now = new Date();

    // Format the date and time
    const formattedDate = now.toLocaleDateString('en-US', {
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric'
    });

    const formattedTime = now.toLocaleTimeString('en-US', {
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit'
    });

    dateTimeElement.textContent = `${formattedDate} | ${formattedTime}`;
}

// Update the date and time immediately and then every second
updateDateTime();
setInterval(updateDateTime, 1000);

document.querySelector('.notification-bell').addEventListener('click', function() {
    const notificationBar = document.getElementById('notification-bar');
    notificationBar.classList.toggle('open');
});

document.querySelector('.close-notification-bar').addEventListener('click', function() {
    const notificationBar = document.getElementById('notification-bar');
    notificationBar.classList.remove('open');
});

