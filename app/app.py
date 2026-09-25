import os
import time
import uuid
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from databricks import sql
from databricks.sdk.core import Config

# ----------------------------------------------------------------------------
# Northwind Mutual — Retention & Risk Command Center (Databricks App)
# Surfaces the full data journey: governed gold (UC) via a SQL warehouse for
# analytics, and Lakebase Postgres for the operational agent workbench (OLTP).
# ----------------------------------------------------------------------------
CATALOG, SCHEMA = "sunmin_catalog", "insurance_demo"
WID = os.getenv("WAREHOUSE_ID", "148ccb90800933a1")
LAKEBASE_INSTANCE = os.getenv("LAKEBASE_INSTANCE", "insurance-febar-lakebase")
LAKEBASE_DB = os.getenv("PGDATABASE", "databricks_postgres")
TEAL, DARK, RED, AMBER, GREEN, MUTED = "#1B5161", "#1B3037", "#FF3620", "#FFAB00", "#00A972", "#618793"
TIER_COLORS = {"High": RED, "Medium": AMBER, "Low": GREEN}

st.set_page_config(page_title="Northwind Mutual — Retention & Risk", page_icon="🛡️", layout="wide")

cfg = Config()

@st.cache_resource
def _conn():
    return sql.connect(server_hostname=cfg.host,
                       http_path=f"/sql/1.0/warehouses/{WID}",
                       credentials_provider=lambda: cfg.authenticate)


# ---- Lakebase (Postgres) connection for the operational agent workbench ----
def _pg_connect():
    """Connect to Lakebase Postgres. Prefers platform-injected PG* env vars
    (Databricks App database resource); otherwise mints a short-lived OAuth
    token via the Databricks SDK and connects as the app's identity."""
    import psycopg2
    host = os.getenv("PGHOST"); user = os.getenv("PGUSER"); pw = os.getenv("PGPASSWORD")
    port = os.getenv("PGPORT", "5432"); db = os.getenv("PGDATABASE", LAKEBASE_DB)
    if not (host and user and pw):
        from databricks.sdk import WorkspaceClient
        w = WorkspaceClient()
        inst = w.database.get_database_instance(name=LAKEBASE_INSTANCE)
        host = inst.read_write_dns
        cred = w.database.generate_database_credential(
            request_id=str(uuid.uuid4()), instance_names=[LAKEBASE_INSTANCE])
        pw = cred.token
        user = user or w.current_user.me().user_name
    return psycopg2.connect(host=host, port=port, dbname=db, user=user,
                            password=pw, sslmode="require")

def pg_query(query: str, params=None) -> pd.DataFrame:
    conn = _pg_connect()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()

def pg_execute(query: str, params=None):
    conn = _pg_connect()
    try:
        with conn.cursor() as c:
            c.execute(query, params)
        conn.commit()
    finally:
        conn.close()

@st.cache_data(ttl=600, show_spinner=False)
def q(query: str, _tries: int = 5) -> pd.DataFrame:
    # Resilient to cold-start / restarted warehouse: retry with backoff and
    # drop the cached (possibly stale) connection between attempts.
    last = None
    for i in range(_tries):
        try:
            with _conn().cursor() as c:
                c.execute(query)
                return c.fetchall_arrow().to_pandas()
        except Exception as e:
            last = e
            _conn.clear()          # force a fresh connection next attempt
            time.sleep(3 * (i + 1))  # let a cold serverless warehouse spin up
    raise last

def fq(t):  # fully-qualified
    return f"{CATALOG}.{SCHEMA}.{t}"

# ---- Styling ----
st.markdown(f"""
<style>
.block-container {{padding-top: 1.6rem; max-width: 1300px;}}
h1, h2, h3 {{color: {DARK};}}
div[data-testid="stMetric"] {{
  background: #ffffff; border: 1px solid #E6EAEC; border-left: 5px solid {TEAL};
  border-radius: 10px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(27,48,55,.06);
}}
div[data-testid="stMetricValue"] {{color: {DARK}; font-weight: 700;}}
div[data-testid="stMetricLabel"] {{color: {MUTED};}}
.hero {{background: {DARK}; color:#fff; padding: 22px 26px; border-radius: 12px; margin-bottom: 18px;}}
.hero h1 {{color:#fff; margin:0; font-size: 1.7rem;}}
.hero p {{color:#9EB7BE; margin:.35rem 0 0 0;}}
.story {{background:#F6F8F9; border-left:4px solid {RED}; padding:10px 16px; border-radius:6px; color:{DARK}; margin:6px 0 14px 0;}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🛡️ Northwind Mutual — Retention &amp; Risk Command Center</h1>
  <p>P&amp;C &amp; Life book of business · powered by the unified Policyholder 360, a non-renewal ML model, and a GenAI Retention Copilot</p>
</div>
""", unsafe_allow_html=True)

