{{ config(materialized='view') }}

select
    cast(customer_id as integer) as customer_id,
    customer_name,
    segment,
    signup_date,
    country
from {{ ref('raw_customers') }}
where customer_id is not null
