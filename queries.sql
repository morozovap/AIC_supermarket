-- ============================================================
--  ZLAGODA  —  queries.sql
--  Every operation required by the functional requirements,
--  grouped by user role and tagged with the requirement number
--  (M = Manager item, C = Cashier item).
--
--  HOW TO USE
--  Each query is written with a concrete EXAMPLE VALUE so you can
--  run it as-is against the seeded database and see real rows.
--  The example value is the part that comes from the user at run
--  time. In the Flask app you replace that literal with a %s
--  placeholder and pass the value separately, e.g.
--
--      WHERE empl_surname = 'Tkachenko'      -- here, for testing
--      WHERE empl_surname = %s               -- in app code
--
--  Lines marked  -- <param: ...>  show which value is dynamic.
-- ============================================================


-- ############################################################
--  SECTION 1 — MANAGER
-- ############################################################

-- M5. All employees, sorted by surname.
SELECT id_employee, empl_surname, empl_name, empl_patronymic,
       empl_role, salary, date_of_start, phone_number, city, street, zip_code
FROM employee
ORDER BY empl_surname;

-- M6. All employees who are cashiers, sorted by surname.
SELECT id_employee, empl_surname, empl_name, phone_number, city, street
FROM employee
WHERE empl_role = 'Cashier'                       -- <param: role>
ORDER BY empl_surname;

-- M7. All loyalty-card customers, sorted by surname.
SELECT card_number, cust_surname, cust_name, cust_patronymic,
       phone_number, city, street, zip_code, percent
FROM customer_card
ORDER BY cust_surname;

-- M8. All categories, sorted by name.
SELECT category_number, category_name
FROM category
ORDER BY category_name;

-- M9. All products, sorted by name (with their category).
SELECT p.id_product, p.product_name, p.characteristics, c.category_name
FROM product p
JOIN category c ON p.category_number = c.category_number
ORDER BY p.product_name;

-- M10. All store products, sorted by quantity in stock.
SELECT sp.upc, p.product_name, sp.selling_price,
       sp.products_number, sp.promotional_product
FROM store_product sp
JOIN product p ON sp.id_product = p.id_product
ORDER BY sp.products_number;

-- M11. By an employee's surname, find their phone and address.
SELECT empl_surname, empl_name, phone_number, city, street, zip_code
FROM employee
WHERE empl_surname = 'Tkachenko';                 -- <param: surname>

-- M12. Customers with a given discount percent, sorted by surname.
SELECT card_number, cust_surname, cust_name, phone_number, percent
FROM customer_card
WHERE percent = 10                                -- <param: percent>
ORDER BY cust_surname;

-- M13. All products in a given category, sorted by name.
SELECT p.product_name, p.characteristics
FROM product p
JOIN category c ON p.category_number = c.category_number
WHERE c.category_name = 'Dairy'                   -- <param: category name>
ORDER BY p.product_name;

-- M14. By UPC: selling price, quantity, name and characteristics.
SELECT sp.upc, p.product_name, p.characteristics,
       sp.selling_price, sp.products_number
FROM store_product sp
JOIN product p ON sp.id_product = p.id_product
WHERE sp.upc = '001000000001';                    -- <param: upc>

-- M15. All promotional products, sorted by quantity (swap ORDER BY for name).
SELECT sp.upc, p.product_name, sp.selling_price, sp.products_number
FROM store_product sp
JOIN product p ON sp.id_product = p.id_product
WHERE sp.promotional_product = TRUE
ORDER BY sp.products_number;                       -- or: ORDER BY p.product_name

-- M16. All non-promotional products, sorted by quantity (or name).
SELECT sp.upc, p.product_name, sp.selling_price, sp.products_number
FROM store_product sp
JOIN product p ON sp.id_product = p.id_product
WHERE sp.promotional_product = FALSE
ORDER BY sp.products_number;                       -- or: ORDER BY p.product_name

-- M17. All receipts by a given cashier in a time period.
--      (Use M-RECEIPT-CONTENTS below to expand any one receipt.)
SELECT check_number, print_date, card_number, sum_total, vat
FROM receipt
WHERE id_employee = 'E002'                         -- <param: cashier id>
  AND print_date >= '2026-06-01'                   -- <param: period start>
  AND print_date <  '2026-07-01'                   -- <param: period end (exclusive)>