# ---- KPIs ----
kpi = q(f"""
  SELECT round(sum(annual_premium)/1e6,1) book_m,
         round(sum(CASE WHEN risk_tier IN ('High','Medium') THEN premium_at_risk ELSE 0 END)/1e6,2) risk_m,
         sum(CASE WHEN risk_tier='High' THEN 1 ELSE 0 END) high_n,
         round(avg(churned)*100,1) churn_rate,
         count(*) total_ph
  FROM {fq('gold_book_scored')}
""").iloc[0]
camp = q(f"SELECT * FROM {fq('gold_campaign_outcomes')}")
treated = camp[camp.cohort.str.startswith("Treated")].iloc[0]
control = camp[camp.cohort.str.startswith("Control")].iloc[0]
lift = float(treated.save_rate) - float(control.save_rate)
recover_proj = float(kpi.risk_m) * lift  # $M recoverable at the proven incremental lift

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Annual Book Premium", f"${kpi.book_m}M", f"{int(kpi.total_ph):,} policyholders")
c2.metric("Premium at Risk", f"${kpi.risk_m}M", "High + Medium tiers", delta_color="inverse")
c3.metric("High-Risk Policyholders", f"{int(kpi.high_n):,}", "flagged by the model", delta_color="inverse")
c4.metric("Book Non-Renewal Rate", f"{kpi.churn_rate}%", "of the in-force book", delta_color="inverse")
c5.metric("Recoverable / yr", f"${recover_proj:.1f}M", f"at proven +{lift*100:.0f}pt lift", delta_color="normal")

tabs = st.tabs(["📉  The Trend", "🎯  Where the Risk Sits", "🔍  Why They Leave",
                "💰  Proof It Works", "🤖  Retention Copilot", "🗂️  Agent Workbench"])

# ---- STORY 1: TREND ----
with tabs[0]:
    st.markdown('<div class="story"><b>The story:</b> retention slipped through the rate-hardening cycle — but the last few months are bending the curve as proactive outreach begins.</div>', unsafe_allow_html=True)
    tr = q(f"SELECT month, retention_rate, renewed, lapsed, premium_lost, premium_retained FROM {fq('gold_retention_trend')} ORDER BY month_start").copy()
    left, right = st.columns([3, 2])
    with left:
        fig = px.line(tr, x="month", y="retention_rate", markers=True, title="Renewal (persistency) rate — trailing 18 months")
        fig.update_traces(line_color=TEAL, line_width=3)
        fig.update_layout(yaxis_tickformat=".0%", yaxis_title="Retention rate", xaxis_title=None, height=380, plot_bgcolor="white")
        fig.add_hline(y=0.85, line_dash="dot", line_color=MUTED, annotation_text="target 85%")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig2 = go.Figure()
        fig2.add_bar(x=tr.month, y=tr.premium_lost, name="Premium lost", marker_color=RED)
        fig2.add_bar(x=tr.month, y=tr.premium_retained, name="Premium retained", marker_color=GREEN)
        fig2.update_layout(barmode="stack", title="Premium retained vs lost at renewal", height=380,
                           plot_bgcolor="white", legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig2, use_container_width=True)
    st.caption(f"Last 12 months: **{int(tr.tail(12).lapsed.sum()):,}** policies lapsed · **${tr.tail(12).premium_lost.sum()/1e6:.1f}M** premium walked out the door.")

