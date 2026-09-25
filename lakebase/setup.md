# Lakebase (operational serving) — setup

Provisioned Lakebase Postgres behind the Retention Command Center app. Two-way store:
the high-risk **worklist** is synced Delta→Postgres (read side); agent **dispositions** are
native Postgres OLTP writes.

## 1. Provision the instance

```bash
databricks api post /api/2.0/database/instances --profile azure-sunmin \
  --json '{"name":"insurance-febar-lakebase","capacity":"CU_1"}'
```

## 2. Serving worklist table in UC (with a primary key, for the synced table)

```sql
CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.gold_agent_worklist AS
SELECT policyholder_id, first_name, last_name, state, product_line,
       round(churn_probability,4) AS churn_probability, risk_tier,
       round(premium_at_risk,2)  AS premium_at_risk,
       premium_change_pct, num_complaints, num_denied_claims, num_cancel_intent, retention_brief
FROM sunmin_catalog.insurance_demo.gold_retention_copilot;

ALTER TABLE sunmin_catalog.insurance_demo.gold_agent_worklist ALTER COLUMN policyholder_id SET NOT NULL;
ALTER TABLE sunmin_catalog.insurance_demo.gold_agent_worklist ADD CONSTRAINT pk_agent_worklist PRIMARY KEY (policyholder_id);
```

## 3. Register a UC database catalog + create the synced table (reverse ETL)

```bash
databricks database create-database-catalog insurance_lakebase insurance-febar-lakebase databricks_postgres \
  --create-database-if-not-exists --profile azure-sunmin

databricks database create-synced-database-table --profile azure-sunmin --json '{
  "name": "insurance_lakebase.public.agent_worklist",
  "database_instance_name": "insurance-febar-lakebase",
  "logical_database_name": "databricks_postgres",
  "spec": {
    "source_table_full_name": "sunmin_catalog.insurance_demo.gold_agent_worklist",
    "primary_key_columns": ["policyholder_id"],
    "scheduling_policy": "SNAPSHOT",
    "create_database_objects_if_missing": true
  }
}'
```

## 4. Native OLTP table for agent dispositions (write side)

```sql
-- via: databricks psql insurance-febar-lakebase --profile azure-sunmin
CREATE SCHEMA IF NOT EXISTS retention;
CREATE TABLE IF NOT EXISTS retention.case_dispositions (
    disposition_id  BIGSERIAL PRIMARY KEY,
    policyholder_id TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'open',   -- open | in_progress | saved | lost
    assigned_agent  TEXT,
    outcome         TEXT,                            -- discount_applied, callback_scheduled, ...
    notes           TEXT,
    contacted_at    TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_disp_ph     ON retention.case_dispositions(policyholder_id);
CREATE INDEX IF NOT EXISTS idx_disp_status ON retention.case_dispositions(status);
```

## 5. Grant the app service principal (role = SP client id) after the app has the db resource

```sql
GRANT USAGE ON SCHEMA retention TO "<app-sp-client-id>";
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA retention TO "<app-sp-client-id>";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA retention TO "<app-sp-client-id>";
GRANT USAGE ON SCHEMA public TO "<app-sp-client-id>";
GRANT SELECT ON public.agent_worklist TO "<app-sp-client-id>";
```
