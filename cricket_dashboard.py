import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="Cricket Analytics", layout="wide", page_icon="🏏",
                   initial_sidebar_state="collapsed")

RAW_BASE = "https://raw.githubusercontent.com/mmrayyan2005-dev/cricket-analytics_-/main"

BG="#080c14"; CARD="#131929"; TEXT="#e8edf5"; GRID="#1e2840"
FC={"ODI":"#00e5a0","Test":"#3d8bff","T20I":"#ff4d6d",
    "IPL":"#fb923c","PSL":"#a78bfa","WPL":"#f472b6","BBL":"#fb7185","CPL":"#34d399"}
FORMATS=["ODI","Test","T20I","IPL","PSL","WPL","BBL","CPL"]
FORMAT_META={
    "ODI":("🌐","#00e5a0","#00c88a"),"Test":("🏛️","#3d8bff","#6aa8ff"),
    "T20I":("⚡","#ff4d6d","#ff7b8e"),"IPL":("🏏","#fb923c","#fbbf24"),
    "PSL":("🟣","#a78bfa","#c4b5fd"),"WPL":("💜","#f472b6","#fb7185"),
    "BBL":("🔥","#fb7185","#fda4af"),"CPL":("🌴","#34d399","#00e5a0"),
}
BASE=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
          font=dict(color=TEXT,family="Inter,sans-serif",size=12),
          legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,
                      bgcolor="rgba(0,0,0,0)",font=dict(size=11)),
          xaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,color=TEXT,fixedrange=True),
          yaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,color=TEXT,fixedrange=True),
          dragmode=False)
M_DEFAULT=dict(l=8,r=8,t=48,b=8)
M_BARV=dict(l=8,r=8,t=48,b=60)
CFG=dict(config={"displayModeBar":False,"scrollZoom":False,"doubleClick":False,"responsive":True},use_container_width=True)

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap');
:root{
  --bg:#080c14;--surface:#0e1420;--card:#131929;--border:#1e2840;
  --accent:#00e5a0;--accent2:#3d8bff;--warn:#ff4d6d;--gold:#fbbf24;
  --text:#e8edf5;--muted:#5a6580;--subtle:#8899bb;
  --radius:14px;--radius-sm:8px;
  --font-head:'Syne',sans-serif;--font-body:'Inter',sans-serif;
}
html,body,[class*="css"]{font-family:var(--font-body);background:var(--bg);color:var(--text)}
.block-container{padding:0 !important;max-width:100% !important}
[data-testid="stSidebar"]{display:none !important}
[data-testid="stMetric"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;padding:14px 16px!important;position:relative;overflow:hidden}
[data-testid="stMetric"]:hover{border-color:#2e4060!important}
[data-testid="stMetric"]::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--accent),var(--accent2));opacity:0.5}
[data-testid="stMetricLabel"]{font-size:10px!important;font-weight:600!important;color:var(--muted)!important;text-transform:uppercase;letter-spacing:1px!important}
[data-testid="stMetricValue"]{font-family:var(--font-head)!important;font-size:22px!important;font-weight:800!important;color:var(--text)!important;line-height:1.2!important}
div[data-baseweb="tab-list"]{gap:4px!important;flex-wrap:wrap!important;background:transparent!important;border-bottom:1px solid var(--border)!important;padding-bottom:6px!important}
div[data-baseweb="tab"]{border-radius:var(--radius-sm)!important;padding:6px 14px!important;background:var(--card)!important;font-weight:600!important;font-size:12px!important;color:var(--subtle)!important;border:1px solid var(--border)!important}
div[data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(135deg,#004d35,#003d68)!important;border-color:var(--accent)!important;color:var(--accent)!important}
div[data-baseweb="tab-highlight"],div[data-baseweb="tab-border"]{display:none!important}
[data-testid="stTextInput"] input{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--radius-sm)!important;color:var(--text)!important;font-size:15px!important;padding:11px 14px!important}
[data-testid="stTextInput"] input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(0,229,160,.1)!important}
[data-testid="stSelectbox"]>div>div{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--radius-sm)!important}
[data-testid="stRadio"]>div{flex-wrap:wrap!important;gap:5px!important}
[data-testid="stRadio"] label{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--radius-sm)!important;padding:5px 13px!important;font-size:12px!important;font-weight:600!important;color:var(--subtle)!important;cursor:pointer}
[data-testid="stRadio"] label:has(input:checked){border-color:var(--accent)!important;color:var(--accent)!important;background:rgba(0,229,160,.08)!important}
.stDataFrame{border-radius:var(--radius)!important;overflow:hidden!important;border:1px solid var(--border)!important}
.stDataFrame thead th{font-size:11px!important;font-weight:700!important;text-transform:uppercase;letter-spacing:.6px;background:var(--surface)!important;color:var(--muted)!important;padding:10px 12px!important}
.stDataFrame tbody td{font-size:12px!important;padding:8px 12px!important}
hr{border:none!important;border-top:1px solid var(--border)!important;margin:16px 0!important}
.js-plotly-plot{touch-action:pan-y!important}
div[data-testid="stHorizontalBlock"]>div[data-testid="column"]{min-width:0!important;flex:1 1 auto}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
@keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.8)}}
.ca-fade{animation:fadeUp .4s ease both}
.ca-shimmer{background:linear-gradient(90deg,var(--accent) 0%,var(--accent2) 40%,var(--accent) 80%);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 3s linear infinite}
.ca-live{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--accent);animation:pulse-dot 1.8s ease infinite;vertical-align:middle;margin-right:4px}

/* ── TOP NAV BAR ── */
.ca-topnav{
  position:sticky;top:0;z-index:999;
  background:rgba(8,12,20,.92);
  backdrop-filter:blur(16px);
  -webkit-backdrop-filter:blur(16px);
  border-bottom:1px solid var(--border);
  padding:0 24px;
  display:flex;align-items:center;gap:0;
  height:56px;
  width:100%;
  box-sizing:border-box;
}
.ca-topnav-brand{
  display:flex;align-items:center;gap:8px;
  font-family:var(--font-head);font-size:16px;font-weight:800;
  color:#fff;white-space:nowrap;margin-right:24px;flex-shrink:0;
}
.ca-topnav-brand span{color:var(--accent)}
.ca-topnav-links{
  display:flex;align-items:center;gap:2px;
  flex:1;overflow-x:auto;
  scrollbar-width:none;-ms-overflow-style:none;
}
.ca-topnav-links::-webkit-scrollbar{display:none}
.ca-navbtn{
  display:flex;align-items:center;gap:5px;
  padding:6px 12px;border-radius:8px;
  font-size:12px;font-weight:600;
  color:var(--subtle);white-space:nowrap;
  cursor:pointer;border:none;background:transparent;
  transition:all .15s;font-family:var(--font-body);
  text-decoration:none;
}
.ca-navbtn:hover{background:rgba(255,255,255,.06);color:var(--text)}
.ca-navbtn.active{background:rgba(0,229,160,.1);color:var(--accent)}
.ca-topnav-status{
  display:flex;align-items:center;gap:6px;
  padding:4px 10px;border-radius:20px;
  background:rgba(0,229,160,.06);border:1px solid rgba(0,229,160,.15);
  font-size:10px;font-weight:600;color:var(--accent);
  white-space:nowrap;flex-shrink:0;margin-left:12px;
}
.ca-content{padding:20px 24px 40px}

