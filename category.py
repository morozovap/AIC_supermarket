from db import execute_query

def get_all_categories():
    query = "SELECT * FROM category ORDER BY category_name;"
    return execute_query(query, fetch=True)

def add_category(category_number, category_name):
    query = "INSERT INTO category (category_number, category_name) VALUES (%s, %s);"
    execute_query(query, (category_number, category_name))

def update_category(category_number, category_name):
    query = "UPDATE category SET category_name = %s WHERE category_number = %s;"
    execute_query(query, (category_name, category_number))
    
def get_category_by_number(category_number):
    """Отримати дані однієї категорії за її номером для форми редагування"""
    query = "SELECT category_number, category_name FROM category WHERE category_number = %s;"
    result = execute_query(query, (category_number,), fetch=True)
    return result[0] if result else None

def delete_category(category_number):
    query = "DELETE FROM category WHERE category_number = %s;"
    execute_query(query, (category_number,))

if __name__ == '__main__':
    for cat in get_all_categories():
        print(cat)