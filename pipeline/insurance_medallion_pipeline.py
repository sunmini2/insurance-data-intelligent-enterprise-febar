"""
Northwind Mutual — Insurance medallion (Lakeflow declarative pipeline).

Ingests three raw source-system extracts from a UC Volume via Auto Loader and
builds the governed Policyholder 360, entirely declaratively:

    raw_landing/ (Volume)                bronze (streaming tables, Auto Loader)
      policy_admin/*.csv     ---->   bronze_policy_admin
      claims/*.json          ---->   bronze_claims
      crm/*.json             ---->   bronze_crm_interactions
                                          |
                                          v  silver (conformed per-policyholder)
                             silver_claims_agg, silver_interactions_agg
                                          |
                                          v  gold
                             gold_policyholder_360  (unified 360 + churn label)

Modern Spark Declarative Pipelines syntax: `from pyspark import pipelines as dp`.
`@dp.table` yields a STREAMING table when the query is a readStream (bronze) and a
MATERIALIZED VIEW when the query is batch (silver/gold). No real customer data.
"""
from pyspark import pipelines as dp
from pyspark.sql import functions as F

VOL = "/Volumes/sunmin_catalog/insurance_demo/raw_landing"


# ----------------------------------------------------------------------------
# BRONZE — Auto Loader incremental ingest of each raw source system
# ----------------------------------------------------------------------------
@dp.table(
    name="bronze_policy_admin",
    comment="BRONZE: Policy Administration System (relational, CSV export). One row per policy. Auto Loader ingest.",
    table_properties={"quality": "bronze"},
)
def bronze_policy_admin():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(f"{VOL}/policy_admin")
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.col("_metadata.file_path"))
    )


@dp.table(
    name="bronze_claims",
    comment="BRONZE: Claims Management System (JSON). Free-text adjuster_notes feed the GenAI layer. Auto Loader ingest.",
    table_properties={"quality": "bronze"},
)
def bronze_claims():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(f"{VOL}/claims")
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.col("_metadata.file_path"))
    )


@dp.table(
    name="bronze_crm_interactions",
    comment="BRONZE: CRM / call-center SaaS export (JSON). Free-text notes + complaint + sentiment signal. Auto Loader ingest.",
    table_properties={"quality": "bronze"},
)
def bronze_crm_interactions():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(f"{VOL}/crm")
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.col("_metadata.file_path"))
    )


# ----------------------------------------------------------------------------
# SILVER — conform each source to one row per policyholder
# ----------------------------------------------------------------------------
@dp.table(
    name="silver_claims_agg",
    comment="SILVER: per-policyholder claims rollup (counts, denied/open, settlement latency).",
    table_properties={"quality": "silver"},
)
@dp.expect_or_drop("valid_policyholder", "policyholder_id IS NOT NULL")
def silver_claims_agg():
    return (
        spark.read.table("bronze_claims")
        .groupBy("policyholder_id")
        .agg(
            F.count("*").alias("num_claims"),
            F.round(F.sum("claim_amount"), 2).alias("total_claim_amount"),
            F.sum(F.expr("CASE WHEN claim_status='denied' THEN 1 ELSE 0 END")).alias("num_denied_claims"),
            F.sum(F.expr("CASE WHEN claim_status='open' THEN 1 ELSE 0 END")).alias("num_open_claims"),
            F.round(F.avg("days_to_settle"), 1).alias("avg_days_to_settle"),
            F.max("claim_date").alias("last_claim_date"),
        )
    )


@dp.table(
    name="silver_interactions_agg",
    comment="SILVER: per-policyholder CRM rollup (complaints, sentiment, cancel/shopping intent, billing contacts).",
    table_properties={"quality": "silver"},
)
@dp.expect_or_drop("valid_policyholder", "policyholder_id IS NOT NULL")
def silver_interactions_agg():
    return (
        spark.read.table("bronze_crm_interactions")
        .groupBy("policyholder_id")
        .agg(
            F.count("*").alias("num_interactions"),
            F.sum(F.col("complaint_flag").cast("int")).alias("num_complaints"),
            F.round(F.avg("sentiment_score"), 3).alias("avg_sentiment"),
            F.sum(F.expr("CASE WHEN reason='Cancellation / Shopping Competitor' THEN 1 ELSE 0 END")).alias("num_cancel_intent"),
            F.sum(F.expr("CASE WHEN reason='Billing / Premium Increase' THEN 1 ELSE 0 END")).alias("num_billing_contacts"),
            F.max("interaction_date").alias("last_interaction_date"),
        )
    )


# ----------------------------------------------------------------------------
# GOLD — unified Policyholder 360 (features + historical non-renewal label)
# ----------------------------------------------------------------------------
@dp.table(
    name="gold_policyholder_360",
    comment="GOLD: unified Policyholder 360 — one row per policyholder joining Policy Admin + Claims + CRM. Features + non-renewal (churn) label. Governed by Unity Catalog; email PII protected by a column mask.",
    table_properties={"quality": "gold"},
)
@dp.expect_or_drop("has_premium", "annual_premium IS NOT NULL AND annual_premium > 0")
def gold_policyholder_360():
    p = spark.read.table("bronze_policy_admin")
    c = spark.read.table("silver_claims_agg")
    i = spark.read.table("silver_interactions_agg")
    return (
        p.join(c, "policyholder_id", "left")
        .join(i, "policyholder_id", "left")
        .select(
            p["policyholder_id"], "first_name", "last_name", "email", "state", "age",
            "product_line", "acquisition_channel", "issue_date", "policies_held",
            "annual_premium", "renewal_premium", "coverage_amount", "autopay_enrolled",
            F.round(F.datediff(F.current_date(), F.col("issue_date")) / 365.25, 1).alias("tenure_years"),
            F.round((F.col("renewal_premium") / F.col("annual_premium") - 1) * 100, 1).alias("premium_change_pct"),
            F.coalesce("num_claims", F.lit(0)).alias("num_claims"),
            F.coalesce("total_claim_amount", F.lit(0.0)).alias("total_claim_amount"),
            F.coalesce("num_denied_claims", F.lit(0)).alias("num_denied_claims"),
            F.coalesce("num_open_claims", F.lit(0)).alias("num_open_claims"),
            F.coalesce("avg_days_to_settle", F.lit(0.0)).alias("avg_days_to_settle"),
            F.coalesce("num_interactions", F.lit(0)).alias("num_interactions"),
            F.coalesce("num_complaints", F.lit(0)).alias("num_complaints"),
            F.coalesce("avg_sentiment", F.lit(0.75)).alias("avg_sentiment"),
            F.coalesce("num_cancel_intent", F.lit(0)).alias("num_cancel_intent"),
            F.coalesce("num_billing_contacts", F.lit(0)).alias("num_billing_contacts"),
            F.col("churned").cast("int").alias("churned"),
        )
    )
