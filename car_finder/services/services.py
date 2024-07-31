import sqlite3
from datetime import datetime, timedelta
import os

admin_password = '777'
applications_db = 'database/applications.db'
drivers_db = 'database/drivers.db'
passengers_db = 'database/passengers.db'
admins_db = 'database/admins.db'
locations_db = 'database/locations.db'
dialogue_db = 'database/dialogue.db'
log_db = 'database/log.db'
logs_dir = 'logs'

# Ensure logs directory exists
os.makedirs(logs_dir, exist_ok=True)
def get_username_by_tg_id(tg_id):
    conn = sqlite3.connect(passengers_db)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM passengers WHERE tg_id = ?", (tg_id,))
    username = cursor.fetchone()
    conn.close()
    return username[0] if username else None

def log_chat_start(passenger_id, driver_id):
    passenger_username = get_username_by_tg_id(passenger_id)
    driver_username = get_username_by_tg_id(driver_id)
    timestamp = datetime.now().strftime("%m%d%H%M")
    filename = f"{timestamp}_{passenger_username}_to_{driver_username}.txt"
    filepath = os.path.join(logs_dir, filename)
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"@{passenger_username} with @{driver_username}\n")
    
    # Сохранение пути в log.db
    conn = sqlite3.connect('database/log.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO log (passenger_id, driver_id, filepath) VALUES (?, ?, ?)',
                   (passenger_id, driver_id, filepath))
    conn.commit()
    conn.close()
    
    return filepath

def log_chat_message(filepath, sender_id, message):
    sender_username = get_username_by_tg_id(sender_id)
    print(f"Logging message from {sender_username} to {filepath}")  # Debugging log
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"@{sender_username}: {message}\n")

def log_chat_end(filepath, passenger_id, driver_id):
    passenger_username = get_username_by_tg_id(passenger_id)
    driver_username = get_username_by_tg_id(driver_id)
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"chat @{passenger_username} with @{driver_username} was closed\n")
        f.write("----------------------------------------------------\n")
    
    # Удаление записи из log.db
    conn = sqlite3.connect(log_db)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM log WHERE passenger_id = ? AND driver_id = ?', (passenger_id, driver_id))
    conn.commit()
    conn.close()

