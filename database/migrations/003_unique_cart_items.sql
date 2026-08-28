-- Collapse legacy duplicate cart rows before enforcing one row per user/product.
WITH totals AS (
    SELECT user_id, product_id, MIN(id) AS keep_id, SUM(quantity) AS total_quantity
    FROM cart_items
    GROUP BY user_id, product_id
    HAVING COUNT(*) > 1
)
UPDATE cart_items AS item
SET quantity = totals.total_quantity
FROM totals
WHERE item.id = totals.keep_id;

WITH duplicates AS (
    SELECT id,
           ROW_NUMBER() OVER (
               PARTITION BY user_id, product_id
               ORDER BY id
           ) AS row_number
    FROM cart_items
)
DELETE FROM cart_items
WHERE id IN (SELECT id FROM duplicates WHERE row_number > 1);

CREATE UNIQUE INDEX IF NOT EXISTS uq_cart_items_user_product
    ON cart_items (user_id, product_id);
