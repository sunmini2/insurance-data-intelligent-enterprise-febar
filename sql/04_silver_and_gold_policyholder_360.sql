-- Layer 1 (Silver + Gold): conform the 3 sources on policyholder_id and build the unified Policyholder 360.
-- Silver aggregates:
CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.silver_claims_agg AS
SELECT policyholder_id,
  count(*) AS num_claims,
  round(sum(claim_amount),2) AS total_claim_amount,
  sum(CASE WHEN claim_status='denied' THEN 1 ELSE 0 END) AS num_denied_claims,
  sum(CASE WHEN claim_status='open' THEN 1 ELSE 0 END) AS num_open_claims,
  round(avg(days_to_settle),1) AS avg_days_to_settle,
  max(claim_date) AS last_claim_date
FROM sunmin_catalog.insurance_demo.bronze_claims GROUP BY policyholder_id;
---GO---
CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.silver_interactions_agg AS
SELECT policyholder_id,
  count(*) AS num_interactions,
  sum(cast(complaint_flag AS int)) AS num_complaints,
  round(avg(sentiment_score),3) AS avg_sentiment,
  sum(CASE WHEN reason='Cancellation / Shopping Competitor' THEN 1 ELSE 0 END) AS num_cancel_intent,
  sum(CASE WHEN reason='Billing / Premium Increase' THEN 1 ELSE 0 END) AS num_billing_contacts,
  max(interaction_date) AS last_interaction_date
FROM sunmin_catalog.insurance_demo.bronze_crm_interactions GROUP BY policyholder_id;
---GO---
-- Gold Policyholder 360 (final, churn label ~calibrated via Bernoulli draw on real drivers):
CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.gold_policyholder_360
COMMENT 'GOLD: unified Policyholder 360 - one row per policyholder joining Policy Admin + Claims + CRM. Features + churn (non-renewal) label.'
AS
WITH j AS (
  SELECT
    p.policyholder_id, p.first_name, p.last_name, p.email, p.state, p.age,
    p.product_line, p.acquisition_channel, p.issue_date, p.policies_held,
    p.annual_premium, p.renewal_premium, p.coverage_amount, p.autopay_enrolled,
    round(datediff(current_date(), p.issue_date)/365.25, 1) AS tenure_years,
    round((p.renewal_premium/p.annual_premium - 1)*100, 1) AS premium_change_pct,
    coalesce(c.num_claims,0) AS num_claims,
    coalesce(c.total_claim_amount,0) AS total_claim_amount,
    coalesce(c.num_denied_claims,0) AS num_denied_claims,
    coalesce(c.num_open_claims,0) AS num_open_claims,
    coalesce(c.avg_days_to_settle,0) AS avg_days_to_settle,
    coalesce(i.num_interactions,0) AS num_interactions,
    coalesce(i.num_complaints,0) AS num_complaints,
    coalesce(i.avg_sentiment,0.75) AS avg_sentiment,
    coalesce(i.num_cancel_intent,0) AS num_cancel_intent,
    coalesce(i.num_billing_contacts,0) AS num_billing_contacts
  FROM sunmin_catalog.insurance_demo.bronze_policy_admin p
  LEFT JOIN sunmin_catalog.insurance_demo.silver_claims_agg c USING (policyholder_id)
  LEFT JOIN sunmin_catalog.insurance_demo.silver_interactions_agg i USING (policyholder_id)
),
scored AS (
  SELECT *,
    1/(1+exp(-( -1.35
      + 0.05*premium_change_pct + 0.95*num_cancel_intent + 0.4*num_complaints
      + 0.55*num_denied_claims + 0.007*avg_days_to_settle + 0.3*num_open_claims
      + CASE WHEN autopay_enrolled THEN -0.7 ELSE 0.15 END
      + CASE WHEN tenure_years < 2 THEN 0.6 ELSE -0.12*tenure_years END
      + (0.75 - avg_sentiment)*1.4 ))) AS churn_prob_latent
  FROM j
)
SELECT * EXCEPT(churn_prob_latent),
  CASE WHEN rand() < churn_prob_latent THEN 1 ELSE 0 END AS churned
FROM scored;
---GO---
SELECT count(*) ph, round(avg(churned)*100,1) churn_rate_pct FROM sunmin_catalog.insurance_demo.gold_policyholder_360;
---GO---
SELECT autopay_enrolled, round(avg(churned)*100,1) churn_pct, count(*) n FROM sunmin_catalog.insurance_demo.gold_policyholder_360 GROUP BY autopay_enrolled ORDER BY autopay_enrolled;
