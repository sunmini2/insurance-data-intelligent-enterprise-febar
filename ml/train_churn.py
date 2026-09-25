# Databricks notebook source
# MAGIC %pip install mlflow scikit-learn --quiet
# COMMAND ----------
dbutils.library.restartPython()
# COMMAND ----------
import json
import mlflow, mlflow.sklearn
import pandas as pd, numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score
from mlflow.models.signature import infer_signature

CATALOG, SCHEMA = "sunmin_catalog", "insurance_demo"
mlflow.set_registry_uri("databricks-uc")

# COMMAND ----------
df = spark.table(f"{CATALOG}.{SCHEMA}.gold_policyholder_360").toPandas()
FEATURES = ["age","tenure_years","annual_premium","premium_change_pct","policies_held",
            "num_claims","total_claim_amount","num_denied_claims","num_open_claims",
            "avg_days_to_settle","num_interactions","num_complaints","avg_sentiment",
            "num_cancel_intent","num_billing_contacts"]
df["autopay_int"] = df["autopay_enrolled"].astype(int)
FEATURES = FEATURES + ["autopay_int"]
X, y = df[FEATURES], df["churned"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

# COMMAND ----------
user = spark.sql('select current_user()').collect()[0][0]
mlflow.set_experiment(f"/Users/{user}/insurance_churn")
with mlflow.start_run(run_name="gbt_churn") as run:
    model = GradientBoostingClassifier(n_estimators=200, max_depth=3, learning_rate=0.1, random_state=42)
    model.fit(Xtr, ytr)
    proba = model.predict_proba(Xte)[:,1]
    auc = roc_auc_score(yte, proba); ap = average_precision_score(yte, proba)
    mlflow.log_metric("test_auc", auc); mlflow.log_metric("test_avg_precision", ap)
    mlflow.log_param("n_features", len(FEATURES))
    sig = infer_signature(Xtr, model.predict_proba(Xtr)[:,1])
    mlflow.sklearn.log_model(model, "model", signature=sig,
        serialization_format="cloudpickle",
        registered_model_name=f"{CATALOG}.{SCHEMA}.policyholder_churn")
    print(f"AUC={auc:.3f}  AvgPrecision={ap:.3f}")
    fi = sorted(zip(FEATURES, model.feature_importances_), key=lambda x:-x[1])
    print("Top drivers:", [(f, round(i,3)) for f,i in fi[:6]])

# COMMAND ----------
df["churn_probability"] = model.predict_proba(df[FEATURES])[:,1]
df["risk_tier"] = pd.cut(df["churn_probability"], bins=[-0.01,0.25,0.55,1.01], labels=["Low","Medium","High"]).astype(str)
out = df[["policyholder_id","churn_probability","risk_tier","annual_premium","renewal_premium"]].copy()
out["churn_probability"] = out["churn_probability"].round(4)
out["premium_at_risk"] = out["renewal_premium"].round(2)
out["scored_at"] = pd.Timestamp.utcnow().tz_localize(None)
sdf = spark.createDataFrame(out[["policyholder_id","churn_probability","risk_tier","premium_at_risk","scored_at"]])
sdf.write.mode("overwrite").option("overwriteSchema","true").saveAsTable(f"{CATALOG}.{SCHEMA}.gold_churn_scores")
print("Wrote gold_churn_scores:", sdf.count(), "rows")

# COMMAND ----------
# Summarize risk tiers + premium at risk and return everything as JSON (captured as text evidence)
tiers = out.groupby("risk_tier").agg(n=("policyholder_id","count"),
                                     premium_at_risk=("premium_at_risk","sum")).round(0)
summary = {
    "test_auc": round(float(auc), 4),
    "test_avg_precision": round(float(ap), 4),
    "n_features": len(FEATURES),
    "rows_scored": int(len(out)),
    "risk_tiers": {t: {"n": int(r.n), "premium_at_risk": float(r.premium_at_risk)}
                   for t, r in tiers.iterrows()},
    "premium_at_risk_high_med": float(out[out.risk_tier.isin(["High","Medium"])]["premium_at_risk"].sum()),
    "top_drivers": [(f, round(float(i), 4)) for f, i in fi[:6]],
}
print("SUMMARY:", json.dumps(summary, indent=2))
dbutils.notebook.exit(json.dumps(summary))
