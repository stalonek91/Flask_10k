document.addEventListener('DOMContentLoaded', function() {
    const totalHours = /* Total hours from server */;
    const container = document.getElementById('hour-container');

    for (let i = 0; i < 10000; i++) {
        const square = document.createElement('div');
        square.className = 'hour-square';

        if (i < totalHours) {
            square.classList.add('hour-square-filled');
        } else if (i < totalHours + 0.5) {
            square.classList.add('hour-square-half-filled');
        }

        container.appendChild(square);
    }
});
