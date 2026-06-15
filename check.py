from db import execute_query, transaction
import psycopg2.extras

def get_all_receipts():
    query = "SELECT * FROM receipt ORDER BY print_date DESC;"
    return execute_query(query, fetch=True)

def get_receipt_with_details(check_number):
    query = """
    SELECT r.check_number, r.print_date, r.id_employee, r.card_number, r.sum_total, r.vat,
           s.upc, p.product_name, s.product_number, s.selling_price
    FROM receipt r
    JOIN sale s ON r.check_number = s.check_number
    JOIN store_product sp ON s.upc = sp.upc
    JOIN product p ON sp.id_product = p.id_product
    WHERE r.check_number = %s;
    """
    return execute_query(query, (check_number,), fetch=True)

def get_receipts_by_cashier_and_period(id_employee, start_date, end_date):
    query = """
    SELECT r.check_number, r.print_date, r.sum_total, r.vat,
           s.upc, p.product_name, s.product_number, s.selling_price
    FROM receipt r
    JOIN sale s ON r.check_number = s.check_number
    JOIN store_product sp ON s.upc = sp.upc
    JOIN product p ON sp.id_product = p.id_product
    WHERE r.id_employee = %s AND r.print_date >= %s AND r.print_date <= %s
    ORDER BY r.print_date DESC;
    """
    return execute_query(query, (id_employee, start_date, end_date), fetch=True)

def get_all_receipts_by_period(start_date, end_date):
    query = """
    SELECT r.check_number, r.print_date, r.id_employee, r.sum_total, r.vat,
           s.upc, p.product_name, s.product_number, s.selling_price
    FROM receipt r
    JOIN sale s ON r.check_number = s.check_number
    JOIN store_product sp ON s.upc = sp.upc
    JOIN product p ON sp.id_product = p.id_product
    WHERE r.print_date >= %s AND r.print_date <= %s
    ORDER BY r.print_date DESC;
    """
    return execute_query(query, (start_date, end_date), fetch=True)

def get_receipts_by_cashier_today(id_employee):
    query = """
    SELECT * FROM receipt 
    WHERE id_employee = %s AND DATE(print_date) = CURRENT_DATE
    ORDER BY print_date DESC;
    """
    return execute_query(query, (id_employee,), fetch=True)

def get_total_sum_by_cashier_and_period(id_employee, start_date, end_date):
    query = """
    SELECT COALESCE(SUM(sum_total), 0) AS total FROM receipt
    WHERE id_employee = %s AND print_date >= %s AND print_date <= %s;
    """
    return execute_query(query, (id_employee, start_date, end_date), fetch=True)

def get_total_sum_by_period(start_date, end_date):
    query = """
    SELECT COALESCE(SUM(sum_total), 0) AS total FROM receipt
    WHERE print_date >= %s AND print_date <= %s;
    """
    return execute_query(query, (start_date, end_date), fetch=True)

def get_total_units_sold_by_product_and_period(upc, start_date, end_date):
    query = """
    SELECT COALESCE(SUM(s.product_number), 0) AS total_units
    FROM sale s
    JOIN receipt r ON s.check_number = r.check_number
    WHERE s.upc = %s AND r.print_date >= %s AND r.print_date <= %s;
    """
    return execute_query(query, (upc, start_date, end_date), fetch=True)

def add_receipt(check_number, id_employee, card_number, print_date, sum_total):
    query = """
    INSERT INTO receipt (check_number, id_employee, card_number, print_date, sum_total)
    VALUES (%s, %s, %s, %s, %s);
    """
    execute_query(query, (check_number, id_employee, card_number, print_date, sum_total))

def add_sale(upc, check_number, product_number, selling_price):
    query = """
    INSERT INTO sale (upc, check_number, product_number, selling_price)
    VALUES (%s, %s, %s, %s);
    """
    execute_query(query, (upc, check_number, product_number, selling_price))

def delete_receipt(check_number):
    query = "DELETE FROM receipt WHERE check_number = %s;"
    execute_query(query, (check_number,))

def create_receipt(check_number, id_employee, card_number, print_date, items):
    with transaction() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        sum_total = 0
        processed_items = []

        for item in items:
            upc = item['upc']
            qty = item['product_number']
            
            cursor.execute("SELECT selling_price, products_number FROM store_product WHERE upc = %s FOR UPDATE;", (upc,))
            product = cursor.fetchone()
            
            if not product:
                raise ValueError(f"Товар з UPC {upc} не знайдено.")
            if product['products_number'] < qty:
                raise ValueError(f"Недостатньо товару {upc} на складі. Залишок: {product['products_number']}")
                
            price = product['selling_price']
            sum_total += price * qty
            processed_items.append({'upc': upc, 'qty': qty, 'price': price})
            
            cursor.execute("""
                UPDATE store_product 
                SET products_number = products_number - %s 
                WHERE upc = %s;
            """, (qty, upc))

        if card_number:
            cursor.execute("SELECT percent FROM customer_card WHERE card_number = %s;", (card_number,))
            card = cursor.fetchone()
            if card:
                discount = card['percent'] / 100.0
                sum_total = float(sum_total) * (1.0 - float(discount))

        cursor.execute("""
            INSERT INTO receipt (check_number, id_employee, card_number, print_date, sum_total)
            VALUES (%s, %s, %s, %s, %s);
        """, (check_number, id_employee, card_number, print_date, sum_total))

        for p_item in processed_items:
            cursor.execute("""
                INSERT INTO sale (upc, check_number, product_number, selling_price)
                VALUES (%s, %s, %s, %s);
            """, (p_item['upc'], check_number, p_item['qty'], p_item['price']))