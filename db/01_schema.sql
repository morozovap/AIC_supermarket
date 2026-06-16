-- ZLAGODA database schema (DDL)

CREATE TABLE category (
    category_number INTEGER       PRIMARY KEY,
    category_name   VARCHAR(50)   NOT NULL
);

CREATE TABLE employee (
    id_employee     VARCHAR(10)   PRIMARY KEY,
    empl_surname    VARCHAR(50)   NOT NULL,
    empl_name       VARCHAR(50)   NOT NULL,
    empl_patronymic VARCHAR(50),
    empl_role       VARCHAR(10)   NOT NULL,
    salary          DECIMAL(13,4) NOT NULL CHECK (salary >= 0),
    date_of_birth   DATE          NOT NULL,
    date_of_start   DATE          NOT NULL,
    phone_number    VARCHAR(13)   NOT NULL,
    city            VARCHAR(50)   NOT NULL,
    street          VARCHAR(50)   NOT NULL,
    zip_code        VARCHAR(9)    NOT NULL,
    login           VARCHAR(50)   UNIQUE NOT NULL,
    -- bcrypt hash is always 60 chars
    password_hash   VARCHAR(60)   NOT NULL,
    CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '18 years'),
    CHECK (empl_role IN ('Manager', 'Cashier'))
);

CREATE TABLE customer_card (
    card_number     VARCHAR(13)   PRIMARY KEY,
    cust_surname    VARCHAR(50)   NOT NULL,
    cust_name       VARCHAR(50)   NOT NULL,
    cust_patronymic VARCHAR(50),
    phone_number    VARCHAR(13)   NOT NULL,
    city            VARCHAR(50),
    street          VARCHAR(50),
    zip_code        VARCHAR(9),
    percent         INTEGER       NOT NULL CHECK (percent >= 0 AND percent <= 100)
);

CREATE TABLE product (
    id_product      INTEGER       PRIMARY KEY,
    category_number INTEGER       NOT NULL
                    REFERENCES category(category_number)
                    ON UPDATE CASCADE ON DELETE NO ACTION,
    product_name    VARCHAR(50)   NOT NULL,
    producer        VARCHAR(50)   NOT NULL,
    characteristics VARCHAR(100)  NOT NULL
);

CREATE TABLE store_product (
    upc                 VARCHAR(12)   PRIMARY KEY,
    upc_prom            VARCHAR(12)
                        REFERENCES store_product(upc)
                        ON UPDATE CASCADE ON DELETE SET NULL,
    id_product          INTEGER       NOT NULL
                        REFERENCES product(id_product)
                        ON UPDATE CASCADE ON DELETE NO ACTION,
    selling_price       DECIMAL(13,4) NOT NULL CHECK (selling_price >= 0),
    products_number     INTEGER       NOT NULL CHECK (products_number >= 0),
    promotional_product BOOLEAN       NOT NULL
);

-- At most one regular and one promotional store-product per product.
CREATE UNIQUE INDEX uq_one_regular_per_product
    ON store_product (id_product) WHERE promotional_product = FALSE;
CREATE UNIQUE INDEX uq_one_promo_per_product
    ON store_product (id_product) WHERE promotional_product = TRUE;

-- A promotional item is always priced at 80% of its regular twin.
CREATE OR REPLACE FUNCTION set_promo_price() RETURNS TRIGGER AS $func$
BEGIN
    IF NEW.promotional_product AND NEW.upc_prom IS NOT NULL THEN
        SELECT ROUND(selling_price * 0.8, 4) INTO NEW.selling_price
        FROM store_product WHERE upc = NEW.upc_prom;
    END IF;
    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

CREATE TRIGGER trg_promo_price
    BEFORE INSERT OR UPDATE ON store_product
    FOR EACH ROW EXECUTE FUNCTION set_promo_price();

CREATE TABLE receipt (
    check_number  VARCHAR(10)   PRIMARY KEY,
    id_employee   VARCHAR(10)   NOT NULL
                  REFERENCES employee(id_employee)
                  ON UPDATE CASCADE ON DELETE NO ACTION,
    card_number   VARCHAR(13)
                  REFERENCES customer_card(card_number)
                  ON UPDATE CASCADE ON DELETE NO ACTION,
    print_date    TIMESTAMP     NOT NULL,
    sum_total     DECIMAL(13,4) NOT NULL CHECK (sum_total >= 0),
    -- VAT is always 20% of sum_total, computed by the database
    vat           DECIMAL(13,4) GENERATED ALWAYS AS (ROUND(sum_total * 0.2, 4)) STORED
);

CREATE TABLE sale (
    upc            VARCHAR(12)   NOT NULL
                   REFERENCES store_product(upc)
                   ON UPDATE CASCADE ON DELETE NO ACTION,
    check_number   VARCHAR(10)   NOT NULL
                   REFERENCES receipt(check_number)
                   ON UPDATE CASCADE ON DELETE CASCADE,
    product_number INTEGER       NOT NULL CHECK (product_number > 0),
    selling_price  DECIMAL(13,4) NOT NULL CHECK (selling_price >= 0),
    PRIMARY KEY (upc, check_number)
);