ORDER BY print_date;

-- M18. All receipts by ALL cashiers in a time period (with cashier name).
SELECT r.check_number, r.print_date, e.empl_surname AS cashier,
       r.card_number, r.sum_total, r.vat
FROM receipt r
JOIN employee e ON r.id_employee = e.id_employee
WHERE r.print_date >= '2026-06-01'                 -- <param: period start>
  AND r.print_date <  '2026-07-01'                 -- <param: period end>
ORDER BY r.print_date;

-- M-RECEIPT-CONTENTS. The items of one receipt: name, quantity, price, line total.
--      (Shared by M17, M18 and Cashier C11.)
SELECT pr.product_name, s.product_number, s.selling_price,
       (s.product_number * s.selling_price) AS line_total
FROM sale s
JOIN store_product sp ON s.upc = sp.upc
JOIN product pr       ON sp.id_product = pr.id_product
WHERE s.check_number = 'R0001';                    -- <param: check number>

-- M19. Total takings of a given cashier in a period.
SELECT COALESCE(SUM(sum_total), 0) AS total_sales
FROM receipt
WHERE id_employee = 'E002'                         -- <param: cashier id>
  AND print_date >= '2026-06-01'                   -- <param: period start>
  AND print_date <  '2026-07-01';                  -- <param: period end>

-- M20. Total takings of ALL cashiers in a period.
SELECT COALESCE(SUM(sum_total), 0) AS total_sales
FROM receipt
WHERE print_date >= '2026-06-01'                   -- <param: period start>
  AND print_date <  '2026-07-01';                  -- <param: period end>

-- M21. Total quantity of a given product sold in a period.
--      Joins via id_product so regular + promotional UPCs both count.
SELECT COALESCE(SUM(s.product_number), 0) AS qty_sold
FROM sale s
JOIN receipt r        ON s.check_number = r.check_number
JOIN store_product sp ON s.upc = sp.upc
WHERE sp.id_product = 4                             -- <param: product id>
  AND r.print_date >= '2026-06-01'                  -- <param: period start>
  AND r.print_date <  '2026-07-01';                 -- <param: period end>

-- M4 (reports). Reports are just SELECTs over each table; M5–M10 already
--      provide employees / customers / categories / products / store products.
--      A receipts report:
SELECT r.check_number, r.print_date, e.empl_surname AS cashier,
       r.card_number, r.sum_total, r.vat
FROM receipt r
JOIN employee e ON r.id_employee = e.id_employee
ORDER BY r.print_date;


-- ############################################################
--  SECTION 2 — CASHIER
-- ############################################################

-- C1. All products, sorted by name.
SELECT p.id_product, p.product_name, p.characteristics, c.category_name
FROM product p
JOIN category c ON p.category_number = c.category_number
ORDER BY p.product_name;

-- C2. All store products, sorted by name.
SELECT sp.upc, p.product_name, sp.selling_price,
       sp.products_number, sp.promotional_product
FROM store_product sp
JOIN product p ON sp.id_product = p.id_product
ORDER BY p.product_name;

-- C3. All loyalty-card customers, sorted by surname.
SELECT card_number, cust_surname, cust_name, phone_number, percent
FROM customer_card
ORDER BY cust_surname;

-- C4. Search products by name.
SELECT id_product, product_name, characteristics
FROM product
WHERE product_name ILIKE '%milk%'                  -- <param: search text, wrapped in %...%>
ORDER BY product_name;

-- C5. Search products in a given category, sorted by name.
SELECT p.product_name, p.characteristics
FROM product p
JOIN category c ON p.category_number = c.category_number
WHERE c.category_name = 'Dairy'                    -- <param: category name>
ORDER BY p.product_name;

-- C6. Search customers by surname.
SELECT card_number, cust_surname, cust_name, phone_number, percent
FROM customer_card
WHERE cust_surname ILIKE 'kov%'                    -- <param: surname prefix>
ORDER BY cust_surname;

-- C9. Receipts the logged-in cashier created TODAY.
SELECT check_number, print_date, card_number, sum_total, vat
FROM receipt
WHERE id_employee = 'E002'                         -- <param: logged-in cashier id>
  AND print_date >= CURRENT_DATE
  AND print_date <  CURRENT_DATE + INTERVAL '1 day'
ORDER BY print_date;

