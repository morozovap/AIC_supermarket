from db import execute_query

def get_all_products():
    query = "SELECT * FROM product ORDER BY product_name;"
    return execute_query(query, fetch=True)

def search_products_by_name(name):
    query = "SELECT * FROM product WHERE product_name ILIKE %s ORDER BY product_name;"
    return execute_query(query, (f"%{name}%",), fetch=True)

def get_products_by_category(category_number):
    query = "SELECT * FROM product WHERE category_number = %s ORDER BY product_name;"
    return execute_query(query, (category_number,), fetch=True)

def add_product(id_product, category_number, product_name, producer, characteristics):
    query = """
    INSERT INTO product (id_product, category_number, product_name, producer, characteristics)
    VALUES (%s, %s, %s, %s, %s);
    """
    execute_query(query, (id_product, category_number, product_name, producer, characteristics))

def update_product(id_product, category_number, product_name, producer, characteristics):
    query = """
    UPDATE product 
    SET category_number = %s, product_name = %s, producer = %s, characteristics = %s
    WHERE id_product = %s;
    """
    execute_query(query, (category_number, product_name, producer, characteristics, id_product))
    
def get_product_by_id(id_product):
    query = "SELECT * FROM product WHERE id_product = %s;"
    result = execute_query(query, (id_product,), fetch=True)
    return result[0] if result else None

def delete_product(id_product):
    query = "DELETE FROM product WHERE id_product = %s;"
    execute_query(query, (id_product,))

if __name__ == '__main__':
    for p in get_all_products():
        print(p)