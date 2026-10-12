with order_item_totals as (

    select
        order_id,
        count(*) as item_count,
        sum(quantity * unit_price) as total_amount

    from {{ ref('int_order_items_current') }}
    group by order_id

)

select
    orders.order_id,
    orders.customer_id,
    orders.order_status,
    orders.order_date,
    orders.updated_at,
    coalesce(totals.item_count, 0) as item_count,
    coalesce(totals.total_amount, 0) as total_amount

from {{ ref('int_orders_current') }} as orders
left join order_item_totals as totals
    on orders.order_id = totals.order_id
