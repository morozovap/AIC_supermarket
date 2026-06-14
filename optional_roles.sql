-- ============================================================
--  ZLAGODA  —  optional_roles.sql   (OPTIONAL, run manually)
--
--  Demonstrates role enforcement at the DATABASE level. This is a
--  bonus: in your Flask app the primary enforcement happens in code
--  (the logged-in user's role decides which routes/queries run). Some
--  graders like to also see it in the database, which this file shows.
--
--  Run it once, by hand, AFTER the schema exists:
--    docker exec -it zlagoda_db psql -U zlagoda_admin -d zlagoda -f /path/optional_roles.sql
--  (It is deliberately NOT in the db/ auto-init folder.)
-- ============================================================

-- Two group roles, mirroring the two user types.
CREATE ROLE manager_role;
CREATE ROLE cashier_role;

-- MANAGER: full control over all data.
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO manager_role;

-- CASHIER: can read the catalogue and customers, create sales, and
-- add/update customer cards — but cannot touch employees, products,
-- categories, or delete anything.
GRANT SELECT ON category, product, store_product, customer_card, receipt, sale, employee
    TO cashier_role;
GRANT INSERT ON receipt, sale            TO cashier_role;   -- create receipts
GRANT INSERT, UPDATE ON customer_card    TO cashier_role;   -- manage loyalty cards
GRANT UPDATE (products_number) ON store_product TO cashier_role;  -- only adjust stock

-- Create real login users and put them in a role. Replace the passwords.
-- CREATE USER manager_anna  LOGIN PASSWORD 'set-me';
-- CREATE USER cashier_ihor  LOGIN PASSWORD 'set-me';
-- GRANT manager_role TO manager_anna;
-- GRANT cashier_role TO cashier_ihor;

-- After this, a cashier user trying  DELETE FROM employee ...  is refused
-- by PostgreSQL itself, on top of whatever the application enforces.
