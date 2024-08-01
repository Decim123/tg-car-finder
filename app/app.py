import platform
import geopy.distance
from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
import asyncio
import logging
from logging.handlers import RotatingFileHandler

API_TOKEN = '7420735125:AAFAgsUbMfg_fCIKkyWjlx8fSe7h8FE1kCc'

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)

# Инициализируем нового бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Создадим event loop и сохраним его
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def get_db_connection(db_name):
    try:
        conn = sqlite3.connect(db_name, timeout=10)
        app.logger.debug(f'Successfully connected to the database: {db_name}')
        return conn
    except sqlite3.Error as e:
        app.logger.error(f'Failed to connect to the database: {db_name}. Error: {e}')
        raise

def get_active_admins():
    conn = get_db_connection('database/admins.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tg_id, username FROM users WHERE status = 'active'")
    admins = cursor.fetchall()
    conn.close()
    return admins

def get_user_data(tg_id):
    conn = get_db_connection('database/locations.db')
    cursor = conn.cursor()
    app.logger.debug(f"Executing SQL: SELECT latitude, longitude, last_updated, role FROM locations WHERE tg_id = {tg_id}")
    cursor.execute("SELECT latitude, longitude, last_updated, role FROM locations WHERE tg_id = ?", (tg_id,))
    user_data = cursor.fetchone()
    conn.close()
    app.logger.debug(f'Fetched user data for tg_id={tg_id}: {user_data}')
    return user_data

def update_user_data(tg_id, role):
    conn = get_db_connection('database/locations.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO locations (tg_id, role, status)
        VALUES (?, ?, 'active')
        ON CONFLICT(tg_id) DO UPDATE SET
        role = excluded.role,
        status = 'active';
    """, (tg_id, role))
    conn.commit()
    conn.close()

def is_user_in_active_dialogue(tg_id):
    conn = get_db_connection('database/dialogue.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM dialogue WHERE passenger_id = ? OR driver_id = ?", (tg_id, tg_id))
    dialogue = cursor.fetchone()
    conn.close()
    
    if dialogue and dialogue[0] == 'active':
        return True
    return False

def update_user_status():
    conn = get_db_connection('database/locations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tg_id, last_updated FROM locations")
    users = cursor.fetchall()
    
    now = datetime.now()
    for user in users:
        tg_id, last_updated = user
        last_updated_dt = datetime.strptime(last_updated, '%Y-%m-%dT%H:%M:%S.%f')
        if now - last_updated_dt > timedelta(seconds=200):
            cursor.execute("UPDATE locations SET status = 'inactive' WHERE tg_id = ?", (tg_id,))
        else:
            cursor.execute("UPDATE locations SET status = 'active' WHERE tg_id = ?", (tg_id,))
    
    conn.commit()
    conn.close()

def get_user_status(tg_id):
    conn = get_db_connection('database/locations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM locations WHERE tg_id = ?", (tg_id,))
    status = cursor.fetchone()[0]
    conn.close()
    return status

def get_users_by_role(current_tg_id, current_role):
    app.logger.debug("Запрос пользователей по роли. current_tg_id: %s, current_role: %s", current_tg_id, current_role)
    update_user_status()

    conn = get_db_connection('database/locations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tg_id, latitude, longitude, role, status FROM locations WHERE status = 'active'")
    users = cursor.fetchall()
    app.logger.debug("Полученные пользователи: %s", users)
    conn.close()
    
    current_user = get_user_data(current_tg_id)
    if not current_user:
        return [], False

    current_lat, current_lon = current_user[:2]

    user_distances = []
    active_drivers_exist = False

    for user in users:
        user_tg_id, user_lat, user_lon, user_role, user_status = user
        if user_tg_id == current_tg_id:
            continue
        
        if user_role == 'driver':
            active_drivers_exist = True
            conn = get_db_connection('database/dialogue.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dialogue WHERE driver_id = ? AND status = 'active'", (user_tg_id,))
            active_dialogue = cursor.fetchone()
            conn.close()
            if active_dialogue:
                continue
        
        distance = geopy.distance.distance((current_lat, current_lon), (user_lat, user_lon)).km
        
        if (current_role == 'driver' and user_role == 'passenger') or (current_role == 'passenger' and user_role == 'driver'):
            if user_role == 'driver':
                conn = get_db_connection('database/drivers.db')
                cursor = conn.cursor()
                cursor.execute("SELECT car_number, car_model, surname, name, username, comment FROM drivers WHERE tg_id = ?", (user_tg_id,))
                driver_data = cursor.fetchone()
                conn.close()
                if driver_data:
                    car_number, car_model, surname, name, username, comment = driver_data
                    user_distances.append({
                        'tg_id': user_tg_id,
                        'role': user_role,
                        'car_number': car_number,
                        'car_model': car_model,
                        'surname': surname,
                        'name': name,
                        'username': username,
                        'distance': distance,
                        'comment': comment,
                        'latitude': user_lat,
                        'longitude': user_lon,
                        'status': user_status
                    })
            elif user_role == 'passenger':
                conn = get_db_connection('database/passengers.db')
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM passengers WHERE tg_id = ?", (user_tg_id,))
                passenger_data = cursor.fetchone()
                conn.close()
                if passenger_data:
                    username, = passenger_data
                    user_distances.append({
                        'tg_id': user_tg_id,
                        'role': user_role,
                        'username': username,
                        'distance': distance,
                        'latitude': user_lat,
                        'longitude': user_lon,
                        'status': user_status
                    })
    
    app.logger.debug("Список пользователей после обработки: %s", user_distances)
    return user_distances, active_drivers_exist

@app.route('/')
def index():
    tg_id = request.args.get('tg_id')
    role = request.args.get('role')

    app.logger.debug(f'index() called with tg_id={tg_id} and role={role}')

    if not tg_id or not role:
        return "Missing 'tg_id' or 'role' parameter", 400

    if role == 'driver':
        status = get_user_status(tg_id)
        update_user_data(tg_id, role)
        app.logger.debug(f'get_user_status() returned {status} for tg_id={tg_id}')
        return render_template('index.html', tg_id=tg_id, role=role, status=status, active_drivers_exist=True)

    if is_user_in_active_dialogue(tg_id):
        return render_template('active.html', tg_id=tg_id, role=role)

    status = get_user_status(tg_id)
    update_user_data(tg_id, role)
    users, active_drivers_exist = get_users_by_role(tg_id, role)
    app.logger.debug(f'get_users_by_role() returned {len(users)} users for tg_id={tg_id} and role={role}')
    return render_template('index.html', tg_id=tg_id, role=role, status=status, active_drivers_exist=active_drivers_exist)

@app.route('/dialogue_map_data')
def dialogue_map_data():
    driver_id = request.args.get('driver_id')
    passenger_id = request.args.get('passenger_id')

    # Получаем информацию о водителе
    conn = get_db_connection('database/locations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude FROM locations WHERE tg_id = ?", (driver_id,))
    driver_location = cursor.fetchone()
    conn.close()

    conn = get_db_connection('database/drivers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT surname, name, car_number, car_model, comment FROM drivers WHERE tg_id = ?", (driver_id,))
    driver_info = cursor.fetchone()
    conn.close()

    # Получаем информацию о пассажире
    conn = get_db_connection('database/locations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude FROM locations WHERE tg_id = ?", (passenger_id,))
    passenger_location = cursor.fetchone()
    conn.close()

    return jsonify({
        'driver': {
            'latitude': driver_location[0],
            'longitude': driver_location[1],
            'surname': driver_info[0],
            'name': driver_info[1],
            'car_number': driver_info[2],
            'car_model': driver_info[3],
            'comment': driver_info[4]
        },
        'passenger': {
            'latitude': passenger_location[0],
            'longitude': passenger_location[1]
        }
    })

@app.route('/dialogue_map')
def dialogue_map():
    driver_id = request.args.get('driver_id')
    passenger_id = request.args.get('passenger_id')

    app.logger.debug(f'dialogue_map() called with driver_id={driver_id} and passenger_id={passenger_id}')

    # Получаем информацию о водителе
    conn = get_db_connection('database/locations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations WHERE tg_id = ?", (driver_id,))
    driver_data = cursor.fetchone()
    conn.close()

    # Получаем информацию о пассажире
    conn = get_db_connection('database/locations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations WHERE tg_id = ?", (passenger_id,))
    passenger_data = cursor.fetchone()
    conn.close()

    return render_template('dialogue_map.html', driver_data=driver_data, passenger_data=passenger_data)

@app.route('/user_data')
def user_data():
    tg_id = request.args.get('tg_id')
    app.logger.debug(f'user_data() called with tg_id={tg_id}')
    try:
        user_data = get_user_data(tg_id)
        if user_data:
            latitude, longitude, last_updated, role = user_data
            return jsonify({
                'latitude': latitude,
                'longitude': longitude,
                'last_updated': last_updated,
                'role': role
            })
        else:
            app.logger.error(f'User data not found for tg_id={tg_id}')
            return jsonify({'error': 'User not found'}), 404  # Return a 404 error if user not found
    except Exception as e:
        app.logger.error(f'Error getting user data for tg_id={tg_id}: {e}')
        return jsonify({'error': str(e)}), 500  # Return a 500 error for other exceptions

@app.route('/users_by_role')
def users_by_role():
    current_tg_id = request.args.get('current_tg_id')
    current_role = request.args.get('role')

    app.logger.debug(f'users_by_role() called with current_tg_id={current_tg_id} and current_role={current_role}')

    if not current_tg_id or not current_role:
        return jsonify({'error': 'Missing current_tg_id or role'}), 400

    if current_role not in ['driver', 'passenger']:
        return jsonify({'error': 'Invalid role'}), 400

    users, active_drivers_exist = get_users_by_role(current_tg_id, current_role)
    return jsonify({'users': users, 'active_drivers_exist': active_drivers_exist})


@app.route('/add_dialogue', methods=['POST'])
def add_dialogue():
    data = request.get_json()
    passenger_id = data.get('passenger_id')
    driver_id = data.get('driver_id')

    app.logger.debug(f'add_dialogue() called with passenger_id={passenger_id} and driver_id={driver_id}')

    try:
        conn = get_db_connection('database/dialogue.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM dialogue WHERE passenger_id = ?", (passenger_id,))
        existing_record = cursor.fetchone()

        if existing_record:
            cursor.execute("UPDATE dialogue SET driver_id = ?, status = 'wait' WHERE passenger_id = ?", (driver_id, passenger_id))
            message = 'Dialogue updated successfully'
        else:
            cursor.execute("INSERT INTO dialogue (passenger_id, driver_id, status) VALUES (?, ?, 'wait')", (passenger_id, driver_id))
            message = 'Dialogue added successfully'

        conn.commit()
        conn.close()
        return jsonify({'message': message}), 200
    except sqlite3.Error as e:
        app.logger.error(f'Error adding dialogue for passenger_id={passenger_id} and driver_id={driver_id}: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/driver_reg', methods=['GET', 'POST'])
def driver_reg():
    if request.method == 'GET':
        tg_id = request.args.get('tg_id')
        return render_template('reg.html', tg_id=tg_id)

    if request.method == 'POST':
        data = request.form
        tg_id = data.get('tg_id')
        name = data.get('name')
        surname = data.get('surname')
        car_number = data.get('car_number')
        car_model = data.get('car_model')
        comment = data.get('comment')

        conn = get_db_connection('database/passengers.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM passengers WHERE tg_id = ?", (tg_id,))
        passenger_data = cursor.fetchone()
        conn.close()

        if passenger_data:
            username, = passenger_data
            conn = get_db_connection('database/applications.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO applications (tg_id, username, name, surname, car_number, car_model, comment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tg_id, username, name, surname, car_number, car_model, comment))
            conn.commit()
            conn.close()

            # Используем сохранённый event loop для вызова асинхронной функции
            try:
                app.logger.debug("Before calling notify_admins")
                loop.run_until_complete(notify_admins(tg_id, username, name, surname, car_number, car_model, comment))
                app.logger.debug("After calling notify_admins")
            except Exception as e:
                app.logger.error(f"Error in notify_admins: {e}")

            return jsonify({'success': True})

        return jsonify({'success': False})

@app.route('/log', methods=['POST'])
def log():
    message = request.form.get('message')
    if message:
        app.logger.info(f'Client log: {message}')
        return 'Logged', 200
    app.logger.error('No message provided in /log endpoint')
    return 'No message', 400

async def notify_admins(tg_id, username, name, surname, car_number, car_model, comment):
    admins = get_active_admins()
    application = {
        'tg_id': tg_id,
        'username': username,
        'name': name,
        'surname': surname,
        'car_number': car_number,
        'car_model': car_model,
        'comment': comment
    }

    message_text = (
        "<b>Новая заявка:</b>\n\n"
        "Используйте /applications в основном боте чтоб ответить на заявку\n\n"
        f"Telegram: @{application['username']}\n"
        f"Имя: {application['name']}\n"
        f"Фамилия: {application['surname']}\n"
        f"Номер авто: {application['car_number']}\n"
        f"Модель авто: {application['car_model']}\n"
        f"Примечание: {application['comment']}\n\n"
    )

    for admin in admins:
        admin_tg_id = admin[0]
        try:
            app.logger.debug(f"Sending message to admin {admin_tg_id}")
            await bot.send_message(admin_tg_id, message_text)
        except Exception as e:
            app.logger.error(f"Failed to send message to admin {admin_tg_id}: {e}")
            continue  # Игнорируем ошибку и переходим к следующему администратору

if __name__ == '__main__':
    app.run(debug=True)
