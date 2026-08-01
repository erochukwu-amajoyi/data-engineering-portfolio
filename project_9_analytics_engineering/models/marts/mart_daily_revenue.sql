{{ config(materialized='table') }}

select
    order_date,
    count(distinct order_id) as order_count,
    sum(total_units) as units_sold,
    round(sum(order_revenue), 2) as revenue,
    round(avg(order_revenue), 2) as average_order_value
from {{ ref('fct_orders') }}
group by order_date
