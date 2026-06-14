-- ============================================================
--  ZLAGODA  —  test data  [revised after review]
--  - products now include a producer
--  - employees now include login + bcrypt password_hash
--    (all three log in with the password:  zlagoda123 )
--  - receipt sum_total now reflects the customer-card discount;
--    vat is computed automatically (generated column).
-- ============================================================

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

-- Regular items first, then the promotional item (its price is set to
-- 80% of the regular juice automatically by the trigger -> 36.00).
INSERT INTO store_product
    (upc, upc_prom, id_product, selling_price, products_number, promotional_product) VALUES
    ('001000000001', NULL, 1, 32.50, 100, FALSE),
    ('001000000002', NULL, 2, 18.00,  50, FALSE),
    ('001000000003', NULL, 3, 22.00,  40, FALSE),
    ('001000000004', NULL, 4, 45.00,  30, FALSE);

INSERT INTO store_product
    (upc, upc_prom, id_product, selling_price, products_number, promotional_product) VALUES
    ('001000000104', '001000000004', 4, 0, 10, TRUE);   -- price overwritten to 36.00 by trigger

-- Receipts. sum_total = net amount the customer paid (line totals minus
-- the card discount); vat is generated, so it is NOT listed here.
--   R0001: milk 32.50 + yogurt 18.00 = 50.50, card C001 (5%)  -> 47.9750
--   R0002: bread 2 x 22.00          = 44.00, no card          -> 44.0000
--   R0003: juice 45.00 + promo 36.00 = 81.00, card C002 (10%) -> 72.9000
INSERT INTO receipt (check_number, id_employee, card_number, print_date, sum_total) VALUES
    ('R0001', 'E002', 'C001', '2026-06-01 10:15:00', 47.9750),
    ('R0002', 'E002', NULL,   '2026-06-02 14:30:00', 44.0000),
    ('R0003', 'E003', 'C002', '2026-06-05 09:00:00', 72.9000);

-- Sale lines store the GROSS per-unit price at sale time (the discount
-- applies to the receipt total, not to individual lines).
INSERT INTO sale (upc, check_number, product_number, selling_price) VALUES
    ('001000000001', 'R0001', 1, 32.50),
    ('001000000002', 'R0001', 1, 18.00),
    ('001000000003', 'R0002', 2, 22.00),
    ('001000000004', 'R0003', 1, 45.00),
    ('001000000104', 'R0003', 1, 36.00);
