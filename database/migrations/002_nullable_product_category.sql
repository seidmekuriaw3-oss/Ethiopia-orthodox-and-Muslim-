-- Align existing installations with fk_products_category ON DELETE SET NULL.
ALTER TABLE products ALTER COLUMN category_id DROP NOT NULL;

ALTER TABLE products DROP CONSTRAINT IF EXISTS fk_products_category;
ALTER TABLE products
    ADD CONSTRAINT fk_products_category
    FOREIGN KEY (category_id) REFERENCES categories(id)
    ON DELETE SET NULL;
