from db import execute_query
from auth import hash_password

def get_all_employees():
    query = "SELECT * FROM employee ORDER BY empl_surname;"
    return execute_query(query, fetch=True)

def get_cashiers():
    query = "SELECT * FROM employee WHERE empl_role = 'Cashier' ORDER BY empl_surname;"
    return execute_query(query, fetch=True)

def get_employee_by_id(id_employee):
    query = "SELECT * FROM employee WHERE id_employee = %s;"
    result = execute_query(query, (id_employee,), fetch=True)
    return result[0] if result else None

def get_employee_by_login(login):
    """Повертає працівника за логіном (для авторизації)."""
    query = "SELECT * FROM employee WHERE login = %s;"
    result = execute_query(query, (login,), fetch=True)
    return result[0] if result else None

def add_employee(id_employee, surname, name, patronymic, role, salary, birth_date,
                 start_date, phone, city, street, zip_code, login, plain_password):
    hashed_password = hash_password(plain_password)
    query = """
    INSERT INTO employee 
    (id_employee, empl_surname, empl_name, empl_patronymic, empl_role, salary,
     date_of_birth, date_of_start, phone_number, city, street, zip_code, login, password_hash)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    params = (id_employee, surname, name, patronymic, role, salary, birth_date,
              start_date, phone, city, street, zip_code, login, hashed_password)
    execute_query(query, params)

def update_employee(id_employee, surname, name, patronymic, role, salary, birth_date,
                    start_date, phone, city, street, zip_code, login):
    query = """
    UPDATE employee 
    SET empl_surname = %s, empl_name = %s, empl_patronymic = %s, empl_role = %s, 
        salary = %s, date_of_birth = %s, date_of_start = %s, phone_number = %s, 
        city = %s, street = %s, zip_code = %s, login = %s
    WHERE id_employee = %s;
    """
    params = (surname, name, patronymic, role, salary, birth_date, start_date,
              phone, city, street, zip_code, login, id_employee)
    execute_query(query, params)

def delete_employee(id_employee):
    query = "DELETE FROM employee WHERE id_employee = %s;"
    execute_query(query, (id_employee,))

if __name__ == '__main__':
    for emp in get_all_employees():
        print(emp)
