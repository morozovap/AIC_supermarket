import mimetypes
mimetypes.add_type('text/css', '.css')

from flask import Flask, render_template, request, redirect, url_for, session, flash
import category
import employee
import product
import customer_card
import check
import store_product
import datetime
import uuid

from auth import verify_password

app = Flask(__name__)
app.secret_key = 'zlagoda-secret-key-2026'  # потрібен для сесій

# ── Декоратори захисту ──────────────────────────────────────────
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'id_employee' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def manager_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'Manager':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── АВТОРИЗАЦІЯ ─────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login_input = request.form['username']
        password    = request.form['password']

        emp_data = employee.get_employee_by_login(login_input)
        
        if emp_data:
            # Беремо перший рядок (на випадок якщо БД повернула список)
            emp = emp_data[0] if isinstance(emp_data, list) else emp_data
            
            # --- УНІВЕРСАЛЬНИЙ ФІКС ---
            # Перетворюємо словник на звичайний список значень
            if hasattr(emp, 'values'):
                emp_list = list(emp.values())
            else:
                emp_list = list(emp)
                
            print("ДАНІ ПРАЦІВНИКА (СПИСОК):", emp_list) 
            
            # Тепер безпечно беремо елементи за номерами
            password_hash = emp_list[-1]  # Останній елемент (пароль)
            
            if verify_password(password, password_hash):
                session['id_employee'] = emp_list[0]  # ID
                session['role']        = emp_list[4]  # Роль (Manager/Cashier)
                session['name']        = f"{emp_list[1]} {emp_list[2]}" # Прізвище та Ім'я
                
                if session['role'] == 'Manager':
                    return redirect(url_for('manager_employees'))
                else:
                    return redirect(url_for('cashier_sell'))
            else:
                error = "Неправильний логін або пароль"
        else:
            error = "Неправильний логін або пароль"
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── ПРАЦІВНИКИ (тільки менеджер) ────────────────────────────────
@app.route('/manager/employees')
@manager_required
def manager_employees():
    try:
        employees_list = employee.get_all_employees() or []
    except Exception as e:
        employees_list = []
        print(f"Помилка БД: {e}")
    return render_template('manager_dashboard.html', employees=employees_list)

@app.route('/manager/employees/add', methods=['GET', 'POST'])
@manager_required
def add_employee():
    if request.method == 'POST':
        data = request.form
        try:
            employee.add_employee(
                data['id_employee'], data['surname'], data['name'], data['patronymic'],
                data['role'], data['salary'], data['birth_date'], data['start_date'],
                data['phone'], data['city'], data['street'], data['zip_code'],
                data['login'], data['password']
            )
            return redirect(url_for('manager_employees'))
        except Exception as e:
            print(f"Помилка при збереженні працівника: {e}")
    return render_template('add_employee.html')

@app.route('/manager/employees/delete/<id_employee>')
@manager_required
def delete_employee(id_employee):
    employee.delete_employee(id_employee)
    return redirect(url_for('manager_employees'))

@app.route('/manager/employees/edit/<id_employee>', methods=['GET', 'POST'])
@manager_required
def edit_employee(id_employee):
    if request.method == 'POST':
        data = request.form
        employee.update_employee(
            id_employee, data['surname'], data['name'], data['patronymic'],
            data['role'], data['salary'], data['birth_date'], data['start_date'],
            data['phone'], data['city'], data['street'], data['zip_code'], data['login']
        )
        return redirect(url_for('manager_employees'))
    emp = employee.get_employee_by_id(id_employee)
    return render_template('edit_employee.html', employee=emp)

# ── ТОВАРИ ──────────────────────────────────────────────────────
@app.route('/manager/products')
@manager_required
def manager_products():
    try:
        products_list = product.get_all_products() or []
    except Exception as e:
        products_list = []
        print(f"Помилка БД: {e}")
    return render_template('manager_products.html', products=products_list)

