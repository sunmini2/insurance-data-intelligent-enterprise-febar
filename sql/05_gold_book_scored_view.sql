CREATE OR REPLACE VIEW sunmin_catalog.insurance_demo.gold_book_scored AS
SELECT s.policyholder_id, s.churn_probability, s.risk_tier, s.premium_at_risk,
  g.first_name, g.last_name, g.state, g.product_line, g.acquisition_channel,
  g.tenure_years, g.annual_premium, g.premium_change_pct,
  g.num_claims, g.num_denied_claims, g.num_open_claims,
  g.num_complaints, g.num_cancel_intent, g.avg_sentiment, g.autopay_enrolled, g.churned
FROM sunmin_catalog.insurance_demo.gold_churn_scores s
JOIN sunmin_catalog.insurance_demo.gold_policyholder_360 g USING (policyholder_id);
---GO---
SELECT count(*) FROM sunmin_catalog.insurance_demo.gold_book_scored;
---GO---
-- KPI query
SELECT count(*) AS total_ph, round(sum(annual_premium),0) AS book_premium,
  sum(CASE WHEN risk_tier='High' THEN 1 ELSE 0 END) AS high_risk_ph,
  round(sum(CASE WHEN risk_tier IN ('High','Medium') THEN premium_at_risk ELSE 0 END),0) AS premium_at_risk,
  round(avg(churn_probability),3) AS avg_churn_prob
FROM sunmin_catalog.insurance_demo.gold_book_scored;
---GO---
-- by tier
SELECT risk_tier, count(*) n, round(sum(premium_at_risk),0) premium_at_risk FROM sunmin_catalog.insurance_demo.gold_book_scored GROUP BY risk_tier;
---GO---
-- driver comparison by tier
SELECT risk_tier, round(avg(premium_change_pct),1) avg_hike, round(avg(num_complaints),2) avg_complaints, round(avg(num_cancel_intent),2) avg_cancel FROM sunmin_catalog.insurance_demo.gold_book_scored GROUP BY risk_tier;