def get_log_filepath(passenger_id, driver_id):
    conn = sqlite3.connect(log_db)
    cursor = conn.cursor()
    cursor.execute('SELECT filepath FROM log WHERE passenger_id = ? AND driver_id = ?', (passenger_id, driver_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def add_driver_id_username(tg_id, username):
    conn = sqlite3.connect(applications_db)
    cur = conn.cursor()
    cur.execute('SELECT tg_id FROM applications WHERE tg_id = ?', (tg_id,))
    data = cur.fetchone()

    if data is None:
        cur.execute('INSERT INTO applications (tg_id, username) VALUES (?, ?)', (tg_id, username))
        conn.commit()
    else:
        print(f'application with tg_id={tg_id} already exists.')
    conn.close()

def add_driver_name(tg_id, name):
    conn = sqlite3.connect(applications_db)
    cur = conn.cursor()
    cur.execute('SELECT tg_id FROM applications WHERE tg_id = ?', (tg_id,))
    cur.execute('UPDATE applications SET name = ? WHERE tg_id = ?', (name, tg_id))
    conn.commit()
    conn.close()

def add_driver_surname(tg_id, surname):
    conn = sqlite3.connect(applications_db)
    cur = conn.cursor()
    cur.execute('SELECT tg_id FROM applications WHERE tg_id = ?', (tg_id,))
    cur.execute('UPDATE applications SET surname = ? WHERE tg_id = ?', (surname, tg_id))
    conn.commit()
    conn.close()

def add_driver_car_number(tg_id, car_number):
    conn = sqlite3.connect(applications_db)
    cur = conn.cursor()
    cur.execute('SELECT tg_id FROM applications WHERE tg_id = ?', (tg_id,))
    cur.execute('UPDATE applications SET car_number = ? WHERE tg_id = ?', (car_number, tg_id))
    conn.commit()
    conn.close()

def add_driver_car_model(tg_id, car_model):
    conn = sqlite3.connect(applications_db)
    cur = conn.cursor()
    cur.execute('SELECT tg_id FROM applications WHERE tg_id = ?', (tg_id,))
    cur.execute('UPDATE applications SET car_model = ? WHERE tg_id = ?', (car_model, tg_id))
    conn.commit()
    conn.close()

def add_driver_comment(tg_id, comment):
    conn = sqlite3.connect(applications_db)
    cur = conn.cursor()
    cur.execute('SELECT tg_id FROM applications WHERE tg_id = ?', (tg_id,))
    cur.execute('UPDATE applications SET comment = ? WHERE tg_id = ?', (comment, tg_id))
    conn.commit()
    conn.close()

def check_admin_pass(password):
    if admin_password == password:
        return 'poijhnugasdrfansjk'
    else:
        return 'wrong password'

def add_or_update_admin(tg_id, username, status):
    conn = sqlite3.connect(admins_db)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT COUNT(*) FROM users WHERE tg_id = ?
    ''', (tg_id,))
    count = cursor.fetchone()[0]

    if count > 0:
        cursor.execute('''
        UPDATE users SET status = ?, username = ? WHERE tg_id = ?
        ''', (status, username, tg_id))
    else:
        cursor.execute('''
        INSERT INTO users (tg_id, username, status) VALUES (?, ?, ?)
        ''', (tg_id, username, status))
    conn.commit()
    conn.close()

def check_admin_exists(tg_id):
    conn = sqlite3.connect(admins_db)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT 1 FROM users WHERE tg_id = ? LIMIT 1
    ''', (tg_id,))
    result = cursor.fetchone()
    conn.close()

    return result is not None

def get_active_admins():
    conn = sqlite3.connect(admins_db)
    cursor = conn.cursor()
    cursor.execute("SELECT tg_id, username FROM users WHERE status = 'active'")
    admins = cursor.fetchall()
    conn.close()
    return admins

def get_application(tg_id):
    conn = sqlite3.connect(applications_db)
    cursor = conn.cursor()
    cursor.execute("SELECT tg_id, username, name, surname, car_number, car_model, comment FROM applications WHERE tg_id = ?", (tg_id,))
    application = cursor.fetchone()
    conn.close()
    return application

def get_usernames():
    conn = sqlite3.connect(applications_db)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM applications")
    usernames = cursor.fetchall()
    conn.close()
    return [username[0] for username in usernames]

def copy_user_to_drivers(username):
    conn_applications = sqlite3.connect(applications_db)
    cursor_applications = conn_applications.cursor()
    cursor_applications.execute("SELECT * FROM applications WHERE username = ?", (username,))
    user_data = cursor_applications.fetchone()
    
    if user_data:
        conn_drivers = sqlite3.connect(drivers_db)
        cursor_drivers = conn_drivers.cursor()
        cursor_drivers.execute('''
            INSERT OR REPLACE INTO drivers (tg_id, username, name, surname, car_number, car_model, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', user_data)
        conn_drivers.commit()
        conn_drivers.close()
    conn_applications.close()

def delete_user_from_applications(username):
    conn = sqlite3.connect(applications_db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def get_tg_id_by_username(username):
    conn = sqlite3.connect(applications_db)
    cursor = conn.cursor()
    cursor.execute("SELECT tg_id FROM applications WHERE username = ?", (username,))
    tg_id = cursor.fetchone()[0]
    conn.close()
    return tg_id

def insert_location(tg_id, latitude, longitude):
    with sqlite3.connect(locations_db) as conn:
        cursor = conn.cursor()
        last_updated = datetime.now().isoformat()
        status = 'active'
        cursor.execute('SELECT 1 FROM locations WHERE tg_id = ?', (tg_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute('''
                UPDATE locations
                SET latitude = ?, longitude = ?, last_updated = ?, status = ?
                WHERE tg_id = ?
            ''', (latitude, longitude, last_updated, status, tg_id))
        else:
            cursor.execute('''
                INSERT INTO locations (tg_id, latitude, longitude, last_updated, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (tg_id, latitude, longitude, last_updated, status))
        conn.commit()


def chat_logs():
    logs_dir = 'logs'
    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.txt')]
    log_files.sort(key=lambda x: datetime.strptime(x[:8], '%m%d%H%M'), reverse=True)
    recent_logs = log_files[:5]
    log_contents = []
    for log_file in recent_logs:
        with open(os.path.join(logs_dir, log_file), 'r', encoding='utf-8') as f:
            log_contents.append(f.read())
    log_messages = []
    for i, content in enumerate(log_contents):
        log_messages.append(f"Log {i+1}:\n{content}\n")
    log_message = "\n".join(log_messages)
    return log_message

def stop_sharing_location(tg_id):
    with sqlite3.connect(locations_db) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE locations
            SET latitude = NULL,
                longitude = NULL,
                last_updated = ?
            WHERE tg_id = ?
        ''', (datetime.now().isoformat(), tg_id))
        conn.commit()
    
def is_recent_update(tg_id):
    with sqlite3.connect(locations_db) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT last_updated FROM locations WHERE tg_id = ?', (tg_id,))
        result = cursor.fetchone()
        
        if result:
            last_updated_str = result[0]
            last_updated = datetime.fromisoformat(last_updated_str)
            current_time = datetime.now()
            time_difference = current_time - last_updated
            if time_difference > timedelta(minutes=2):
                return False
            else:
                return True
        else:
            return False
        
def check_driver_exists(tg_id):
    conn = sqlite3.connect(drivers_db)
    cursor = conn.cursor()
    query = "SELECT EXISTS (SELECT 1 FROM drivers WHERE tg_id = ?)"
    cursor.execute(query, (tg_id,))
    result = cursor.fetchone()[0]
    conn.close()
    return bool(result)

def update_user(tg_id, username, name):
    conn = sqlite3.connect(passengers_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(1) FROM passengers WHERE tg_id = ?", (tg_id,))
    exists = cursor.fetchone()[0]

    if exists:
        cursor.execute("""
            UPDATE passengers
            SET username = ?, name = ?
            WHERE tg_id = ?
        """, (username, name, tg_id))
    else:
        cursor.execute("""
            INSERT INTO passengers (tg_id, username, name)
            VALUES (?, ?, ?)
        """, (tg_id, username, name))
    conn.commit()
    conn.close()

def get_status_by_passenger_id(passenger_id):
    conn = sqlite3.connect(dialogue_db)
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM dialogue WHERE passenger_id = ?', (passenger_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None

def get_driver_id_by_passenger_id(passenger_id):
    conn = sqlite3.connect(dialogue_db)
    cursor = conn.cursor()    
    cursor.execute('SELECT driver_id FROM dialogue WHERE passenger_id = ?', (passenger_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return None
    
def update_status_by_passenger_id(passenger_id, new_status):
    conn = sqlite3.connect(dialogue_db)
    cursor = conn.cursor()
    cursor.execute('UPDATE dialogue SET status = ? WHERE passenger_id = ?', (new_status, passenger_id))
    conn.commit()
    conn.close()

def get_active_passenger_by_driver_id(driver_id):
    conn = sqlite3.connect(dialogue_db)
    cursor = conn.cursor()
    cursor.execute('SELECT passenger_id FROM dialogue WHERE driver_id = ? AND status = "active"', (driver_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return False
    
def set_dialogues_inactive_by_driver_id(driver_id):
    conn = sqlite3.connect(dialogue_db)
    cursor = conn.cursor()
    cursor.execute('UPDATE dialogue SET status = "inactive" WHERE driver_id = ?', (driver_id,))
    conn.commit()
    conn.close()

def remove_driver_id_by_passenger_id(passenger_id):
    conn = sqlite3.connect(dialogue_db)
    cursor = conn.cursor()
    cursor.execute('UPDATE dialogue SET driver_id = NULL WHERE passenger_id = ?', (passenger_id,))
    conn.commit()
    conn.close()

def list_of_admins():
    conn = sqlite3.connect(admins_db)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    usernames = cursor.fetchall()
    formatted_usernames = [f"{i+1} @{username[0]}" for i, username in enumerate(usernames)]
    conn.close()
    return "\n".join(formatted_usernames)

def delete_admin(username):
    conn = sqlite3.connect(admins_db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def list_of_drivers():
    conn = sqlite3.connect(drivers_db)
    cursor = conn.cursor()
    cursor.execute("SELECT username, surname, name, car_number, car_model, comment FROM drivers")
    drivers_data = cursor.fetchall()
    conn.close()

    if not drivers_data:
        return "No drivers found."
    output = ""

    for index, driver in enumerate(drivers_data, start=1):
        username, surname, name, car_number, car_model, comment = driver
        output += f"{index}. @{username} {surname} {name}\n"
        output += f"    {car_number} {car_model}\n"
        output += f"    {comment}\n\n"
    return output

def delete_driver(username):
    conn = sqlite3.connect(drivers_db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM drivers WHERE username=?", (username,))
    conn.commit()

    if cursor.rowcount > 0:
        message = f"Запись с username '{username}' успешно удалена из базы данных."
    else:
        message = f"Запись с username '{username}' не была найдена в базе данных."
    conn.close()

    return message

def list_of_users():
    conn = sqlite3.connect(passengers_db)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM passengers")
    users = cursor.fetchall()
    conn.close()

    if not users:
        return "Нет пользователей в базе данных."
    
    user_list = []
    for index, (username,) in enumerate(users, start=1):
        user_list.append(f"{index} {username}")
    
    return "\n".join(user_list)

def get_active_applications():
    conn = sqlite3.connect(applications_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications")
    applications = cursor.fetchall()
    conn.close()
    result = ""
    for application in applications:
        result += (
            "<b>Заявка:</b>\n\n"
            f"Telegram: @{application[1]}\n"
            f"Имя: {application[2]}\n"
            f"Фамилия: {application[3]}\n"
            f"Номер авто: {application[4]}\n"
            f"Модель авто: {application[5]}\n"
            f"Примечание: {application[6]}\n\n"
        )
    
    return result