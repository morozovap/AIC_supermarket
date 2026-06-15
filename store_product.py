from db import execute_query

def get_all_store_products_by_quantity():
    query = "SELECT * FROM store_product ORDER BY products_number;"
    return execute_query(query, fetch=True)

def get_all_store_products_by_name():
    query = """
    SELECT sp.upc, sp.upc_prom, sp.id_product, sp.selling_price, sp.products_number,
           sp.promotional_product, p.product_name 
    FROM store_product sp 
    JOIN product p ON sp.id_product = p.id_product 
    ORDER BY p.product_name;
    """
    return execute_query(query, fetch=True)

def get_promotional_products(sort_by_quantity=False):
    if sort_by_quantity:
        query = """
        SELECT sp.upc, sp.upc_prom, sp.id_product, sp.selling_price, sp.products_number,
               sp.promotional_product, p.product_name
        FROM store_product sp 
        JOIN product p ON sp.id_product = p.id_product 
        WHERE sp.promotional_product = TRUE 
        ORDER BY sp.products_number;
        """
    else:
        query = """
        SELECT sp.upc, sp.upc_prom, sp.id_product, sp.selling_price, sp.products_number,
               sp.promotional_product, p.product_name
        FROM store_product sp 
        JOIN product p ON sp.id_product = p.id_product 
        WHERE sp.promotional_product = TRUE 
        ORDER BY p.product_name;
        """
    return execute_query(query, fetch=True)

def get_non_promotional_products(sort_by_quantity=False):
    if sort_by_quantity:
        query = """
        SELECT sp.upc, sp.upc_prom, sp.id_product, sp.selling_price, sp.products_number,
               sp.promotional_product, p.product_name
        FROM store_product sp 
        JOIN product p ON sp.id_product = p.id_product 
        WHERE sp.promotional_product = FALSE 
        ORDER BY sp.products_number;
        """
    else:
        query = """
        SELECT sp.upc, sp.upc_prom, sp.id_product, sp.selling_price, sp.products_number,
               sp.promotional_product, p.product_name
        FROM store_product sp 
        JOIN product p ON sp.id_product = p.id_product 
        WHERE sp.promotional_product = FALSE 
        ORDER BY p.product_name;
        """
    return execute_query(query, fetch=True)

def get_product_details_by_upc(upc):
    query = """
    SELECT sp.selling_price, sp.products_number, p.product_name, p.characteristics
    FROM store_product sp
    JOIN product p ON sp.id_product = p.id_product
    WHERE sp.upc = %s;
    """
    return execute_query(query, (upc,), fetch=True)

def get_product_quantity(upc):
    """Return current stock quantity for a given UPC."""
    query = "SELECT products_number FROM store_product WHERE upc = %s;"
    result = execute_query(query, (upc,), fetch=True)
    return result[0][0] if result else 0

def add_store_product(upc, upc_prom, id_product, selling_price, products_number, promotional_product):
    query = """
    INSERT INTO store_product (upc, upc_prom, id_product, selling_price, products_number, promotional_product)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    execute_query(query, (upc, upc_prom, id_product, selling_price, products_number, promotional_product))

def update_store_product(upc, upc_prom, id_product, selling_price, products_number, promotional_product):
    query = """
    UPDATE store_product 
    SET upc_prom = %s, id_product = %s, selling_price = %s, products_number = %s, promotional_product = %s
    WHERE upc = %s;
    """
    execute_query(query, (upc_prom, id_product, selling_price, products_number, promotional_product, upc))

def decrease_quantity(upc, amount):
    """Decrease product stock after a sale. Raises ValueError if not enough stock."""
    query = """
    UPDATE store_product 
    SET products_number = products_number - %s 
    WHERE upc = %s AND products_number >= %s
    RETURNING products_number;
    """
    result = execute_query(query, (amount, upc, amount), fetch=True)
    if not result:
        raise ValueError(f"Недостатньо товару на складі для UPC {upc}")

def delete_store_product(upc):
    query = "DELETE FROM store_product WHERE upc = %s;"
    execute_query(query, (upc,))

if __name__ == '__main__':
    for sp in get_all_store_products_by_quantity():
        print(sp)
