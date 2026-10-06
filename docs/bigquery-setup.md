# One-time GCP / BigQuery setup

This project's M2 onward writes to BigQuery, so before starting M2 you need
a Google Cloud project with billing enabled (see "Why billing is needed"
below) and local auth configured. This is a one-time setup, not something
that can be scripted into `docker compose up`.

## 1. Create a project and enable billing

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and
   create a new project (e.g. `ecommerce-cdc-analytics`).
2. Link a billing account. New accounts get a free trial credit (~$300,
   good for 90 days) — BigQuery usage for a project this small (a handful
   of tiny tables, dbt runs a few times a week) will stay well under a
   dollar even without the trial credit. GCP does **not** auto-charge once
   the trial ends or the credit runs out; it just stops letting you use
   paid features until you explicitly upgrade.
3. **Recommended:** set a budget alert (Billing → Budgets & alerts) for a
   low threshold (e.g. $5) so you get an email if anything unexpected
   happens — effectively free peace of mind.

### Why billing is needed (not just the free sandbox)

A GCP project *without* billing linked runs BigQuery in **Sandbox mode**,
which blocks **all DML** (`INSERT`, `UPDATE`, `DELETE`, `MERGE`) and
streaming inserts — only `CREATE TABLE AS SELECT` / `CREATE VIEW`-style DDL
works. That's enough for M3/M4's table/view models, but dbt's `snapshot`
feature (M5) generates `MERGE` statements to maintain history, so it can't
run in Sandbox mode at all. Enabling billing removes this restriction.

## 2. Enable the BigQuery API

In the Cloud Console: APIs & Services → Library → search "BigQuery API" →
Enable. (Usually already enabled by default for new projects, but check.)

## 3. Install the gcloud CLI

```bash
sudo apt-get install apt-transport-https ca-certificates gnupg curl
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install google-cloud-cli
```

## 4. Authenticate

```bash
gcloud init                                  # pick/create the project interactively
gcloud auth application-default login        # local dev credentials, no service account key to manage
```

## 5. Verify

```bash
bq ls --project_id=<YOUR_PROJECT_ID>
```

An empty (but non-error) dataset list confirms the project, API, and auth
are all working. Ready for M2.
