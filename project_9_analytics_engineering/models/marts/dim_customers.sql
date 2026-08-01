{{ config(materialized='table') }}

select
    customers.customer_id,
    customers.customer_name,
    customers.segment,
    customers.country,
    customers.signup_date,
    min(enriched.order_date) as first_order_date,
    max(enriched.order_date) as most_recent_order_date,
    count(distinct enriched.order_id) as order_count,
    coalesce(round(sum(enriched.gross_revenue), 2), 0) as lifetime_revenue,
    case
        when count(distinct enriched.order_id) > 1 then 1
        else 0
    end as is_repeat_customer
from {{ ref('stg_customers') }} as customers
left join {{ ref('int_order_items_enriched') }} as enriched
    on customers.customer_id = enriched.customer_id
group by
    customers.customer_id,
    customers.customer_name,
    customers.segment,
    customers.country,
    customers.signup_date
