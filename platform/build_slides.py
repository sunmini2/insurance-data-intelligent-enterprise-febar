import json, subprocess, sys, urllib.request, urllib.error
TOKEN=subprocess.run(["gcloud","auth","application-default","print-access-token"],capture_output=True,text=True).stdout.strip()
QUOTA="gcp-dev-field-eng-aiapiquota"; BASE="https://slides.googleapis.com/v1/presentations"
PID="1tZdU7_eSmJCygEgmYhsakkzSRSgenq_htCPgM8SVB1A"
def api(url, method="POST", body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url, data=data, method=method,
        headers={"Authorization":f"Bearer {TOKEN}","x-goog-user-project":QUOTA,"Content-Type":"application/json"})
    try: return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:900]); sys.exit(1)
_n=[0]
def oid(): _n[0]+=1; return f"o{_n[0]:05d}x"
def rgb(h): h=h.lstrip('#'); return {"red":int(h[0:2],16)/255,"green":int(h[2:4],16)/255,"blue":int(h[4:6],16)/255}
C={"teal":"#1B5161","dark":"#1B3037","red":"#FF3620","amber":"#FFAB00","green":"#00A972","muted":"#618793","white":"#FFFFFF",
   "lgray":"#F1F1F1","lteal":"#9EB7BE","cardteal":"#E9F0F2","cardgray":"#EEF1F2","cardgreen":"#E3F3EC","callout":"#98102A"}
IN=914400
info=api(f"{BASE}/{PID}","GET")
reqs=[{"deleteObject":{"objectId":s["objectId"]}} for s in info["slides"]]
SL=["slide1","slide2","slide3","slide4","slide5"]
reqs+=[{"createSlide":{"objectId":s,"slideLayoutReference":{"predefinedLayout":"BLANK"}}} for s in SL]
api(f"{BASE}/{PID}:batchUpdate", body={"requests":reqs})

def shape(r,sid,typ,x,y,w,h,fill=None,line=False):
    o=oid(); r.append({"createShape":{"objectId":o,"shapeType":typ,"elementProperties":{"pageObjectId":sid,
        "size":{"width":{"magnitude":w,"unit":"EMU"},"height":{"magnitude":h,"unit":"EMU"}},
        "transform":{"scaleX":1,"scaleY":1,"translateX":x,"translateY":y,"unit":"EMU"}}}})
    props={"outline":{"propertyState":"NOT_RENDERED"}} if not line else {}
    if fill is not None: props["shapeBackgroundFill"]={"solidFill":{"color":{"rgbColor":rgb(fill)}}}
    if props: r.append({"updateShapeProperties":{"objectId":o,"fields":",".join(props.keys()),"shapeProperties":props}})
    return o
def box(r,sid,x,y,w,h): return shape(r,sid,"TEXT_BOX",x,y,w,h)
def txt(r,o,t): r.append({"insertText":{"objectId":o,"text":t,"insertionIndex":0}})
def st(r,o,size,color,bold=False,rng=None):
    tr={"type":"ALL"} if rng is None else {"type":"FIXED_RANGE","startIndex":rng[0],"endIndex":rng[1]}
    r.append({"updateTextStyle":{"objectId":o,"textRange":tr,"fields":"bold,fontSize,foregroundColor,fontFamily",
        "style":{"bold":bold,"fontSize":{"magnitude":size,"unit":"PT"},"fontFamily":"Barlow","foregroundColor":{"opaqueColor":{"rgbColor":rgb(color)}}}}})
def para(r,o,align="START",space=None):
    stl={"alignment":align}; f="alignment"
    if space is not None: stl["spaceBelow"]={"magnitude":space,"unit":"PT"}; f+=",spaceBelow"
    r.append({"updateParagraphStyle":{"objectId":o,"textRange":{"type":"ALL"},"style":stl,"fields":f}})
def bullets(r,o): r.append({"createParagraphBullets":{"objectId":o,"textRange":{"type":"ALL"},"bulletPreset":"BULLET_DISC_CIRCLE_SQUARE"}})
def bg(r,sid,color): r.append({"updatePageProperties":{"objectId":sid,"fields":"pageBackgroundFill",
    "pageProperties":{"pageBackgroundFill":{"solidFill":{"color":{"rgbColor":rgb(color)}}}}}})
def ctitle(r,sid,title,size=20):
    t=box(r,sid,int(0.5*IN),int(0.32*IN),int(9.0*IN),int(0.7*IN)); txt(r,t,title); st(r,t,size,C["teal"],True); para(r,t)
    shape(r,sid,"RECTANGLE",int(0.52*IN),int(1.0*IN),int(1.05*IN),int(0.05*IN),C["red"])
