from db import execute_query

def get_all_employees():
    query = "SELECT * FROM employee ORDER BY empl_surname;"
    return execute_query(query, fetch=True)

def get_employee_by_id(id_employee):
    query = "SELECT * FROM employee WHERE id_employee = %s;"
    result = execute_query(query, (id_employee,), fetch=True)
    return result[0] if result else None

def get_employee_by_login(login):
    query = "SELECT * FROM employee WHERE login = %s;"
    return execute_query(query, (login,), fetch=True)

def add_employee(id_employee, surname, name, patronymic, role, salary, birth_date, start_date, phone, city, street, zip_code, login, password):
    from auth import hash_password
    pwd_hash = hash_password(password)
    query = """
    INSERT INTO employee (id_employee, empl_surname, empl_name, empl_patronymic, empl_role, salary, date_of_birth, date_of_start, phone_number, city, street, zip_code, login, password_hash)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    execute_query(query, (id_employee, surname, name, patronymic, role, salary, birth_date, start_date, phone, city, street, zip_code, login, pwd_hash))

def update_employee(id_employee, surname, name, patronymic, role, salary, birth_date, start_date, phone, city, street, zip_code, login):
    query = """
    UPDATE employee 
    SET empl_surname = %s, empl_name = %s, empl_patronymic = %s, empl_role = %s, salary = %s, 
        date_of_birth = %s, date_of_start = %s, phone_number = %s, city = %s, street = %s, zip_code = %s, login = %s
    WHERE id_employee = %s;
    """
    execute_query(query, (surname, name, patronymic, role, salary, birth_date, start_date, phone, city, street, zip_code, login, id_employee))

def delete_employee(id_employee):
    query = "DELETE FROM employee WHERE id_employee = %s;"
    execute_query(query, (id_employee,))

def search_employees(search_surname='', role_filter='all'):
    query = "SELECT * FROM employee WHERE 1=1"
    params = []

    if role_filter == 'Cashier':
        query += " AND (empl_role ILIKE 'Cashier' OR empl_role ILIKE 'Касир')"
    elif role_filter == 'Manager':
        query += " AND (empl_role ILIKE 'Manager' OR empl_role ILIKE 'Менеджер')"

    if search_surname:
        query += " AND empl_surname ILIKE %s"
        params.append(f"%{search_surname}%")

    query += " ORDER BY empl_surname;"
    
    return execute_query(query, tuple(params) if params else None, fetch=True)

if __name__ == '__main__':
    for emp in get_all_employees():
        print(emp)