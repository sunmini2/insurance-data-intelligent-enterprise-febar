# Evidence — Stage 4: Lakebase (operational serving)

**Instance:** `insurance-febar-lakebase` (Provisioned, CU_1) · PostgreSQL 16.15
**DNS:** `ep-orange-base-e1jzzgfv.database.eastus2.azuredatabricks.net`
**UC database catalog:** `insurance_lakebase` → logical db `databricks_postgres`

Two-way operational store behind the Retention Command Center app:

- **Read side** — `public.agent_worklist`: the 666 high-risk cases + GenAI briefs, kept in
  sync from Delta gold (`gold_agent_worklist`) by a Databricks **synced table** (reverse ETL,
  SNAPSHOT policy, pipeline `ae520a31-f07e-4dc4-9e5b-d0eb9091ca68`).
- **Write side** — `retention.case_dispositions`: native Postgres OLTP table where retention
  agents claim a case, set status, log the outcome + notes (low-latency writes the app makes).

## Synced table came ONLINE

```
SYNCED_TABLE_PROVISIONING_PIPELINE_RESOURCES
SYNCED_TABLE_PROVISIONING_INITIAL_SNAPSHOT
SYNCED_TABLE_ONLINE_NO_PENDING_UPDATE     <-- initial snapshot complete
```

## Read side — worklist served from Postgres (psql)

```
 worklist_rows | prem_at_risk_m
---------------+----------------
           666 |           1.64

 policyholder_id | first_name | last_name | state | product_line | churn_prob | premium_at_risk
-----------------+------------+-----------+-------+--------------+------------+-----------------
 PH0100255       | Thomas     | Perez     | AZ    | Life         |      0.987 |         2802.69
 PH0101882       | Thomas     | Brown     | MA    | Life         |      0.980 |         1599.31
 PH0104799       | Daniel     | Smith     | WA    | Auto         |      0.975 |         2729.36
 PH0104142       | Betty      | Wilson    | MA    | Umbrella     |      0.973 |         2365.82
 PH0101600       | Sandra     | Robinson  | GA    | Auto         |      0.970 |         4634.34
```

## Write side — OLTP disposition write + read-back (psql)

```sql
CREATE TABLE retention.case_dispositions (
    disposition_id BIGSERIAL PRIMARY KEY, policyholder_id TEXT NOT NULL,
    status TEXT DEFAULT 'open', assigned_agent TEXT, outcome TEXT, notes TEXT,
    contacted_at TIMESTAMPTZ, updated_at TIMESTAMPTZ DEFAULT now());

INSERT INTO retention.case_dispositions (policyholder_id,status,assigned_agent,outcome,notes,contacted_at)
VALUES ('PH0100001','saved','sunmin.lee','discount_applied','Applied 8% loyalty discount; customer renewed on the call.', now());
```
```
 disposition_id | policyholder_id | status | assigned_agent |     outcome
----------------+-----------------+--------+----------------+------------------
              1 | PH0100001       | saved  | sunmin.lee     | discount_applied
```

## Two-way join served to the app (worklist ⨝ dispositions)

```
 policyholder_id | first_name | last_name | churn_prob | status | outcome | assigned_agent
-----------------+------------+-----------+------------+--------+---------+----------------
 PH0100255       | Thomas     | Perez     |      0.987 |        |         |
 PH0101882       | Thomas     | Brown     |      0.980 |        |         |
 ...
```

The app reads the synced worklist and writes dispositions back to Postgres in the same
request — a real operational (OLTP) loop on top of the governed analytical gold layer.
