-- Optional: database-level role enforcement. Run manually after schema exists:
--   docker exec -it zlagoda_db psql -U zlagoda_admin -d zlagoda -f /path/optional_roles.sql

CREATE ROLE manager_role;
CREATE ROLE cashier_role;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO manager_role;

GRANT SELECT ON category, product, store_product, customer_card, receipt, sale, employee
    TO cashier_role;
GRANT INSERT ON receipt, sale            TO cashier_role;
GRANT INSERT, UPDATE ON customer_card    TO cashier_role;
GRANT UPDATE (products_number) ON store_product TO cashier_role;

-- Create real login users and assign roles (replace passwords):
-- CREATE USER manager_anna  LOGIN PASSWORD 'set-me';
-- CREATE USER cashier_ihor  LOGIN PASSWORD 'set-me';
-- GRANT manager_role TO manager_anna;
-- GRANT cashier_role TO cashier_ihor;