@app.route('/manager/products/add', methods=['GET', 'POST'])
@manager_required
def add_product():
    if request.method == 'POST':
        try:
            product.add_product(
                request.form['id_product'], request.form['category_number'],
                request.form['product_name'], request.form['producer'],
                request.form['characteristics']
            )
            return redirect(url_for('manager_products'))
        except Exception as e:
            print(f"Помилка при збереженні товару: {e}")
    categories = category.get_all_categories() or []
    return render_template('add_product.html', categories=categories)

@app.route('/manager/products/delete/<id_product>')
@manager_required
def delete_product(id_product):
    product.delete_product(id_product)
    return redirect(url_for('manager_products'))

@app.route('/manager/products/edit/<id_product>', methods=['GET', 'POST'])
@manager_required
def edit_product(id_product):
    if request.method == 'POST':
        product.update_product(
            id_product, request.form['category_number'],
            request.form['product_name'], request.form['producer'],
            request.form['characteristics']
        )
        return redirect(url_for('manager_products'))
    prod = product.get_product_by_id(id_product)
    categories = category.get_all_categories() or []
    return render_template('edit_product.html', product=prod, categories=categories)

# --- ТОВАРИ В МАГАЗИНІ (STORE_PRODUCT) ---

# 1. Перегляд усіх товарів на полицях
@app.route('/manager/store_products')
@manager_required
def manager_store_products():
    products = store_product.get_all_store_products_by_name() or []
    return render_template('store_products.html', products=products)

# 2. Додавання нової партії (з автоматичною переоцінкою)
@app.route('/manager/store_products/add', methods=['GET', 'POST'])
@manager_required
def add_store_product():
    error = None
    if request.method == 'POST':
        data = request.form
        try:
            # 1. Додаємо нову партію товару на полицю
            store_product.add_store_product(
                data['upc'],
                data.get('upc_prom') or None,
                data['id_product'],
                data['selling_price'],
                data['products_number'],
                data.get('promotional_product') == 'on'
            )
            
            # 2. ГЛОБАЛЬНА ПЕРЕОЦІНКА
            # Оновлюємо ціну для всіх існуючих неакційних партій цього товару
            from db import execute_query
            update_price_query = """
                UPDATE store_product 
                SET selling_price = %s 
                WHERE id_product = %s AND promotional_product = FALSE;
            """
            execute_query(update_price_query, (data['selling_price'], data['id_product']))
            
            # Якщо все успішно — повертаємося до списку товарів у магазині
            return redirect(url_for('manager_store_products'))
            
        except Exception as e:
            print(f"Помилка при додаванні партії: {e}")
            error = f"Помилка бази даних: Можливо, товар з таким UPC вже існує, або не всі поля заповнені."

    # Якщо це GET-запит або сталася помилка — показуємо форму
    base_products = product.get_all_products() or []
    return render_template('add_store_product.html', products=base_products, error=error)

# 3. Видалення товару з полиці
@app.route('/manager/store_products/delete/<upc>')
@manager_required
def delete_store_product(upc):
    store_product.delete_store_product(upc)
    return redirect(url_for('manager_store_products'))

# 4. Ручне редагування ціни/кількості
@app.route('/manager/store_products/edit/<upc>', methods=['GET', 'POST'])
@manager_required
def edit_store_product(upc):
    if request.method == 'POST':
        store_product.update_store_product(
            upc, request.form['upc_prom'], request.form['id_product'],
            request.form['selling_price'], request.form['products_number'],
            request.form.get('promotional_product') == 'on'
        )
        return redirect(url_for('manager_store_products'))
    
    prod_data = store_product.get_product_details_by_upc(upc)
    return render_template('edit_store_product.html', product=prod_data[0], upc=upc)

# ── КАТЕГОРІЇ ───────────────────────────────────────────────────
@app.route('/manager/categories')
@manager_required
def manager_categories():
    categories = category.get_all_categories() or []
    return render_template('manager_categories.html', categories=categories)

@app.route('/manager/categories/add', methods=['POST'])
@manager_required
def add_category():
    category.add_category(request.form['category_number'], request.form['category_name'])
    return redirect(url_for('manager_categories'))

