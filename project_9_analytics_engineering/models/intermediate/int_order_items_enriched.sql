{{ config(materialized='view') }}

select
    orders.order_id,
    orders.customer_id,
    customers.customer_name,
    customers.segment,
    customers.country,
    orders.product_id,
    products.product_name,
    products.category,
    orders.order_date,
    orders.quantity,
    products.unit_price,
    orders.unit_discount,
    round((orders.quantity * products.unit_price) - orders.unit_discount, 2) as gross_revenue
from {{ ref('stg_orders') }} as orders
inner join {{ ref('stg_customers') }} as customers
    on orders.customer_id = customers.customer_id
inner join {{ ref('stg_products') }} as products
    on orders.product_id = products.product_id