-- C10. Receipts the logged-in cashier created in a given period.
SELECT check_number, print_date, card_number, sum_total, vat
FROM receipt
WHERE id_employee = 'E002'                         -- <param: logged-in cashier id>
  AND print_date >= '2026-06-01'                   -- <param: period start>
  AND print_date <  '2026-07-01'                   -- <param: period end>
ORDER BY print_date;

-- C11. Full info for one receipt by its number: header + line items.
--      Query A — the receipt header:
SELECT r.check_number, r.print_date, r.sum_total, r.vat,
       e.empl_surname AS cashier, r.card_number
FROM receipt r
JOIN employee e ON r.id_employee = e.id_employee
WHERE r.check_number = 'R0003';                    -- <param: check number>
--      Query B — the items in that receipt (same as M-RECEIPT-CONTENTS):
SELECT pr.product_name, s.product_number, s.selling_price,
       (s.product_number * s.selling_price) AS line_total
FROM sale s
JOIN store_product sp ON s.upc = sp.upc
JOIN product pr       ON sp.id_product = pr.id_product
WHERE s.check_number = 'R0003';                    -- <param: check number>

-- C12. All promotional products, sorted by quantity (or name).
SELECT sp.upc, p.product_name, sp.selling_price, sp.products_number
FROM store_product sp
JOIN product p ON sp.id_product = p.id_product
WHERE sp.promotional_product = TRUE
ORDER BY sp.products_number;                        -- or: ORDER BY p.product_name

-- C13. All non-promotional products, sorted by quantity (or name).
SELECT sp.upc, p.product_name, sp.selling_price, sp.products_number
FROM store_product sp
JOIN product p ON sp.id_product = p.id_product
WHERE sp.promotional_product = FALSE
ORDER BY sp.products_number;                        -- or: ORDER BY p.product_name

-- C14. By UPC: selling price and quantity in stock.
SELECT upc, selling_price, products_number
FROM store_product
WHERE upc = '001000000001';                         -- <param: upc>

-- C15. The logged-in cashier's own full record.
SELECT *
FROM employee
WHERE id_employee = 'E002';                          -- <param: logged-in employee id>


-- ############################################################
--  SECTION 3 — INSERT (requirement "Введення")
--  New employee / category / product / store product /
--  customer card. (New receipt = Section 6.)
-- ############################################################

-- New category
INSERT INTO category (category_number, category_name)
VALUES (4, 'Snacks');

-- New employee. password_hash must be a bcrypt hash produced by the app
-- (Python: bcrypt.hashpw(...)), never the plain password. The hash below
-- corresponds to the password "zlagoda123".
INSERT INTO employee
    (id_employee, empl_surname, empl_name, empl_patronymic, empl_role,
     salary, date_of_birth, date_of_start, phone_number, city, street, zip_code,
     login, password_hash)
VALUES
    ('E004', 'Koval', 'Petro', 'Ivanovych', 'Cashier',
     14200.00, '1995-04-18', '2024-03-01', '+380504445566', 'Kyiv', 'Sadova 7', '04004',
     'pkoval', '$2b$12$jHKZDHSvya4Ak0LOAIFLXe48lNAfod5E079sHj04oX.fcFGXfxFFy');

-- New product (now includes the producer/manufacturer)
INSERT INTO product (id_product, category_number, product_name, producer, characteristics)
VALUES (5, 4, 'Potato Chips', 'Lays', 'Salted 150g');

-- New store product (regular item)
INSERT INTO store_product
    (upc, upc_prom, id_product, selling_price, products_number, promotional_product)
VALUES ('001000000005', NULL, 5, 28.00, 60, FALSE);

-- New customer card
INSERT INTO customer_card
    (card_number, cust_surname, cust_name, cust_patronymic,
     phone_number, city, street, zip_code, percent)
VALUES ('C003', 'Lysenko', 'Maria', 'Andriivna',
        '+380673334455', 'Kyiv', 'Hrushevskoho 2', '05005', 7);


-- ############################################################
--  SECTION 4 — UPDATE (requirement "Оновлення")
--  Employee / category / product / store product / customer card.
--  Each updates by primary key.
-- ############################################################

UPDATE employee
SET salary = 15000.00, phone_number = '+380509998877'
WHERE id_employee = 'E002';                          -- <param: employee id>

UPDATE category
SET category_name = 'Fresh Dairy'
WHERE category_number = 1;                            -- <param: category number>

