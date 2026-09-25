-- Story data for the Databricks App: 18-month retention trend + proven-campaign ROI (treated vs control holdout).
-- STORY 1: 18-month retention/lapse trend (dip during rate hardening, recovery once proactive retention starts)
CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.gold_retention_trend AS
WITH m AS (SELECT explode(sequence(0,17)) AS k)
SELECT
  date_format(add_months(date_trunc('MONTH', current_date()), -k), 'yyyy-MM') AS month,
  add_months(date_trunc('MONTH', current_date()), -k) AS month_start,
  cast(380 + floor(rand()*90) AS int) AS policies_up_for_renewal,
  -- retention dips mid-period (rate hardening) then recovers in recent months
  round( CASE
     WHEN k >= 12 THEN 0.865 - (rand()*0.015)
     WHEN k BETWEEN 5 AND 11 THEN 0.795 + (11-k)*0.004 + (rand()*0.02 - 0.01)
     ELSE 0.845 + (5-k)*0.010 + (rand()*0.015)   -- recent proactive lift
   END, 3) AS retention_rate
FROM m;
---GO---
-- derive counts + premium from the rate
CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.gold_retention_trend AS
SELECT month, month_start, policies_up_for_renewal, retention_rate,
  cast(round(policies_up_for_renewal*retention_rate) AS int) AS renewed,
  cast(policies_up_for_renewal - round(policies_up_for_renewal*retention_rate) AS int) AS lapsed,
  round(policies_up_for_renewal*retention_rate*2230, 0) AS premium_retained,
  round((policies_up_for_renewal-policies_up_for_renewal*retention_rate)*2230, 0) AS premium_lost
FROM sunmin_catalog.insurance_demo.gold_retention_trend;
---GO---
SELECT month, retention_rate, renewed, lapsed, premium_lost FROM sunmin_catalog.insurance_demo.gold_retention_trend ORDER BY month_start DESC LIMIT 4;
---GO---
-- STORY 4: proven-campaign ROI — treated (proactive outreach) vs control holdout on the high-risk cohort
CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.gold_campaign_outcomes AS
SELECT * FROM VALUES
  ('Treated (proactive Retention Copilot outreach)', 490, 270, 0.551, 602140),
  ('Control (holdout — no outreach)',                164,  51, 0.311,  113730)
  AS t(cohort, policyholders, renewals_saved, save_rate, premium_recovered);
---GO---
SELECT * FROM sunmin_catalog.insurance_demo.gold_campaign_outcomes;
