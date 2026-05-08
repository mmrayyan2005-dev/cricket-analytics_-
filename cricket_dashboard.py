import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(page_title="Cricket Analytics", layout="wide", page_icon="🏏",
                   initial_sidebar_state="collapsed")

# ── GitHub raw base ──────────────────────────────────────────────────────────
RAW_BASE = "https://raw.githubusercontent.com/mmrayyan2005-dev/cricket-analytics-/main"

# ── Design Tokens ────────────────────────────────────────────────────────────
BG    = "#080c14"
CARD  = "#0e1524"
CARD2 = "#131c2e"
TEXT  = "#dce3f0"
MUT   = "#5a6a8a"
GRID  = "#1a2336"
BORDER= "#1e2d47"

FC = {
    "ODI":  "#00d4a0",
    "Test": "#4d9eff",
    "T20I": "#ff4f6d",
    "IPL":  "#ffb830",
    "PSL":  "#a78bfa",
    "WPL":  "#f472b6",
    "BBL":  "#fb923c",
    "CPL":  "#34d399",
}
FORMATS = ["ODI", "Test", "T20I", "IPL", "PSL", "WPL", "BBL", "CPL"]

FORMAT_META = {
    "ODI":  ("🌐", "#00d4a0", "#00a37a"),
    "Test": ("🏛️", "#4d9eff", "#2563eb"),
    "T20I": ("⚡", "#ff4f6d", "#be123c"),
    "IPL":  ("🏏", "#ffb830", "#d97706"),
    "PSL":  ("🟣", "#a78bfa", "#7c3aed"),
    "WPL":  ("💜", "#f472b6", "#be185d"),
    "BBL":  ("🔥", "#fb923c", "#c2410c"),
    "CPL":  ("🌴", "#34d399", "#059669"),
}

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT, family="Inter, sans-serif", size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    xaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, color=TEXT, fixedrange=True),
    yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, color=TEXT, fixedrange=True),
    dragmode=False,
)
MD = dict(l=8, r=8, t=44, b=8)
MD_BAR = dict(l=8, r=8, t=44, b=56)
CFG = dict(config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False, "responsive": True},
           use_container_width=True)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;background:{BG};color:{TEXT}}}
