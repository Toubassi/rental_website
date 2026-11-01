
const bell = document.getElementById('notification-bell');
const count = document.getElementById('notification-count');
const dropdown = document.getElementById('notification-dropdown');
const notificationList = document.getElementById('notification-list');

// Get notifications from Django
fetch('/notifications/')
    .then(response => response.json())
    .then(data => {

        let notifications = data.notifications;

        // Show notification count
        count.innerText = notifications.length;

        // Display notifications
        notificationList.innerHTML = '';

        if (notifications.length === 0) {
            notificationList.innerText = 'No notifications yet.';
        }

        for (let i = 0; i < notifications.length; i++) {

            let notification = document.createElement('a');

            notification.innerText = notifications[i].message;
            notification.href = '/my-booking-requests/';

            notificationList.appendChild(notification);
        }
    });

// Open and close notifications
bell.addEventListener('click', function () {
    dropdown.classList.toggle('show');
});
