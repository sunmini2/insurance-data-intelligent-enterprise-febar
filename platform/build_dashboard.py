import json, subprocess, uuid
PROFILE="azure-sunmin"; WH="95e9741b3507f86d"
SC="sunmin_catalog.insurance_demo"; DID=open("/tmp/dashid.txt").read().strip()
def wid(): return uuid.uuid4().hex[:8]
def ds(n,d,q): return {"name":n,"displayName":d,"queryLines":[q]}
TEAL,DARK,RED,AMBER,GREEN,MUTED="#1B5161","#1B3037","#FF3620","#FFAB00","#00A972","#618793"
TIER=["#FF3621","#FFAB00","#00A972"]

datasets=[
 ds("kpis","KPIs", f"SELECT round(sum(b.annual_premium)/1e6,1) book_m, round(sum(CASE WHEN b.risk_tier IN ('High','Medium') THEN b.premium_at_risk ELSE 0 END)/1e6,2) risk_m, sum(CASE WHEN b.risk_tier='High' THEN 1 ELSE 0 END) high_n, round(avg(b.churned)*100,1) churn_rate, round(sum(CASE WHEN b.risk_tier IN ('High','Medium') THEN b.premium_at_risk ELSE 0 END)/1e6 * (SELECT max(save_rate)-min(save_rate) FROM {SC}.gold_campaign_outcomes),2) recover_m FROM {SC}.gold_book_scored b "),
 ds("trend","Trend", f"SELECT month, month_start, retention_rate, premium_retained, premium_lost FROM {SC}.gold_retention_trend ORDER BY month_start "),
 ds("by_tier","By Tier", f"SELECT risk_tier, round(sum(premium_at_risk*churn_probability)/1e6,2) prem_m FROM {SC}.gold_book_scored GROUP BY risk_tier "),
 ds("by_product","By Product", f"SELECT product_line, round(sum(premium_at_risk*churn_probability)/1e6,2) prem_m FROM {SC}.gold_book_scored GROUP BY product_line ORDER BY prem_m DESC "),
 ds("by_state","By State", f"SELECT state, round(sum(premium_at_risk*churn_probability)/1e3,0) prem_k FROM {SC}.gold_book_scored GROUP BY state ORDER BY prem_k DESC LIMIT 10 "),
 ds("drivers","Drivers", f"SELECT risk_tier, round(avg(premium_change_pct),1) avg_hike, round(avg(num_cancel_intent),2) avg_shopping FROM {SC}.gold_book_scored GROUP BY risk_tier "),
 ds("campaign","Campaign", f"SELECT cohort, save_rate, premium_recovered FROM {SC}.gold_campaign_outcomes "),
 ds("copilot","Copilot", f"SELECT first_name, last_name, state, product_line, round(churn_probability,2) churn_prob, round(premium_at_risk,0) premium_at_risk, premium_change_pct hike_pct, num_complaints, retention_brief FROM {SC}.gold_retention_copilot ORDER BY churn_probability DESC LIMIT 25 "),
]
def text(n,md,x,y,w,h): return {"widget":{"name":n,"multilineTextboxSpec":{"lines":[md]}},"position":{"x":x,"y":y,"width":w,"height":h}}
def counter(n,dsn,f,t,x,y,w=1,h=3):
    return {"widget":{"name":n,"queries":[{"name":"main_query","query":{"datasetName":dsn,"fields":[{"name":f,"expression":f"`{f}`"}],"disaggregated":True}}],
        "spec":{"version":2,"widgetType":"counter","encodings":{"value":{"fieldName":f,"displayName":t}},"frame":{"showTitle":True,"title":t}}},"position":{"x":x,"y":y,"width":w,"height":h}}
# PRE-AGGREGATED bar: simple field refs + disaggregated True (one row per category already)
def bar(n,dsn,xf,yf,title,x,y,w=3,h=6,colors=None,sort=None):
    xsc={"type":"categorical"}
    if sort: xsc["sort"]={"by":sort}
    enc={"x":{"fieldName":xf,"scale":xsc,"displayName":xf},"y":{"fieldName":yf,"scale":{"type":"quantitative"},"displayName":title},"label":{"show":True}}
    spec={"version":3,"widgetType":"bar","encodings":enc,"frame":{"showTitle":True,"title":title}}
    if colors: spec["mark"]={"colors":colors}
    return {"widget":{"name":n,"queries":[{"name":"main_query","query":{"datasetName":dsn,"fields":[{"name":xf,"expression":f"`{xf}`"},{"name":yf,"expression":f"`{yf}`"}],"disaggregated":True}}],"spec":spec},"position":{"x":x,"y":y,"width":w,"height":h}}
def line(n,dsn,xf,yf,title,x,y,w,h):
    enc={"x":{"fieldName":xf,"scale":{"type":"temporal"},"displayName":"Month"},"y":{"fieldName":yf,"scale":{"type":"quantitative"},"displayName":"Retention rate"}}
    return {"widget":{"name":n,"queries":[{"name":"main_query","query":{"datasetName":dsn,"fields":[{"name":xf,"expression":f"`{xf}`"},{"name":yf,"expression":f"`{yf}`"}],"disaggregated":True}}],
        "spec":{"version":3,"widgetType":"line","encodings":enc,"frame":{"showTitle":True,"title":title},"mark":{"colors":[TEAL]}}},"position":{"x":x,"y":y,"width":w,"height":h}}
