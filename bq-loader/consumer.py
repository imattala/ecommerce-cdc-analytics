"""Reads Debezium CDC events from Kafka and micro-batch loads them into
BigQuery raw_* tables (one per source table), preserving the CDC operation
type and source timestamp so downstream dbt models can reconstruct history.

Append-only, at-least-once: on a crash between a BigQuery load and the
Kafka offset commit, some rows may be reloaded on restart. That's fine for
a raw landing log - dbt's intermediate layer already needs "latest row per
key wins" logic regardless of whether the raw log has occasional dupes.
"""
import json
import os
import time
from datetime import datetime, timezone

from confluent_kafka import Consumer
from google.cloud import bigquery

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
TOPIC_PREFIX = os.environ.get("TOPIC_PREFIX", "ecommerce")
TABLES = os.environ.get("TABLES", "customers,products,orders,order_items").split(",")
GCP_PROJECT = os.environ["GCP_PROJECT"]
BQ_DATASET = os.environ.get("BQ_DATASET", "ecommerce_raw")
BATCH_INTERVAL_SECONDS = float(os.environ.get("BATCH_INTERVAL_SECONDS", "10"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "500"))

TOPICS = [f"{TOPIC_PREFIX}.public.{table}" for table in TABLES]


def table_name_from_topic(topic: str) -> str:
    return topic.split(".")[-1]


def build_row(event: dict) -> dict | None:
    op = event.get("op")
    source = event.get("source", {})
    base = event.get("before") if op == "d" else event.get("after")
    if base is None:
        return None
    return {
        **base,
        "_cdc_op": op,
        "_cdc_source_ts_ms": source.get("ts_ms"),
        "_cdc_loaded_at": datetime.now(timezone.utc).isoformat(),
    }


def ensure_dataset(client: bigquery.Client):
    client.create_dataset(bigquery.Dataset(f"{client.project}.{BQ_DATASET}"), exists_ok=True)


def flush_table(client: bigquery.Client, table: str, rows: list[dict]):
    table_ref = f"{client.project}.{BQ_DATASET}.{table}"
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    job = client.load_table_from_json(rows, table_ref, job_config=job_config)
    job.result()
    print(f"[loaded] {table}: {len(rows)} rows")


def main():
    client = bigquery.Client(project=GCP_PROJECT)
    ensure_dataset(client)

    consumer = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "bq-loader",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })
    consumer.subscribe(TOPICS)
    print(f"Subscribed to {TOPICS}")

    buffers: dict[str, list[dict]] = {table: [] for table in TABLES}
    last_flush = time.monotonic()

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is not None and not msg.error():
                value = msg.value()
                if value is not None:  # skip Debezium's delete tombstones
                    event = json.loads(value)
                    table = table_name_from_topic(msg.topic())
                    row = build_row(event)
                    if row is not None:
                        buffers[table].append(row)

            due_by_time = time.monotonic() - last_flush >= BATCH_INTERVAL_SECONDS
            due_by_size = any(len(rows) >= BATCH_SIZE for rows in buffers.values())
            if due_by_time or due_by_size:
                for table, rows in buffers.items():
                    if rows:
                        flush_table(client, table, rows)
                        buffers[table] = []
                consumer.commit()
                last_flush = time.monotonic()
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
