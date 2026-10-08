select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    _cdc_op,
    timestamp_millis(_cdc_source_ts_ms) as _cdc_source_ts,
    _cdc_loaded_at
from {{ source('ecommerce_raw', 'order_items') }}
