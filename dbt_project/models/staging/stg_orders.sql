select
    order_id,
    customer_id,
    order_status,
    timestamp_micros(order_date) as order_date,
    timestamp_micros(updated_at) as updated_at,
    _cdc_op,
    timestamp_millis(_cdc_source_ts_ms) as _cdc_source_ts,
    _cdc_loaded_at
from {{ source('ecommerce_raw', 'orders') }}
