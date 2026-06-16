import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'zlagoda')
DB_USER = os.environ.get('DB_USER', 'zlagoda_admin')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'bdPassword2026')

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@contextmanager
def transaction():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            # Return rows as tuples for compatibility with positional indexing
            if result and hasattr(result[0], 'values'):
                return [tuple(row.values()) for row in result]
            return result
        conn.commit()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    try:
        result = execute_query("SELECT * FROM employee LIMIT 1;", fetch=True)
        print("Connection OK:", result)
    except Exception as e:
        print(f"Connection failed: {e}")
