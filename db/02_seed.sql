-- ZLAGODA seed data. All seeded employees log in with password: zlagoda123

INSERT INTO category (category_number, category_name) VALUES
    (1, 'Dairy'),
    (2, 'Bakery'),
    (3, 'Beverages');

INSERT INTO employee
    (id_employee, empl_surname, empl_name, empl_patronymic, empl_role,
     salary, date_of_birth, date_of_start, phone_number, city, street, zip_code,
     login, password_hash) VALUES
    ('E001', 'Bondarenko', 'Iryna',  'Petrivna',  'Manager',
     25000.00, '1988-03-12', '2020-01-10', '+380501112233', 'Kyiv', 'Khreshchatyk 1', '01001',
     'ibondarenko', '$2b$12$jHKZDHSvya4Ak0LOAIFLXe48lNAfod5E079sHj04oX.fcFGXfxFFy'),
    ('E002', 'Tkachenko',  'Andrii', 'Olehovych', 'Cashier',
     14000.00, '1996-07-21', '2022-05-01', '+380502223344', 'Kyiv', 'Sichovykh 5',    '02002',
     'atkachenko', '$2b$12$jHKZDHSvya4Ak0LOAIFLXe48lNAfod5E079sHj04oX.fcFGXfxFFy'),
    ('E003', 'Melnyk',     'Olena',  'Ivanivna',  'Cashier',
     14500.00, '1999-11-02', '2023-02-15', '+380503334455', 'Kyiv', 'Lesi Ukrainky 9','03003',
     'omelnyk', '$2b$12$jHKZDHSvya4Ak0LOAIFLXe48lNAfod5E079sHj04oX.fcFGXfxFFy');

INSERT INTO customer_card
    (card_number, cust_surname, cust_name, cust_patronymic, phone_number, city, street, zip_code, percent) VALUES
    ('C001', 'Shevchenko', 'Taras', 'Hryhorovych', '+380671112233', 'Kyiv', 'Franka 3', '01004', 5),
    ('C002', 'Kovalenko',  'Olena', NULL,          '+380672223344', NULL,   NULL,       NULL,    10);

INSERT INTO product (id_product, category_number, product_name, producer, characteristics) VALUES
    (1, 1, 'Milk 1L',      'Galychyna',    'Pasteurized 2.5%'),
    (2, 1, 'Yogurt',       'Danone',       'Strawberry 300g'),
    (3, 2, 'White Bread',  'Kyivkhlib',    '500g loaf'),
    (4, 3, 'Orange Juice', 'Sandora',      '1L carton');

INSERT INTO store_product
    (upc, upc_prom, id_product, selling_price, products_number, promotional_product) VALUES
    ('001000000001', NULL, 1, 32.50, 100, FALSE),
    ('001000000002', NULL, 2, 18.00,  50, FALSE),
    ('001000000003', NULL, 3, 22.00,  40, FALSE),
    ('001000000004', NULL, 4, 45.00,  30, FALSE);

-- Promotional price is overwritten to 36.00 by trg_promo_price (80% of 45.00).
INSERT INTO store_product
    (upc, upc_prom, id_product, selling_price, products_number, promotional_product) VALUES
    ('001000000104', '001000000004', 4, 0, 10, TRUE);

-- sum_total already has the loyalty-card discount applied; vat is generated.
INSERT INTO receipt (check_number, id_employee, card_number, print_date, sum_total) VALUES
    ('R0001', 'E002', 'C001', '2026-06-01 10:15:00', 47.9750),
    ('R0002', 'E002', NULL,   '2026-06-02 14:30:00', 44.0000),
    ('R0003', 'E003', 'C002', '2026-06-05 09:00:00', 72.9000);

INSERT INTO sale (upc, check_number, product_number, selling_price) VALUES
    ('001000000001', 'R0001', 1, 32.50),
    ('001000000002', 'R0001', 1, 18.00),
    ('001000000003', 'R0002', 2, 22.00),
    ('001000000004', 'R0003', 1, 45.00),
    ('001000000104', 'R0003', 1, 36.00);
