select
    product_id,
    name,
    category,
    price,
    timestamp_micros(created_at) as created_at,
    timestamp_micros(updated_at) as updated_at,
    _cdc_op,
    timestamp_millis(_cdc_source_ts_ms) as _cdc_source_ts,
    _cdc_loaded_at
from {{ source('ecommerce_raw', 'products') }}
