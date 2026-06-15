import bcrypt
from db import execute_query

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate(login, password):
    query = """
    SELECT id_employee, empl_role, password_hash 
    FROM employee 
    WHERE login = %s;
    """
    result = execute_query(query, (login,), fetch=True)
    
    if not result:
        return None
        
    user = result[0]
    
    if verify_password(password, user['password_hash']):
        return {
            'id_employee': user['id_employee'],
            'empl_role': user['empl_role']
        }
        
    return None