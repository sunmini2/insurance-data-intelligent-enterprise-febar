# Evidence — Stage 3a: ML (non-renewal / churn model)

**Notebook:** `ml/train_churn.py` (serverless job run `851744482403869`, result SUCCESS)
**Model:** `sunmin_catalog.insurance_demo.policyholder_churn` (GradientBoostingClassifier, MLflow-tracked, Unity Catalog registered)
**Trained on:** `gold_policyholder_360` produced by the Lakeflow pipeline (5,200 policyholders, 16 features)

## Metrics + scoring summary (returned as the notebook's `dbutils.notebook.exit` JSON)

```json
{
  "test_auc": 0.7656,
  "test_avg_precision": 0.5881,
  "n_features": 16,
  "rows_scored": 5200,
  "risk_tiers": {
    "High":   {"n": 666,  "premium_at_risk": 1636571.0},
    "Medium": {"n": 1451, "premium_at_risk": 3460615.0},
    "Low":    {"n": 3083, "premium_at_risk": 7228539.0}
  },
  "premium_at_risk_high_med": 5097186.09,
  "top_drivers": [
    ["tenure_years", 0.1626],
    ["premium_change_pct", 0.1605],
    ["num_complaints", 0.1093],
    ["avg_sentiment", 0.0987],
    ["num_cancel_intent", 0.0984],
    ["autopay_int", 0.0932]
  ]
}
```

## Scored output written to `gold_churn_scores`, joined in `gold_book_scored`

```
-- KPI roll-up (gold_book_scored)
total_ph   book_premium   high_risk_ph   premium_at_risk   avg_churn_prob
5200       11,615,498     666            5,097,186         0.271

-- by risk tier
risk_tier   n      premium_at_risk
High        666    1,636,571
Medium      1451   3,460,615
Low         3083   7,228,539

-- driver contrast by tier (the model separates them cleanly)
risk_tier   avg_hike   avg_complaints   avg_cancel
High        11.5%      1.35             0.57
Medium      7.8%       0.72             0.23
Low         4.2%       0.27             0.05
```

**Read:** the model finds **666 high-risk** policyholders and, weighted across High+Medium,
**$5.1M of premium is at risk**. The strongest drivers are short tenure, big renewal premium
hikes, complaints, poor sentiment, competitor-shopping calls, and no autopay — all addressable.
