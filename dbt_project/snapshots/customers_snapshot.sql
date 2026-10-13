{% snapshot customers_snapshot %}

{{
    config(
      target_schema='ecommerce_dbt_snapshots',
      unique_key='customer_id',
      strategy='timestamp',
      updated_at='updated_at',
      invalidate_hard_deletes=true,
    )
}}

select * from {{ ref('int_customers_current') }}

{% endsnapshot %}
