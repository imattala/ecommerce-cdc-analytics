select
    customer_id,
    first_name,
    last_name,
    email,
    address,
    created_at,
    updated_at
from {{ ref('int_customers_current') }}
