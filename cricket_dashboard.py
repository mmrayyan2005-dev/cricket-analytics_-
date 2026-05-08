import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(page_title="Cricket Analytics", layout="wide", page_icon="🏏",
                   initial_sidebar_state="collapsed")

RAW_BASE = "https://raw.githubusercontent.com/mmrayyan2005-dev/cricket-analytics-/main"

BG="#0f1117"; CARD="#1e2130"; TEXT="#f0f0f0"; GRID="#2a2d3e"
FC={
    "ODI":"#00b894","Test":"#0984e3","T20I":"#d63031",
    "IPL":"#e17055","PSL":"#6c5ce7",
    "WPL":"#fd79a8","BBL":"#ff7675","CPL":"#55efc4",
}
FORMATS=["ODI","Test","T20I","IPL","PSL","WPL","BBL","CPL"]

FORMAT_META={
    "ODI":("🌐","#00b894","#00cec9"),
    "Test":("🏛️","#0984e3","#74b9ff"),
    "T20I":("⚡","#d63031","#ff7675"),
    "IPL":("🏏","#e17055","#fdcb6e"),
    "PSL":("🟣","#6c5ce7","#a29bfe"),
    "WPL":("💜","#fd79a8","#fdcb6e"),
    "BBL":("🔥","#ff7675","#fab1a0"),
    "CPL":("🌴","#55efc4","#00b894"),
}

BASE=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
          font=dict(color=TEXT,family="DM Sans,sans-serif",size=12),
          legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,
                      bgcolor="rgba(0,0,0,0)",font=dict(size=11)),
          xaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,color=TEXT,fixedrange=True),
          yaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,color=TEXT,fixedrange=True),
          dragmode=False)