UPDATE product
SET product_name = 'Milk 1L (UHT)', characteristics = 'Ultra-pasteurized 2.5%'
WHERE id_product = 1;                                -- <param: product id>

-- Store product: re-pricing one item (the spec's "переоцінка" sets a new price).
UPDATE store_product
SET selling_price = 34.90, products_number = 120
WHERE upc = '001000000001';                          -- <param: upc>

UPDATE customer_card
SET phone_number = '+380671110000', percent = 8
WHERE card_number = 'C001';                          -- <param: card number>


-- ############################################################
--  SECTION 5 — DELETE (requirement "Вилучення")
--  Employee / product / store product / category / receipt /
--  customer card. Each deletes by primary key.
--  NOTE: foreign keys may block a delete (e.g. a category still
--  used by products) — that is the database protecting integrity.
-- ############################################################

DELETE FROM customer_card WHERE card_number = 'C003';   -- <param: card number>
DELETE FROM store_product WHERE upc = '001000000005';   -- <param: upc>
DELETE FROM product       WHERE id_product = 5;          -- <param: product id>
DELETE FROM category      WHERE category_number = 4;     -- <param: category number>
DELETE FROM employee      WHERE id_employee = 'E004';    -- <param: employee id>
-- Deleting a receipt also removes its sale lines (ON DELETE CASCADE on sale).
DELETE FROM receipt       WHERE check_number = 'R0003';  -- <param: check number>


-- ############################################################
--  SECTION 6 — MAKING A SALE (Cashier "create receipt")
--  Several statements that must succeed or fail together, so they
--  are wrapped in a transaction (BEGIN ... COMMIT). If any step
--  fails, ROLLBACK undoes the whole thing — you never get a
--  half-finished receipt.
-- ############################################################

BEGIN;

-- 1) Create the receipt header (sum_total filled in at step 4).
--    vat is NOT listed: it is a generated column the database fills in.
INSERT INTO receipt (check_number, id_employee, card_number, print_date, sum_total)
VALUES ('R0100', 'E002', 'C001', NOW(), 0);           -- <params: check no, cashier, card-or-NULL>

-- 2) Add the purchased items. selling_price is copied from the shelf
--    so the receipt keeps the real price even after a later re-pricing.
INSERT INTO sale (upc, check_number, product_number, selling_price)
SELECT sp.upc, 'R0100', v.qty, sp.selling_price
FROM (VALUES                                           -- <param: list of (upc, quantity)>
        ('001000000001', 2),
        ('001000000003', 1)
     ) AS v(upc, qty)
JOIN store_product sp ON sp.upc = v.upc;

-- 3) Reduce stock by the quantities just sold.
UPDATE store_product sp
SET products_number = sp.products_number - s.product_number
FROM sale s
WHERE s.check_number = 'R0100' AND s.upc = sp.upc;

-- 4) Compute the receipt total from its lines and apply the card discount
--    (if any). We only write sum_total — vat is recomputed automatically
--    by the generated column. The card's percent is resolved inside the
--    subquery so the outer UPDATE only matches on check_number.
UPDATE receipt r
SET sum_total = calc.net
FROM (
    SELECT s.check_number,
           ROUND(SUM(s.product_number * s.selling_price)
                 * (1 - COALESCE(cc.percent, 0) / 100.0), 4) AS net
    FROM sale s
    JOIN receipt rr            ON rr.check_number = s.check_number
    LEFT JOIN customer_card cc ON cc.card_number = rr.card_number
    WHERE s.check_number = 'R0100'                 -- <param: check number>
    GROUP BY s.check_number, cc.percent
) AS calc
WHERE r.check_number = calc.check_number;

COMMIT;
-- If something went wrong instead, you would run:  ROLLBACK;


-- ############################################################
--  SECTION 7 — MAINTENANCE
-- ############################################################

-- Receipt retention: the spec keeps receipts for 3 years. Run this
-- periodically (e.g. a scheduled job / pg_cron) to purge older ones.
-- Their sale lines are removed automatically (ON DELETE CASCADE).
DELETE FROM receipt
WHERE print_date < CURRENT_DATE - INTERVAL '3 years';

-- Changing a password (the hash is produced by the app, not by SQL):
-- UPDATE employee SET password_hash = %s WHERE id_employee = %s;
