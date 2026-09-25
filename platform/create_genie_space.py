import json, subprocess, uuid
PROFILE="azure-sunmin"; WH="148ccb90800933a1"; SC="sunmin_catalog.insurance_demo"
def gid(): return uuid.uuid4().hex
instr = ("This Genie Space serves executives at a P&C and Life insurance carrier (Northwind Mutual). "
"The core entity is the policyholder; 'churn' means non-renewal at the policy anniversary. "
"gold_book_scored is the primary table with ML churn_probability, risk_tier (High/Medium/Low) and premium_at_risk per policyholder. "
"'Premium at risk' = sum of premium_at_risk; 'book premium' = sum of annual_premium; non-renewal rate = avg(churned)*100. "
"When asked who is at risk, prefer risk_tier='High'. Key drivers: premium_change_pct, num_complaints, num_cancel_intent (competitor shopping), denied claims. Express currency in USD.")
questions=["What is our total annual book premium and non-renewal rate?",
 "How much premium is at risk in the High and Medium tiers?",
 "Which product line has the highest non-renewal rate?",
 "Show the top 10 high-risk policyholders by premium at risk.",
 "What is the average renewal premium increase for High-risk vs Low-risk policyholders?"]
tables=sorted([f"{SC}.gold_book_scored",f"{SC}.gold_policyholder_360",f"{SC}.gold_retention_copilot"])
serialized={"version":2,
 "config":{"sample_questions":[{"id":gid(),"question":[q]} for q in questions]},
 "data_sources":{"tables":[{"identifier":t} for t in tables]},
 "instructions":{"text_instructions":[{"id":gid(),"content":[instr]}]}}
payload={"title":"Insurance Retention & Risk — Executive Genie",
 "description":"Natural-language Q&A over the P&C/Life book: premium at risk, non-renewal drivers, and the retention worklist.",
 "warehouse_id":WH,"serialized_space":json.dumps(serialized)}
p=subprocess.run(["databricks","api","post","/api/2.0/genie/spaces","--profile",PROFILE,"--json",json.dumps(payload)],capture_output=True,text=True)
print("rc",p.returncode)
if p.returncode!=0: print("ERR",p.stderr[:1500]); raise SystemExit
r=json.loads(p.stdout); sid=r.get("space_id") or r.get("id")
print("SPACE_ID="+str(sid)); open("/tmp/genieid.txt","w").write(str(sid))
