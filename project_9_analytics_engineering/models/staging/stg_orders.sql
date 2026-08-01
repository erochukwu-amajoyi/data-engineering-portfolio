{{ config(materialized='view') }}

select
    cast(order_id as integer) as order_id,
    cast(customer_id as integer) as customer_id,
    cast(product_id as integer) as product_id,
    order_date,
    cast(quantity as integer) as quantity,
    cast(coalesce(unit_discount, 0) as real) as unit_discount
from {{ ref('raw_orders') }}
where order_id is not null
