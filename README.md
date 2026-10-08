# ecommerce-cdc-analytics

![Postgres](https://img.shields.io/badge/Postgres-CDC-336791?logo=postgresql&logoColor=white)
![Debezium](https://img.shields.io/badge/Debezium-CDC-red)
![Kafka](https://img.shields.io/badge/Kafka-KRaft-231F20?logo=apachekafka&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-BigQuery-FF694B?logo=dbt&logoColor=white)
![BigQuery](https://img.shields.io/badge/Google-BigQuery-4285F4?logo=googlebigquery&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Change data capture from a synthetic e-commerce Postgres database, through
Kafka/Debezium, into BigQuery, transformed with dbt (staging → intermediate
→ marts, with snapshots for slowly-changing dimension history).

Built as a portfolio project, one milestone at a time. See open issues/PRs
for progress.

## Architecture

```
Postgres (OLTP: customers, products, orders, order_items)
        │  WAL / logical replication
        ▼
Debezium Postgres connector (Kafka Connect)
        │  per-table CDC topics, JSON
        ▼
   Kafka (KRaft mode)
        │
        ▼
Python CDC→BigQuery loader (micro-batch consumer, append-only)
        │  raw_* tables: full CDC event log (op type + source ts preserved)
        ▼
  BigQuery (sandbox project)
     staging models (dbt) — typed/cleaned
        │
     intermediate models — collapse CDC log to current-row-per-key
     dbt snapshots — slowly-changing dimension history (customers/products)
        │
     marts — fact_orders, dim_customers, dim_products + dbt tests
```

## Status

Work in progress — see the [issues](../../issues) for the milestone breakdown.

- [x] M1 — CDC ingest: Postgres + Debezium + Kafka
- [x] M2 — Land in BigQuery
- [x] M3 — dbt staging + intermediate
- [ ] M4 — dbt marts + tests
- [ ] M5 — SCD history (dbt snapshots)
- [ ] M6 — Polish

## Running it

**Prerequisites:** Docker + Docker Compose for the CDC half (Postgres,
Kafka, Debezium). From M2 onward, a Google Cloud project with billing
enabled and the BigQuery API on — see
[docs/bigquery-setup.md](docs/bigquery-setup.md) (billing is required, not
just the free sandbox — dbt snapshots in M5 need DML, which Sandbox mode
blocks entirely; realistic usage at this project's scale stays well under
the free trial credit either way). Once that's done:

```
cp .env.example .env     # fill in GCP_PROJECT_ID
gcloud auth application-default login
docker compose up -d --build
```

`bq-loader` mounts your local Application Default Credentials
(`~/.config/gcloud/application_default_credentials.json`) read-only into
the container — no service account key to manage.

dbt transformations run separately against BigQuery (not inside
docker-compose) — see [dbt_project/](dbt_project/README.md).

Stop everything with:

```
docker compose down
```

### Local UIs

| Service          | URL                              |
|-------------------|-----------------------------------|
| Kafka UI (Kafbat)  | http://localhost:8085            |
| Kafka Connect REST | http://localhost:8083/connectors |

## License

MIT
