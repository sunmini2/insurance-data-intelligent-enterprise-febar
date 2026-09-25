import sys, json, subprocess, time
PROFILE="azure-sunmin"; WAREHOUSE="148ccb90800933a1"
def run_sql(sql):
    payload = {"warehouse_id": WAREHOUSE, "statement": sql, "wait_timeout": "50s", "catalog":"sunmin_catalog"}
    p = subprocess.run(["databricks","api","post","/api/2.0/sql/statements","--profile",PROFILE,"--json",json.dumps(payload)],capture_output=True, text=True)
    if p.returncode != 0: return {"error": p.stderr[:2000]}
    r = json.loads(p.stdout); stmt_id = r.get("statement_id"); state = r.get("status",{}).get("state")
    while state in ("PENDING","RUNNING"):
        time.sleep(2)
        p2 = subprocess.run(["databricks","api","get",f"/api/2.0/sql/statements/{stmt_id}","--profile",PROFILE],capture_output=True, text=True)
        r = json.loads(p2.stdout); state = r.get("status",{}).get("state")
    if state != "SUCCEEDED": return {"error": json.dumps(r.get("status",{}))[:2000]}
    res = r.get("result",{}); return {"ok": True, "rows": res.get("data_array"), "schema":[c["name"] for c in r.get("manifest",{}).get("schema",{}).get("columns",[])]}
if __name__=="__main__":
    sql = sys.stdin.read()
    for stmt in [s.strip() for s in sql.split("\n---GO---\n") if s.strip()]:
        out = run_sql(stmt)
        if out.get("error"): print("ERROR:\n", stmt[:300], "\n>>", out["error"]); sys.exit(1)
        label = stmt.strip().split("\n")[0][:70]
        print(f"OK: {label}")
        if out.get("rows"):
            for row in out["rows"][:30]: print("   ", row)