def card(r,sid,x,y,w,h,fill,title,desc,tcolor):
    o=shape(r,sid,"ROUND_RECTANGLE",x,y,w,h,fill)
    full=title+"\n"+desc
    txt(r,o,full); st(r,o,8,C["dark"]); st(r,o,9.5,tcolor,True,rng=[0,len(title)])
    r.append({"updateParagraphStyle":{"objectId":o,"textRange":{"type":"ALL"},"style":{"alignment":"CENTER"},"fields":"alignment"}})
    r.append({"updateShapeProperties":{"objectId":o,"fields":"contentAlignment","shapeProperties":{"contentAlignment":"MIDDLE"}}})
    return o

# ============ SLIDE 1 — TITLE ============
r=[]; bg(r,"slide1",C["dark"])
t=box(r,"slide1",int(0.55*IN),int(1.35*IN),int(9.0*IN),int(1.0*IN)); txt(r,t,"From Scattered Data to Retained Premium"); st(r,t,30,C["white"],True); para(r,t)
shape(r,"slide1","RECTANGLE",int(0.57*IN),int(2.5*IN),int(1.6*IN),int(0.07*IN),C["red"])
s=box(r,"slide1",int(0.55*IN),int(2.7*IN),int(9.2*IN),int(0.7*IN)); txt(r,s,"Turning an $11.6M book's blind spots into a governed, AI-powered retention engine"); st(r,s,15,C["lteal"]); para(r,s)
# stat strip
stats=[("$4.8M","premium at risk today"),("+24 pts","proven retention lift"),("~$1.2M / yr","recoverable premium")]
sx=int(0.55*IN)
for big,lab in stats:
    o=box(r,"slide1",sx,int(4.15*IN),int(2.9*IN),int(0.95*IN)); txt(r,o,big+"\n"+lab)
    st(r,o,22,C["amber"] if big!="+24 pts" else C["green"],True); st(r,o,11,C["lteal"],rng=[len(big)+1,len(big)+1+len(lab)])
    para(r,o,"START"); sx+=int(3.05*IN)
f=box(r,"slide1",int(0.55*IN),int(5.15*IN),int(9.0*IN),int(0.35*IN)); txt(r,f,"Solutions Architect · Insurance (P&C / Life)"); st(r,f,10,C["muted"]); para(r,f)
api(f"{BASE}/{PID}:batchUpdate", body={"requests":r})

# ============ SLIDE 2 — PROBLEM / COST OF INACTION ============
r=[]; bg(r,"slide2",C["white"]); ctitle(r,"slide2","The $4.8M You Can't See Coming")
lh=box(r,"slide2",int(0.55*IN),int(1.2*IN),int(4.35*IN),int(0.4*IN)); txt(r,lh,"WHAT'S HAPPENING"); st(r,lh,12,C["teal"],True); para(r,lh)
lb=box(r,"slide2",int(0.6*IN),int(1.65*IN),int(4.35*IN),int(2.7*IN))
txt(r,lb,"Data fractured across policy admin, claims and CRM — no single source of truth\nRetention, risk and pricing decisions run on gut feel and stale spreadsheets\nYears of claims notes and customer history sit unused as a dormant asset")
st(r,lb,12.5,C["dark"]); para(r,lb,space=10); bullets(r,lb)
rh=box(r,"slide2",int(5.15*IN),int(1.2*IN),int(4.35*IN),int(0.4*IN)); txt(r,rh,"WHAT IT'S COSTING YOU"); st(r,rh,12,C["red"],True); para(r,rh)
rb=box(r,"slide2",int(5.2*IN),int(1.65*IN),int(4.35*IN),int(2.7*IN))
txt(r,rb,"~1 in 4 renewals lapsing — $4.8M of premium at risk, invisible until the notice goes out\nDecisions take weeks; every executive meeting debates whose numbers are right\nGeneric service at scale — no proactive save, no personalization, no learning loop")
st(r,rb,12.5,C["dark"]); para(r,rb,space=10); bullets(r,rb)
cb=shape(r,"slide2","ROUND_RECTANGLE",int(0.55*IN),int(4.55*IN),int(8.95*IN),int(0.85*IN),C["callout"])
txt(r,cb,"The question isn't whether to modernize — it's what another renewal cycle of flying blind costs you.")
st(r,cb,13,C["white"],True)
r.append({"updateParagraphStyle":{"objectId":cb,"textRange":{"type":"ALL"},"style":{"alignment":"CENTER"},"fields":"alignment"}})
r.append({"updateShapeProperties":{"objectId":cb,"fields":"contentAlignment","shapeProperties":{"contentAlignment":"MIDDLE"}}})
api(f"{BASE}/{PID}:batchUpdate", body={"requests":r})

