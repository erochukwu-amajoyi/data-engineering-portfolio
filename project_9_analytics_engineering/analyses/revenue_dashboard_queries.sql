-- Daily revenue trend
select
    order_date,
    order_count,
    units_sold,
    revenue,
    average_order_value
from {{ ref('mart_daily_revenue') }}
order by order_date;

-- Highest-value customers
select
    customer_name,
    segment,
    order_count,
    lifetime_revenue,
    average_order_value,
    value_band
from {{ ref('mart_customer_lifetime_value') }}
order by lifetime_revenue desc;

-- Product performance
select
    product_name,
    category,
    units_sold,
    product_revenue
from {{ ref('dim_products') }}
order by product_revenue desc;
