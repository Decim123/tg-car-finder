import sqlite3

def clear_database(db_path):
    try:
        # Подключение к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Получение списка всех таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Удаление данных из каждой таблицы
        for table_name in tables:
            cursor.execute(f"DELETE FROM {table_name[0]};")
            print(f"Таблица {table_name[0]} очищена.")

        # Сохранение изменений и закрытие соединения
        conn.commit()
        conn.close()
        print("Очистка базы данных завершена.")

    except sqlite3.Error as error:
        print(f"Ошибка при работе с базой данных: {error}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")

# Путь к вашей базе данных
db_path = 'database/dialogue.db'

clear_database(db_path)
