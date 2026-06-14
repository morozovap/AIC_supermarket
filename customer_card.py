from db import execute_query

def get_all_customers():
    query = "SELECT * FROM customer_card ORDER BY cust_surname;"
    return execute_query(query, fetch=True)

def get_customers_by_percent(percent):
    query = "SELECT * FROM customer_card WHERE percent = %s ORDER BY cust_surname;"
    return execute_query(query, (percent,), fetch=True)

def search_customers_by_surname(surname):
    query = "SELECT * FROM customer_card WHERE cust_surname ILIKE %s ORDER BY cust_surname;"
    return execute_query(query, (f"%{surname}%",), fetch=True)

def add_customer(card_number, surname, name, patronymic, phone, city, street, zip_code, percent):
    query = """
    INSERT INTO customer_card 
    (card_number, cust_surname, cust_name, cust_patronymic, phone_number, city, street, zip_code, percent)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    params = (card_number, surname, name, patronymic, phone, city, street, zip_code, percent)
    execute_query(query, params)

def update_customer(card_number, surname, name, patronymic, phone, city, street, zip_code, percent):
    query = """
    UPDATE customer_card 
    SET cust_surname = %s, cust_name = %s, cust_patronymic = %s, phone_number = %s, 
        city = %s, street = %s, zip_code = %s, percent = %s
    WHERE card_number = %s;
    """
    params = (surname, name, patronymic, phone, city, street, zip_code, percent, card_number)
    execute_query(query, params)

def delete_customer(card_number):
    query = "DELETE FROM customer_card WHERE card_number = %s;"
    execute_query(query, (card_number,))

if __name__ == '__main__':
    for cust in get_all_customers():
        print(cust)