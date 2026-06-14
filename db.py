import psycopg2
from psycopg2 import Error

DB_CONFIG = {
    'dbname': 'zlagoda',
    'user': 'zlagoda_admin',
    'password': 'bdPassword2026',
    'host': 'localhost',
    'port': '5432'
}

def get_connection():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Помилка підключення до БД: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    connection = get_connection()
    if not connection:
        return None

    cursor = connection.cursor()
    result = None

    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
    except Error as e:
        print(f"Помилка виконання запиту: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return result

if __name__ == '__main__':
    conn = get_connection()
    if conn:
        print("Супер! Python успішно підключився до бази даних Zlagoda!")
        conn.close()