M_DEFAULT=dict(l=8,r=8,t=48,b=8)
M_BARV=dict(l=8,r=8,t=48,b=60)
CFG=dict(config={"displayModeBar":False,"scrollZoom":False,"doubleClick":False,"responsive":True},use_container_width=True)

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;background:{BG};color:{TEXT}}}
[data-testid="stMetric"]{{background:{CARD};border-radius:12px;padding:14px 18px;border:1px solid {GRID}}}
[data-testid="stMetricLabel"]{{font-size:11px;color:#aaa;text-transform:uppercase;letter-spacing:.5px}}
[data-testid="stMetricValue"]{{font-size:22px;font-weight:700;color:{TEXT}}}
[data-testid="column"]{{min-width:90px!important}}
.js-plotly-plot{{touch-action:pan-y!important}}
div[data-baseweb="tab-list"]{{gap:6px}}
div[data-baseweb="tab"]{{border-radius:8px;padding:6px 16px;background:{CARD};font-weight:600}}
div[data-baseweb="tab"][aria-selected="true"]{{background:#00b894!important;color:#fff!important}}
.stDataFrame{{border-radius:10px;overflow:hidden}}
</style>""",unsafe_allow_html=True)

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

st.sidebar.title("🏏 Cricket Analytics")
cr1,cr2=st.sidebar.columns([1,2])
if cr1.button("🔄 Refresh"):
    st.cache_data.clear(); st.rerun()
cr2.caption(f"Cached at\n{datetime.now().strftime('%H:%M %d %b')}")
st.sidebar.markdown(f"""<div style='background:{CARD};border-radius:8px;padding:10px 12px;font-size:12px;color:#aaa;margin:4px 0 8px 0'>
<b style='color:#00b894'>⚡ Live updates</b><br>Data auto-refreshes every hour from GitHub. Hit 🔄 for fresh data.</div>""",unsafe_allow_html=True)

with st.spinner("Loading cricket data..."):
    (batting,bowling,bat_fmt,bowl_fmt,bat_yr,bowl_yr,bat_ven,bat_opp,
     bowl_ven,bowl_opp,bvb,wvb,bat_form,bowl_form,bat_sim,bowl_sim,bat_inn,bowl_inn)=load()

def get_all_formats(df,col="format"):
    if df.empty or col not in df.columns: return ["ODI","Test","T20I","IPL","PSL"]
    return sorted(df[col].unique().tolist(),key=lambda x:FORMATS.index(x) if x in FORMATS else 99)

ALL_FMT=get_all_formats(bat_fmt)

def avail(df,col):
    return sorted(df[col].unique().tolist(),key=lambda x:FORMATS.index(x) if x in FORMATS else 99)

# ── Smart search: tries exact, then last name, then fuzzy first/last ──────
def find_rows(df, name_col, query):
    """Smart search: tries 4 strategies to match player names across naming conventions."""
    if df.empty: return pd.DataFrame()
    q = query.strip()
    # 1. Direct contains (handles most cases)
    mask = df[name_col].str.contains(q, case=False, na=False)
    if mask.any(): return df[mask]
    parts = q.split()
    # 2. Each word individually (handles "Smriti" finding "Smriti Mandhana" or "S Mandhana")
    for part in parts:
        if len(part) >= 4:
            mask = df[name_col].str.contains(part, case=False, na=False)
            if mask.any(): return df[mask]
    # 3. Last name only (handles "Mandhana" -> "S Mandhana")
    if len(parts) >= 2:
        last = parts[-1]
        if len(last) >= 4:
            mask = df[name_col].str.contains(last, case=False, na=False)
            if mask.any(): return df[mask]
    # 4. Initial + last name  e.g. "Smriti Mandhana" -> "S Mandhana"
    if len(parts) >= 2:
        initial = parts[0][0].upper()
        last = parts[-1]
        pattern = rf"(?i)\b{initial}\w*\s+{last}"
        mask = df[name_col].str.contains(pattern, case=False, na=False, regex=True)
        if mask.any(): return df[mask]
    return pd.DataFrame()

def ch(fig, h=380, margin=None):
    fig.update_layout(**BASE, height=h, margin=margin or M_DEFAULT)
    st.plotly_chart(fig, **CFG)

def bar_h(df, x, y, col, scale, title, min_h=400):
    """Horizontal bar — auto-sizes height so bars are never squished."""
    if df.empty: return go.Figure()
    n = len(df)
    h = max(min_h, n * 52 + 80)          # 52px per bar minimum
    xmax = float(df[x].max()) * 1.22
    fig = px.bar(df, x=x, y=y, orientation="h", color=col,
                 color_continuous_scale=scale, title=title)
    fig.update_traces(marker_line_width=0,
                      text=df[x].round(1).astype(str),
                      textposition="outside",
                      textfont=dict(size=11, color=TEXT),
                      cliponaxis=False)
    fig.update_layout(**BASE, height=h, coloraxis_showscale=False,
                      margin=dict(l=20, r=90, t=48, b=8), bargap=0.28)
    fig.update_yaxes(categoryorder="total ascending", showgrid=False,
                     title="", tickfont=dict(size=12, color=TEXT),
                     automargin=True, tickmode="linear")
    fig.update_xaxes(showgrid=True, gridcolor=GRID, title="",
                     tickfont=dict(size=11), range=[0, xmax])
    return fig

def bar_v(df, x, y, title, color, h=360):
    if df.empty: return go.Figure()
    fig = px.bar(df, x=x, y=y, text=y, title=title, color_discrete_sequence=[color])
    fig.update_traces(textposition="outside", textfont=dict(size=12, color=TEXT),
                      marker_line_width=0)
    fig.update_layout(**BASE, height=h, showlegend=False, margin=M_BARV)
    fig.update_xaxes(tickmode="linear", tickangle=-40, showgrid=False,
                     tickfont=dict(size=12), automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor=GRID)
    return fig

def line(df, x, y, title, color, h=280):
    if df.empty: return go.Figure()
    fig = px.line(df, x=x, y=y, markers=True, title=title)
    fig.update_traces(line=dict(color=color, width=3),
                      marker=dict(size=8, color=color,
                                  line=dict(width=2, color=BG)))
    fig.update_layout(**BASE, height=h, margin=M_DEFAULT)
    return fig

def donut(labels, values, colors, title):
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors, line=dict(color=BG, width=3)),
        textinfo="percent+label", textfont=dict(size=13, color=TEXT)))
    fig.update_layout(**BASE, height=320, title=title,
                      showlegend=False, margin=M_DEFAULT)
    return fig

def metrics(d):
    cols = st.columns(len(d))
    for c, (k, v) in zip(cols, d.items()): c.metric(k, v)

def page_banner(emoji, title, subtitle, ga, gb, glow):
    st.markdown(f"""<div style="background:linear-gradient(135deg,{ga} 0%,{gb} 100%);border-radius:16px;padding:22px 24px;margin:0 0 20px 0;border:1px solid {glow}44">
  <div style="display:flex;align-items:center;gap:14px">
    <div style="font-size:44px">{emoji}</div>
    <div><div style="color:#fff;font-size:22px;font-weight:800">{title}</div>
    <div style="color:#aabbcc;font-size:13px;margin-top:3px">{subtitle}</div></div>
  </div></div>""",unsafe_allow_html=True)

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
    "smriti":"Smriti Mandhana","mandhana":"Smriti Mandhana",
    "smriti mandhana":"Smriti Mandhana",
    "shafali":"Shafali Verma","verma":"Shafali Verma",
    "harmanpreet":"Harmanpreet Kaur","kaur":"Harmanpreet Kaur",
    "deepti":"Deepti Sharma","mithali":"Mithali Raj","raj":"Mithali Raj",
    "jhulan":"Jhulan Goswami","goswami":"Jhulan Goswami","richa":"Richa Ghosh",
    "healy":"AJ Healy","perry":"EA Perry","gardner":"A Gardner",
    "sciver":"NR Sciver","tahlia":"TM McGrath","mcgrath":"TM McGrath",
    "amelia":"AMC Kerr","kerr":"AMC Kerr","devine":"SFM Devine",
}
def resolve(name): return NAME_ALIASES.get(name.strip().lower(), name)

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
    "Mithali Raj":"Mithali Raj","Jhulan Goswami":"Jhulan Goswami",
    "Richa Ghosh":"Richa Ghosh cricketer","AJ Healy":"Alyssa Healy",
    "EA Perry":"Ellyse Perry","A Gardner":"Ashleigh Gardner",
    "NR Sciver":"Nat Sciver-Brunt","TM McGrath":"Tahlia McGrath",
    "AMC Kerr":"Amelia Kerr","SFM Devine":"Sophie Devine",
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_wiki(cricsheet_name, search_name):
    try:
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
        bio=bio.replace("..",".").strip()
        ir=requests.get("https://en.wikipedia.org/w/api.php",
            params={"action":"query","titles":page_title,"prop":"revisions",
                    "rvprop":"content","rvslots":"main","format":"json","rvsection":0},
            timeout=8,headers={"User-Agent":"CricketAnalyticsApp/2.0"})
        ir.raise_for_status()
        pages=ir.json().get("query",{}).get("pages",{})
        wt=next(iter(pages.values())).get("revisions",[{}])[0].get("slots",{}).get("main",{}).get("*","")
        import re
        def clean(v):
            v=re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]",r"\2",v)
            v=re.sub(r"\{\{[^}]+\}\}","",v); v=re.sub(r"<[^>]+>","",v)
            return v.strip().strip("|").strip()
        def ef(text,keys):
            for k in keys:
                m=re.search(r"\|\s*"+re.escape(k)+r"\s*=\s*([^\n\|}{]{2,80})",text,re.IGNORECASE)
                if m:
                    v=clean(m.group(1))
                    if len(v)>3: return v
            return ""
        def er(text,keys):
            for k in keys:
                m=re.search(r"\|\s*"+re.escape(k)+r"\s*=\s*([^\n]{2,150})",text,re.IGNORECASE)
                if m: return m.group(1).strip()
            return ""
        def pd2(v):
            if not v: return ""
            mo=["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            m=re.search(r"\{\{(?:dts|birth date(?:[^|]*)?)\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|\s*(\d{1,2})",v,re.IGNORECASE)
            if m:
                try: return f"{int(m.group(3))} {mo[int(m.group(2))]} {m.group(1)}"
                except: pass
            m2=re.search(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})",v)
            if m2:
                try:
                    mx=int(m2.group(2))
                    if 1<=mx<=12: return f"{int(m2.group(3))} {mo[mx]} {m2.group(1)}"
                except: pass
            m3=re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",v)
            if m3: return f"{int(m3.group(1))} {m3.group(2)[:3].capitalize()} {m3.group(3)}"
            m4=re.search(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})",v)
            if m4: return f"{int(m4.group(2))} {m4.group(1)[:3].capitalize()} {m4.group(3)}"
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
        odi_d=pd2(er(wt,["odidebutdate","ODIdebutdate","odi_debut_date"]))
        test_d=pd2(er(wt,["testdebutdate","Testdebutdate","test_debut_date"]))
        t20_d=pd2(er(wt,["t20idebutdate","T20Idebutdate","T20debutdate","t20_debut_date"]))
        any_d=pd2(er(wt,["debutdate","debut_date","internationaldebutdate"]))
        role_raw=ef(wt,["role","batting_style","batting style","bowling_style","bowling style"])
        # Strip any remaining wikilinks like [[Batter (cricket)]]
        role_raw=re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]",r"\2",role_raw)
        role_raw=re.sub(r"\{\{[^}]+\}\}","",role_raw).strip()
        # If wikitext role looks like garbage, fall back to Wikipedia description
        desc=data.get("description","")
        if not role_raw or "[[" in role_raw or len(role_raw)<3:
            role_raw=desc[:60] if desc else ""
        nation=ef(wt,["country","nationality","national_side","national side"])
        return {"title":data.get("title",page_title),"bio":bio,"img":img,
                "born":born[:60] if born else "",
                "odi_debut":odi_d if odi_d else any_d,
                "test_debut":test_d if test_d else any_d,
                "t20_debut":t20_d if t20_d else any_d,
                "ipl_debut":"","psl_debut":"","wpl_debut":"",
                "role":role_raw[:60] if role_raw else "",
                "nation":nation[:40] if nation else ""}
    except Exception: return None

def show_player_card(cricsheet_name, search_name, fmt="ODI", compact=False):
    card=get_wiki(cricsheet_name,search_name)
    if not card:
        st.markdown(f"""<div style="background:{CARD};border-radius:14px;padding:14px 16px;margin:0 0 16px 0;border:1px solid #2d3561">
  <div style="color:#aaa;font-size:13px">📖 Profile unavailable for {cricsheet_name}</div></div>""",unsafe_allow_html=True)
        return
    img_w=88 if compact else 110; img_h=108 if compact else 135
    img_html=""
    if card["img"]:
        img_html=f'<div style="flex-shrink:0"><img src="{card["img"]}" style="width:{img_w}px;height:{img_h}px;object-fit:cover;border-radius:10px;border:2px solid #2d3561;display:block;box-shadow:0 4px 14px #000a"></div>'
    fmt_key={"ODI":"odi_debut","Test":"test_debut","T20I":"t20_debut","IPL":"ipl_debut",
             "PSL":"psl_debut","WPL":"wpl_debut","BBL":"odi_debut","CPL":"odi_debut"}.get(fmt,"odi_debut")
    debut=card.get(fmt_key,"") or card.get("odi_debut","") or card.get("test_debut","") or card.get("t20_debut","")
    psz="10px" if compact else "11px"
    pills=""
    if card["born"]: pills+=f'<span style="background:#1e2a3a;color:#00b894;padding:3px 8px;border-radius:20px;font-size:{psz};font-weight:600;margin:2px 2px 2px 0;display:inline-block;white-space:nowrap">🎂 {card["born"]}</span>'
    if card["nation"]: pills+=f'<span style="background:#1e2a3a;color:#0984e3;padding:3px 8px;border-radius:20px;font-size:{psz};font-weight:600;margin:2px 2px 2px 0;display:inline-block;white-space:nowrap">🌍 {card["nation"]}</span>'
    if card["role"]: pills+=f'<span style="background:#1e2a3a;color:#fdcb6e;padding:3px 8px;border-radius:20px;font-size:{psz};font-weight:600;margin:2px 2px 2px 0;display:inline-block;white-space:nowrap">🏏 {card["role"][:30]}</span>'
    if debut: pills+=f'<span style="background:#1e2a3a;color:#e17055;padding:3px 8px;border-radius:20px;font-size:{psz};font-weight:600;margin:2px 2px 2px 0;display:inline-block;white-space:nowrap">🎯 {fmt}: {debut}</span>'
    max_sents=2 if compact else 4
    short_bio=". ".join(card["bio"].split(". ")[:max_sents])+"." if card["bio"] else ""
    name_sz="15px" if compact else "20px"
    st.markdown(f"""<div style="background:linear-gradient(135deg,#1a1f3a,#0f1117);border-radius:14px;padding:14px;margin:0 0 14px 0;border:1px solid #2d3561;display:flex;gap:12px;align-items:flex-start;overflow:hidden;box-sizing:border-box;width:100%">
  {img_html}
  <div style="flex:1;min-width:0;overflow:hidden">
    <div style="color:#fff;font-size:{name_sz};font-weight:800;margin-bottom:6px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{card["title"]}</div>
    <div style="display:flex;flex-wrap:wrap;gap:3px;margin-bottom:7px">{pills}</div>
    <div style="color:#8899bb;font-size:12px;line-height:1.6;overflow:hidden;display:-webkit-box;-webkit-line-clamp:{max_sents+1};-webkit-box-orient:vertical">{short_bio}</div>
  </div>
</div>""",unsafe_allow_html=True)

section=st.sidebar.radio("Navigate",[
    "🔍 Player Search","⚔️ Head to Head","🏟️ Player vs Venue",
    "🌍 Player vs Opponent","🤜 Batter vs Bowler",
    "📈 Performance Over Years","🏆 Leaderboard",
    "🤖 Similar Players","🔥 Form & Ratings"])

# ══ 1. PLAYER SEARCH ═══════════════════════════════════════════════════════
if section=="🔍 Player Search":
    badges="".join([f'<span style="background:linear-gradient(135deg,{FORMAT_META.get(f,("","#00b894","#00b894"))[1]},{FORMAT_META.get(f,("","#00b894","#00b894"))[2]});color:#fff;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:700">{FORMAT_META.get(f,("🏏","",""))[0]} {f}</span>' for f in ALL_FMT])
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0d1b2a,#1a1f3a,#0d1b2a);border-radius:20px;padding:36px 24px 28px;margin:0 0 24px 0;border:1px solid #2d3561;text-align:center">
  <div style="font-size:56px;margin-bottom:10px">🏏</div>
  <h1 style="color:#fff;margin:0 0 6px;font-size:28px;font-weight:800">Cricket Analytics</h1>
  <p style="color:#8899bb;font-size:14px;margin:0 0 20px">Ball-by-ball records · ODI · Test · T20I · IPL · PSL · WPL · BBL · CPL</p>
  <div style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-bottom:20px">{badges}</div>
  <p style="color:#556;font-size:13px;margin:0">Try: <span style="color:#00b894;font-weight:600">Babar</span> · <span style="color:#0984e3;font-weight:600">Kohli</span> · <span style="color:#fd79a8;font-weight:600">Smriti</span> · <span style="color:#6c5ce7;font-weight:600">Shaheen</span> · <span style="color:#ff7675;font-weight:600">Maxwell (BBL)</span></p>
</div>""",unsafe_allow_html=True)

    name=st.text_input("🔍  Search player","",placeholder="e.g. Babar, Kohli, Smriti, Harmanpreet, Maxwell...")
    if name:
        sname=resolve(name)
        # Use smart find_rows for both bat and bowl
        ab_rows=find_rows(bat_fmt,"striker",sname)
        aw_rows=find_rows(bowl_fmt,"bowler",sname)
        ab=ab_rows["format"].unique().tolist() if not ab_rows.empty else []
        aw=aw_rows["format"].unique().tolist() if not aw_rows.empty else []
        avl=sorted(set(ab+aw),key=lambda x:FORMATS.index(x) if x in FORMATS else 99)
        if not avl:
            st.error(f"No data found for '{name}'. Try a different spelling or ensure their format data is loaded.")
            st.stop()

        fmt=st.radio("📋 Format",avl,horizontal=True)
        clr=FC.get(fmt,"#00b894")
        bat=find_rows(bat_fmt[(bat_fmt["format"]==fmt)], "striker", sname)
        bowl=find_rows(bowl_fmt[(bowl_fmt["format"]==fmt)], "bowler", sname)
        display_name=bat["striker"].iloc[0] if len(bat)>0 else (bowl["bowler"].iloc[0] if len(bowl)>0 else sname)
        show_player_card(display_name,name,fmt)

        if len(bat)>0:
            p=bat.sort_values("runs",ascending=False).iloc[0]
            st.subheader(f"🏏 {p['striker']} — Batting ({fmt})")
            metrics({"Matches":int(p["matches"]),"Runs":f"{int(p['runs']):,}","Average":p["average"]})
            metrics({"Strike Rate":p["strike_rate"],"4s":int(p["fours"]),"6s":int(p["sixes"])})
            metrics({"Dismissals":int(p["dismissals"]),"Dot Ball %":f"{p['dot_pct']}%","Boundary %":f"{p['boundary_pct']}%"})
            h100=int(p["hundreds"]) if "hundreds" in p.index and pd.notna(p.get("hundreds")) else "—"
            h50=int(p["fifties"]) if "fifties" in p.index and pd.notna(p.get("fifties")) else "—"
            hs=int(p["highest"]) if "highest" in p.index and pd.notna(p.get("highest")) else "—"
            dk=int(p["ducks"]) if "ducks" in p.index and pd.notna(p.get("ducks")) else "—"
            ps=round(float(p["player_score"]),1) if "player_score" in p.index and pd.notna(p.get("player_score")) else "—"
            metrics({"100s":h100,"50s":h50,"Highest Score":hs,"Ducks":dk,"⭐ Player Score":ps})

            by=find_rows(bat_yr[bat_yr["format"]==fmt],"striker",sname).sort_values("year") if not bat_yr.empty else pd.DataFrame()
            if len(by)>1:
                ch(bar_v(by,"year","runs","Runs per Year",clr))
                c1,c2=st.columns(2)
                with c1: ch(line(by,"year","average","Batting Average",clr),280)
                with c2: ch(line(by,"year","strike_rate","Strike Rate","#fdcb6e"),280)

            fr=int(p["fours"])*4; sr=int(p["sixes"])*6; or_=max(0,int(p["runs"])-fr-sr)
            ch(donut(["Fours","Sixes","Other"],[fr,sr,or_],[clr,"#d63031","#636e72"],"Scoring Breakdown"),320)

        st.divider()
        if len(bowl)>0:
            p2=bowl.sort_values("wickets",ascending=False).iloc[0]
            st.subheader(f"🎳 {p2['bowler']} — Bowling ({fmt})")
            metrics({"Matches":int(p2["matches"]),"Wickets":int(p2["wickets"]),"Economy":p2["economy"]})
            metrics({"Average":p2["average"],"Strike Rate":p2["strike_rate"],"Dot Ball %":f"{p2['dot_pct']}%"})
            fw=int(p2["five_wkts"]) if "five_wkts" in p2.index and pd.notna(p2.get("five_wkts")) else "—"
            bb=p2.get("best_bowling","—") if "best_bowling" in p2.index else "—"
            metrics({"5-Wicket Hauls":fw,"Best Bowling":bb})
            by2=find_rows(bowl_yr[bowl_yr["format"]==fmt],"bowler",sname).sort_values("year") if not bowl_yr.empty else pd.DataFrame()
            if len(by2)>1:
                ch(bar_v(by2,"year","wickets","Wickets per Year",clr))
                c1,c2=st.columns(2)
                with c1: ch(line(by2,"year","economy","Economy Rate","#d63031"),280)
                with c2: ch(line(by2,"year","average","Bowling Average","#6c5ce7"),280)

        if len(bat)==0 and len(bowl)==0:
            st.warning(f"No {fmt} data for '{display_name}'. This format may not have downloaded.")

# ══ 2. HEAD TO HEAD ════════════════════════════════════════════════════════
elif section=="⚔️ Head to Head":
    page_banner("⚔️","Head to Head","Pick two players and see who dominates across formats","#1a0a2e","#2d1b4e","#6c5ce7")
    c1,c2=st.columns(2)
    n1=c1.text_input("Player 1","Kohli"); n2=c2.text_input("Player 2","Babar Azam")
    fmt=st.radio("Format",ALL_FMT,horizontal=True)
    if n1 and n2:
        s1=resolve(n1); s2=resolve(n2)
        b1=find_rows(bat_fmt[bat_fmt["format"]==fmt],"striker",s1)
        b2=find_rows(bat_fmt[bat_fmt["format"]==fmt],"striker",s2)
        if len(b1)==0 or len(b2)==0:
            st.error(f"One or both players have no {fmt} data.")
        else:
            p1=b1.iloc[0]; p2=b2.iloc[0]; p1n=p1["striker"]; p2n=p2["striker"]
            cc1,cc2=st.columns(2)
            with cc1: show_player_card(p1n,n1,fmt,compact=True)
            with cc2: show_player_card(p2n,n2,fmt,compact=True)
            st.subheader(f"🏏 Batting — {fmt}")
            LABELS={"runs":"Runs","fours":"Fours","sixes":"Sixes","average":"Avg",
                    "strike_rate":"Strike Rate","dot_pct":"Dot %","boundary_pct":"Boundary %"}
            for title,ml in [("🏏 Volume",["runs","fours","sixes"]),
                              ("📈 Rates",["average","strike_rate"]),
                              ("📊 Percentages",["dot_pct","boundary_pct"])]:
                pretty=[LABELS.get(m,m) for m in ml]
                v1=[float(p1.get(m,0)) for m in ml]; v2=[float(p2.get(m,0)) for m in ml]
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
                                  height=max(220,len(ml)*120),margin=dict(l=20,r=100,t=48,b=8))
                fig.update_yaxes(showgrid=False,tickfont=dict(size=14),title="",automargin=True)
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

# ══ 3. PLAYER VS VENUE ═════════════════════════════════════════════════════
elif section=="🏟️ Player vs Venue":
    page_banner("🏟️","Player vs Venue","How does a player perform at different grounds?","#0a1a1a","#0d2b2b","#00b894")
    name=st.text_input("Player name","Kohli"); st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=(find_rows(bat_ven,"striker",sname) if st_=="Batting"
             else find_rows(bowl_ven,"bowler",sname))
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

# ══ 4. PLAYER VS OPPONENT ══════════════════════════════════════════════════
elif section=="🌍 Player vs Opponent":
    page_banner("🌍","Player vs Opponent","Find which teams a player dominates — and which trouble them","#0a1020","#0d1e3a","#0984e3")
    name=st.text_input("Player name","Kohli"); st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=(find_rows(bat_opp,"striker",sname) if st_=="Batting"
             else find_rows(bowl_opp,"bowler",sname))
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

# ══ 5. BATTER VS BOWLER ════════════════════════════════════════════════════
elif section=="🤜 Batter vs Bowler":
    page_banner("🤜","Batter vs Bowler","The ultimate matchup — who has the edge ball by ball?","#1a0a0a","#2e1010","#d63031")
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

# ══ 6. PERFORMANCE OVER YEARS ══════════════════════════════════════════════
elif section=="📈 Performance Over Years":
    page_banner("📈","Performance Over Years","Track how a player has evolved season by season","#0a150a","#0d2a10","#00b894")
    name=st.text_input("Player name","Kohli"); st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=(find_rows(bat_yr,"striker",sname) if st_=="Batting"
             else find_rows(bowl_yr,"bowler",sname))
        if len(src)==0: st.error("Player not found!")
        else:
            fmt=st.radio("Format",avail(src,"format"),horizontal=True)
            by=src[src["format"]==fmt].sort_values("year"); clr=FC.get(fmt,"#00b894")
            if st_=="Batting":
                ch(bar_v(by,"year","runs","Runs per Year",clr))
                c1,c2=st.columns(2)
                with c1: ch(line(by,"year","average","Batting Average",clr),280)
                with c2: ch(line(by,"year","strike_rate","Strike Rate","#fdcb6e"),280)
                st.dataframe(by[["year","matches","runs","average","strike_rate","fours","sixes"]].reset_index(drop=True))
            else:
                ch(bar_v(by,"year","wickets","Wickets per Year",clr))
                c1,c2=st.columns(2)
                with c1: ch(line(by,"year","economy","Economy Rate","#d63031"),280)
                with c2: ch(line(by,"year","average","Bowling Average","#6c5ce7"),280)
                st.dataframe(by[["year","matches","wickets","economy","average","dot_pct"]].reset_index(drop=True))

# ══ 7. LEADERBOARD ═════════════════════════════════════════════════════════
elif section=="🏆 Leaderboard":
    page_banner("🏆","Leaderboard","The greatest — ranked by format and stat","#1a1400","#2e2400","#fdcb6e")
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

# ══ 8. SIMILAR PLAYERS ═════════════════════════════════════════════════════
elif section=="🤖 Similar Players":
    page_banner("🤖","Similar Players","ML-powered: find cricketers who play just like your favourite","#0a0a1a","#1a1a3a","#a29bfe")
    st.markdown("Uses **KMeans clustering + cosine similarity** on career stats to find statistically similar players.")
    st_type=st.radio("Type",["Batter","Bowler"],horizontal=True)
    name=st.text_input("Player name","Babar"); fmt=st.radio("Format",ALL_FMT,horizontal=True)
    if name:
        sname=resolve(name)
        if st_type=="Batter":
            src=find_rows(bat_sim[bat_sim["format"]==fmt],"striker",sname)
            if len(src)==0: st.error(f"No ML data for '{name}' in {fmt}. They may have <200 runs in this format.")
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

# ══ 9. FORM & RATINGS ══════════════════════════════════════════════════════
elif section=="🔥 Form & Ratings":
    page_banner("🔥","Form & Ratings","Who is on fire right now? Last 2 seasons vs career average","#1a0800","#2e1500","#e17055")
    fmt=st.radio("Format",ALL_FMT,horizontal=True)
    tab1,tab2,tab3=st.tabs(["🏏 Batting Form","🎳 Bowling Form","⭐ Player Scores"])
    with tab1:
        src=bat_form[bat_form["format"]==fmt].copy() if not bat_form.empty else pd.DataFrame()
        t1,t2=st.tabs(["🔥 On Fire","📉 Struggling"])
        with t1:
            top=src[src["form_score"]>=110].sort_values("form_score",ascending=False).head(20) if len(src)>0 else pd.DataFrame()
            if len(top)>0:
                ch(bar_h(top,"form_score","striker","form_score","Oranges",f"🔥 On Fire Batters ({fmt})"))
                st.dataframe(top[["striker","form_label","form_score","recent_avg","career_avg","recent_sr","career_sr"]].reset_index(drop=True))
            else: st.info("No batters in 'On Fire' form for this format yet.")
        with t2:
            bot=src[src["form_score"]<70].sort_values("form_score").head(20) if len(src)>0 else pd.DataFrame()
            if len(bot)>0:
                ch(bar_h(bot,"form_score","striker","form_score","Blues",f"📉 Struggling Batters ({fmt})"))
                st.dataframe(bot[["striker","form_label","form_score","recent_avg","career_avg"]].reset_index(drop=True))
            else: st.info("No batters struggling in this format.")
    with tab2:
        src2=bowl_form[bowl_form["format"]==fmt].copy() if not bowl_form.empty else pd.DataFrame()
        t1,t2=st.tabs(["🔥 On Fire","📉 Struggling"])
        with t1:
            top2=src2[src2["form_score"]>=110].sort_values("form_score",ascending=False).head(20) if len(src2)>0 else pd.DataFrame()
            if len(top2)>0:
                ch(bar_h(top2,"form_score","bowler","form_score","Oranges",f"🔥 On Fire Bowlers ({fmt})"))
                st.dataframe(top2[["bowler","form_label","form_score","recent_econ","career_econ","recent_avg","career_avg"]].reset_index(drop=True))
            else: st.info("No bowlers in 'On Fire' form for this format yet.")
        with t2:
            bot2=src2[src2["form_score"]<70].sort_values("form_score").head(20) if len(src2)>0 else pd.DataFrame()
            if len(bot2)>0:
                ch(bar_h(bot2,"form_score","bowler","form_score","Blues",f"📉 Struggling Bowlers ({fmt})"))
                st.dataframe(bot2[["bowler","form_label","form_score","recent_econ","career_econ"]].reset_index(drop=True))
            else: st.info("No bowlers struggling in this format.")
    with tab3:
        ps=bat_sim[bat_sim["format"]==fmt].sort_values("player_score",ascending=False).head(25) if not bat_sim.empty else pd.DataFrame()
        if len(ps)>0:
            ch(bar_h(ps,"player_score","striker","player_score","Teal",f"⭐ Top 25 Player Scores ({fmt})"))
            st.caption("Score = Average 30% · Strike Rate 25% · Boundary% 20% · Runs volume 15% · Non-dot% 10%")
            st.dataframe(ps[["striker","player_score","average","strike_rate","boundary_pct","runs"]].reset_index(drop=True))
        else: st.info(f"No player score data for {fmt} yet.")
