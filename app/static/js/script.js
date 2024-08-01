let map;
let userMarker;
let otherMarkers = [];

// Define custom icons
const passengerIcon = L.icon({
    iconUrl: 'static/icons/passenger.png',
    iconSize: [16, 24],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
});

const driverIcon = L.icon({
    iconUrl: 'static/icons/driver.png',
    iconSize: [16, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
});

function initializeMap(latitude, longitude, role) {
    console.log(`Initializing map with latitude=${latitude}, longitude=${longitude}, role=${role}`);
    map = L.map('map').setView([latitude, longitude], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    userMarker = L.marker([latitude, longitude], { icon: role === 'driver' ? driverIcon : passengerIcon }).addTo(map)
        .bindPopup('Вы здесь').openPopup();
}

function updateMap(latitude, longitude, role) {
    console.log(`Updating map with latitude=${latitude}, longitude=${longitude}, role=${role}`);
    if (userMarker) {
        userMarker.setLatLng([latitude, longitude]);
        userMarker.setIcon(role === 'driver' ? driverIcon : passengerIcon);
        map.setView([latitude, longitude]);
    } else {
        userMarker = L.marker([latitude, longitude], { icon: role === 'driver' ? driverIcon : passengerIcon }).addTo(map)
            .bindPopup('Вы здесь').openPopup();
    }
}

function updateUserData(tg_id, role) {
    console.log(`updateUserData called with tg_id=${tg_id}, role=${role}`);
    $.getJSON('/user_data', { tg_id: tg_id })
        .done(function(data) {
            console.log(`updateUserData response: ${JSON.stringify(data)}`);
            if (!data.error) {
                if (!map) {
                    initializeMap(data.latitude, data.longitude, role);
                } else {
                    updateMap(data.latitude, data.longitude, role);
                }
            } else {
                console.error("Error fetching user data: ", data.error);
            }
        })
        .fail(function(jqxhr, textStatus, error) {
            console.error("Request Failed: ", textStatus, error);
            console.log(`Request Failed: ${textStatus}, ${error}`);
        });
}

function updateUsersByRole(role, current_tg_id) {
    console.log(`updateUsersByRole called with role=${role}, current_tg_id=${current_tg_id}`);
    $.getJSON('/users_by_role', { role: role, current_tg_id: current_tg_id })
    .done(function(response) {
        console.log(`updateUsersByRole response: ${JSON.stringify(response)}`);
        if (!response.error) {
            let users = response.users;  // Исправлено: получить users из response.users
            let activeDriversExist = response.active_drivers_exist;  // Исправлено: получить activeDriversExist из response.active_drivers_exist

            $('#user-list').empty();
            otherMarkers.forEach(marker => map.removeLayer(marker));
            otherMarkers = [];

            // Сортировка пользователей по расстоянию
            users.sort((a, b) => a.distance - b.distance);

            let activeDrivers = 0;

            users.forEach(function(user) {
                if (user.status === 'active') {
                    const userCard = $(`
                        <div class="user-card" data-passenger-id="${current_tg_id}" data-driver-id="${user.tg_id}">
                            <!-- Весь остальной контент вашей карточки пользователя -->
                        </div>
                    `);

                    let distanceText = '';
                    let distanceClass = '';

                    if (user.distance < 1) {
                        distanceText = `${(user.distance * 1000).toFixed(0)} m`;
                        distanceClass = 'distance-green';
                    } else {
                        distanceText = `${user.distance.toFixed(2)} km`;
                        if (user.distance <= 5) {
                            distanceClass = 'distance-green';
                        } else if (user.distance <= 10) {
                            distanceClass = 'distance-orange';
                        } else {
                            distanceClass = 'distance-red';
                        }
                    }

                    if (user.role === 'driver') {
                        userCard.addClass('driver');
                        userCard.append(`
                            <style>
                                #driver-navbar {
                                    display: none;
                                }

                                #driver-navbar-content {
                                    display: none !important;
                                }
                            </style>
                            <div class="car-info">
                                <div class="car-number">${user.car_number}</div>
                                <div class="car-model">${user.car_model}</div>
                                <div class="distance ${distanceClass}">${distanceText}</div>
                            </div>
                            
                            <div class="user-details">
                                <div class="user-name">${user.surname} ${user.name}</div>
                                <div class="comment">Примечание: ${user.comment}</div>
                            </div>
                        `);
                        activeDrivers++;
                    } else if (user.role === 'passenger') {
                        userCard.addClass('passenger');
                        userCard.append(`
                            <style>
                                #navbar-content {
                                    display: none !important;
                                }
                                
                                #no-drivers-message {
                                    display: none !important;
                                }
                            </style>
                            <div class="user-details">
                                <div class="user-name">${user.surname} ${user.name}</div>
                                <div class="comment">Примечание: ${user.comment}</div>
                            </div>
                        `);
                    }

                    $('#user-list').append(userCard);

                    userCard.on('click', function() {
                        const passenger_id = $(this).data('passenger-id');
                        const driver_id = $(this).data('driver-id');
                        const car_number = $(this).find('.car-number').text();
                        const car_model = $(this).find('.car-model').text();

                        handleUserInteraction(passenger_id, driver_id, car_number, car_model);
                    });

                    const icon = user.role === 'driver' ? driverIcon : passengerIcon;
                    const marker = L.marker([user.latitude, user.longitude], { icon: icon }).addTo(map)
                        .bindPopup(`${user.role === 'driver' ? user.car_number : '@' + user.username}: ${distanceText}`);

                    marker.on('click', function() {
                        handleUserInteraction(current_tg_id, user.tg_id, user.car_number, user.car_model);
                    });

                    otherMarkers.push(marker);
                }
            });

            if (role === 'passenger') {
                if (activeDrivers === 0) {
                    $('#driver-navbar').addClass('hidden');
                    $('#no-drivers-message').removeClass('hidden');
                } else {
                    $('#driver-navbar').addClass('hidden');
                    $('#no-drivers-message').addClass('hidden');
                }
            } else if (role === 'driver') {
                $('#driver-navbar').removeClass('hidden');
                $('#no-drivers-message').addClass('hidden');
            }
        }
    })
    .fail(function(jqxhr, textStatus, error) {
        console.error("Request Failed: ", textStatus, error);
        console.log(`Request Failed: ${textStatus}, ${error}`);
    });
}

function handleUserInteraction(passenger_id, driver_id, car_number, car_model) {
    console.log(`handleUserInteraction called with passenger_id=${passenger_id}, driver_id=${driver_id}, car_number=${car_number}, car_model=${car_model}`);
    // Отправка POST-запроса на сервер
    $.ajax({
        url: '/add_dialogue',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            passenger_id: passenger_id,
            driver_id: driver_id
        }),
        success: function(response) {
            console.log(`Dialogue added successfully: ${JSON.stringify(response)}`);
            showDialogueMessage(car_number, car_model); // Вызов функции для показа сообщения
        },
        error: function(jqxhr, textStatus, error) {
            console.log(`Error adding dialogue: ${JSON.stringify(error)}`);
            console.error("Error adding dialogue: ", textStatus, error);
        }
    });
}

