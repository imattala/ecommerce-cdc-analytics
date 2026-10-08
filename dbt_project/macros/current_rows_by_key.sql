{% macro current_rows_by_key(relation, key_column, order_column='_cdc_source_ts') %}

{#
  Collapses a CDC event log (every insert/update/delete, append-only) down
  to the latest row per key reflecting live source state - the one
  genuinely new dbt-on-CDC pattern this project demonstrates. Excludes
  keys whose latest event is a delete, since those no longer exist in the
  source.
#}

with ranked as (

    select
        *,
        row_number() over (
            partition by {{ key_column }}
            order by {{ order_column }} desc
        ) as _rn

    from {{ relation }}

)

select * except (_rn)
from ranked
where _rn = 1 and _cdc_op != 'd'

{% endmacro %}
