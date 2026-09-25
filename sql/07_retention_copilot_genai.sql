CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.gold_retention_copilot AS
SELECT
  policyholder_id, first_name, last_name, state, product_line,
  churn_probability, risk_tier, premium_at_risk,
  premium_change_pct, num_complaints, num_denied_claims, num_cancel_intent,
  ai_query(
    'databricks-gpt-oss-120b',
    concat(
      'You are a retention strategist at a P&C and Life insurance carrier. Based ONLY on the policyholder data below, write a concise retention brief with exactly three labeled sections and nothing else. ',
      'Format:\n',
      'WHY AT RISK: <one sentence naming the top 1-2 drivers>\n',
      'NEXT BEST ACTION: <one specific action the retention agent should take>\n',
      'DRAFT OUTREACH: <2 warm sentences addressed to the customer by first name>\n\n',
      'DATA:\n',
      'Name: ', first_name, ' ', last_name, ' (', state, ')\n',
      'Product: ', product_line, ', tenure ', cast(tenure_years as string), ' years, autopay=', cast(autopay_enrolled as string), '\n',
      'Renewal premium change: ', cast(premium_change_pct as string), '%\n',
      'Claims: ', cast(num_claims as string), ' total, ', cast(num_denied_claims as string), ' denied, ', cast(num_open_claims as string), ' open\n',
      'Service: ', cast(num_complaints as string), ' complaints, ', cast(num_cancel_intent as string), ' cancellation/shopping calls, avg sentiment ', cast(round(avg_sentiment,2) as string), '\n',
      'Recent CRM notes: ', substr(crm_notes,1,600), '\n',
      'Recent claim notes: ', substr(claim_notes,1,400)
    )
  ) AS retention_brief
FROM sunmin_catalog.insurance_demo.gold_highrisk_context;
---GO---
SELECT count(*) briefs FROM sunmin_catalog.insurance_demo.gold_retention_copilot;
