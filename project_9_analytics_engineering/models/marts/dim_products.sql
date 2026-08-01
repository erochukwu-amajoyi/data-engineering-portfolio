{{ config(materialized='table') }}

select
    products.product_id,
    products.product_name,
    products.category,
    products.unit_price,
    coalesce(sum(enriched.quantity), 0) as units_sold,
    coalesce(round(sum(enriched.gross_revenue), 2), 0) as product_revenue
from {{ ref('stg_products') }} as products
left join {{ ref('int_order_items_enriched') }} as enriched
    on products.product_id = enriched.product_id
group by
    products.product_id,
    products.product_name,
    products.category,
    products.unit_price