def multibar(n,dsn,xf,yfields,title,x,y,w,h,colors):
    fields=[{"name":xf,"expression":f"`{xf}`"}]+[{"name":f,"expression":f"`{f}`"} for f,_ in yfields]
    enc={"x":{"fieldName":xf,"scale":{"type":"categorical"},"displayName":"Month"},"y":{"scale":{"type":"quantitative"},"fields":[{"fieldName":f,"displayName":d} for f,d in yfields]}}
    return {"widget":{"name":n,"queries":[{"name":"main_query","query":{"datasetName":dsn,"fields":fields,"disaggregated":True}}],
        "spec":{"version":3,"widgetType":"bar","encodings":enc,"frame":{"showTitle":True,"title":title},"mark":{"colors":colors}}},"position":{"x":x,"y":y,"width":w,"height":h}}
def table(n,dsn,cols,title,x,y,w=6,h=10):
    return {"widget":{"name":n,"queries":[{"name":"main_query","query":{"datasetName":dsn,"fields":[{"name":c[0],"expression":f"`{c[0]}`"} for c in cols],"disaggregated":True}}],
        "spec":{"version":2,"widgetType":"table","encodings":{"columns":[{"fieldName":c[0],"displayName":c[1]} for c in cols]},"frame":{"showTitle":True,"title":title}}},"position":{"x":x,"y":y,"width":w,"height":h}}

L=[
 text("title","# 🛡️  Northwind Mutual — Retention & Risk Command Center",0,0,6,1),
 text("sub","P&C & Life book · unified Policyholder 360 + non-renewal ML model + GenAI Retention Copilot   —   *backup view to the Databricks App*",0,1,6,1),
 counter("k1","kpis","book_m","Annual Book Premium ($M)",0,2,2,3),
 counter("k2","kpis","risk_m","Premium at Risk H+M ($M)",2,2,1,3),
 counter("k3","kpis","high_n","High-Risk Policyholders",3,2,1,3),
 counter("k4","kpis","churn_rate","Non-Renewal Rate (%)",4,2,1,3),
 counter("k5","kpis","recover_m","Recoverable / yr ($M)",5,2,1,3),
 text("h1","## 📉  Retention trend — slipping through rate-hardening, now bending back up",0,5,6,1),
 line("t1","trend","month_start","retention_rate","Renewal / persistency rate (trailing 18 months)",0,6,3,6),
 multibar("t2","trend","month",[("premium_retained","Premium retained"),("premium_lost","Premium lost")],"Premium retained vs lost at renewal",3,6,3,6,[GREEN,RED]),
 text("h2","## 🎯  Where the risk sits",0,12,6,1),
 bar("r1","by_tier","risk_tier","prem_m","Expected premium at risk by tier ($M)",0,13,2,6,TIER),
 bar("r2","by_product","product_line","prem_m","Expected premium at risk by product ($M)",2,13,2,6,[TEAL],sort="y-reversed"),
 bar("r3","by_state","state","prem_k","Top states by expected premium at risk ($K)",4,13,2,6,[AMBER],sort="y-reversed"),
 text("h3","## 🔍  Why they leave  (high-risk cohort skews on premium hikes & competitor shopping)",0,19,6,1),
 bar("d1","drivers","risk_tier","avg_hike","Avg renewal premium increase by tier (%)",0,20,3,6,TIER),
 bar("d2","drivers","risk_tier","avg_shopping","Avg competitor-shopping calls by tier",3,20,3,6,TIER),
 text("h4","## 💰  Proof it works — proactive outreach vs holdout",0,26,6,1),
 bar("c1","campaign","cohort","save_rate","Renewal save rate — treated vs control",0,27,3,6,[GREEN,MUTED]),
 bar("c2","campaign","cohort","premium_recovered","Premium recovered ($)",3,27,3,6,[GREEN,MUTED]),
 text("h5","## 🤖  Retention Copilot — GenAI next-best-action worklist",0,33,6,1),
 table("tbl","copilot",[("first_name","First"),("last_name","Last"),("state","State"),("product_line","Product"),("churn_prob","Churn Prob"),("premium_at_risk","Premium at Risk $"),("hike_pct","Hike %"),("num_complaints","Complaints"),("retention_brief","GenAI Retention Brief")],"Prioritized worklist",0,34,6,10),
]
serialized={"datasets":datasets,"pages":[{"name":wid(),"displayName":"Command Center","pageType":"PAGE_TYPE_CANVAS","layout":L}],"uiSettings":{"theme":{"widgetHeaderAlignment":"ALIGNMENT_UNSPECIFIED"}}}
payload={"display_name":"Insurance Retention & Risk Command Center","warehouse_id":WH,"serialized_dashboard":json.dumps(serialized)}
p=subprocess.run(["databricks","api","patch",f"/api/2.0/lakeview/dashboards/{DID}","--profile",PROFILE,"--json",json.dumps(payload)],capture_output=True,text=True)
print("patch rc",p.returncode, p.stderr[:600] if p.returncode else "OK")
pub=subprocess.run(["databricks","api","post",f"/api/2.0/lakeview/dashboards/{DID}/published","--profile",PROFILE,"--json",json.dumps({"embed_credentials":True,"warehouse_id":WH})],capture_output=True,text=True)
print("publish rc",pub.returncode, pub.stderr[:300] if pub.returncode else "OK")
