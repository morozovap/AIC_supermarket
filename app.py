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

# ── КАСИР
@app.route('/cashier/profile')
@login_required
def cashier_profile():
    user_id = session.get('user_id') or session.get('id_employee')
    
    try:
        emp = employee.get_employee_by_id(user_id)
    except Exception as e:
        emp = None
        print(f"Помилка при завантаженні профілю касира: {e}")
        
    return render_template('cashier_profile.html', emp=emp)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── ПРАЦІВНИКИ (тільки менеджер) ────────────────────────────────
@app.route('/manager/employees')
@manager_required
def manager_employees():
    # Ловимо параметри з GET-запиту
    search_surname = request.args.get('search_surname', '')
    role_filter = request.args.get('role_filter', 'all')

    try:
        # Викликаємо нашу нову розумну функцію пошуку
        employees_list = employee.search_employees(search_surname, role_filter) or []
    except Exception as e:
        employees_list = []
        print(f"Помилка БД при пошуку працівників: {e}")
        
    return render_template('manager_dashboard.html', 
                           employees=employees_list,
                           search_surname=search_surname,
                           role_filter=role_filter)

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
    category_filter = request.args.get('category_filter', 'all')
    try:
        # Використовуємо ТВОЮ готову функцію з product.py
        if category_filter != 'all':
            products_list = product.get_products_by_category(int(category_filter)) or []
        else:
            products_list = product.get_all_products() or []
            
        categories = category.get_all_categories() or []
    except Exception as e:
        products_list = []
        categories = []
        print(f"Помилка при отриманні товарів за категорією: {e}")
        
    return render_template('manager_products.html', 
                           products=products_list, 
                           categories=categories, 
                           category_filter=category_filter)

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
    search = request.args.get('search', '').strip()
    promo_filter = request.args.get('promo_filter', 'all')
    sort_by = request.args.get('sort_by', 'name')  # 'name' або 'quantity'

    from db import execute_query

    # Базовий запит для виведення товарів на полицях
    query = """
        SELECT sp.upc, sp.upc_prom, sp.id_product, sp.selling_price, sp.products_number, 
               sp.promotional_product, p.product_name, c.category_name
        FROM store_product sp
        JOIN product p ON sp.id_product = p.id_product
        JOIN category c ON p.category_number = c.category_number
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (p.product_name ILIKE %s OR sp.upc ILIKE %s)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    if promo_filter == 'promo':
        query += " AND sp.promotional_product = TRUE"
    elif promo_filter == 'non_promo':
        query += " AND sp.promotional_product = FALSE"

    # ФІКС СОРТУВАННЯ: Повна підтримка всіх трьох режимів з інтерфейсу
    if sort_by == 'qty_desc':
        query += " ORDER BY sp.products_number DESC, p.product_name ASC;"
    elif sort_by == 'qty_asc':
        query += " ORDER BY sp.products_number ASC, p.product_name ASC;"
    else:
        query += " ORDER BY p.product_name ASC, sp.products_number DESC;"

    try:
        products = execute_query(query, tuple(params) if params else None, fetch=True) or []
    except Exception as e:
        products = []
        print(f"Помилка сортування товарів на полицях: {e}")
    
    return render_template('manager_store_products.html', 
                           products=products, 
                           search=search, 
                           promo_filter=promo_filter, 
                           sort_by=sort_by)

# 2. Додавання нової партії (Декілька товарів одночасно)
@app.route('/manager/store_products/add', methods=['GET', 'POST'])
@manager_required
def add_store_product():
    error = None
    if request.method == 'POST':
        # Отримуємо масиви даних з форми (як у чеках)
        upcs = request.form.getlist('upc[]')
        id_products = request.form.getlist('id_product[]')
        quantities = request.form.getlist('products_number[]')
        prices = request.form.getlist('selling_price[]')

        try:
            # Проходимося циклом по кожному доданому рядку
            for i in range(len(upcs)):
                upc = upcs[i].strip()
                if not upc: 
                    continue # Пропускаємо порожні рядки

                id_prod = id_products[i]
                qty = int(quantities[i])
                price = float(prices[i])

                # Шукаємо, чи є вже такий штрих-код на полиці
                existing_product = store_product.get_product_details_by_upc(upc)

                if existing_product:
                    # Товар є -> ОНОВЛЮЄМО КІЛЬКІСТЬ
                    current_qty = existing_product[0][1] # індекс 1 - це products_number згідно твого get_product_details_by_upc
                    new_qty = current_qty + qty
                    store_product.update_store_product(upc, None, id_prod, price, new_qty, False)
                else:
                    # Товар новий -> СТВОРЮЄМО
                    store_product.add_store_product(upc, None, id_prod, price, qty, False)

                # ГЛОБАЛЬНА ПЕРЕОЦІНКА для всіх неакційних партій цього базового товару
                from db import execute_query
                update_price_query = """
                    UPDATE store_product 
                    SET selling_price = %s 
                    WHERE id_product = %s AND promotional_product = FALSE;
                """
                execute_query(update_price_query, (price, id_prod))

            return redirect(url_for('manager_store_products'))
            
        except Exception as e:
            print(f"Помилка при додаванні партії: {e}")
            error = f"Помилка бази даних. Перевірте правильність введених даних."

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

# 5. Створення акційного товару (Логіка кнопки "Уцінити")
@app.route('/manager/store_products/promo/<upc>', methods=['GET', 'POST'])
@manager_required
def promo_store_product(upc):
    error = None
    from db import execute_query
    
    query = """
        SELECT sp.upc, sp.id_product, sp.selling_price, sp.products_number, p.product_name, sp.upc_prom
        FROM store_product sp
        JOIN product p ON sp.id_product = p.id_product
        WHERE sp.upc = %s;
    """
    result = execute_query(query, (upc,), fetch=True)
    if not result:
        return "Товар не знайдено", 404
        
    prod = result[0]
    # Формуємо акційну ціну як 80% від основної вартості
    promo_price = round(float(prod[2]) * 0.8, 2)
    
    if request.method == 'POST':
        promo_upc = request.form['promo_upc'].strip()
        promo_qty = int(request.form['promo_qty'])
        
        if promo_qty > prod[3]:
            error = f"Не можна уцінити більше, ніж є на полиці (макс. {prod[3]} шт/кг)."
        elif promo_upc == upc:
            error = "Акційний штрих-код не може збігатися зі звичайним штрих-кодом."
        else:
            try:
                check_promo = execute_query("SELECT products_number FROM store_product WHERE upc = %s;", (promo_upc,), fetch=True)
                
                if check_promo:
                    new_promo_qty = check_promo[0][0] + promo_qty
                    execute_query("""
                        UPDATE store_product 
                        SET selling_price = %s, products_number = %s 
                        WHERE upc = %s;
                    """, (promo_price, new_promo_qty, promo_upc))
                else:
                    store_product.add_store_product(promo_upc, None, prod[1], promo_price, promo_qty, True)
                
                # 1. Оновлюємо оригінальний товар (зменшуємо к-сть і зв'язуємо з акційним UPC)
                new_regular_qty = prod[3] - promo_qty
                execute_query("""
                    UPDATE store_product 
                    SET products_number = %s, upc_prom = %s 
                    WHERE upc = %s;
                """, (new_regular_qty, promo_upc, upc))
                
                # ── ФІКС АВТОМАТИЧНОГО ЗВ'ЯЗКУ (БЛОК 3) ──
                # 2. Акційному товару теж залізобетонно прописуємо лінк назад на його оригінал
                execute_query("""
                    UPDATE store_product 
                    SET upc_prom = %s 
                    WHERE upc = %s;
                """, (upc, promo_upc))
                
                return redirect(url_for('manager_store_products'))
            except Exception as e:
                print(f"Помилка при створенні акції: {e}")
                error = "Помилка бази даних. Перевірте унікальність акційного UPC."
                
    return render_template('promo_store_product.html', prod=prod, promo_price=promo_price, error=error)

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

@app.route('/manager/categories/edit/<int:cat_num>', methods=['GET', 'POST'])
@manager_required
def edit_category(cat_num):
    if request.method == 'POST':
        new_name = request.form['category_name']
        try:
            category.update_category(cat_num, new_name)
            return redirect(url_for('manager_categories'))
        except Exception as e:
            print(f"Помилка при оновленні категорії: {e}")
            return "Помилка при збереженні змін."

    # Отримуємо поточну назву категорії, щоб менеджер бачив, що він редагує
    cat_data = category.get_category_by_number(cat_num)
    return render_template('edit_category.html', category=cat_data, cat_num=cat_num)

# ── КЛІЄНТИ ─────────────────────────────────────────────────────
@app.route('/manager/customers')
@login_required
def manager_customers():
    search_surname = request.args.get('search_surname', '').strip()
    percent_filter = request.args.get('percent_filter', 'all')

    try:
        # Використовуємо ТВОЇ готові функції з customer_card.py
        if search_surname:
            customers = customer_card.search_customers_by_surname(search_surname) or []
            # Якщо одночасно вибрано і відсоток, фільтруємо результат прямо в Python
            if percent_filter != 'all':
                customers = [c for c in customers if str(c[8]) == str(percent_filter)]
        elif percent_filter != 'all':
            customers = customer_card.get_customers_by_percent(int(percent_filter)) or []
        else:
            customers = customer_card.get_all_customers() or []

        # Збираємо унікальні відсотки для випадаючого списку (фільтра)
        from db import execute_query
        percents_raw = execute_query("SELECT DISTINCT percent FROM customer_card ORDER BY percent;", fetch=True) or []
        percents = [p[0] for p in percents_raw]
        
    except Exception as e:
        customers = []
        percents = []
        print(f"Помилка при фільтрації клієнтів: {e}")

    return render_template('manager_customers.html', 
                           customers=customers, 
                           percents=percents, 
                           search_surname=search_surname, 
                           percent_filter=percent_filter)

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

@app.route('/manager/customers/edit/<card_number>', methods=['GET', 'POST'])
@login_required
def edit_customer(card_number):
    if request.method == 'POST':
        data = request.form
        try:
            customer_card.update_customer(
                card_number, data['surname'], data['name'], data['patronymic'],
                data['phone'], data['city'], data['street'], data['zip_code'], data['percent']
            )
            return redirect(url_for('manager_customers'))
        except Exception as e:
            print(f"Помилка при оновленні картки клієнта: {e}")
            return "Помилка при збереженні змін."

    # Отримуємо дані для заповнення полів форми
    cust = customer_card.get_customer_by_card_number(card_number)
    return render_template('edit_customer.html', customer=cust, card_number=card_number)

# ── ЧЕКИ ────────────────────────────────────────────────────────
@app.route('/manager/checks')
@login_required
def manager_checks():
    # Отримуємо параметри фільтрації з GET-запиту
    cashier_filter = request.args.get('cashier_filter', 'all')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    from db import execute_query

    # 1. Отримуємо список усіх касирів для випадаючого списку (Вимога M17)
    try:
        cashiers = execute_query(
            "SELECT id_employee, empl_surname, empl_name FROM employee WHERE LOWER(empl_role) IN ('cashier', 'касир') ORDER BY empl_surname;", 
            fetch=True
        ) or []
    except Exception as e:
        cashiers = []
        print(f"Помилка завантаження списку касирів: {e}")

    # 2. Будуємо динамічний SQL-запит для чеків із підтягуванням ПІБ касира
    query = """
        SELECT r.check_number, r.card_number, r.print_date, r.sum_total, r.vat, e.empl_surname, e.empl_name
        FROM receipt r
        JOIN employee e ON r.id_employee = e.id_employee
        WHERE 1=1
    """
    params = []

    # Фільтр за конкретним касиром (M17)
    if cashier_filter != 'all':
        query += " AND r.id_employee = %s"
        params.append(cashier_filter)
        
    # Фільтр за періодом дат (M18)
    if start_date:
        query += " AND r.print_date::date >= %s::date"
        params.append(start_date)
        
    if end_date:
        query += " AND r.print_date::date <= %s::date"
        params.append(end_date)

    query += " ORDER BY r.print_date DESC;"

    try:
        checks_list = execute_query(query, tuple(params) if params else None, fetch=True) or []
    except Exception as e:
        checks_list = []
        print(f"Помилка БД при фільтрації чеків менеджером: {e}")

    return render_template('manager_checks.html', 
                           checks=checks_list, 
                           cashiers=cashiers,
                           cashier_filter=cashier_filter,
                           start_date=start_date,
                           end_date=end_date)

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

@app.route('/cashier/my-checks')
@login_required
def cashier_my_checks():
    user_id = session.get('id_employee')
    
    # Визначаємо поточну дату комп'ютера
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    start_date = request.args.get('start_date', today_str)
    end_date = request.args.get('end_date', today_str)
    filter_type = request.args.get('filter_type', 'today')
    
    if filter_type == 'today':
        start_date = today_str
        end_date = today_str
        
    from db import execute_query
    
    # ФІКС: Змінено "receipts" на точну назву таблиці з бази даних "receipt"
    query = """
        SELECT check_number, card_number, print_date, sum_total, vat
        FROM receipt
        WHERE id_employee = %s AND print_date::date BETWEEN %s::date AND %s::date
        ORDER BY print_date DESC;
    """
    try:
        checks = execute_query(query, (user_id, start_date, end_date), fetch=True) or []
    except Exception as e:
        checks = []
        print(f"Помилка завантаження чеків касира: {e}")
        
    return render_template('cashier_checks.html', checks=checks, start_date=start_date, end_date=end_date, filter_type=filter_type)

@app.route('/cashier/my-checks/details/<check_number>')
@login_required
def cashier_check_details(check_number):
    from db import execute_query
    query = """
        SELECT s.product_number, s.selling_price, p.product_name
        FROM sale s
        JOIN store_product sp ON s.upc = sp.upc
        JOIN product p ON sp.id_product = p.id_product
        WHERE s.check_number = %s;
    """
    details = execute_query(query, (check_number,), fetch=True) or []
    return render_template('cashier_check_details.html', details=details, check_number=check_number)

@app.route('/api/search-customers')
@login_required
def api_search_customers():
    surname = request.args.get('surname', '').strip()
    if not surname:
        return []
    import customer_card
    try:
        res = customer_card.search_customers_by_surname(surname) or []
        return [{'card_number': c[0], 'cust_surname': c[1], 'cust_name': c[2], 'percent': c[8]} for c in res]
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/get-product-details')
@login_required
def api_get_product_details():
    upc = request.args.get('upc', '').strip()
    if not upc:
        return None
    import store_product
    try:
        res = store_product.get_product_details_by_upc(upc)
        if res:
            return {
                'selling_price': float(res[0][0]),
                'products_number': res[0][1],
                'product_name': res[0][2],
                'characteristics': res[0][3]
            }
        return None
    except Exception as e:
        return {'error': str(e)}, 500

# ── ПРОДАЖ (касир) ──────────────────────────────────────────────
@app.route('/cashier/sell', methods=['GET', 'POST'])
@login_required
def cashier_sell():
    if request.method == 'POST':
        error = None
        check_number = request.form.get('check_number', '').strip()
        card_number  = request.form.get('card_number') or None
        id_employee  = session['id_employee']

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

                # 1. Створюємо чек у базі даних
                check.add_receipt(check_number, id_employee, card_number, print_date, total_sum)

                # 2. Проходимо по товарах, додаємо продажі та жорстко списуємо залишки
                from db import execute_query
                for upc, qty_str, price_str in zip(upcs, quantities, prices):
                    qty   = int(qty_str)
                    price = float(price_str)
                    
                    # Додаємо запис у таблицю продажів
                    check.add_sale(upc, check_number, qty, price)
                    
                    # ФІКС: Пряме залізобетонне списання кількості з гарантованим коммітом
                    decrease_stock_query = """
                        UPDATE store_product 
                        SET products_number = products_number - %s 
                        WHERE upc = %s;
                    """
                    execute_query(decrease_stock_query, (qty, upc), fetch=False)

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
    
@app.route('/cashier/products')
@login_required
def cashier_products():
    search_text = request.args.get('search_text', '').strip()
    category_filter = request.args.get('category_filter', 'all')
    promo_filter = request.args.get('promo_filter', 'all')
    
    from db import execute_query
    query = """
        SELECT sp.upc, sp.selling_price, sp.products_number, sp.promotional_product, 
               p.product_name, p.characteristics, c.category_name
        FROM store_product sp
        JOIN product p ON sp.id_product = p.id_product
        JOIN category c ON p.category_number = c.category_number
        WHERE 1=1
    """
    params = []
    if search_text:
        query += " AND (p.product_name ILIKE %s OR sp.upc ILIKE %s)"
        params.append(f"%{search_text}%")
        params.append(f"%{search_text}%")
    if category_filter != 'all':
        query += " AND p.category_number = %s"
        params.append(int(category_filter))
    if promo_filter == 'promo':
        query += " AND sp.promotional_product = TRUE"
    elif promo_filter == 'non_promo':
        query += " AND sp.promotional_product = FALSE"
        
    query += " ORDER BY p.product_name ASC;"
    
    try:
        products = execute_query(query, tuple(params) if params else None, fetch=True) or []
        categories = execute_query("SELECT * FROM category ORDER BY category_name;", fetch=True) or []
    except Exception as e:
        products = []
        categories = []
        print(f"Помилка пошуку товарів для касира: {e}")
        
    return render_template('cashier_products.html', products=products, categories=categories,
                           search_text=search_text, category_filter=category_filter, promo_filter=promo_filter)
    
# ── АНАЛІТИЧНІ ЗВІТИ ДЛЯ МЕНЕДЖЕРА ──────────────────────────────
@app.route('/manager/reports', methods=['GET', 'POST'])
@manager_required
def manager_reports():
    from db import execute_query
    
    # Визначаємо дати за замовчуванням (поточний місяць 2026 року)
    today = datetime.date.today()
    default_start = today.replace(day=1).strftime('%Y-%m-%d')
    default_end = today.strftime('%Y-%m-%d')

    start_date = request.args.get('start_date', default_start)
    end_date = request.args.get('end_date', default_end)
    
    # Параметри для нових точкових звітів (M19 та M21)
    target_cashier = request.args.get('target_cashier', '').strip()
    target_product = request.args.get('target_product', '').strip()

    # 1. Списки для випадаючих списків фільтрації
    try:
        cashiers_list = execute_query(
            "SELECT id_employee, empl_surname, empl_name FROM employee WHERE LOWER(empl_role) IN ('cashier', 'касир') ORDER BY empl_surname;", 
            fetch=True
        ) or []
    except Exception as e:
        cashiers_list = []
        print(f"Помилка завантаження касирів для звітів: {e}")

    # 2. Вимога M20 — Загальна сума (виторг та ПДВ) усіх касирів за період
    finance_query = """
        SELECT COUNT(check_number) as total_checks,
               COALESCE(SUM(sum_total), 0) as total_revenue,
               COALESCE(SUM(vat), 0) as total_vat
        FROM receipt
        WHERE print_date::date BETWEEN %s::date AND %s::date;
    """
    try:
        finance_res = execute_query(finance_query, (start_date, end_date), fetch=True)
        finance = finance_res[0] if finance_res else (0, 0, 0)
    except Exception as e:
        finance = (0, 0, 0)
        print(f"Помилка M20: {e}")

    # 3. Вимога M19 — Загальна сума конкретного касира за період
    cashier_revenue = 0.0
    selected_cashier_name = ""
    if target_cashier:
        m19_query = """
            SELECT COALESCE(SUM(sum_total), 0) 
            FROM receipt 
            WHERE id_employee = %s AND print_date::date BETWEEN %s::date AND %s::date;
        """
        try:
            res = execute_query(m19_query, (target_cashier, start_date, end_date), fetch=True)
            cashier_revenue = float(res[0][0]) if res else 0.0
            
            # Беремо ім'я для гарного відображення в результатах
            for c in cashiers_list:
                if c[0] == target_cashier:
                    selected_cashier_name = f"{c[1]} {c[2]}"
                    break
        except Exception as e:
            print(f"Помилка M19: {e}")

    # 4. Вимога M21 — Кількість одиниць певного товару, проданого за період
    product_sales_results = []
    if target_product:
        m21_query = """
            SELECT p.product_name, sp.upc, COALESCE(SUM(s.product_number), 0) as sold_qty, COALESCE(SUM(s.product_number * s.selling_price), 0) as total_sum
            FROM sale s
            JOIN store_product sp ON s.upc = sp.upc
            JOIN product p ON sp.id_product = p.id_product
            JOIN receipt r ON s.check_number = r.check_number
            WHERE (sp.upc = %s OR p.product_name ILIKE %s)
              AND r.print_date::date BETWEEN %s::date AND %s::date
            GROUP BY p.product_name, sp.upc;
        """
        try:
            product_sales_results = execute_query(
                m21_query, (target_product, f"%{target_product}%", start_date, end_date), fetch=True
            ) or []
        except Exception as e:
            print(f"Помилка M21: {e}")

    # 5. Стандартний рейтинг касирів та Топ-5 (для загального аналізу)
    cashier_rank_query = """
        SELECT r.id_employee, e.empl_surname, e.empl_name, COUNT(r.check_number), SUM(r.sum_total)
        FROM receipt r
        JOIN employee e ON r.id_employee = e.id_employee
        WHERE r.print_date::date BETWEEN %s::date AND %s::date
        GROUP BY r.id_employee, e.empl_surname, e.empl_name
        ORDER BY SUM(r.sum_total) DESC;
    """
    popular_query = """
        SELECT sp.upc, p.product_name, SUM(s.product_number) as sold_qty, SUM(s.product_number * s.selling_price) as total_sales
        FROM sale s
        JOIN store_product sp ON s.upc = sp.upc
        JOIN product p ON sp.id_product = p.id_product
        JOIN receipt r ON s.check_number = r.check_number
        WHERE r.print_date::date BETWEEN %s::date AND %s::date
        GROUP BY sp.upc, p.product_name
        ORDER BY sold_qty DESC
        LIMIT 5;
    """
    try:
        cashiers = execute_query(cashier_rank_query, (start_date, end_date), fetch=True) or []
        popular_products = execute_query(popular_query, (start_date, end_date), fetch=True) or []
    except Exception as e:
        cashiers, popular_products = [], []
        print(f"Помилка завантаження рейтингів: {e}")

    return render_template('manager_reports.html', 
                           finance=finance, 
                           cashiers=cashiers, 
                           products=popular_products,
                           cashiers_list=cashiers_list,
                           start_date=start_date, 
                           end_date=end_date,
                           target_cashier=target_cashier,
                           cashier_revenue=cashier_revenue,
                           selected_cashier_name=selected_cashier_name,
                           target_product=target_product,
                           product_sales_results=product_sales_results)

if __name__ == '__main__':
    app.run(debug=True)
