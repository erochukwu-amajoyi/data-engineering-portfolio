{{ config(materialized='table') }}

select
    order_id,
    customer_id,
    order_date,
    count(*) as line_count,
    sum(quantity) as total_units,
    round(sum(gross_revenue), 2) as order_revenue
from {{ ref('int_order_items_enriched') }}
group by
    order_id,
    customer_id,
    order_date