::-webkit-scrollbar{{width:6px;height:6px}}
::-webkit-scrollbar-track{{background:{CARD}}}
::-webkit-scrollbar-thumb{{background:{BORDER};border-radius:4px}}
[data-testid="stMetric"]{{background:linear-gradient(135deg,{CARD} 0%,{CARD2} 100%);border-radius:14px;padding:14px 18px;border:1px solid {BORDER};transition:border-color .2s}}
[data-testid="stMetric"]:hover{{border-color:#2e4a7a}}
[data-testid="stMetricLabel"]{{font-size:10px;color:{MUT};text-transform:uppercase;letter-spacing:1px;font-weight:600}}
[data-testid="stMetricValue"]{{font-size:22px;font-weight:800;color:{TEXT};letter-spacing:-0.5px}}
div[data-baseweb="tab-list"]{{gap:6px;background:transparent}}
div[data-baseweb="tab"]{{border-radius:10px;padding:7px 16px;background:{CARD};border:1px solid {BORDER};font-weight:600;font-size:13px}}
div[data-baseweb="tab"][aria-selected="true"]{{background:linear-gradient(135deg,#0f2a4a,#0d1f38)!important;border-color:#2e4a7a!important}}
[data-testid="stSidebar"]{{background:{CARD}!important;border-right:1px solid {BORDER}}}
.stTextInput input{{background:{CARD2}!important;border:1px solid {BORDER}!important;border-radius:10px!important;color:{TEXT}!important;font-size:14px!important;padding:10px 14px!important}}
.stTextInput input:focus{{border-color:#2e4a7a!important;box-shadow:0 0 0 2px rgba(77,158,255,0.15)!important}}
.stSelectbox>div>div{{background:{CARD2}!important;border:1px solid {BORDER}!important;border-radius:10px!important}}
.stDataFrame{{border-radius:12px;overflow:hidden}}
hr{{border-color:{BORDER};margin:20px 0}}
.js-plotly-plot{{touch-action:pan-y!important}}
[data-testid="column"]{{min-width:80px!important}}
</style>
""", unsafe_allow_html=True)


# ── Data Loader ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load():
    def read(name):
        try:
            return pd.read_csv(f"{RAW_BASE}/{name}")
        except:
            return pd.DataFrame()
    return (
        read("cricket_batting_stats.csv"),
        read("cricket_bowling_stats.csv"),
        read("cricket_batting_by_format.csv"),
        read("cricket_bowling_by_format.csv"),
        read("cricket_batting_yearly.csv"),
        read("cricket_bowling_yearly.csv"),
        read("cricket_batting_venue.csv"),
        read("cricket_batting_opponent.csv"),
        read("cricket_bowling_venue.csv"),
        read("cricket_bowling_opponent.csv"),
        read("cricket_batter_vs_bowler.csv"),
        read("cricket_bowler_vs_batter.csv"),
        read("cricket_bat_form_ratings.csv"),
        read("cricket_bowl_form_ratings.csv"),
        read("cricket_bat_similarity.csv"),
        read("cricket_bowl_similarity.csv"),
        read("cricket_bat_innings.csv"),
        read("cricket_bowl_innings.csv"),
    )


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 4px 12px;text-align:center">
      <div style="font-size:36px">🏏</div>
      <div style="font-size:17px;font-weight:800;color:{TEXT};margin:6px 0 2px">Cricket Analytics</div>
      <div style="font-size:11px;color:{MUT}">Ball-by-ball · All formats</div>
    </div>
    """, unsafe_allow_html=True)

    section = st.radio("Navigate", [
        "🔍 Player Search",
        "⚔️ Head to Head",
        "🏟️ Player vs Venue",
        "🌍 Player vs Opponent",
        "🤜 Batter vs Bowler",
        "📈 Performance Over Years",
        "🏆 Leaderboard",
        "🤖 Similar Players",
        "🔥 Form & Ratings",
    ], label_visibility="collapsed")

    st.markdown("<hr style='margin:12px 0'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    if c1.button("🔄", help="Refresh data"):
        st.cache_data.clear(); st.rerun()
    c2.caption(f"Updated {datetime.now().strftime('%H:%M · %d %b')}")
    st.markdown(f"""
    <div style="background:{CARD2};border:1px solid {BORDER};border-radius:10px;padding:10px 12px;font-size:11px;color:{MUT};margin-top:8px">
      <span style="color:#00d4a0;font-weight:700">⚡ Live</span> — auto-refreshes every hour from Cricsheet via GitHub
    </div>
    """, unsafe_allow_html=True)


# ── Load data ────────────────────────────────────────────────────────────────
with st.spinner("Loading cricket data…"):
    (batting, bowling, bat_fmt, bowl_fmt, bat_yr, bowl_yr,
     bat_ven, bat_opp, bowl_ven, bowl_opp,
     bvb, wvb, bat_form, bowl_form, bat_sim, bowl_sim,
     bat_inn, bowl_inn) = load()


# ── Helpers ──────────────────────────────────────────────────────────────────
def avail(df, col="format"):
    if df.empty or col not in df.columns:
        return FORMATS
    return sorted(df[col].unique().tolist(), key=lambda x: FORMATS.index(x) if x in FORMATS else 99)

def get_all_formats(df, col="format"):
    if df.empty or col not in df.columns:
        return ["ODI", "Test", "T20I", "IPL", "PSL"]
    return sorted(df[col].unique().tolist(), key=lambda x: FORMATS.index(x) if x in FORMATS else 99)

ALL_FMT = get_all_formats(bat_fmt)

def ch(fig, h=320, margin=None):
    fig.update_layout(**BASE, height=h, margin=margin or MD)
    st.plotly_chart(fig, **CFG)

def bar_h(df, x, y, col, scale, title):
    max_chars = int(df[y].astype(str).str.len().max()) if len(df) > 0 else 20
    lm = max(220, int(max_chars * 8 + 30))
    h  = max(380, len(df) * 54)
    xmax = float(df[x].max()) * 1.2 if len(df) > 0 else 1
    fig = px.bar(df, x=x, y=y, orientation="h", color=col,
                 color_continuous_scale=scale, title=title)
    fig.update_traces(marker_line_width=0, text=df[x].round(1).astype(str),
                      textposition="outside", textfont=dict(size=10, color=TEXT), cliponaxis=False)
    fig.update_layout(**BASE, height=h, coloraxis_showscale=False,
                      margin=dict(l=lm, r=80, t=44, b=8), bargap=0.3)
    fig.update_yaxes(categoryorder="total ascending", showgrid=False, title="",
                     tickfont=dict(size=12, color=TEXT), automargin=False, tickmode="linear")
    fig.update_xaxes(showgrid=True, gridcolor=GRID, title="", tickfont=dict(size=11), range=[0, xmax])
    return fig

def bar_v(df, x, y, title, color, h=320):
    fig = px.bar(df, x=x, y=y, text=y, title=title, color_discrete_sequence=[color])
    fig.update_traces(textposition="outside", textfont=dict(size=11, color=TEXT),
                      marker_line_width=0, marker_color=color)
    fig.update_layout(**BASE, height=h, showlegend=False, margin=MD_BAR)
    fig.update_xaxes(tickmode="linear", tickangle=-35, showgrid=False,
                     tickfont=dict(size=11), automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor=GRID)
    return fig

def line(df, x, y, title, color, h=260):
    fig = px.line(df, x=x, y=y, markers=True, title=title)
    fig.update_traces(line=dict(color=color, width=2.5),
                      marker=dict(size=7, color=color, line=dict(width=1.5, color=BG)))
    fig.update_layout(**BASE, height=h, margin=MD)
    return fig

def donut(labels, values, colors, title, h=290):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.56,
        marker=dict(colors=colors, line=dict(color=BG, width=2)),
        textinfo="percent+label", textfont=dict(size=12, color=TEXT),
    ))
    fig.update_layout(**BASE, height=h, title=title, showlegend=False, margin=MD)
    return fig

def metrics(d):
    cols = st.columns(len(d))
    for col, (k, v) in zip(cols, d.items()):
        col.metric(k, v)

def section_banner(emoji, title, subtitle, accent):
    st.markdown(f"""
    <div style="background:linear-gradient(120deg,{BG} 0%,{CARD2} 60%,{BG} 100%);
         border-radius:16px;padding:20px 24px;margin:0 0 20px;
         border-left:4px solid {accent};border:1px solid {BORDER};border-left:4px solid {accent}">
      <div style="display:flex;align-items:center;gap:14px">
        <div style="font-size:36px;flex-shrink:0">{emoji}</div>
        <div>
          <div style="color:#fff;font-size:20px;font-weight:800;letter-spacing:-0.3px">{title}</div>
          <div style="color:{MUT};font-size:13px;margin-top:3px">{subtitle}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def fmt_badge(fmt):
    m = FORMAT_META.get(fmt, ("🏏", "#00d4a0", "#00d4a0"))
    return f'<span style="background:{m[1]}22;color:{m[1]};padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid {m[1]}44">{m[0]} {fmt}</span>'

def stat_pill(label, value, color):
    return f'<span style="background:{color}18;color:{color};border:1px solid {color}44;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;display:inline-block;margin:2px">{label}: <b>{value}</b></span>'


# ── Name resolution ──────────────────────────────────────────────────────────
NAME_ALIASES = {
    "steve smith":"SPD Smith","smith":"SPD Smith","hazelwood":"JR Hazlewood",
    "josh hazelwood":"JR Hazlewood","hazlewood":"JR Hazlewood","warner":"DA Warner",
    "david warner":"DA Warner","rohit":"RG Sharma","rohit sharma":"RG Sharma",
    "bumrah":"JJ Bumrah","jasprit bumrah":"JJ Bumrah","starc":"MA Starc",
    "mitchell starc":"MA Starc","kohli":"V Kohli","virat kohli":"V Kohli",
    "babar":"Babar Azam","babar azam":"Babar Azam",
    "de villiers":"AB de Villiers","ab de villiers":"AB de Villiers",
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
    "shafali":"Shafali Verma","harmanpreet":"Harmanpreet Kaur","kaur":"Harmanpreet Kaur",
    "deepti":"Deepti Sharma","mithali":"Mithali Raj","raj":"Mithali Raj",
    "jhulan":"Jhulan Goswami","healy":"AJ Healy","perry":"EA Perry",
    "gardner":"A Gardner","sciver":"NR Sciver","tahlia":"TM McGrath","mcgrath":"TM McGrath",
    "amelia":"AMC Kerr","kerr":"AMC Kerr","devine":"SFM Devine",
}
def resolve(name):
    return NAME_ALIASES.get(name.strip().lower(), name)

WIKI_NAMES = {
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
    "AJ Healy":"Alyssa Healy","EA Perry":"Ellyse Perry","A Gardner":"Ashleigh Gardner",
    "NR Sciver":"Nat Sciver-Brunt","TM McGrath":"Tahlia McGrath",
    "AMC Kerr":"Amelia Kerr","SFM Devine":"Sophie Devine",
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_wiki(cricsheet_name, search_name):
    try:
        import re
        wiki_title = WIKI_NAMES.get(cricsheet_name, search_name + " cricketer")
        sr = requests.get("https://en.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":wiki_title,
                    "format":"json","utf8":1,"srlimit":3},
            timeout=8, headers={"User-Agent":"CricketAnalyticsApp/3.0"})
        sr.raise_for_status()
        results = sr.json().get("query",{}).get("search",[])
        if not results: return None
        page_title = results[0]["title"]
        safe = page_title.replace(" ","_")
        rr = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe}",
            timeout=8, headers={"User-Agent":"CricketAnalyticsApp/3.0"})
        rr.raise_for_status()
        data = rr.json()
        img = data.get("thumbnail",{}).get("source","")
        bio = data.get("extract","")
        sents = [s.strip() for s in bio.split(".") if len(s.strip())>15]
        bio = ". ".join(sents[:4])+"." if sents else bio[:400]
        ir = requests.get("https://en.wikipedia.org/w/api.php",
            params={"action":"query","titles":page_title,"prop":"revisions",
                    "rvprop":"content","rvslots":"main","format":"json","rvsection":0},
            timeout=8, headers={"User-Agent":"CricketAnalyticsApp/3.0"})
        ir.raise_for_status()
        pages = ir.json().get("query",{}).get("pages",{})
        wt = next(iter(pages.values())).get("revisions",[{}])[0].get("slots",{}).get("main",{}).get("*","")
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
        def pd2(v):
            if not v: return ""
            mo=["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            m=re.search(r"\{\{(?:dts|birth date(?:[^|]*)?)\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|\s*(\d{1,2})",v,re.IGNORECASE)
            if m:
                try: return f"{int(m.group(3))} {mo[int(m.group(2))]} {m.group(1)}"
                except: pass
            m2=re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",v)
            if m2: return f"{int(m2.group(1))} {m2.group(2)[:3].capitalize()} {m2.group(3)}"
            return ""
        def er(text,keys):
            for k in keys:
                m=re.search(r"\|\s*"+re.escape(k)+r"\s*=\s*([^\n]{2,150})",text,re.IGNORECASE)
                if m: return m.group(1).strip()
            return ""
        born=""
        bd=re.search(r"\{\{birth date(?:\s*and age)?\s*\|([^}]+)\}\}",wt,re.IGNORECASE)
        if bd:
            parts=[p.strip() for p in bd.group(1).split("|") if p.strip().isdigit()]
            mo2=["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            if len(parts)>=3:
                try: born=f"{int(parts[2])} {mo2[int(parts[1])]} {parts[0]}"
                except: pass
        if not born: born=ef(wt,["birth_date","birthdate","born"])
        odi_d=pd2(er(wt,["odidebutdate","ODIdebutdate"]))
        test_d=pd2(er(wt,["testdebutdate","Testdebutdate"]))
        t20_d=pd2(er(wt,["t20idebutdate","T20Idebutdate","T20debutdate"]))
        any_d=pd2(er(wt,["debutdate","debut_date"]))
        role=ef(wt,["role","batting_style","bowling_style"])
        nation=ef(wt,["country","nationality","national_side"])
        return {
            "title":data.get("title",page_title),"bio":bio,"img":img,
            "born":born[:60] if born else "",
            "odi_debut":odi_d or any_d,"test_debut":test_d or any_d,
            "t20_debut":t20_d or any_d,"ipl_debut":"","psl_debut":"",
            "wpl_debut":"","bbl_debut":"","cpl_debut":"",
            "role":role[:80] if role else data.get("description","")[:60],
            "nation":nation[:40] if nation else "",
        }
    except Exception:
        return None

def show_player_card(cricsheet_name, search_name, fmt="ODI", compact=False):
    card = get_wiki(cricsheet_name, search_name)
    acc = FC.get(fmt, "#00d4a0")
    if not card:
        st.markdown(f'<div style="background:{CARD};border-radius:14px;padding:16px;margin:0 0 16px;border:1px solid {BORDER}"><div style="color:{MUT};font-size:13px">📖 Profile unavailable</div></div>', unsafe_allow_html=True)
        return
    iw = 84 if compact else 104
    ih = 104 if compact else 128
    img_html = f'<div style="flex-shrink:0"><img src="{card["img"]}" style="width:{iw}px;height:{ih}px;object-fit:cover;border-radius:10px;border:2px solid {acc}55;display:block"></div>' if card["img"] else ""
    fmt_key = {"ODI":"odi_debut","Test":"test_debut","T20I":"t20_debut","IPL":"ipl_debut",
               "PSL":"psl_debut","WPL":"wpl_debut","BBL":"bbl_debut","CPL":"cpl_debut"}.get(fmt,"odi_debut")
    debut = card.get(fmt_key,"") or card.get("odi_debut","") or card.get("test_debut","") or card.get("t20_debut","")
    pills = ""
    if card["born"]:   pills += stat_pill("🎂", card["born"], "#00d4a0")
    if card["nation"]: pills += stat_pill("🌍", card["nation"], "#4d9eff")
    if card["role"]:   pills += stat_pill("🏏", card["role"][:30], "#ffb830")
    if debut:          pills += stat_pill(f"🎯 {fmt}", debut, acc)
    max_s = 2 if compact else 4
    short_bio = ". ".join(card["bio"].split(". ")[:max_s])+"." if card["bio"] else ""
    nsz = "15px" if compact else "19px"
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{CARD} 0%,{CARD2} 100%);border-radius:16px;
         padding:16px;margin:0 0 16px;border:1px solid {BORDER};border-left:3px solid {acc};
         display:flex;gap:14px;align-items:flex-start;overflow:hidden;box-sizing:border-box;width:100%">
      {img_html}
      <div style="flex:1;min-width:0">
        <div style="color:#fff;font-size:{nsz};font-weight:800;margin-bottom:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{card["title"]}</div>
        <div style="display:flex;flex-wrap:wrap;gap:3px;margin-bottom:8px">{pills}</div>
        <div style="color:{MUT};font-size:12px;line-height:1.65;overflow:hidden;display:-webkit-box;-webkit-line-clamp:{max_s+1};-webkit-box-orient:vertical">{short_bio}</div>
      </div>
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — PLAYER SEARCH
# ════════════════════════════════════════════════════════════════════════════
if section == "🔍 Player Search":
    badges = " ".join([fmt_badge(f) for f in ALL_FMT])
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{BG} 0%,{CARD2} 50%,{BG} 100%);
         border-radius:20px;padding:40px 28px 32px;margin:0 0 24px;border:1px solid {BORDER};text-align:center">
      <div style="font-size:52px;margin-bottom:12px">🏏</div>
      <h1 style="color:#fff;margin:0 0 8px;font-size:30px;font-weight:900;letter-spacing:-1px">Cricket Analytics</h1>
      <p style="color:{MUT};font-size:14px;margin:0 0 20px">Ball-by-ball records across all major formats</p>
      <div style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-bottom:20px">{badges}</div>
      <p style="color:#374a6a;font-size:12px;margin:0">Try: <span style="color:#00d4a0;font-weight:600">Babar</span> · <span style="color:#4d9eff;font-weight:600">Kohli</span> · <span style="color:#f472b6;font-weight:600">Smriti</span> · <span style="color:#a78bfa;font-weight:600">Shaheen</span> · <span style="color:#ffb830;font-weight:600">Rohit</span></p>
    </div>
    """, unsafe_allow_html=True)

    name = st.text_input("🔍  Search player", "", placeholder="e.g. Babar, Kohli, Smriti, Shaheen…")
    if name:
        sname = resolve(name)
        ab = bat_fmt[bat_fmt["striker"].str.contains(sname,case=False,na=False)]["format"].unique().tolist() if not bat_fmt.empty else []
        aw = bowl_fmt[bowl_fmt["bowler"].str.contains(sname,case=False,na=False)]["format"].unique().tolist() if not bowl_fmt.empty else []
        avl = sorted(set(ab+aw), key=lambda x: FORMATS.index(x) if x in FORMATS else 99)
        if not avl:
            st.error(f"No data found for **'{name}'**. Check spelling or try a different name."); st.stop()

        fmt = st.radio("📋 Format", avl, horizontal=True)
        clr = FC.get(fmt,"#00d4a0")
        bat  = bat_fmt[(bat_fmt["striker"].str.contains(sname,case=False,na=False)) & (bat_fmt["format"]==fmt)]
        bowl = bowl_fmt[(bowl_fmt["bowler"].str.contains(sname,case=False,na=False)) & (bowl_fmt["format"]==fmt)]
        display_name = bat["striker"].iloc[0] if len(bat)>0 else (bowl["bowler"].iloc[0] if len(bowl)>0 else sname)
        show_player_card(display_name, name, fmt)

        if len(bat)>0:
            p = bat.sort_values("runs",ascending=False).iloc[0]
            st.markdown(f"### 🏏 {p['striker']} — Batting · {fmt}")
            metrics({"Matches":int(p["matches"]),"Runs":f"{int(p['runs']):,}","Average":p["average"]})
            metrics({"Strike Rate":p["strike_rate"],"4s":int(p["fours"]),"6s":int(p["sixes"])})
            metrics({"Dismissals":int(p["dismissals"]),"Dot %":f"{p['dot_pct']}%","Boundary %":f"{p['boundary_pct']}%"})
            h100 = int(p["hundreds"]) if "hundreds" in p.index and pd.notna(p.get("hundreds")) else "—"
            h50  = int(p["fifties"])  if "fifties"  in p.index and pd.notna(p.get("fifties"))  else "—"
            hs   = int(p["highest"])  if "highest"  in p.index and pd.notna(p.get("highest"))  else "—"
            dk   = int(p["ducks"])    if "ducks"    in p.index and pd.notna(p.get("ducks"))    else "—"
            ps   = round(float(p["player_score"]),1) if "player_score" in p.index and pd.notna(p.get("player_score")) else "—"
            metrics({"100s":h100,"50s":h50,"Highest":hs,"Ducks":dk,"⭐ Score":ps})

            by = bat_yr[(bat_yr["striker"].str.contains(sname,case=False,na=False))&(bat_yr["format"]==fmt)].sort_values("year") if not bat_yr.empty else pd.DataFrame()
            if len(by)>1:
                ch(bar_v(by,"year","runs","Runs per Year",clr))
                c1,c2 = st.columns(2)
                with c1: ch(line(by,"year","average","Batting Average",clr),260)
                with c2: ch(line(by,"year","strike_rate","Strike Rate","#ffb830"),260)

            fr=int(p["fours"])*4; sr=int(p["sixes"])*6; or_=max(0,int(p["runs"])-fr-sr)
            ch(donut(["Fours","Sixes","Other"],[fr,sr,or_],[clr,"#ff4f6d","#374a6a"],"Scoring Breakdown"))

        st.divider()
        if len(bowl)>0:
            p2 = bowl.sort_values("wickets",ascending=False).iloc[0]
            st.markdown(f"### 🎳 {p2['bowler']} — Bowling · {fmt}")
            metrics({"Matches":int(p2["matches"]),"Wickets":int(p2["wickets"]),"Economy":p2["economy"]})
            metrics({"Average":p2["average"],"Strike Rate":p2["strike_rate"],"Dot %":f"{p2['dot_pct']}%"})
            fw = int(p2["five_wkts"]) if "five_wkts" in p2.index and pd.notna(p2.get("five_wkts")) else "—"
            bb = p2.get("best_bowling","—") if "best_bowling" in p2.index else "—"
            metrics({"5-Wkt Hauls":fw,"Best Bowling":bb})
            by2 = bowl_yr[(bowl_yr["bowler"].str.contains(sname,case=False,na=False))&(bowl_yr["format"]==fmt)].sort_values("year") if not bowl_yr.empty else pd.DataFrame()
            if len(by2)>1:
                ch(bar_v(by2,"year","wickets","Wickets per Year",clr))
                c1,c2 = st.columns(2)
                with c1: ch(line(by2,"year","economy","Economy Rate","#ff4f6d"),260)
                with c2: ch(line(by2,"year","average","Bowling Average","#a78bfa"),260)

        if len(bat)==0 and len(bowl)==0:
            st.warning(f"No {fmt} data found for **'{name}'**.")


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — HEAD TO HEAD
# ════════════════════════════════════════════════════════════════════════════
elif section == "⚔️ Head to Head":
    section_banner("⚔️","Head to Head","Pick two players and see who dominates across formats","#a78bfa")
    c1,c2 = st.columns(2)
    n1 = c1.text_input("Player 1","Kohli")
    n2 = c2.text_input("Player 2","Babar Azam")
    fmt = st.radio("Format",ALL_FMT,horizontal=True)
    if n1 and n2:
        s1=resolve(n1); s2=resolve(n2)
        b1=bat_fmt[(bat_fmt["striker"].str.contains(s1,case=False,na=False))&(bat_fmt["format"]==fmt)]
        b2=bat_fmt[(bat_fmt["striker"].str.contains(s2,case=False,na=False))&(bat_fmt["format"]==fmt)]
        if len(b1)==0 or len(b2)==0:
            st.error(f"One or both players have no {fmt} data.")
        else:
            p1=b1.iloc[0]; p2=b2.iloc[0]; p1n=p1["striker"]; p2n=p2["striker"]
            cc1,cc2 = st.columns(2)
            with cc1: show_player_card(p1n,n1,fmt,compact=True)
            with cc2: show_player_card(p2n,n2,fmt,compact=True)

            st.markdown(f"### 🏏 Batting Comparison — {fmt}")
            LABELS={"runs":"Runs","fours":"Fours","sixes":"Sixes","average":"Avg",
                    "strike_rate":"Strike Rate","dot_pct":"Dot %","boundary_pct":"Boundary %"}
            for title,ml in [("Volume Stats",["runs","fours","sixes"]),
                              ("Rate Stats",["average","strike_rate"]),
                              ("Percentage Stats",["dot_pct","boundary_pct"])]:
                pretty=[LABELS.get(m,m) for m in ml]
                v1=[float(p1.get(m,0)) for m in ml]; v2=[float(p2.get(m,0)) for m in ml]
                xmax=max(v1+v2)*1.22 if max(v1+v2)>0 else 10
                fig=go.Figure()
                fig.add_trace(go.Bar(name=p1n,y=pretty,x=v1,orientation="h",
                    marker=dict(color=FC["ODI"],opacity=0.9,line=dict(width=0)),
                    text=[f"{v:.1f}" for v in v1],textposition="outside",
                    textfont=dict(size=11,color=TEXT),cliponaxis=False))
                fig.add_trace(go.Bar(name=p2n,y=pretty,x=v2,orientation="h",
                    marker=dict(color=FC["Test"],opacity=0.9,line=dict(width=0)),
                    text=[f"{v:.1f}" for v in v2],textposition="outside",
                    textfont=dict(size=11,color=TEXT),cliponaxis=False))
                fig.update_layout(**BASE,barmode="group",title=title,
                                  height=max(200,len(ml)*110),margin=dict(l=120,r=90,t=44,b=8))
                fig.update_yaxes(showgrid=False,tickfont=dict(size=13),title="",automargin=True)
                fig.update_xaxes(showgrid=True,gridcolor=GRID,title="",fixedrange=True,range=[0,xmax])
                st.plotly_chart(fig,**CFG)

            by1  = bat_yr[(bat_yr["striker"].str.contains(s1,case=False,na=False))&(bat_yr["format"]==fmt)].copy() if not bat_yr.empty else pd.DataFrame()
            by2y = bat_yr[(bat_yr["striker"].str.contains(s2,case=False,na=False))&(bat_yr["format"]==fmt)].copy() if not bat_yr.empty else pd.DataFrame()
            if len(by1)>0 and len(by2y)>0:
                by1["player"]=p1n; by2y["player"]=p2n
                combined=pd.concat([by1,by2y]).sort_values("year")
                fy=px.line(combined,x="year",y="runs",color="player",markers=True,
                           title=f"Runs per Year — {fmt}",
                           color_discrete_map={p1n:FC["ODI"],p2n:FC["Test"]})
                fy.update_traces(line=dict(width=2.5),marker=dict(size=8))
                fy.update_layout(**BASE,height=340,margin=dict(l=50,r=20,t=44,b=40))
                fy.update_xaxes(title="Year",tickmode="linear",dtick=2,showgrid=True,gridcolor=GRID)
                fy.update_yaxes(title="Runs",showgrid=True,gridcolor=GRID)
                st.plotly_chart(fy,**CFG)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PLAYER VS VENUE
# ════════════════════════════════════════════════════════════════════════════
elif section == "🏟️ Player vs Venue":
    section_banner("🏟️","Player vs Venue","How does a player perform at different grounds?","#00d4a0")
    name=st.text_input("Player name","Kohli")
    st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=(bat_ven[bat_ven["striker"].str.contains(sname,case=False,na=False)] if st_=="Batting"
             else bowl_ven[bowl_ven["bowler"].str.contains(sname,case=False,na=False)])
        if len(src)==0: st.error("Player not found!")
        else:
            fmt=st.radio("Format",avail(src),horizontal=True); df_v=src[src["format"]==fmt]
            if st_=="Batting":
                m=st.selectbox("Metric",["runs","average","strike_rate","fours","sixes"])
                df_v=df_v.sort_values(m,ascending=False).head(15)
                ch(bar_h(df_v,m,"venue",m,"Teal",f"{df_v['striker'].iloc[0]} — {m} by Venue ({fmt})"))
                st.dataframe(df_v[["venue","innings","runs","average","strike_rate"]].reset_index(drop=True))
            else:
                m=st.selectbox("Metric",["wickets","economy","average","dot_pct"])
                df_v=df_v.sort_values(m,ascending=False).head(15)
                ch(bar_h(df_v,m,"venue",m,"Reds",f"{df_v['bowler'].iloc[0]} — {m} by Venue ({fmt})"))
                st.dataframe(df_v[["venue","innings","wickets","economy","average"]].reset_index(drop=True))


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4 — PLAYER VS OPPONENT
# ════════════════════════════════════════════════════════════════════════════
elif section == "🌍 Player vs Opponent":
    section_banner("🌍","Player vs Opponent","Which teams does a player dominate — and which trouble them?","#4d9eff")
    name=st.text_input("Player name","Kohli")
    st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=(bat_opp[bat_opp["striker"].str.contains(sname,case=False,na=False)] if st_=="Batting"
             else bowl_opp[bowl_opp["bowler"].str.contains(sname,case=False,na=False)])
        if len(src)==0: st.error("Player not found!")
        else:
            fmt=st.radio("Format",avail(src),horizontal=True); df_o=src[src["format"]==fmt]
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


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5 — BATTER VS BOWLER
# ════════════════════════════════════════════════════════════════════════════
elif section == "🤜 Batter vs Bowler":
    section_banner("🤜","Batter vs Bowler","The ultimate matchup — who has the edge ball by ball?","#ff4f6d")
    mt=st.radio("Look up a…",["Batter","Bowler"],horizontal=True)
    if mt=="Batter":
        name=st.text_input("Batter name","Babar Azam")
        if name:
            sname=resolve(name); src=bvb[bvb["striker"].str.contains(sname,case=False,na=False)]
            if len(src)==0: st.error("Not found!")
            else:
                fmt=st.radio("Format",avail(src),horizontal=True); df_m=src[src["format"]==fmt]
                m=st.selectbox("Sort by",["balls_faced","runs","strike_rate","dismissals"])
                df_m=df_m.sort_values(m,ascending=False).head(20)
                ch(bar_h(df_m,m,"bowler",m,"Greens",f"Top 20 bowlers faced — {m} ({fmt})"))
                st.dataframe(df_m[["bowler","balls_faced","runs","strike_rate","dismissals"]].reset_index(drop=True))
    else:
        name=st.text_input("Bowler name","Shaheen")
        if name:
            sname=resolve(name); src=wvb[wvb["bowler"].str.contains(sname,case=False,na=False)]
            if len(src)==0: st.error("Not found!")
            else:
                fmt=st.radio("Format",avail(src),horizontal=True); df_m=src[src["format"]==fmt]
                m=st.selectbox("Sort by",["wickets","economy","dot_pct","runs_given"])
                df_m=df_m.sort_values(m,ascending=(m in ["economy","dot_pct"])).head(20)
                ch(bar_h(df_m,m,"striker",m,"Reds",f"Top 20 batters bowled to — {m} ({fmt})"))
                st.dataframe(df_m[["striker","balls_bowled","runs_given","wickets","economy"]].reset_index(drop=True))


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6 — PERFORMANCE OVER YEARS
# ════════════════════════════════════════════════════════════════════════════
elif section == "📈 Performance Over Years":
    section_banner("📈","Performance Over Years","Track how a player has evolved season by season","#00d4a0")
    name=st.text_input("Player name","Kohli")
    st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=(bat_yr[bat_yr["striker"].str.contains(sname,case=False,na=False)] if st_=="Batting"
             else bowl_yr[bowl_yr["bowler"].str.contains(sname,case=False,na=False)])
        if len(src)==0: st.error("Player not found!")
        else:
            fmt=st.radio("Format",avail(src),horizontal=True)
            by=src[src["format"]==fmt].sort_values("year"); clr=FC.get(fmt,"#00d4a0")
            if st_=="Batting":
                ch(bar_v(by,"year","runs","Runs per Year",clr))
                c1,c2=st.columns(2)
                with c1: ch(line(by,"year","average","Batting Average",clr),260)
                with c2: ch(line(by,"year","strike_rate","Strike Rate","#ffb830"),260)
                st.dataframe(by[["year","matches","runs","average","strike_rate","fours","sixes"]].reset_index(drop=True))
            else:
                ch(bar_v(by,"year","wickets","Wickets per Year",clr))
                c1,c2=st.columns(2)
                with c1: ch(line(by,"year","economy","Economy Rate","#ff4f6d"),260)
                with c2: ch(line(by,"year","average","Bowling Average","#a78bfa"),260)
                st.dataframe(by[["year","matches","wickets","economy","average","dot_pct"]].reset_index(drop=True))


# ════════════════════════════════════════════════════════════════════════════
# SECTION 7 — LEADERBOARD
# ════════════════════════════════════════════════════════════════════════════
elif section == "🏆 Leaderboard":
    section_banner("🏆","Leaderboard","The greatest — ranked by format and stat","#ffb830")
    fmt=st.radio("Format",ALL_FMT,horizontal=True)
    tab1,tab2=st.tabs(["🏏 Batting","🎳 Bowling"])
    with tab1:
        bs=bat_fmt[bat_fmt["format"]==fmt]
        c1,c2=st.columns(2)
        sb=c1.selectbox("Rank by",["runs","average","strike_rate","sixes","hundreds","player_score"])
        mr=c2.slider("Min runs",0,3000,200,100); tn=st.slider("Top N",5,30,15)
        lb=bs[bs["runs"]>=mr].sort_values(sb,ascending=False).head(tn).reset_index(drop=True)
        lb.insert(0,"Rank",range(1,len(lb)+1))
        ch(bar_h(lb,sb,"striker",sb,"Teal",f"Top {tn} {fmt} Batters — {sb}"),max(350,tn*30))
        show_cols=[c for c in ["Rank","striker","matches","runs","average","strike_rate","hundreds","fifties","highest","player_score"] if c in lb.columns]
        st.dataframe(lb[show_cols].reset_index(drop=True))
    with tab2:
        ws=bowl_fmt[bowl_fmt["format"]==fmt]
        c1,c2=st.columns(2)
        sb2=c1.selectbox("Rank by",["wickets","economy","average","dot_pct","five_wkts"])
        mw=c2.slider("Min wickets",0,100,10,5); tn2=st.slider("Top N bowlers",5,30,15)
        lb2=ws[ws["wickets"]>=mw].sort_values(sb2,ascending=(sb2 in ["economy","average"])).head(tn2).reset_index(drop=True)
        lb2.insert(0,"Rank",range(1,len(lb2)+1))
        ch(bar_h(lb2,"wickets","bowler","economy","Sunset",f"Top {tn2} {fmt} Bowlers"),max(350,tn2*30))
        show_cols2=[c for c in ["Rank","bowler","matches","wickets","economy","average","five_wkts","best_bowling"] if c in lb2.columns]
        st.dataframe(lb2[show_cols2].reset_index(drop=True))


# ════════════════════════════════════════════════════════════════════════════
# SECTION 8 — SIMILAR PLAYERS
# ════════════════════════════════════════════════════════════════════════════
elif section == "🤖 Similar Players":
    section_banner("🤖","Similar Players","ML-powered: find cricketers who play just like your favourite","#a78bfa")
    st.markdown(f"<div style='color:{MUT};font-size:13px;margin-bottom:16px'>Uses <b style='color:{TEXT}'>KMeans clustering</b> on career stats to find statistically similar players.</div>", unsafe_allow_html=True)
    st_type=st.radio("Type",["Batter","Bowler"],horizontal=True)
    name=st.text_input("Player name","Babar"); fmt=st.radio("Format",ALL_FMT,horizontal=True)
    if name:
        sname=resolve(name)
        if st_type=="Batter":
            src=bat_sim[(bat_sim["striker"].str.contains(sname,case=False,na=False))&(bat_sim["format"]==fmt)]
            if len(src)==0: st.error(f"No ML data for **'{name}'** in {fmt}. They may have <200 runs in this format.")
            else:
                p=src.iloc[0]; cluster=int(p["cluster"])
                same=bat_sim[(bat_sim["cluster"]==cluster)&(bat_sim["format"]==fmt)]
                same=same[~same["striker"].str.contains(sname,case=False,na=False)]
                same=same.sort_values("average",ascending=False).head(10)
                st.markdown(f"**Players most similar to {p['striker']} in {fmt}** · Cluster #{cluster}")
                ch(bar_h(same,"average","striker","average","Purples",f"Similar Batters — {fmt}"))
                st.dataframe(same[["striker","runs","average","strike_rate","boundary_pct","player_score"]].reset_index(drop=True))
        else:
            src=bowl_sim[(bowl_sim["bowler"].str.contains(sname,case=False,na=False))&(bowl_sim["format"]==fmt)]
            if len(src)==0: st.error(f"No ML data for **'{name}'** in {fmt}. They may have <20 wickets.")
            else:
                p=src.iloc[0]; cluster=int(p["cluster"])
                same=bowl_sim[(bowl_sim["cluster"]==cluster)&(bowl_sim["format"]==fmt)]
                same=same[~same["bowler"].str.contains(sname,case=False,na=False)]
                same=same.sort_values("wickets",ascending=False).head(10)
                st.markdown(f"**Bowlers most similar to {p['bowler']} in {fmt}** · Cluster #{cluster}")
                ch(bar_h(same,"wickets","bowler","economy","Reds",f"Similar Bowlers — {fmt}"))
                st.dataframe(same[["bowler","wickets","economy","average","dot_pct"]].reset_index(drop=True))


# ════════════════════════════════════════════════════════════════════════════
# SECTION 9 — FORM & RATINGS
# ════════════════════════════════════════════════════════════════════════════
elif section == "🔥 Form & Ratings":
    section_banner("🔥","Form & Ratings","Who is on fire right now? Last 2 seasons vs career average","#fb923c")
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
            else: st.info(f"No batters in 'On Fire' form for {fmt} yet.")
        with t2:
            bot=src[src["form_score"]<70].sort_values("form_score").head(20) if len(src)>0 else pd.DataFrame()
            if len(bot)>0:
                ch(bar_h(bot,"form_score","striker","form_score","Blues",f"📉 Struggling Batters ({fmt})"))
                st.dataframe(bot[["striker","form_label","form_score","recent_avg","career_avg"]].reset_index(drop=True))
            else: st.info(f"No batters struggling in {fmt}.")

    with tab2:
        src2=bowl_form[bowl_form["format"]==fmt].copy() if not bowl_form.empty else pd.DataFrame()
        t1,t2=st.tabs(["🔥 On Fire","📉 Struggling"])
        with t1:
            top2=src2[src2["form_score"]>=110].sort_values("form_score",ascending=False).head(20) if len(src2)>0 else pd.DataFrame()
            if len(top2)>0:
                ch(bar_h(top2,"form_score","bowler","form_score","Oranges",f"🔥 On Fire Bowlers ({fmt})"))
                st.dataframe(top2[["bowler","form_label","form_score","recent_econ","career_econ","recent_avg","career_avg"]].reset_index(drop=True))
            else: st.info(f"No bowlers on fire in {fmt} yet.")
        with t2:
            bot2=src2[src2["form_score"]<70].sort_values("form_score").head(20) if len(src2)>0 else pd.DataFrame()
            if len(bot2)>0:
                ch(bar_h(bot2,"form_score","bowler","form_score","Blues",f"📉 Struggling Bowlers ({fmt})"))
                st.dataframe(bot2[["bowler","form_label","form_score","recent_econ","career_econ"]].reset_index(drop=True))
            else: st.info(f"No bowlers struggling in {fmt}.")

    with tab3:
        ps=bat_sim[bat_sim["format"]==fmt].sort_values("player_score",ascending=False).head(20) if not bat_sim.empty else pd.DataFrame()
        if len(ps)>0:
            ch(bar_h(ps,"player_score","striker","player_score","Teal",f"⭐ Top 20 Player Scores ({fmt})"))
            st.markdown(f"<div style='color:{MUT};font-size:12px;margin-top:4px'>Score = Average 30% · Strike Rate 25% · Boundary% 20% · Runs volume 15% · Non-dot% 10%</div>", unsafe_allow_html=True)
            st.dataframe(ps[["striker","player_score","average","strike_rate","boundary_pct","runs"]].reset_index(drop=True))
        else: st.info(f"No player score data for {fmt} yet.")