@app.route('/manager/categories/delete/<int:cat_num>')
@manager_required
def delete_category(cat_num):
    category.delete_category(cat_num)
    return redirect(url_for('manager_categories'))

# ── КЛІЄНТИ ─────────────────────────────────────────────────────
@app.route('/manager/customers')
@login_required
def manager_customers():
    customers = customer_card.get_all_customers() or []
    return render_template('manager_customers.html', customers=customers)

@app.route('/manager/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        data = request.form
        customer_card.add_customer(
            data['card_number'], data['surname'], data['name'], data['patronymic'],
            data['phone'], data['city'], data['street'], data['zip_code'], data['percent']
        )
        return redirect(url_for('manager_customers'))
    return render_template('add_customer.html')

@app.route('/manager/customers/delete/<card_number>')
@manager_required
def delete_customer(card_number):
    customer_card.delete_customer(card_number)
    return redirect(url_for('manager_customers'))

# ── ЧЕКИ ────────────────────────────────────────────────────────
@app.route('/manager/checks')
@login_required
def manager_checks():
    try:
        checks_list = check.get_all_receipts() or []
    except Exception as e:
        checks_list = []
        print(f"Помилка БД: {e}")
    return render_template('manager_checks.html', checks=checks_list)

@app.route('/manager/check/<check_number>')
@login_required
def view_check_details(check_number):
    details = check.get_receipt_with_details(check_number)
    return render_template('check_details.html', details=details)

@app.route('/manager/checks/delete/<check_number>')
@manager_required
def delete_check(check_number):
    check.delete_receipt(check_number)
    return redirect(url_for('manager_checks'))

# ── ПРОДАЖ (касир) ──────────────────────────────────────────────
@app.route('/cashier/sell', methods=['GET', 'POST'])
@login_required
def cashier_sell():
    if request.method == 'POST':
        error = None
        check_number = request.form.get('check_number', '').strip()
        card_number  = request.form.get('card_number') or None
        id_employee  = session['id_employee']  # береться з сесії — реальний ID

        upcs       = request.form.getlist('upc[]')
        quantities = request.form.getlist('quantity[]')
        prices     = request.form.getlist('price[]')

        # Валідація
        if not check_number:
            error = "Вкажіть номер чека."
        elif not upcs or all(u == '' for u in upcs):
            error = "Додайте хоча б один товар."
        elif len(set(upcs)) != len(upcs):
            error = "Один і той самий товар зустрічається двічі в чеку."

        if not error:
            for upc, qty_str in zip(upcs, quantities):
                try:
                    qty = int(qty_str)
                except ValueError:
                    error = f"Некоректна кількість для UPC {upc}."; break
                available = store_product.get_product_quantity(upc)
                if qty > available:
                    error = f"На складі лише {available} шт. для UPC {upc}."
                    break

        if not error:
            try:
                total_sum  = float(request.form.get('total_sum', 0))
                print_date = datetime.datetime.now()

                check.add_receipt(check_number, id_employee, card_number, print_date, total_sum)

                for upc, qty_str, price_str in zip(upcs, quantities, prices):
                    qty   = int(qty_str)
                    price = float(price_str)
                    check.add_sale(upc, check_number, qty, price)
                    store_product.decrease_quantity(upc, qty)

                return redirect(url_for('view_check_details', check_number=check_number))

            except Exception as e:
                print(f"Помилка при продажі: {e}")
                error = f"Помилка при збереженні чека: {e}"

        products  = store_product.get_all_store_products_by_name() or []
        customers = customer_card.get_all_customers() or []
        return render_template('sell_product.html',
                               products=products, customers=customers,
                               error=error, auto_check_number=check_number)

    # GET
    auto_number = str(uuid.uuid4())[:10].upper()
    products  = store_product.get_all_store_products_by_name() or []
    customers = customer_card.get_all_customers() or []
    return render_template('sell_product.html',
                           products=products, customers=customers,
                           error=None, auto_check_number=auto_number)

if __name__ == '__main__':
    app.run(debug=True)
