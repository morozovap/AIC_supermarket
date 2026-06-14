import mimetypes
mimetypes.add_type('text/css', '.css')

from flask import Flask, render_template, request, redirect, url_for
import category
import employee 
import product
import customer_card
import check
import store_product
import datetime


app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "1234":
            return redirect(url_for('manager_employees'))
        else:
            error = "Неправильний логін або пароль"
    return render_template('login.html', error=error)

# --- ПРАЦІВНИКИ ---
@app.route('/manager/employees')
def manager_employees():
    try:
        employees_list = employee.get_all_employees()
        if employees_list is None: employees_list = []
    except Exception as e:
        employees_list = []
        print(f"Помилка БД: {e}")
    return render_template('manager_dashboard.html', employees=employees_list)

@app.route('/manager/employees/add', methods=['GET', 'POST'])
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
def delete_employee(id_employee):
    employee.delete_employee(id_employee)
    return redirect(url_for('manager_employees'))

@app.route('/manager/employees/edit/<id_employee>', methods=['GET', 'POST'])
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

# --- ТОВАРИ ---
@app.route('/manager/products')
def manager_products():
    try:
        products_list = product.get_all_products()
        if products_list is None: products_list = []
    except Exception as e:
        products_list = []
        print(f"Помилка БД: {e}")
    return render_template('manager_products.html', products=products_list)

@app.route('/manager/products/add', methods=['GET', 'POST'])
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
def delete_product(id_product):
    product.delete_product(id_product)
    return redirect(url_for('manager_products'))

@app.route('/manager/products/edit/<id_product>', methods=['GET', 'POST'])
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

# --- КАТЕГОРІЇ ---
@app.route('/manager/categories')
def manager_categories():
    categories = category.get_all_categories() or []
    return render_template('manager_categories.html', categories=categories)

@app.route('/manager/categories/add', methods=['POST'])
def add_category():
    category.add_category(request.form['category_number'], request.form['category_name'])
    return redirect(url_for('manager_categories'))

@app.route('/manager/categories/delete/<int:cat_num>')
def delete_category(cat_num):
    category.delete_category(cat_num)
    return redirect(url_for('manager_categories'))

# --- КЛІЄНТИ ---
@app.route('/manager/customers')
def manager_customers():
    customers = customer_card.get_all_customers() or []
    return render_template('manager_customers.html', customers=customers)

@app.route('/manager/customers/add', methods=['GET', 'POST'])
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
def delete_customer(card_number):
    customer_card.delete_customer(card_number)
    return redirect(url_for('manager_customers'))

# --- ЧЕКИ ---
@app.route('/manager/checks')
def manager_checks():
    try:
        checks_list = check.get_all_receipts()
        if checks_list is None: checks_list = []
    except Exception as e:
        checks_list = []
        print(f"Помилка БД: {e}")
    return render_template('manager_checks.html', checks=checks_list)

@app.route('/manager/check/<check_number>')
def view_check_details(check_number):
    details = check.get_receipt_with_details(check_number)
    return render_template('check_details.html', details=details)

@app.route('/cashier/sell', methods=['GET', 'POST'])
def cashier_sell():
    if request.method == 'POST':
        try:
            # 1. Збираємо дані з форми
            check_number = request.form['check_number']
            id_employee = "1" # (Тут поки хардкод, в ідеалі брати з сесії)
            card_number = request.form.get('card_number') or None
            qty = int(request.form['quantity'])
            price = float(request.form['price'])
            total_sum = float(request.form['total_sum'])
            vat = total_sum * 0.2 # Припустимо ПДВ 20%
            upc = request.form['upc']
            print_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 2. Зберігаємо чек
            check.add_receipt(check_number, id_employee, card_number, print_date, total_sum, vat)
            
            # 3. Зберігаємо деталі продажу
            check.add_sale(upc, check_number, qty, price)
            
            return redirect(url_for('manager_checks'))
        except Exception as e:
            print(f"Помилка при продажі: {e}")
            return "Помилка при збереженні. Перевірте, чи номер чека унікальний!"

    # GET-запит: завантажуємо дані
    products = store_product.get_all_store_products_by_name()
    customers = customer_card.get_all_customers()
    return render_template('sell_product.html', products=products, customers=customers)

if __name__ == '__main__':
    app.run(debug=True)