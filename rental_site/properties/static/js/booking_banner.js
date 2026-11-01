// Booking banner under the nav: shows the 3 newest booking updates
// (approved / rejected) that the user has not dismissed yet.
// Dismissed updates are remembered in this browser (localStorage).
(function () {
    const banner = document.getElementById('booking-banner');
    if (!banner) {
        return;
    }

    const STORAGE_KEY = 'hf-dismissed-notices';
    const MAX_SHOWN = 3;

    // Read the dismissed keys. Works (as an empty list) if localStorage is blocked.
    function readDismissed() {
        try {
            const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
            return Array.isArray(saved) ? saved : [];
        } catch (error) {
            return [];
        }
    }

    function saveDismissed(keys) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(keys));
        } catch (error) {
            // Storage blocked or full: the row still disappears for now.
        }
    }

    function hideIfEmpty() {
        if (!banner.children.length) {
            banner.hidden = true;
        }
    }

    function buildRow(notice, key) {
        const isApproved = notice.status === 'approved';

        const row = document.createElement('div');
        row.className = 'booking-banner-item ' + (isApproved ? 'is-approved' : 'is-rejected');

        const icon = document.createElement('span');
        icon.className = 'booking-banner-icon';
        icon.setAttribute('aria-hidden', 'true');
        icon.textContent = isApproved ? '✓' : '✕';

        const text = document.createElement('span');
        text.className = 'booking-banner-text';
        text.textContent = notice.message;

        const close = document.createElement('button');
        close.type = 'button';
        close.className = 'booking-banner-close';
        close.setAttribute('aria-label', 'Dismiss notification');
        close.textContent = '×';
        close.addEventListener('click', function () {
            row.remove();
            const keys = readDismissed();
            if (!keys.includes(key)) {
                keys.push(key);
                saveDismissed(keys);
            }
            hideIfEmpty();
        });

        row.append(icon, text, close);
        return row;
    }

    fetch('/notifications/')
        .then(response => response.json())
        .then(data => {
            const list = (data && Array.isArray(data.notifications)) ? data.notifications : [];
            const dismissed = readDismissed();

            const toShow = list
                .filter(notice => notice && (notice.status === 'approved' || notice.status === 'rejected'))
                .filter(notice => !dismissed.includes(`${notice.booking_id}-${notice.status}`))
                .slice(0, MAX_SHOWN);

            toShow.forEach(notice => {
                const key = `${notice.booking_id}-${notice.status}`;
                banner.appendChild(buildRow(notice, key));
            });

            banner.hidden = toShow.length === 0;
        })
        .catch(() => {
            // Not logged in, server error or not JSON: keep the banner hidden.
            banner.hidden = true;
        });
})();