/* ── CARDS ── */
.ca-section-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);padding:20px;margin-bottom:16px;
}
.ca-section-header{
  display:flex;align-items:center;gap:10px;margin-bottom:16px;
}
.ca-section-emoji{font-size:24px;line-height:1}
.ca-section-title{font-family:var(--font-head);font-size:18px;font-weight:800;color:#fff}
.ca-section-sub{font-size:12px;color:var(--muted);margin-top:2px}

/* ── HOME GRID ── */
.ca-home-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-bottom:24px}
.ca-feature-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);padding:18px 20px;
  cursor:pointer;transition:all .2s;text-decoration:none;display:block;
}
.ca-feature-card:hover{border-color:#2e4060;transform:translateY(-2px);background:#161d2e}
.ca-feature-icon{font-size:28px;margin-bottom:10px}
.ca-feature-title{font-family:var(--font-head);font-size:15px;font-weight:800;color:#fff;margin-bottom:4px}
.ca-feature-desc{font-size:12px;color:var(--muted);line-height:1.5}

/* ── MOBILE ── */
@media(max-width:640px){
  .ca-content{padding:12px 14px 32px}
  .ca-topnav{padding:0 12px;height:52px}
  .ca-topnav-brand{font-size:14px;margin-right:10px}
  .ca-navbtn{padding:5px 8px;font-size:11px}
  .ca-navbtn .nav-label{display:none}
  .ca-topnav-status{display:none}
  [data-testid="stMetricValue"]{font-size:18px!important}
  [data-testid="stMetricLabel"]{font-size:9px!important}
  [data-testid="stMetric"]{padding:10px 12px!important}
  [data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:8px!important}
  [data-testid="stHorizontalBlock"]>div[data-testid="column"]{width:100%!important;min-width:100%!important;flex:1 1 100%!important}
  div[data-baseweb="tab"]{padding:5px 8px!important;font-size:10px!important}
  .stPlotlyChart{overflow-x:auto!important}
  [data-testid="stRadio"] label{font-size:11px!important;padding:4px 8px!important}
  .ca-home-grid{grid-template-columns:1fr 1fr}
  .ca-feature-icon{font-size:22px;margin-bottom:6px}
  .ca-feature-title{font-size:13px}
  .ca-feature-desc{display:none}
}
@media(min-width:641px) and (max-width:900px){
  .ca-content{padding:16px 18px 32px}
  [data-testid="stMetricValue"]{font-size:20px!important}
}
</style>""", unsafe_allow_html=True)

# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load():
    def read(name):
        try: return pd.read_csv(f"{RAW_BASE}/{name}")
        except: return pd.DataFrame()
    return (read("cricket_batting_stats.csv"),read("cricket_bowling_stats.csv"),
            read("cricket_batting_by_format.csv"),read("cricket_bowling_by_format.csv"),
            read("cricket_batting_yearly.csv"),read("cricket_bowling_yearly.csv"),
            read("cricket_batting_venue.csv"),read("cricket_batting_opponent.csv"),
            read("cricket_bowling_venue.csv"),read("cricket_bowling_opponent.csv"),
            read("cricket_batter_vs_bowler.csv"),read("cricket_bowler_vs_batter.csv"),
            read("cricket_bat_form_ratings.csv"),read("cricket_bowl_form_ratings.csv"),
            read("cricket_bat_similarity.csv"),read("cricket_bowl_similarity.csv"),
            read("cricket_bat_innings.csv"),read("cricket_bowl_innings.csv"))

@st.cache_data(ttl=3600, show_spinner=False)
def get_last_updated():
    try:
        r=requests.get(f"{RAW_BASE}/last_updated.txt",timeout=5)
        if r.status_code==200: return r.text.strip()
    except: pass
    return None

with st.spinner("Loading cricket data..."):
    (batting,bowling,bat_fmt,bowl_fmt,bat_yr,bowl_yr,bat_ven,bat_opp,
     bowl_ven,bowl_opp,bvb,wvb,bat_form,bowl_form,bat_sim,bowl_sim,bat_inn,bowl_inn)=load()

def get_all_formats(df,col="format"):
    if df.empty or col not in df.columns: return ["ODI","Test","T20I","IPL","PSL"]
    return sorted(df[col].unique().tolist(),key=lambda x:FORMATS.index(x) if x in FORMATS else 99)

ALL_FMT=get_all_formats(bat_fmt)

def avail(df,col):
    return sorted(df[col].unique().tolist(),key=lambda x:FORMATS.index(x) if x in FORMATS else 99)

def find_rows(df, name_col, query):
    import re as _re
    if df.empty: return pd.DataFrame()
    q = query.strip()
    if not q: return pd.DataFrame()
    parts = q.split()
    # 1. Exact full match
    mask = df[name_col].str.match(r"(?i)^"+_re.escape(q)+r"$", na=False)
    if mask.any(): return df[mask]
    # 2. Contains full query
    mask = df[name_col].str.contains(_re.escape(q), case=False, na=False)
    if mask.any(): return df[mask]
    # 3. Multi-word: Initial + Last
    if len(parts) >= 2:
        initial = parts[0][0].upper()
        last = _re.escape(parts[-1])
        mask = df[name_col].str.match(rf"(?i)^{initial}\b.*\b{last}$", na=False)
        if mask.any(): return df[mask]
    # 4. Single word: last-word match only
    if len(parts) == 1 and len(q) >= 3:
        mask = df[name_col].str.contains(rf"(?i)\b{_re.escape(q)}$", na=False, regex=True)
        if mask.any(): return df[mask]
        mask = df[name_col].str.contains(rf"(?i)^{_re.escape(q)}\b", na=False, regex=True)
        if mask.any(): return df[mask]
    return pd.DataFrame()

def ch(fig, h=380, margin=None):
    fig.update_layout(**BASE, height=h, margin=margin or M_DEFAULT)
    st.plotly_chart(fig, **CFG)

def bar_h(df, x, y, col, scale, title, min_h=400):
    if df.empty: return go.Figure()
    n = len(df)
    h = max(min_h, n*52+80)
    xmax = float(df[x].max())*1.22
    fig = px.bar(df,x=x,y=y,orientation="h",color=col,color_continuous_scale=scale,title=title)
    fig.update_traces(marker_line_width=0,text=df[x].round(1).astype(str),
                      textposition="outside",textfont=dict(size=11,color=TEXT),cliponaxis=False)
    fig.update_layout(**BASE,height=h,coloraxis_showscale=False,
                      margin=dict(l=20,r=90,t=48,b=8),bargap=0.28)
    fig.update_yaxes(categoryorder="total ascending",showgrid=False,title="",
                     tickfont=dict(size=12,color=TEXT),automargin=True,tickmode="linear")
    fig.update_xaxes(showgrid=True,gridcolor=GRID,title="",tickfont=dict(size=11),range=[0,xmax])
    return fig

def bar_v(df, x, y, title, color, h=360):
    if df.empty: return go.Figure()
    fig = px.bar(df,x=x,y=y,text=y,title=title,color_discrete_sequence=[color])
    fig.update_traces(textposition="outside",textfont=dict(size=12,color=TEXT),marker_line_width=0)
    fig.update_layout(**BASE,height=h,showlegend=False,margin=M_BARV)
    fig.update_xaxes(tickmode="linear",tickangle=-40,showgrid=False,tickfont=dict(size=12),automargin=True)
    fig.update_yaxes(showgrid=True,gridcolor=GRID)
    return fig

def line(df, x, y, title, color, h=280):
    if df.empty: return go.Figure()
    fig = px.line(df,x=x,y=y,markers=True,title=title)
    fig.update_traces(line=dict(color=color,width=3),marker=dict(size=8,color=color,line=dict(width=2,color=BG)))
    fig.update_layout(**BASE,height=h,margin=M_DEFAULT)
    return fig

def donut(labels, values, colors, title):
    fig = go.Figure(go.Pie(labels=labels,values=values,hole=0.55,
        marker=dict(colors=colors,line=dict(color=BG,width=3)),
        textinfo="percent+label",textfont=dict(size=13,color=TEXT)))
    fig.update_layout(**BASE,height=300,title=title,showlegend=False,margin=M_DEFAULT)
    return fig

def metrics(d):
    items=list(d.items())
    chunk=3
    for i in range(0,len(items),chunk):
        cols=st.columns(len(items[i:i+chunk]))
        for c,(k,v) in zip(cols,items[i:i+chunk]): c.metric(k,v)

NAME_ALIASES={
    "steve smith":"SPD Smith","smith":"SPD Smith","hazelwood":"JR Hazlewood",
    "josh hazelwood":"JR Hazlewood","hazlewood":"JR Hazlewood","warner":"DA Warner",
    "david warner":"DA Warner","rohit":"RG Sharma","rohit sharma":"RG Sharma",
    "bumrah":"JJ Bumrah","jasprit bumrah":"JJ Bumrah","starc":"MA Starc",
    "mitchell starc":"MA Starc","kohli":"V Kohli","virat kohli":"V Kohli",
    "babar":"Babar Azam","de villiers":"AB de Villiers","ab de villiers":"AB de Villiers",
    "stokes":"BA Stokes","ben stokes":"BA Stokes","root":"JE Root","joe root":"JE Root",
    "anderson":"JM Anderson","james anderson":"JM Anderson","broad":"SCJ Broad",
    "stuart broad":"SCJ Broad","afridi":"Shahid Afridi","shaheen":"Shaheen Shah Afridi",
    "rizwan":"Mohammad Rizwan","rashid":"Rashid Khan","buttler":"JC Buttler",
    "jos buttler":"JC Buttler","maxwell":"GJ Maxwell","dhoni":"MS Dhoni",
    "sachin":"SR Tendulkar","tendulkar":"SR Tendulkar","ponting":"RT Ponting",
    "sangakkara":"KC Sangakkara","malinga":"SL Malinga",
    "fakhar":"Fakhar Zaman","fakhar zaman":"Fakhar Zaman","imam":"Imam-ul-Haq",
    "iftikhar":"Iftikhar Ahmed","naseem":"Naseem Shah","shadab":"Shadab Khan",
    "smriti":"Smriti Mandhana","mandhana":"Smriti Mandhana","smriti mandhana":"Smriti Mandhana",
    "shafali":"Shafali Verma","verma":"Shafali Verma",
    "harmanpreet":"Harmanpreet Kaur","kaur":"Harmanpreet Kaur",
    "deepti":"Deepti Sharma","mithali":"Mithali Raj","raj":"Mithali Raj",
    "jhulan":"Jhulan Goswami","goswami":"Jhulan Goswami","richa":"Richa Ghosh",
    "healy":"AJ Healy","perry":"EA Perry","gardner":"A Gardner",
    "sciver":"NR Sciver","tahlia":"TM McGrath","mcgrath":"TM McGrath",
    "amelia":"AMC Kerr","kerr":"AMC Kerr","devine":"SFM Devine",
    "kl rahul":"KL Rahul","rahul":"KL Rahul",
}
CRICSHEET_NAME={"Smriti Mandhana":"S Mandhana","Harmanpreet Kaur":"H Kaur",
                "Alyssa Healy":"AJ Healy","Ellyse Perry":"EA Perry","Ashleigh Gardner":"A Gardner"}

def resolve(name):
    display=NAME_ALIASES.get(name.strip().lower(),name)
    return CRICSHEET_NAME.get(display,display)

WIKI_NAMES={
    "V Kohli":"Virat Kohli","Babar Azam":"Babar Azam","SPD Smith":"Steve Smith cricketer",
    "DA Warner":"David Warner cricketer","RG Sharma":"Rohit Sharma","JJ Bumrah":"Jasprit Bumrah",
    "MA Starc":"Mitchell Starc","JR Hazlewood":"Josh Hazlewood","BA Stokes":"Ben Stokes",
    "JE Root":"Joe Root","JM Anderson":"James Anderson cricketer","SCJ Broad":"Stuart Broad",
    "KC Sangakkara":"Kumar Sangakkara","SR Tendulkar":"Sachin Tendulkar","MS Dhoni":"MS Dhoni",
    "RT Ponting":"Ricky Ponting","SL Malinga":"Lasith Malinga","Rashid Khan":"Rashid Khan cricketer",
    "Shahid Afridi":"Shahid Afridi","Mohammad Rizwan":"Mohammad Rizwan cricketer",
    "Shaheen Shah Afridi":"Shaheen Shah Afridi","JC Buttler":"Jos Buttler",
    "GJ Maxwell":"Glenn Maxwell cricketer","AB de Villiers":"AB de Villiers",
    "Fakhar Zaman":"Fakhar Zaman","Imam-ul-Haq":"Imam-ul-Haq",
    "Naseem Shah":"Naseem Shah cricketer","Shadab Khan":"Shadab Khan cricketer",
    "Smriti Mandhana":"Smriti Mandhana","Shafali Verma":"Shafali Verma",
    "Harmanpreet Kaur":"Harmanpreet Kaur","Deepti Sharma":"Deepti Sharma cricketer",
    "AJ Healy":"Alyssa Healy","EA Perry":"Ellyse Perry","A Gardner":"Ashleigh Gardner",
    "KL Rahul":"KL Rahul cricketer",
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_wiki(cricsheet_name, search_name):
    try:
        import re
        wiki_title=WIKI_NAMES.get(cricsheet_name, search_name+" cricketer")
        sr=requests.get("https://en.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":wiki_title,
                    "format":"json","utf8":1,"srlimit":3},
            timeout=8,headers={"User-Agent":"CricketAnalyticsApp/2.0"})
        sr.raise_for_status()
        results=sr.json().get("query",{}).get("search",[])
        if not results: return None
        page_title=results[0]["title"]
        safe=page_title.replace(" ","_")
        rr=requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe}",
            timeout=8,headers={"User-Agent":"CricketAnalyticsApp/2.0"})
        rr.raise_for_status(); data=rr.json()
        img=data.get("thumbnail",{}).get("source","")
        bio=data.get("extract","")
        sents=[s.strip() for s in bio.split(".") if len(s.strip())>15]
        bio=". ".join(sents[:5])+"." if sents else bio[:600]
        bio=bio.replace("..",".")
        ir=requests.get("https://en.wikipedia.org/w/api.php",
            params={"action":"query","titles":page_title,"prop":"revisions",
                    "rvprop":"content","rvslots":"main","format":"json","rvsection":0},
            timeout=8,headers={"User-Agent":"CricketAnalyticsApp/2.0"})
        ir.raise_for_status()
        pages=ir.json().get("query",{}).get("pages",{})
        wt=next(iter(pages.values())).get("revisions",[{}])[0].get("slots",{}).get("main",{}).get("*","")
        def clean(v):
            v=re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]",r"\2",v)
            v=re.sub(r"\{\{[^}]+\}\}","",v); v=re.sub(r"<[^>]+>","",v)
            v=re.sub(r"\[\[.*?\]\]","",v)
            return v.strip().strip("|").strip()
        def ef(text,keys):
            for k in keys:
                m=re.search(r"\|\s*"+re.escape(k)+r"\s*=\s*([^\n\|}{]{2,80})",text,re.IGNORECASE)
                if m:
                    v=clean(m.group(1))
                    if len(v)>3 and "[[" not in v: return v
            return ""
        def er(text,keys):
            for k in keys:
                m=re.search(r"\|\s*"+re.escape(k)+r"\s*=\s*([^\n]{2,150})",text,re.IGNORECASE)
                if m: return m.group(1).strip()
            return ""
        def pd2(v):
            if not v: return ""
            mo=["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            m=re.search(r"\{\{(?:dts|birth date(?:[^|]*)?)[\s|]+([\d]{4})[|\s]+([\d]{1,2})[|\s]+([\d]{1,2})",v,re.IGNORECASE)
            if m:
                try: return f"{int(m.group(3))} {mo[int(m.group(2))]} {m.group(1)}"
                except: pass
            m2=re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",v)
            if m2: return f"{int(m2.group(1))} {m2.group(2)[:3].capitalize()} {m2.group(3)}"
            return ""
        born=""
        bd=re.search(r"\{\{birth date(?:\s*and age)?\s*\|([^}]+)\}\}",wt,re.IGNORECASE)
        if bd:
            parts2=[p.strip() for p in bd.group(1).split("|") if p.strip().isdigit()]
            if len(parts2)>=3:
                mo2=["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                try: born=f"{int(parts2[2])} {mo2[int(parts2[1])]} {parts2[0]}"
                except: pass
        if not born: born=ef(wt,["birth_date","birthdate","born"])
        odi_d=pd2(er(wt,["odidebutdate","ODIdebutdate"]))
        test_d=pd2(er(wt,["testdebutdate","Testdebutdate"]))
        t20_d=pd2(er(wt,["t20idebutdate","T20Idebutdate","T20debutdate"]))
        any_d=pd2(er(wt,["debutdate","debut_date"]))
        role_raw=ef(wt,["role","batting_style","batting style"])
        role_raw=re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]",r"\2",role_raw)
        role_raw=re.sub(r"\{\{[^}]+\}\}","",role_raw).strip()
        desc=data.get("description","")
        if not role_raw or "[[" in role_raw or len(role_raw)<3:
            role_raw=desc[:60] if desc else ""
        nation=ef(wt,["country","nationality","national_side"])
        return {"title":data.get("title",page_title),"bio":bio,"img":img,
                "born":born[:60] if born else "",
                "odi_debut":odi_d or any_d,"test_debut":test_d or any_d,"t20_debut":t20_d or any_d,
                "role":role_raw[:60] if role_raw else "",
                "nation":nation[:40] if nation else ""}
    except: return None

def show_player_card(cricsheet_name, search_name, fmt="ODI", compact=False):
    card=get_wiki(cricsheet_name,search_name)
    if not card:
        st.markdown(f"""<div style="background:{CARD};border-radius:12px;padding:12px 16px;margin:0 0 12px;border:1px solid #2d3561">
  <span style="color:#8899bb;font-size:13px">📖 Profile unavailable for {cricsheet_name}</span></div>""",unsafe_allow_html=True)
        return
    img_w=70 if compact else 96; img_h=88 if compact else 118
    img_html=f'<div style="flex-shrink:0"><img src="{card["img"]}" style="width:{img_w}px;height:{img_h}px;object-fit:cover;border-radius:10px;border:2px solid #2d3561;display:block"></div>' if card["img"] else ""
    fmt_key={"ODI":"odi_debut","Test":"test_debut","T20I":"t20_debut"}.get(fmt,"odi_debut")
    debut=card.get(fmt_key,"") or card.get("odi_debut","") or card.get("test_debut","") or card.get("t20_debut","")
    psz="10px"
    pills=""
    if card["born"]: pills+=f'<span style="background:#1a2540;color:#00e5a0;padding:2px 8px;border-radius:20px;font-size:{psz};font-weight:600;margin:2px 2px 2px 0;display:inline-block">🎂 {card["born"]}</span>'
    if card["nation"]: pills+=f'<span style="background:#1a2540;color:#3d8bff;padding:2px 8px;border-radius:20px;font-size:{psz};font-weight:600;margin:2px 2px 2px 0;display:inline-block">🌍 {card["nation"]}</span>'
    if card["role"]: pills+=f'<span style="background:#1a2540;color:#fbbf24;padding:2px 8px;border-radius:20px;font-size:{psz};font-weight:600;margin:2px 2px 2px 0;display:inline-block">🏏 {card["role"][:28]}</span>'
    if debut: pills+=f'<span style="background:#1a2540;color:#fb923c;padding:2px 8px;border-radius:20px;font-size:{psz};font-weight:600;margin:2px 2px 2px 0;display:inline-block">🎯 {fmt}: {debut}</span>'
    max_sents=2 if compact else 4
    short_bio=". ".join(card["bio"].split(". ")[:max_sents])+"." if card["bio"] else ""
    name_sz="14px" if compact else "18px"
    st.markdown(f"""<div style="background:linear-gradient(135deg,#141d35,#0d1320);border-radius:12px;padding:14px;margin:0 0 12px;border:1px solid #2d3561;display:flex;gap:12px;align-items:flex-start;overflow:hidden;box-sizing:border-box">
  {img_html}
  <div style="flex:1;min-width:0">
    <div style="color:#fff;font-size:{name_sz};font-weight:800;margin-bottom:5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{card["title"]}</div>
    <div style="display:flex;flex-wrap:wrap;gap:3px;margin-bottom:6px">{pills}</div>
    <div style="color:#8899bb;font-size:11px;line-height:1.6;overflow:hidden;display:-webkit-box;-webkit-line-clamp:{max_sents+1};-webkit-box-orient:vertical">{short_bio}</div>
  </div>
</div>""",unsafe_allow_html=True)

# ── TOP NAVIGATION BAR ────────────────────────────────────────────────────────
PAGES=["🏠 Home","🔍 Player Search","⚔️ Head to Head","🏟️ vs Venue",
       "🌍 vs Opponent","🤜 Batter vs Bowler","📈 Over Years",
       "🏆 Leaderboard","🤖 Similar Players","🔥 Form & Ratings"]

if "page" not in st.session_state: st.session_state.page="🏠 Home"

last_upd=get_last_updated()
pkt=datetime.now(timezone(timedelta(hours=5)))
status_txt=f"Updated {last_upd}" if last_upd else f"{pkt.strftime('%H:%M')} PKT"

nav_html='<div class="ca-topnav"><div class="ca-topnav-brand">🏏 Cricket<span>Analytics</span></div><div class="ca-topnav-links">'
for p in PAGES:
    active="active" if st.session_state.page==p else ""
    emoji=p.split()[0]; label=" ".join(p.split()[1:])
    nav_html+=f'<button class="ca-navbtn {active}" onclick="void(0)">{emoji} <span class="nav-label">{label}</span></button>'
nav_html+=f'</div><div class="ca-topnav-status"><span class="ca-live"></span>{status_txt}</div></div>'
st.markdown(nav_html,unsafe_allow_html=True)

# Streamlit native nav (hidden visually, used for actual routing)
with st.sidebar:
    section=st.radio("",PAGES,key="page",label_visibility="collapsed")

st.markdown('<div class="ca-content">', unsafe_allow_html=True)

section=st.session_state.page

# ══ HOME ════════════════════════════════════════════════════════════════════
if section=="🏠 Home":
    # Hero
    fmt_pills="".join([
        f'<span style="background:{FORMAT_META.get(f,("","#00e5a0",""))[1]}18;color:{FORMAT_META.get(f,("","#00e5a0",""))[1]};border:1px solid {FORMAT_META.get(f,("","#00e5a0",""))[1]}44;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:700">'
        f'{FORMAT_META.get(f,("🏏","",""))[0]} {f}</span>'
        for f in ALL_FMT
    ])
    st.markdown(f"""<div class="ca-fade" style="background:linear-gradient(150deg,#080c14,#0c1628,#080c14);border-radius:16px;padding:36px 32px 28px;margin-bottom:24px;border:1px solid var(--border);position:relative;overflow:hidden">
  <div style="position:absolute;top:-80px;left:20%;width:400px;height:300px;background:radial-gradient(ellipse,rgba(0,229,160,.06) 0%,transparent 70%);pointer-events:none"></div>
  <div style="position:absolute;bottom:-60px;right:5%;width:300px;height:220px;background:radial-gradient(ellipse,rgba(61,139,255,.05) 0%,transparent 70%);pointer-events:none"></div>
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
    <span style="font-size:40px">🏏</span>
    <div>
      <h1 style="font-family:'Syne',sans-serif;color:#fff;margin:0;font-size:30px;font-weight:800;letter-spacing:-0.5px">Cricket <span class="ca-shimmer">Analytics</span></h1>
      <p style="color:var(--muted);font-size:13px;margin:4px 0 0">Ball-by-ball data · All-time records · 8 formats</p>
    </div>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:6px;margin:16px 0 18px">{fmt_pills}</div>
  <div style="display:flex;align-items:center;gap:8px;background:rgba(0,229,160,.06);border:1px solid rgba(0,229,160,.15);border-radius:20px;padding:6px 14px;width:fit-content">
    <span class="ca-live"></span><span style="font-size:11px;font-weight:600;color:var(--accent)">Auto-updated daily · Cricsheet (2-3 day lag)</span>
  </div>
</div>""",unsafe_allow_html=True)

    # Quick search
    st.markdown("#### 🔍 Quick Player Search")
    qname=st.text_input("","",placeholder="Type a player name — Babar, Kohli, Smriti, Shaheen, Maxwell...",key="home_search",label_visibility="collapsed")
    if qname:
        st.session_state.page="🔍 Player Search"
        st.session_state["ps_name"]=qname
        st.rerun()

    # Feature cards grid
    st.markdown("#### Explore")
    features=[
        ("⚔️","Head to Head","Compare any two players side by side","⚔️ Head to Head"),
        ("🏟️","Player vs Venue","How a player performs at each ground","🏟️ vs Venue"),
        ("🌍","vs Opponent","Dominance stats against each team","🌍 vs Opponent"),
        ("🤜","Batter vs Bowler","Ball-by-ball matchup data","🤜 Batter vs Bowler"),
        ("📈","Career Timeline","Year-by-year performance charts","📈 Over Years"),
        ("🏆","Leaderboard","Top players ranked by format & stat","🏆 Leaderboard"),
        ("🤖","Similar Players","ML-powered player comparisons","🤖 Similar Players"),
        ("🔥","Form & Ratings","Who's hot, who's cold right now","🔥 Form & Ratings"),
    ]
    cols=st.columns(4)
    for i,(emoji,title,desc,target) in enumerate(features):
        with cols[i%4]:
            if st.button(f"{emoji} **{title}**\n\n{desc}",key=f"feat_{i}",use_container_width=True):
                st.session_state.page=target; st.rerun()

    # Mini leaderboard preview
    st.markdown("---")
    st.markdown("#### 🏆 Quick Leaderboard")
    ql_fmt=st.radio("Format",ALL_FMT,horizontal=True,key="ql_fmt")
    qlc1,qlc2=st.columns(2)
    with qlc1:
        st.markdown("**Top 5 Batters by Runs**")
        top_bat=bat_fmt[bat_fmt["format"]==ql_fmt].sort_values("runs",ascending=False).head(5)[["striker","runs","average","strike_rate"]] if not bat_fmt.empty else pd.DataFrame()
        if not top_bat.empty: st.dataframe(top_bat.reset_index(drop=True),hide_index=True)
    with qlc2:
        st.markdown("**Top 5 Bowlers by Wickets**")
        top_bowl=bowl_fmt[bowl_fmt["format"]==ql_fmt].sort_values("wickets",ascending=False).head(5)[["bowler","wickets","economy","average"]] if not bowl_fmt.empty else pd.DataFrame()
        if not top_bowl.empty: st.dataframe(top_bowl.reset_index(drop=True),hide_index=True)

# ══ PLAYER SEARCH ════════════════════════════════════════════════════════════
elif section=="🔍 Player Search":
    default_name=st.session_state.get("ps_name","")
    st.session_state["ps_name"]=""
    fmt_pills="".join([
        f'<span style="background:{FORMAT_META.get(f,("","#00e5a0",""))[1]}18;color:{FORMAT_META.get(f,("","#00e5a0",""))[1]};border:1px solid {FORMAT_META.get(f,("","#00e5a0",""))[1]}44;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:700">'
        f'{FORMAT_META.get(f,("🏏","",""))[0]} {f}</span>' for f in ALL_FMT])
    st.markdown(f"""<div class="ca-fade" style="background:linear-gradient(160deg,#080c14,#0c1628,#080c14);border-radius:14px;padding:24px;margin-bottom:20px;border:1px solid var(--border)">
  <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px">{fmt_pills}</div>
  <p style="color:var(--muted);font-size:12px;margin:0">Search any player across all formats · Ball-by-ball stats · Wikipedia profiles</p>
</div>""",unsafe_allow_html=True)

    name=st.text_input("","",placeholder="🔍  Player name — e.g. Babar, Kohli, Smriti, Shaheen...",
                       label_visibility="collapsed",value=default_name)
    if name:
        sname=resolve(name)
        ab_rows=find_rows(bat_fmt,"striker",sname)
        aw_rows=find_rows(bowl_fmt,"bowler",sname)
        ab_qual=ab_rows[ab_rows["matches"]>=3] if not ab_rows.empty and "matches" in ab_rows.columns else ab_rows
        aw_qual=aw_rows[aw_rows["matches"]>=3] if not aw_rows.empty and "matches" in aw_rows.columns else aw_rows
        ab=ab_qual["format"].unique().tolist() if not ab_qual.empty else []
        aw=aw_qual["format"].unique().tolist() if not aw_qual.empty else []
        avl=sorted(set(ab+aw),key=lambda x:FORMATS.index(x) if x in FORMATS else 99)
        if not avl:
            st.error(f"No data found for '{name}'. Try a different spelling.")
            st.stop()
        fmt=st.radio("📋 Format",avl,horizontal=True)
        clr=FC.get(fmt,"#00e5a0")
        bat=find_rows(bat_fmt[bat_fmt["format"]==fmt],"striker",sname)
        bowl=find_rows(bowl_fmt[bowl_fmt["format"]==fmt],"bowler",sname)
        display_name=bat["striker"].iloc[0] if len(bat)>0 else (bowl["bowler"].iloc[0] if len(bowl)>0 else sname)
        show_player_card(display_name,name,fmt)
        if last_upd:
            st.markdown(f"""<div style="background:rgba(0,229,160,.05);border:1px solid rgba(0,229,160,.2);border-radius:8px;padding:7px 12px;margin:0 0 12px;font-size:11px;color:#00e5a0">
              ✅ Data last updated: <b>{last_upd}</b> — auto-updated daily from Cricsheet</div>""",unsafe_allow_html=True)
        if len(bat)==0 and len(bowl)==0:
            st.warning(f"No {fmt} data for '{display_name}'.")
        else:
            tab_labels=[]
            if len(bat)>0: tab_labels.append("🏏 Batting")
            if len(bowl)>0: tab_labels.append("🎳 Bowling")
            tab_labels.append("📈 Charts")
            tabs=st.tabs(tab_labels); ti=0
            if len(bat)>0:
                with tabs[ti]:
                    p=bat.sort_values("runs",ascending=False).iloc[0]
                    metrics({"Matches":int(p["matches"]),"Runs":f"{int(p['runs']):,}","Average":p["average"]})
                    metrics({"Strike Rate":p["strike_rate"],"4s":int(p["fours"]),"6s":int(p["sixes"])})
                    metrics({"Dismissals":int(p["dismissals"]),"Dot %":f"{p['dot_pct']}%","Boundary %":f"{p['boundary_pct']}%"})
                    h100=int(p["hundreds"]) if "hundreds" in p.index and pd.notna(p.get("hundreds")) else "—"
                    h50=int(p["fifties"]) if "fifties" in p.index and pd.notna(p.get("fifties")) else "—"
                    hs=int(p["highest"]) if "highest" in p.index and pd.notna(p.get("highest")) else "—"
                    dk=int(p["ducks"]) if "ducks" in p.index and pd.notna(p.get("ducks")) else "—"
                    ps_=round(float(p["player_score"]),1) if "player_score" in p.index and pd.notna(p.get("player_score")) else "—"
                    metrics({"100s":h100,"50s":h50,"Highest":hs,"Ducks":dk,"⭐ Score":ps_})
                    fr=int(p["fours"])*4; sr_=int(p["sixes"])*6; or_=max(0,int(p["runs"])-fr-sr_)
                    ch(donut(["Fours","Sixes","Other"],[fr,sr_,or_],[clr,"#d63031","#636e72"],"Scoring Breakdown"),300)
                ti+=1
            if len(bowl)>0:
                with tabs[ti]:
                    p2=bowl.sort_values("wickets",ascending=False).iloc[0]
                    metrics({"Matches":int(p2["matches"]),"Wickets":int(p2["wickets"]),"Economy":p2["economy"]})
                    metrics({"Average":p2["average"],"Strike Rate":p2["strike_rate"],"Dot %":f"{p2['dot_pct']}%"})
                    fw=int(p2["five_wkts"]) if "five_wkts" in p2.index and pd.notna(p2.get("five_wkts")) else "—"
                    bb=p2.get("best_bowling","—") if "best_bowling" in p2.index else "—"
                    metrics({"5-Wkt Hauls":fw,"Best Bowling":bb})
                ti+=1
            with tabs[ti]:
                if len(bat)>0:
                    p=bat.sort_values("runs",ascending=False).iloc[0]
                    en=p["striker"]
                    by=bat_yr[(bat_yr["format"]==fmt)&(bat_yr["striker"]==en)].sort_values("year") if not bat_yr.empty else pd.DataFrame()
                    if len(by)>1:
                        st.markdown("**🏏 Batting Trends**")
                        ch(bar_v(by,"year","runs","Runs per Year",clr))
                        c1,c2=st.columns(2)
                        with c1: ch(line(by,"year","average","Batting Average",clr),260)
                        with c2: ch(line(by,"year","strike_rate","Strike Rate","#fbbf24"),260)
                if len(bowl)>0:
                    p2=bowl.sort_values("wickets",ascending=False).iloc[0]
                    en2=p2["bowler"]
                    by2=bowl_yr[(bowl_yr["format"]==fmt)&(bowl_yr["bowler"]==en2)].sort_values("year") if not bowl_yr.empty else pd.DataFrame()
                    if len(by2)>1:
                        st.markdown("**🎳 Bowling Trends**")
                        ch(bar_v(by2,"year","wickets","Wickets per Year",clr))
                        c1,c2=st.columns(2)
                        with c1: ch(line(by2,"year","economy","Economy Rate","#d63031"),260)
                        with c2: ch(line(by2,"year","average","Bowling Average","#6c5ce7"),260)

# ══ HEAD TO HEAD ═════════════════════════════════════════════════════════════
elif section=="⚔️ Head to Head":
    st.markdown("## ⚔️ Head to Head")
    st.markdown("Compare any two players side by side across all formats.")
    c1,c2=st.columns(2)
    n1=c1.text_input("Player 1","Kohli"); n2=c2.text_input("Player 2","Babar Azam")
    fmt=st.radio("Format",ALL_FMT,horizontal=True)
    if n1 and n2:
        s1=resolve(n1); s2=resolve(n2)
        b1=find_rows(bat_fmt[bat_fmt["format"]==fmt],"striker",s1)
        b2=find_rows(bat_fmt[bat_fmt["format"]==fmt],"striker",s2)
        if len(b1)==0 or len(b2)==0:
            st.error(f"One or both players have no {fmt} batting data.")
        else:
            p1=b1.iloc[0]; p2_=b2.iloc[0]; p1n=p1["striker"]; p2n=p2_["striker"]
            cc1,cc2=st.columns(2)
            with cc1: show_player_card(p1n,n1,fmt,compact=True)
            with cc2: show_player_card(p2n,n2,fmt,compact=True)
            LABELS={"runs":"Runs","fours":"Fours","sixes":"Sixes","average":"Avg",
                    "strike_rate":"Strike Rate","dot_pct":"Dot %","boundary_pct":"Boundary %"}
            for title,ml in [("🏏 Volume",["runs","fours","sixes"]),
                              ("📈 Rates",["average","strike_rate"]),
                              ("📊 Percentages",["dot_pct","boundary_pct"])]:
                pretty=[LABELS.get(m,m) for m in ml]
                v1=[float(p1.get(m,0)) for m in ml]; v2=[float(p2_.get(m,0)) for m in ml]
                xmax=max(v1+v2)*1.22 if max(v1+v2)>0 else 10
                fig=go.Figure()
                fig.add_trace(go.Bar(name=p1n,y=pretty,x=v1,orientation="h",
                    marker=dict(color=FC["ODI"],opacity=0.9,line=dict(width=0)),
                    text=[f"{v:.1f}" for v in v1],textposition="outside",
                    textfont=dict(size=12,color=TEXT),cliponaxis=False))
                fig.add_trace(go.Bar(name=p2n,y=pretty,x=v2,orientation="h",
                    marker=dict(color=FC["Test"],opacity=0.9,line=dict(width=0)),
                    text=[f"{v:.1f}" for v in v2],textposition="outside",
                    textfont=dict(size=12,color=TEXT),cliponaxis=False))
                fig.update_layout(**BASE,barmode="group",title=title,
                                  height=max(260,len(ml)*140),
                                  margin=dict(l=20,r=110,t=48,b=8),bargap=0.25,bargroupgap=0.08)
                fig.update_yaxes(showgrid=False,tickfont=dict(size=13),title="",automargin=True)
                fig.update_xaxes(showgrid=True,gridcolor=GRID,title="",fixedrange=True,range=[0,xmax])
                st.plotly_chart(fig,**CFG)
            by1=find_rows(bat_yr[bat_yr["format"]==fmt],"striker",s1).copy() if not bat_yr.empty else pd.DataFrame()
            by2y=find_rows(bat_yr[bat_yr["format"]==fmt],"striker",s2).copy() if not bat_yr.empty else pd.DataFrame()
            if len(by1)>0 and len(by2y)>0:
                by1["player"]=p1n; by2y["player"]=p2n
                combined=pd.concat([by1,by2y]).sort_values("year")
                fy=px.line(combined,x="year",y="runs",color="player",markers=True,
                           title=f"Runs per Year — {fmt}",
                           color_discrete_map={p1n:FC["ODI"],p2n:FC["Test"]})
                fy.update_traces(line=dict(width=3),marker=dict(size=9))
                fy.update_layout(**BASE,height=360,margin=dict(l=50,r=20,t=48,b=40))
                fy.update_xaxes(title="Year",tickmode="linear",dtick=2,showgrid=True,gridcolor=GRID)
                fy.update_yaxes(title="Runs",showgrid=True,gridcolor=GRID)
                st.plotly_chart(fy,**CFG)

# ══ VS VENUE ═════════════════════════════════════════════════════════════════
elif section=="🏟️ vs Venue":
    st.markdown("## 🏟️ Player vs Venue")
    st.markdown("How does a player perform at different grounds?")
    name=st.text_input("Player name","Kohli"); st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=find_rows(bat_ven,"striker",sname) if st_=="Batting" else find_rows(bowl_ven,"bowler",sname)
        if len(src)==0: st.error("Player not found! Try a different spelling.")
        else:
            fmt=st.radio("Format",avail(src,"format"),horizontal=True)
            df_v=src[src["format"]==fmt]
            if st_=="Batting":
                m=st.selectbox("Metric",["runs","average","strike_rate","fours","sixes"])
                df_v=df_v.sort_values(m,ascending=False).head(20)
                ch(bar_h(df_v,m,"venue",m,"Greens",f"{df_v['striker'].iloc[0]} — {m} by Venue ({fmt})"))
                st.dataframe(df_v[["venue","innings","runs","average","strike_rate"]].reset_index(drop=True))
            else:
                m=st.selectbox("Metric",["wickets","economy","average","dot_pct"])
                df_v=df_v.sort_values(m,ascending=False).head(20)
                ch(bar_h(df_v,m,"venue",m,"Reds",f"{df_v['bowler'].iloc[0]} — {m} by Venue ({fmt})"))
                st.dataframe(df_v[["venue","innings","wickets","economy","average"]].reset_index(drop=True))

# ══ VS OPPONENT ══════════════════════════════════════════════════════════════
elif section=="🌍 vs Opponent":
    st.markdown("## 🌍 Player vs Opponent")
    st.markdown("Find which teams a player dominates — and which trouble them.")
    name=st.text_input("Player name","Kohli"); st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=find_rows(bat_opp,"striker",sname) if st_=="Batting" else find_rows(bowl_opp,"bowler",sname)
        if len(src)==0: st.error("Player not found! Try a different spelling.")
        else:
            fmt=st.radio("Format",avail(src,"format"),horizontal=True)
            df_o=src[src["format"]==fmt]
            if st_=="Batting":
                m=st.selectbox("Metric",["runs","average","strike_rate","fours","sixes"])
                df_o=df_o.sort_values(m,ascending=False)
                ch(bar_h(df_o,m,"opponent",m,"Blues",f"{df_o['striker'].iloc[0]} — {m} vs Teams ({fmt})"))
                st.dataframe(df_o[["opponent","innings","runs","average","strike_rate"]].reset_index(drop=True))
            else:
                m=st.selectbox("Metric",["wickets","economy","average","dot_pct"])
                df_o=df_o.sort_values(m,ascending=False)
                ch(bar_h(df_o,m,"opponent",m,"Purples",f"{df_o['bowler'].iloc[0]} — {m} vs Teams ({fmt})"))
                st.dataframe(df_o[["opponent","innings","wickets","economy","average"]].reset_index(drop=True))

# ══ BATTER VS BOWLER ═════════════════════════════════════════════════════════
elif section=="🤜 Batter vs Bowler":
    st.markdown("## 🤜 Batter vs Bowler")
    st.markdown("Ball-by-ball matchup data — who has the edge?")
    mt=st.radio("Look up a...",["Batter","Bowler"],horizontal=True)
    if mt=="Batter":
        name=st.text_input("Batter name","Babar Azam")
        if name:
            sname=resolve(name)
            src=find_rows(bvb,"striker",sname)
            if len(src)==0: st.error("Not found!")
            else:
                fmt=st.radio("Format",avail(src,"format"),horizontal=True)
                df_m=src[src["format"]==fmt]
                m=st.selectbox("Sort by",["balls_faced","runs","strike_rate","dismissals"])
                df_m=df_m.sort_values(m,ascending=False).head(20)
                ch(bar_h(df_m,m,"bowler",m,"Greens",f"Top 20 bowlers faced — {m} ({fmt})"))
                st.dataframe(df_m[["bowler","balls_faced","runs","strike_rate","dismissals"]].reset_index(drop=True))
    else:
        name=st.text_input("Bowler name","Shaheen")
        if name:
            sname=resolve(name)
            src=find_rows(wvb,"bowler",sname)
            if len(src)==0: st.error("Not found!")
            else:
                fmt=st.radio("Format",avail(src,"format"),horizontal=True)
                df_m=src[src["format"]==fmt]
                m=st.selectbox("Sort by",["wickets","economy","dot_pct","runs_given"])
                df_m=df_m.sort_values(m,ascending=(m in ["economy","dot_pct"])).head(20)
                ch(bar_h(df_m,m,"striker",m,"Reds",f"Top 20 batters bowled to — {m} ({fmt})"))
                st.dataframe(df_m[["striker","balls_bowled","runs_given","wickets","economy"]].reset_index(drop=True))

# ══ OVER YEARS ═══════════════════════════════════════════════════════════════
elif section=="📈 Over Years":
    st.markdown("## 📈 Performance Over Years")
    st.markdown("Track how a player has evolved season by season.")
    name=st.text_input("Player name","Kohli"); st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=find_rows(bat_yr,"striker",sname) if st_=="Batting" else find_rows(bowl_yr,"bowler",sname)
        if len(src)==0: st.error("Player not found!")
        else:
            fmt=st.radio("Format",avail(src,"format"),horizontal=True)
            by=src[src["format"]==fmt].sort_values("year"); clr=FC.get(fmt,"#00e5a0")
            if st_=="Batting":
                ch(bar_v(by,"year","runs","Runs per Year",clr))
                c1,c2=st.columns(2)
                with c1: ch(line(by,"year","average","Batting Average",clr),280)
                with c2: ch(line(by,"year","strike_rate","Strike Rate","#fbbf24"),280)
                st.dataframe(by[["year","matches","runs","average","strike_rate","fours","sixes"]].reset_index(drop=True))
            else:
                ch(bar_v(by,"year","wickets","Wickets per Year",clr))
                c1,c2=st.columns(2)
                with c1: ch(line(by,"year","economy","Economy Rate","#d63031"),280)
                with c2: ch(line(by,"year","average","Bowling Average","#6c5ce7"),280)
                st.dataframe(by[["year","matches","wickets","economy","average","dot_pct"]].reset_index(drop=True))

# ══ LEADERBOARD ══════════════════════════════════════════════════════════════
elif section=="🏆 Leaderboard":
    st.markdown("## 🏆 Leaderboard")
    st.markdown("The greatest — ranked by format and stat.")
    fmt=st.radio("Format",ALL_FMT,horizontal=True)
    tab1,tab2=st.tabs(["🏏 Batting","🎳 Bowling"])
    with tab1:
        bs=bat_fmt[bat_fmt["format"]==fmt]
        c1,c2=st.columns(2)
        sb=c1.selectbox("Rank by",["runs","average","strike_rate","sixes","hundreds","player_score"])
        mr=c2.slider("Min runs",0,3000,200,100); tn=st.slider("Top N",5,50,20)
        lb=bs[bs["runs"]>=mr].sort_values(sb,ascending=False).head(tn).reset_index(drop=True)
        lb.insert(0,"Rank",range(1,len(lb)+1))
        ch(bar_h(lb,sb,"striker",sb,"Teal",f"Top {tn} {fmt} Batters — {sb}"))
        show_cols=[c for c in ["Rank","striker","matches","runs","average","strike_rate","hundreds","fifties","highest","player_score"] if c in lb.columns]
        st.dataframe(lb[show_cols].reset_index(drop=True))
    with tab2:
        ws=bowl_fmt[bowl_fmt["format"]==fmt]
        c1,c2=st.columns(2)
        sb2=c1.selectbox("Rank by",["wickets","economy","average","dot_pct","five_wkts"])
        mw=c2.slider("Min wickets",0,100,10,5); tn2=st.slider("Top N bowlers",5,50,20)
        lb2=ws[ws["wickets"]>=mw].sort_values(sb2,ascending=(sb2 in ["economy","average"])).head(tn2).reset_index(drop=True)
        lb2.insert(0,"Rank",range(1,len(lb2)+1))
        ch(bar_h(lb2,"wickets","bowler","economy","Sunset",f"Top {tn2} {fmt} Bowlers"))
        show_cols2=[c for c in ["Rank","bowler","matches","wickets","economy","average","five_wkts","best_bowling"] if c in lb2.columns]
        st.dataframe(lb2[show_cols2].reset_index(drop=True))

# ══ SIMILAR PLAYERS ══════════════════════════════════════════════════════════
elif section=="🤖 Similar Players":
    st.markdown("## 🤖 Similar Players")
    st.markdown("ML-powered · KMeans clustering on career stats to find statistically similar players.")
    st_type=st.radio("Type",["Batter","Bowler"],horizontal=True)
    name=st.text_input("Player name","Babar"); fmt=st.radio("Format",ALL_FMT,horizontal=True)
    if name:
        sname=resolve(name)
        if st_type=="Batter":
            src=find_rows(bat_sim[bat_sim["format"]==fmt],"striker",sname)
            if len(src)==0: st.error(f"No ML data for '{name}' in {fmt}. They may have <200 runs.")
            else:
                p=src.iloc[0]; cluster=int(p["cluster"])
                same=bat_sim[(bat_sim["cluster"]==cluster)&(bat_sim["format"]==fmt)]
                same=same[~same["striker"].str.contains(sname,case=False,na=False)]
                same=same.sort_values("average",ascending=False).head(12)
                st.subheader(f"Players most similar to {p['striker']} in {fmt}")
                st.caption(f"⭐ Player Score: {p.get('player_score','—')} | Cluster #{cluster}")
                ch(bar_h(same,"average","striker","average","Purples",f"Similar batters — {fmt}"))
                st.dataframe(same[["striker","runs","average","strike_rate","boundary_pct","player_score"]].reset_index(drop=True))
        else:
            src=find_rows(bowl_sim[bowl_sim["format"]==fmt],"bowler",sname)
            if len(src)==0: st.error(f"No ML data for '{name}' in {fmt}. They may have <20 wickets.")
            else:
                p=src.iloc[0]; cluster=int(p["cluster"])
                same=bowl_sim[(bowl_sim["cluster"]==cluster)&(bowl_sim["format"]==fmt)]
                same=same[~same["bowler"].str.contains(sname,case=False,na=False)]
                same=same.sort_values("wickets",ascending=False).head(12)
                st.subheader(f"Bowlers most similar to {p['bowler']} in {fmt}")
                ch(bar_h(same,"wickets","bowler","economy","Reds",f"Similar bowlers — {fmt}"))
                st.dataframe(same[["bowler","wickets","economy","average","dot_pct"]].reset_index(drop=True))

# ══ FORM & RATINGS ═══════════════════════════════════════════════════════════
elif section=="🔥 Form & Ratings":
    st.markdown("## 🔥 Form & Ratings")
    fmt=st.radio("Format",ALL_FMT,horizontal=True)
    tab1,tab2,tab3,tab4=st.tabs(["🔍 Player Form","🔥 Hot List","📉 Cold List","⭐ Player Scores"])
    with tab1:
        st.markdown("#### Year-by-year form with career reference lines")
        fname=st.text_input("Player name","Kohli",key="form_player")
        ftype=st.radio("Type",["Batting","Bowling"],horizontal=True,key="form_type")
        if fname:
            fsname=resolve(fname)
            if ftype=="Batting":
                pyr=find_rows(bat_yr[bat_yr["format"]==fmt],"striker",fsname)
                if pyr.empty: st.error(f"No {fmt} batting data for '{fname}'.")
                else:
                    pyr=pyr.sort_values("year"); pname=pyr["striker"].iloc[0]
                    career=find_rows(bat_fmt[bat_fmt["format"]==fmt],"striker",fsname)
                    cavg=float(career["average"].iloc[0]) if len(career)>0 else None
                    csr=float(career["strike_rate"].iloc[0]) if len(career)>0 else None
                    latest=pyr.iloc[-1]
                    metrics({"Latest Year":int(latest["year"]),"Runs":f"{int(latest['runs']):,}",
                             "Avg":round(float(latest["average"]),1),"SR":round(float(latest["strike_rate"]),1),"Matches":int(latest["matches"])})
                    clr=FC.get(fmt,"#00e5a0")
                    ch(bar_v(pyr,"year","runs",f"{pname} — Runs per Year ({fmt})",clr))
                    c1,c2=st.columns(2)
                    fig_avg=px.line(pyr,x="year",y="average",markers=True,title=f"{pname} — Batting Average")
                    fig_avg.update_traces(line=dict(color=clr,width=3),marker=dict(size=9,color=clr))
                    if cavg: fig_avg.add_hline(y=cavg,line_dash="dash",line_color="#fbbf24",annotation_text=f"Career {cavg:.1f}",annotation_font=dict(color="#fbbf24",size=11))
                    fig_avg.update_layout(**BASE,height=300,margin=M_DEFAULT)
                    with c1: st.plotly_chart(fig_avg,**CFG)
                    fig_sr=px.line(pyr,x="year",y="strike_rate",markers=True,title=f"{pname} — Strike Rate")
                    fig_sr.update_traces(line=dict(color="#fbbf24",width=3),marker=dict(size=9,color="#fbbf24"))
                    if csr: fig_sr.add_hline(y=csr,line_dash="dash",line_color="#fb923c",annotation_text=f"Career {csr:.1f}",annotation_font=dict(color="#fb923c",size=11))
                    fig_sr.update_layout(**BASE,height=300,margin=M_DEFAULT)
                    with c2: st.plotly_chart(fig_sr,**CFG)
                    fig_b=go.Figure()
                    fig_b.add_trace(go.Bar(name="4s",x=pyr["year"],y=pyr["fours"],marker_color="#00e5a0",opacity=0.85))
                    fig_b.add_trace(go.Bar(name="6s",x=pyr["year"],y=pyr["sixes"],marker_color="#d63031",opacity=0.85))
                    fig_b.update_layout(**BASE,barmode="group",title="Boundaries by Year",height=280,margin=M_BARV,bargap=0.25)
                    st.plotly_chart(fig_b,**CFG)
                    st.dataframe(pyr[["year","matches","runs","average","strike_rate","fours","sixes","dismissals"]].reset_index(drop=True))
            else:
                pyr=find_rows(bowl_yr[bowl_yr["format"]==fmt],"bowler",fsname)
                if pyr.empty: st.error(f"No {fmt} bowling data for '{fname}'.")
                else:
                    pyr=pyr.sort_values("year"); pname=pyr["bowler"].iloc[0]
                    career=find_rows(bowl_fmt[bowl_fmt["format"]==fmt],"bowler",fsname)
                    cecon=float(career["economy"].iloc[0]) if len(career)>0 else None
                    cavg2=float(career["average"].iloc[0]) if len(career)>0 else None
                    latest=pyr.iloc[-1]
                    metrics({"Latest Year":int(latest["year"]),"Wickets":int(latest["wickets"]),
                             "Economy":round(float(latest["economy"]),2),"Average":round(float(latest["average"]),1),"Matches":int(latest["matches"])})
                    clr=FC.get(fmt,"#d63031")
                    ch(bar_v(pyr,"year","wickets",f"{pname} — Wickets per Year ({fmt})","#d63031"))
                    c1,c2=st.columns(2)
                    fig_econ=px.line(pyr,x="year",y="economy",markers=True,title=f"{pname} — Economy")
                    fig_econ.update_traces(line=dict(color="#d63031",width=3),marker=dict(size=9,color="#d63031"))
                    if cecon: fig_econ.add_hline(y=cecon,line_dash="dash",line_color="#fbbf24",annotation_text=f"Career {cecon:.2f}",annotation_font=dict(color="#fbbf24",size=11))
                    fig_econ.update_layout(**BASE,height=300,margin=M_DEFAULT)
                    with c1: st.plotly_chart(fig_econ,**CFG)
                    fig_avg2=px.line(pyr,x="year",y="average",markers=True,title=f"{pname} — Bowling Average")
                    fig_avg2.update_traces(line=dict(color="#6c5ce7",width=3),marker=dict(size=9,color="#6c5ce7"))
                    if cavg2: fig_avg2.add_hline(y=cavg2,line_dash="dash",line_color="#fbbf24",annotation_text=f"Career {cavg2:.1f}",annotation_font=dict(color="#fbbf24",size=11))
                    fig_avg2.update_layout(**BASE,height=300,margin=M_DEFAULT)
                    with c2: st.plotly_chart(fig_avg2,**CFG)
                    st.dataframe(pyr[["year","matches","wickets","economy","average","dot_pct"]].reset_index(drop=True))
    with tab2:
        ftype2=st.radio("Type",["Batting","Bowling"],horizontal=True,key="hot_type")
        n_yrs=st.slider("Recent window (years)",1,5,1,key="hot_yrs")
        min_inn=st.slider("Min innings",3,20,5,key="hot_inn")
        if ftype2=="Batting" and not bat_yr.empty:
            latest_yr=bat_yr["year"].max()
            recent=bat_yr[(bat_yr["format"]==fmt)&(bat_yr["year"]>=latest_yr-n_yrs+1)]
            if not bat_fmt.empty:
                gb=set(bat_fmt[(bat_fmt["format"]==fmt)&(bat_fmt["runs"]>=200)]["striker"].unique())
                recent=recent[recent["striker"].isin(gb)]
            agg=recent.groupby("striker").agg(innings=("matches","sum"),runs=("runs","sum"),
                avg=("average","mean"),sr=("strike_rate","mean"),fours=("fours","sum"),sixes=("sixes","sum")).reset_index()
            agg=agg[agg["innings"]>=min_inn].sort_values("avg",ascending=False).head(25)
            agg["avg"]=agg["avg"].round(1); agg["sr"]=agg["sr"].round(1)
            if len(agg)>0:
                mo=st.selectbox("Rank by",["avg","sr","runs","sixes"],key="hot_bat_m")
                ch(bar_h(agg.sort_values(mo,ascending=False),mo,"striker",mo,"Oranges",f"🔥 Top Batters — {mo} (last {n_yrs}yr, {fmt})"))
                st.dataframe(agg[["striker","innings","runs","avg","sr","fours","sixes"]].reset_index(drop=True))
        elif ftype2=="Bowling" and not bowl_yr.empty:
            latest_yr=bowl_yr["year"].max()
            recent=bowl_yr[(bowl_yr["format"]==fmt)&(bowl_yr["year"]>=latest_yr-n_yrs+1)]
            if not bowl_fmt.empty:
                gb=set(bowl_fmt[(bowl_fmt["format"]==fmt)&(bowl_fmt["wickets"]>=20)]["bowler"].unique())
                recent=recent[recent["bowler"].isin(gb)]
            agg=recent.groupby("bowler").agg(innings=("matches","sum"),wickets=("wickets","sum"),
                econ=("economy","mean"),avg=("average","mean"),dot_pct=("dot_pct","mean")).reset_index()
            agg=agg[agg["innings"]>=min_inn].sort_values("wickets",ascending=False).head(25)
            agg["econ"]=agg["econ"].round(2); agg["avg"]=agg["avg"].round(1)
            if len(agg)>0:
                mo=st.selectbox("Rank by",["wickets","econ","avg","dot_pct"],key="hot_bowl_m")
                ch(bar_h(agg.sort_values(mo,ascending=(mo in ["econ","avg"])),mo,"bowler",mo,"Reds",f"🔥 Top Bowlers — {mo} (last {n_yrs}yr, {fmt})"))
                st.dataframe(agg[["bowler","innings","wickets","econ","avg","dot_pct"]].reset_index(drop=True))
    with tab3:
        ftype3=st.radio("Type",["Batting","Bowling"],horizontal=True,key="cold_type")
        min_career=st.slider("Min career matches",5,30,10,key="cold_min")
        if ftype3=="Batting" and not bat_form.empty:
            src=bat_form[bat_form["format"]==fmt].copy()
            src=src.merge(bat_fmt[bat_fmt["format"]==fmt][["striker","matches","runs"]],on="striker",how="left")
            src=src[(src["runs"]>=200)&(src["matches"]>=min_career)]
            cold=src[src["form_score"]<80].sort_values("form_score").head(20)
            if len(cold)>0:
                ch(bar_h(cold,"form_score","striker","form_score","Reds",f"📉 Struggling Batters ({fmt})"))
                sc=[c for c in ["striker","form_label","form_score","recent_avg","career_avg","recent_sr","career_sr"] if c in cold.columns]
                st.dataframe(cold[sc].reset_index(drop=True))
            else: st.info("No batters in poor form right now.")
        elif ftype3=="Bowling" and not bowl_form.empty:
            src2=bowl_form[bowl_form["format"]==fmt].copy()
            src2=src2.merge(bowl_fmt[bowl_fmt["format"]==fmt][["bowler","matches","wickets"]],on="bowler",how="left")
            src2=src2[(src2["wickets"]>=20)&(src2["matches"]>=min_career)]
            cold2=src2[src2["form_score"]<80].sort_values("form_score").head(20)
            if len(cold2)>0:
                ch(bar_h(cold2,"form_score","bowler","form_score","Reds",f"📉 Struggling Bowlers ({fmt})"))
                sc2=[c for c in ["bowler","form_label","form_score","recent_econ","career_econ","recent_avg","career_avg"] if c in cold2.columns]
                st.dataframe(cold2[sc2].reset_index(drop=True))
            else: st.info("No bowlers in poor form right now.")
    with tab4:
        ps_type=st.radio("Type",["Batting","Bowling"],horizontal=True,key="ps_type")
        if ps_type=="Batting":
            ps=bat_sim[bat_sim["format"]==fmt].sort_values("player_score",ascending=False).head(25) if not bat_sim.empty else pd.DataFrame()
            if len(ps)>0:
                ch(bar_h(ps,"player_score","striker","player_score","Teal",f"⭐ Top 25 Batter Scores ({fmt})"))
                st.caption("Score = Average 30% · Strike Rate 25% · Boundary% 20% · Runs volume 15% · Non-dot% 10%")
                st.dataframe(ps[["striker","player_score","average","strike_rate","boundary_pct","runs"]].reset_index(drop=True))
            else: st.info(f"No data for {fmt}.")
        else:
            ps2=bowl_sim[bowl_sim["format"]==fmt].sort_values("wickets",ascending=False).head(25) if not bowl_sim.empty else pd.DataFrame()
            if len(ps2)>0:
                ch(bar_h(ps2,"wickets","bowler","economy","Purples",f"⭐ Top 25 Bowlers ({fmt})"))
                sc2=[c for c in ["bowler","wickets","economy","average","dot_pct"] if c in ps2.columns]
                st.dataframe(ps2[sc2].reset_index(drop=True))
            else: st.info(f"No data for {fmt}.")

st.markdown('</div>', unsafe_allow_html=True)