# ============ SLIDE 3 — ARCHITECTURE DIAGRAM ============
r=[]; bg(r,"slide3",C["white"]); ctitle(r,"slide3","From Scattered Data to Guided Action — How It Fits Together")
stages=[
 (C["cardgray"], "YOUR DATA, TODAY", "Policy, claims and service records — scattered across systems", C["dark"]),
 (C["cardteal"], "ONE TRUSTED VIEW", "A single, secure picture of every policyholder", C["teal"]),
 (C["cardteal"], "SEE RISK EARLY", "Know who is likely to leave — before the renewal notice", C["teal"]),
 (C["cardteal"], "GUIDED NEXT STEP", "Turn years of history into a ready-to-act recommendation", C["teal"]),
 (C["cardgreen"],"IN YOUR TEAM'S HANDS", "Leaders and agents see it — and act — in one place", C["green"]),
]
bw=int(1.62*IN); step=int(1.9*IN); x0=int(0.35*IN); yb=int(1.75*IN); bh=int(2.15*IN)
for i,(fill,title,desc,tc) in enumerate(stages):
    card(r,"slide3", x0+i*step, yb, bw, bh, fill, title, desc, tc)
    if i<len(stages)-1:
        ax=x0+i*step+bw+int(0.03*IN)
        shape(r,"slide3","RIGHT_ARROW", ax, yb+int(0.85*IN), int(0.24*IN), int(0.45*IN), C["red"])
gv=shape(r,"slide3","ROUND_RECTANGLE",int(0.35*IN),int(4.25*IN),int(9.25*IN),int(0.72*IN),C["teal"])
txt(r,gv,"🔒  Secure, governed and audit-ready at every step — from raw data to the action your team takes")
st(r,gv,12.5,C["white"],True)
r.append({"updateParagraphStyle":{"objectId":gv,"textRange":{"type":"ALL"},"style":{"alignment":"CENTER"},"fields":"alignment"}})
r.append({"updateShapeProperties":{"objectId":gv,"fields":"contentAlignment","shapeProperties":{"contentAlignment":"MIDDLE"}}})
cap=box(r,"slide3",int(0.35*IN),int(5.05*IN),int(9.25*IN),int(0.35*IN)); txt(r,cap,"Built on the controls and tools your teams already trust — nothing to rip and replace."); st(r,cap,10,C["muted"]); para(r,cap,"CENTER")
api(f"{BASE}/{PID}:batchUpdate", body={"requests":r})

# ============ SLIDE 4 — HOW WE SOLVE IT & IMPACT (table) ============
r=[]; bg(r,"slide4",C["white"]); ctitle(r,"slide4","How We Solve It — and What It's Worth to You",19)
api(f"{BASE}/{PID}:batchUpdate", body={"requests":r})
data=[["Executive risk","How we solve it","Proven impact"],
 ["Revenue leaking from silent non-renewals","Predictive churn scoring + GenAI Retention Copilot","+24-pt save rate in test → ~$1.2M/yr recoverable"],
 ["Decisions take weeks; numbers disputed","Governed Policyholder 360 + Genie natural-language Q&A","One source of truth — answers in seconds, not weeks"],
 ["Institutional knowledge sits unused","GenAI turns claims notes + history into next-best-action","Agents act in one screen (~30s) — personalized at scale"],
 ["AI & data-trust / compliance exposure","Unity Catalog governance, lineage & PII controls","Audit-ready, one governed track — no shadow AI"]]
colw=[int(3.0*IN),int(3.3*IN),int(3.1*IN)]; rows=len(data); cols=3; tid="slide4_tbl"
rt=[{"createTable":{"objectId":tid,"rows":rows,"columns":cols,"elementProperties":{"pageObjectId":"slide4",
    "size":{"width":{"magnitude":int(sum(colw)),"unit":"EMU"},"height":{"magnitude":int(3.9*IN),"unit":"EMU"}},
    "transform":{"scaleX":1,"scaleY":1,"translateX":int(0.42*IN),"translateY":int(1.25*IN),"unit":"EMU"}}}}]
for ri in range(rows-1,-1,-1):
    for ci in range(cols-1,-1,-1):
        rt.append({"insertText":{"objectId":tid,"cellLocation":{"rowIndex":ri,"columnIndex":ci},"text":data[ri][ci],"insertionIndex":0}})
api(f"{BASE}/{PID}:batchUpdate", body={"requests":rt})
r2=[{"updateTableCellProperties":{"objectId":tid,"tableRange":{"location":{"rowIndex":0,"columnIndex":0},"rowSpan":1,"columnSpan":cols},
    "fields":"tableCellBackgroundFill","tableCellProperties":{"tableCellBackgroundFill":{"solidFill":{"color":{"rgbColor":rgb(C["teal"])}}}}}}]
