select
    product_id,
    name,
    category,
    price,
    created_at,
    updated_at
from {{ ref('int_products_current') }}
