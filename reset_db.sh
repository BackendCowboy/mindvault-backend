#!/bin/bash

echo "🚨 WARNING: This will erase all data in your Postgres DB."
read -p "Are you sure? (y/N): " confirm

if [[ $confirm != "y" ]]; then
  echo "❌ Cancelled"
  exit 1
fi

echo "🔄 Dropping and recreating public schema..."
docker exec -i mindvault-db psql -U mindvault_user -d mindvault_db <<'SQL'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
SQL

echo "📌 Stamping Alembic to current revision..."
docker exec -it mindvault-api sh -c "alembic stamp head"

echo "⏫ Running Alembic migrations..."
docker exec -it mindvault-api sh -c "alembic upgrade head"

echo "✅ Database reset complete."