#!/bin/sh
set -e

CONNECT_URL="http://kafka-connect:8083"

until curl -sf "$CONNECT_URL/connectors" > /dev/null; do
  echo "Waiting for Kafka Connect REST API..."
  sleep 5
done

echo "Registering ecommerce-postgres-connector..."
curl -s -X PUT "$CONNECT_URL/connectors/ecommerce-postgres-connector/config" \
  -H "Content-Type: application/json" \
  -d @/config/postgres-connector.json

echo
echo "Done."
