# dbt project

Transforms the CDC event log landed in `ecommerce_raw.*` (see `bq-loader/`)
into clean, current-state tables.

- `models/staging/` — typed/cleaned pass-through of the raw CDC columns
  (Debezium's microsecond-epoch timestamps cast to real `TIMESTAMP`s)
- `models/intermediate/` — collapses the CDC log into "current row per
  primary key", via the `current_rows_by_key()` macro
  (`macros/current_rows_by_key.sql`): rank events per key by CDC source
  timestamp, keep the latest, and drop keys whose latest event is a delete

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install dbt-bigquery
```

## Run

Requires the same GCP auth as `bq-loader` (`gcloud auth application-default
login`) and `GCP_PROJECT_ID` set in the environment (or exported from the
repo root's `.env`).

```bash
cd dbt_project
export GCP_PROJECT_ID=<your project id>
.venv/bin/dbt run --profiles-dir .
.venv/bin/dbt test --profiles-dir .   # once tests land in M4
```

(`--profiles-dir .` points dbt at this directory's `profiles.yml` instead
of the usual `~/.dbt/profiles.yml`, so the whole project stays self
contained.)
