document.addEventListener('DOMContentLoaded', function() {
    const mainButton = document.getElementById('main-button');
    const alertButton = document.getElementById('alert-button');
    const driverRegButton = document.getElementById('driver-reg-button');
    const startScreen = document.getElementById('start-screen');

    if (mainButton) {
        mainButton.addEventListener('click', function() {
            startScreen.classList.add('fade-out');
            setTimeout(() => {
                startScreen.style.display = 'none';
            }, 1000); // Соответствует времени анимации в CSS
        });
    }

    if (alertButton) {
        alertButton.addEventListener('click', function() {
            alert('Включите трансляцию геопозиции (live location) перед использованием');
        });
    }

    if (driverRegButton) {
        driverRegButton.addEventListener('click', function() {
            const tgId = driverRegButton.getAttribute('data-tg-id');
            window.location.href = `/driver_reg?tg_id=${tgId}`;
        });
    }

    Telegram.WebApp.ready();
    Telegram.WebApp.expand();
});
