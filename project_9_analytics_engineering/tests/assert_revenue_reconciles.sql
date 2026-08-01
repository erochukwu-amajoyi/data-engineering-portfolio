select
    fact_revenue,
    enriched_revenue
from (
    select
        round((select sum(order_revenue) from {{ ref('fct_orders') }}), 2) as fact_revenue,
        round((select sum(gross_revenue) from {{ ref('int_order_items_enriched') }}), 2) as enriched_revenue
) as reconciliation
where fact_revenue != enriched_revenue