// Function to show the dialogue selection message
function showDialogueMessage(car_number, car_model) {
    const dialogueMessage = `
        <div id="dialogue-message">
            <div class="message-header">Вы выбрали <div class="car-number">${car_number}</div> ${car_model}</div>
            <div class="separator"></div>
            <div class="message-body">Теперь просто закройте мини приложение и начните писать в чат, водитель получит ваши сообщения.</div>
        </div>
    `;

    $('body').append(dialogueMessage);

    setTimeout(() => {
        $('#dialogue-message').remove();
    }, 5000); // Remove the message after 5 seconds
}

function hideStartScreen() {
    $('#start-screen').fadeOut('slow', function() {
        $(this).remove();
    });
}

$(document).ready(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const tg_id = urlParams.get('tg_id');
    const role = urlParams.get('role');
    const status = urlParams.get('status'); // Предполагается, что статус передается в URL

    console.log(`Document ready with tg_id=${tg_id}, role=${role}, status=${status}`);

    // Change navbar handle text based on role
    if (role === 'driver') {
        $('#navbar-handle').text('');
    } else if (role === 'passenger') {
        $('#navbar-handle').text('Ближайшие авто:');
    }

    updateUserData(tg_id, role);
    updateUsersByRole(role, tg_id);

    setInterval(function() {
        updateUserData(tg_id, role);
        updateUsersByRole(role, tg_id);
    }, 10000);

    $('#enter-button').on('click', hideStartScreen);

    let startY = 0; // Переменная для хранения начальной координаты Y

    $('#start-screen').on('touchstart', function(e) {
        if (status === 'inactive') {
            e.preventDefault(); // Отменяем стандартное поведение события touchstart
            return; // Если статус inactive, не обрабатываем дальше
        }

        startY = e.touches[0].pageY; // Запоминаем начальную координату Y
    });

    $('#start-screen').on('touchmove', function(e) {
        if (status === 'inactive') {
            e.preventDefault(); // Отменяем стандартное поведение события touchmove
            return; // Если статус inactive, не обрабатываем дальше
        }

        const moveY = e.touches[0].pageY;
        if (startY - moveY > 50) {
            hideStartScreen();
        }
    });
});
