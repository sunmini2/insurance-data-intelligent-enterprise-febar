-- Assemble grounded context per HIGH-risk policyholder (activates accumulated claims + CRM knowledge)
CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.gold_highrisk_context AS
WITH notes AS (
  SELECT policyholder_id, concat_ws(' | ', collect_list(interaction_notes)) AS crm_notes
  FROM (SELECT policyholder_id, interaction_notes,
               row_number() over (partition by policyholder_id order by interaction_date desc) rn
        FROM sunmin_catalog.insurance_demo.bronze_crm_interactions) WHERE rn<=3
  GROUP BY policyholder_id
),
cl AS (
  SELECT policyholder_id, concat_ws(' | ', collect_list(adjuster_notes)) AS claim_notes
  FROM (SELECT policyholder_id, adjuster_notes,
               row_number() over (partition by policyholder_id order by claim_date desc) rn
        FROM sunmin_catalog.insurance_demo.bronze_claims) WHERE rn<=2
  GROUP BY policyholder_id
)
SELECT s.policyholder_id, s.churn_probability, s.risk_tier, s.premium_at_risk,
  g.first_name, g.last_name, g.state, g.product_line, g.tenure_years,
  g.premium_change_pct, g.num_claims, g.num_denied_claims, g.num_open_claims,
  g.num_complaints, g.num_cancel_intent, g.avg_sentiment, g.autopay_enrolled,
  coalesce(n.crm_notes,'No recent contact on record.') AS crm_notes,
  coalesce(cl.claim_notes,'No claims on record.') AS claim_notes
FROM sunmin_catalog.insurance_demo.gold_churn_scores s
JOIN sunmin_catalog.insurance_demo.gold_policyholder_360 g USING (policyholder_id)
LEFT JOIN notes n USING (policyholder_id)
LEFT JOIN cl USING (policyholder_id)
WHERE s.risk_tier = 'High';
---GO---
SELECT count(*) high_risk FROM sunmin_catalog.insurance_demo.gold_highrisk_context;
