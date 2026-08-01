{{ config(materialized='view') }}

select
    cast(product_id as integer) as product_id,
    product_name,
    category,
    cast(unit_price as real) as unit_price
from {{ ref('raw_products') }}
where product_id is not null