# ---- STORY 2: WHERE THE RISK SITS ----
with tabs[1]:
    st.markdown('<div class="story"><b>The story:</b> weighted by likelihood to leave, expected loss concentrates in the <b>High and Medium</b> tiers — the Low tier holds the most raw premium but the least actual risk. That is where a retention team should aim first.</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        tier = q(f"SELECT risk_tier, round(sum(premium_at_risk*churn_probability)/1e6,2) prem_m FROM {fq('gold_book_scored')} GROUP BY risk_tier")
        fig = px.bar(tier, x="risk_tier", y="prem_m", color="risk_tier", color_discrete_map=TIER_COLORS,
                     title="Expected premium at risk by tier ($M)", text="prem_m",
                     category_orders={"risk_tier": ["High", "Medium", "Low"]})
        fig.update_layout(showlegend=False, height=360, plot_bgcolor="white", xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        prod = q(f"SELECT product_line, round(sum(premium_at_risk*churn_probability)/1e6,2) prem_m FROM {fq('gold_book_scored')} GROUP BY product_line ORDER BY prem_m DESC")
        fig = px.bar(prod, x="prem_m", y="product_line", orientation="h", title="Expected premium at risk by product line ($M)",
                     text="prem_m", color_discrete_sequence=[TEAL])
        fig.update_layout(height=360, plot_bgcolor="white", xaxis_title=None, yaxis_title=None, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    state = q(f"SELECT state, round(sum(premium_at_risk*churn_probability)/1e3,0) prem_k FROM {fq('gold_book_scored')} GROUP BY state ORDER BY prem_k DESC LIMIT 10")
    fig = px.bar(state, x="state", y="prem_k", title="Top 10 states by expected premium at risk ($K)", text="prem_k", color_discrete_sequence=[AMBER])
    fig.update_layout(height=320, plot_bgcolor="white", xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

# ---- STORY 3: WHY THEY LEAVE ----
with tabs[2]:
    st.markdown('<div class="story"><b>The story:</b> high-risk policyholders look different — bigger renewal hikes, more complaints, more competitor-shopping calls, more denied claims. These are addressable.</div>', unsafe_allow_html=True)
    drv = q(f"""SELECT risk_tier,
                round(avg(premium_change_pct),1) hike, round(avg(num_complaints),2) complaints,
                round(avg(num_cancel_intent),2) shopping, round(avg(num_denied_claims),2) denied
             FROM {fq('gold_book_scored')} GROUP BY risk_tier""")
    order = {"High": 0, "Medium": 1, "Low": 2}
    drv = drv.sort_values("risk_tier", key=lambda s: s.map(order))
    metrics = [("hike", "Avg renewal premium increase (%)"), ("complaints", "Avg complaints"),
               ("shopping", "Avg competitor-shopping calls"), ("denied", "Avg denied claims")]
    cols = st.columns(2)
    for i, (col, title) in enumerate(metrics):
        with cols[i % 2]:
            fig = px.bar(drv, x="risk_tier", y=col, color="risk_tier", color_discrete_map=TIER_COLORS,
                         title=title, text=col, category_orders={"risk_tier": ["High", "Medium", "Low"]})
            fig.update_layout(showlegend=False, height=300, plot_bgcolor="white", xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

# ---- STORY 4: PROOF IT WORKS ----
with tabs[3]:
    st.markdown('<div class="story"><b>The story:</b> this is not theory. In a controlled test, policyholders who got proactive Retention Copilot outreach renewed far more often than a holdout — and the recovered premium dwarfs the cost.</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric("Treated save rate", f"{float(treated.save_rate)*100:.0f}%", f"{int(treated.renewals_saved)} of {int(treated.policyholders)} saved")
    b.metric("Control save rate", f"{float(control.save_rate)*100:.0f}%", "holdout — no outreach")
    c.metric("Incremental lift", f"+{lift*100:.0f} pts", f"${float(treated.premium_recovered):,.0f} recovered")
    fig = px.bar(camp, x="cohort", y="save_rate", color="cohort", text=camp.save_rate.map(lambda v: f"{v*100:.0f}%"),
                 color_discrete_sequence=[GREEN, MUTED], title="Renewal save rate — treated vs control")
    fig.update_layout(showlegend=False, yaxis_tickformat=".0%", height=340, plot_bgcolor="white", xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### 🎚️ If you act on the top N high-risk policyholders…")
    hr = q(f"SELECT premium_at_risk FROM {fq('gold_book_scored')} WHERE risk_tier='High' ORDER BY premium_at_risk DESC")
    n = st.slider("Policyholders to work this quarter", 50, int(len(hr)), min(300, int(len(hr))), step=50)
    covered = float(hr.head(n).premium_at_risk.sum())
    expected = covered * lift
    x, y, z = st.columns(3)
    x.metric("At-risk premium covered", f"${covered/1e3:,.0f}K")
    y.metric("Expected premium recovered", f"${expected/1e3:,.0f}K", f"at proven +{lift*100:.0f}pt lift")
    z.metric("Per-policyholder value", f"${expected/max(n,1):,.0f}", "avg recovered / outreach")

# ---- STORY 5: RETENTION COPILOT ----
with tabs[4]:
    st.markdown('<div class="story"><b>The story:</b> for every high-risk policyholder, GenAI turns years of claims notes and call history into a ready-to-act brief — why they will leave, the next best action, and drafted outreach.</div>', unsafe_allow_html=True)
    cop = q(f"""SELECT first_name, last_name, state, product_line, round(churn_probability,2) churn_prob,
                round(premium_at_risk,0) premium_at_risk, premium_change_pct hike_pct, num_complaints,
                retention_brief
             FROM {fq('gold_retention_copilot')} ORDER BY churn_probability DESC""")
    search = st.text_input("🔎 Filter by name or state", "")
    view = cop[cop.apply(lambda r: search.lower() in f"{r.first_name} {r.last_name} {r.state}".lower(), axis=1)] if search else cop
    left, right = st.columns([2, 3])
    with left:
        st.dataframe(view[["first_name", "last_name", "state", "product_line", "churn_prob", "premium_at_risk", "num_complaints"]],
                     hide_index=True, height=460, use_container_width=True)
    with right:
        names = (view.first_name + " " + view.last_name + " · " + view.state).tolist()
        if names:
            pick = st.selectbox("Select a policyholder for the GenAI brief", names, index=0)
            row = view.iloc[names.index(pick)]
            st.markdown(f"### {row.first_name} {row.last_name} — {row.product_line} ({row.state})")
            m1, m2, m3 = st.columns(3)
            m1.metric("Churn probability", f"{row.churn_prob:.0%}")
            m2.metric("Premium at risk", f"${row.premium_at_risk:,.0f}")
            m3.metric("Renewal hike", f"{row.hike_pct:.0f}%")
            st.markdown("**🤖 GenAI Retention Brief**")
            st.info(row.retention_brief)
        else:
            st.warning("No policyholders match that filter.")

# ---- STORY 6: AGENT WORKBENCH (Lakebase operational serving, OLTP two-way) ----
with tabs[5]:
    st.markdown('<div class="story"><b>The story:</b> the analytical gold layer becomes an <b>operational</b> tool. The high-risk worklist is synced to Lakebase (Postgres); retention agents claim a case and log the outcome — low-latency writes straight back to the operational store.</div>', unsafe_allow_html=True)
    try:
        wl = pg_query("""
            SELECT w.policyholder_id, w.first_name, w.last_name, w.state, w.product_line,
                   w.churn_probability, w.premium_at_risk, w.premium_change_pct,
                   w.num_complaints, w.num_cancel_intent, w.retention_brief,
                   d.status, d.assigned_agent, d.outcome, d.notes, d.updated_at
            FROM public.agent_worklist w
            LEFT JOIN LATERAL (
                SELECT status, assigned_agent, outcome, notes, updated_at
                FROM retention.case_dispositions cd
                WHERE cd.policyholder_id = w.policyholder_id
                ORDER BY updated_at DESC LIMIT 1
            ) d ON true
            ORDER BY w.churn_probability DESC
        """)
        wl["status"] = wl["status"].fillna("open")
        a, b, c, d = st.columns(4)
        a.metric("Cases in worklist", f"{len(wl):,}")
        b.metric("Open", f"{int((wl.status=='open').sum()):,}")
        c.metric("Worked", f"{int(wl.status.isin(['in_progress','saved','lost']).sum()):,}")
        d.metric("Saved", f"{int((wl.status=='saved').sum()):,}")

        left, right = st.columns([2, 3])
        with left:
            st.dataframe(wl[["policyholder_id", "first_name", "last_name", "state",
                             "premium_at_risk", "status"]].head(200),
                         hide_index=True, height=460, use_container_width=True)
        with right:
            opts = (wl.first_name + " " + wl.last_name + " · " + wl.state +
                    " · " + wl.policyholder_id).tolist()
            pick = st.selectbox("Select a case to work", opts, index=0) if opts else None
            if pick:
                row = wl.iloc[opts.index(pick)]
                st.markdown(f"### {row.first_name} {row.last_name} — {row.product_line} ({row.state})")
                m1, m2, m3 = st.columns(3)
                m1.metric("Churn probability", f"{float(row.churn_probability):.0%}")
                m2.metric("Premium at risk", f"${float(row.premium_at_risk):,.0f}")
                m3.metric("Current status", str(row.status))
                st.markdown("**🤖 GenAI Retention Brief**")
                st.info(row.retention_brief)
                with st.form("disposition"):
                    st.markdown("**Log an outreach disposition** (writes to Lakebase Postgres)")
                    status = st.selectbox("Status", ["in_progress", "saved", "lost", "open"])
                    outcome = st.selectbox("Outcome", ["discount_applied", "callback_scheduled",
                                                       "coverage_reviewed", "switched_carrier", "no_answer"])
                    agent = st.text_input("Agent", "sunmin.lee")
                    notes = st.text_area("Notes", "")
                    if st.form_submit_button("💾 Save disposition"):
                        pg_execute("""
                            INSERT INTO retention.case_dispositions
                              (policyholder_id, status, assigned_agent, outcome, notes, contacted_at)
                            VALUES (%s, %s, %s, %s, %s, now())
                        """, (row.policyholder_id, status, agent, outcome, notes))
                        st.success(f"Saved disposition for {row.policyholder_id} → {status}. Reload to see it in the worklist.")
    except Exception as e:
        st.warning("Lakebase workbench unavailable in this environment. "
                   "Grant the app's service principal access to the Lakebase instance "
                   f"`{LAKEBASE_INSTANCE}` and its `retention`/`public` schemas. Details: " + str(e)[:300])

st.caption("Databricks App · Streamlit · analytics from governed Gold tables in Unity Catalog "
           "(`sunmin_catalog.insurance_demo`) via a SQL warehouse; operational worklist + dispositions "
           "on Lakebase Postgres. Synthetic data only.")