for ci,cw in enumerate(colw):
    r2.append({"updateTableColumnProperties":{"objectId":tid,"columnIndices":[ci],"fields":"columnWidth","tableColumnProperties":{"columnWidth":{"magnitude":cw,"unit":"EMU"}}}})
for ri in range(1,rows):
    if ri%2==0:
        r2.append({"updateTableCellProperties":{"objectId":tid,"tableRange":{"location":{"rowIndex":ri,"columnIndex":0},"rowSpan":1,"columnSpan":cols},
            "fields":"tableCellBackgroundFill","tableCellProperties":{"tableCellBackgroundFill":{"solidFill":{"color":{"rgbColor":rgb(C["lgray"])}}}}}})
    # emphasize impact column (green)
    r2.append({"updateTableCellProperties":{"objectId":tid,"tableRange":{"location":{"rowIndex":ri,"columnIndex":2},"rowSpan":1,"columnSpan":1},
        "fields":"tableCellBackgroundFill","tableCellProperties":{"tableCellBackgroundFill":{"solidFill":{"color":{"rgbColor":rgb(C["cardgreen"])}}}}}})
for ri in range(rows):
    for ci in range(cols):
        hdr=ri==0
        color=C["white"] if hdr else (C["dark"] if ci==2 else C["dark"])
        r2.append({"updateTextStyle":{"objectId":tid,"cellLocation":{"rowIndex":ri,"columnIndex":ci},"textRange":{"type":"ALL"},
            "fields":"bold,fontSize,foregroundColor,fontFamily","style":{"bold":hdr or ci==0 or ci==2,"fontSize":{"magnitude":11 if hdr else 10,"unit":"PT"},
            "fontFamily":"Barlow","foregroundColor":{"opaqueColor":{"rgbColor":rgb(color)}}}}})
        r2.append({"updateParagraphStyle":{"objectId":tid,"cellLocation":{"rowIndex":ri,"columnIndex":ci},"textRange":{"type":"ALL"},
            "fields":"spaceAbove,spaceBelow","style":{"spaceAbove":{"magnitude":4,"unit":"PT"},"spaceBelow":{"magnitude":4,"unit":"PT"}}}})
api(f"{BASE}/{PID}:batchUpdate", body={"requests":r2})

# ============ SLIDE 5 — 30 DAYS TO FIRST VALUE (timeline) ============
r=[]; bg(r,"slide5",C["white"]); ctitle(r,"slide5","30 Days to First Value")
weeks=[("WEEK 1","Connect live policy & claims via Lakeflow Connect; agree the retention target"),
 ("WEEK 2","Harden the Policyholder 360 in Unity Catalog with your security team"),
 ("WEEK 3","Retrain on your data; validate with actuarial; monitor for drift"),
 ("WEEK 4","Pilot the Retention Copilot on the high-risk book; measure saved renewals")]
bw=int(2.12*IN); step=int(2.28*IN); x0=int(0.42*IN); yb=int(1.5*IN); bh=int(2.0*IN)
for i,(wk,desc) in enumerate(weeks):
    card(r,"slide5", x0+i*step, yb, bw, bh, C["cardteal"], wk, desc, C["teal"])
    if i<len(weeks)-1:
        shape(r,"slide5","RIGHT_ARROW", x0+i*step+bw+int(0.01*IN), yb+int(0.78*IN), int(0.16*IN), int(0.4*IN), C["amber"])
ask=shape(r,"slide5","ROUND_RECTANGLE",int(0.42*IN),int(3.9*IN),int(9.16*IN),int(1.0*IN),C["dark"])
txt(r,ask,"THE ASK: a 30-day paid pilot on your at-risk book.\nFirst value in weeks — measured against a holdout, on your data, not our synthetic numbers.")
st(r,ask,13,C["white"],True); st(r,ask,11.5,C["lteal"],rng=[len("THE ASK: a 30-day paid pilot on your at-risk book.")+1, len("THE ASK: a 30-day paid pilot on your at-risk book.")+1+len("First value in weeks — measured against a holdout, on your data, not our synthetic numbers.")])
r.append({"updateParagraphStyle":{"objectId":ask,"textRange":{"type":"ALL"},"style":{"alignment":"CENTER"},"fields":"alignment"}})
r.append({"updateShapeProperties":{"objectId":ask,"fields":"contentAlignment","shapeProperties":{"contentAlignment":"MIDDLE"}}})
bey=box(r,"slide5",int(0.42*IN),int(5.0*IN),int(9.16*IN),int(0.4*IN)); txt(r,bey,"Then: extend to fraud & loss-ratio, add CI/CD, and scale across the book."); st(r,bey,10,C["muted"]); para(r,bey,"CENTER")
api(f"{BASE}/{PID}:batchUpdate", body={"requests":r})
print("URL=https://docs.google.com/presentation/d/"+PID+"/edit")
