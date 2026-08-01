{{ config(materialized='table') }}

select
    customer_id,
    customer_name,
    segment,
    order_count,
    lifetime_revenue,
    case
        when order_count = 0 then 0
        else round(lifetime_revenue / order_count, 2)
    end as average_order_value,
    case
        when lifetime_revenue >= 600 then 'high_value'
        when lifetime_revenue >= 300 then 'mid_value'
        else 'low_value'
    end as value_band
from {{ ref('dim_customers') }}
