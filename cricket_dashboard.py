import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

st.set_page_config(page_title="Cricket Analytics", layout="wide", page_icon="🏏",
                   initial_sidebar_state="collapsed")

# ── CHANGE THIS to your GitHub raw base URL ──────────────────────────────
RAW_BASE = "https://raw.githubusercontent.com/mmrayyan2005-dev/cricket-analytics-/main"
# ─────────────────────────────────────────────────────────────────────────

BG="#0f1117"; CARD="#1e2130"; TEXT="#f0f0f0"; GRID="#2a2d3e"
FC={"ODI":"#00b894","Test":"#0984e3","T20I":"#d63031","IPL":"#e17055","PSL":"#6c5ce7"}
FORMATS=["ODI","Test","T20I","IPL","PSL"]

BASE=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
          font=dict(color=TEXT,family="Inter,sans-serif",size=12),
          legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,
                      bgcolor="rgba(0,0,0,0)",font=dict(size=11)),
          xaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,color=TEXT,fixedrange=True),
          yaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,color=TEXT,fixedrange=True),
          dragmode=False)

M_DEFAULT=dict(l=8,r=8,t=48,b=8)
M_BARV=dict(l=8,r=8,t=48,b=60)

CFG=dict(config={"displayModeBar":False,"scrollZoom":False,"doubleClick":False,
                  "responsive":True},use_container_width=True)

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;background:{BG};color:{TEXT}}}
[data-testid="stMetric"]{{background:{CARD};border-radius:12px;padding:12px 16px;border:1px solid {GRID}}}
[data-testid="stMetricLabel"]{{font-size:11px;color:#aaa;text-transform:uppercase;letter-spacing:.5px}}
[data-testid="stMetricValue"]{{font-size:20px;font-weight:700;color:{TEXT}}}
[data-testid="column"]{{min-width:90px!important}}
[data-testid="stHorizontalBlock"] > [data-testid="column"] > div {{height:100%;display:flex;flex-direction:column}}
[data-testid="stHorizontalBlock"] > [data-testid="column"] > div > div {{flex:1}}
.js-plotly-plot{{touch-action:pan-y!important}}
div[data-baseweb="tab-list"]{{gap:8px}}
div[data-baseweb="tab"]{{border-radius:8px;padding:6px 14px;background:{CARD}}}
/* Equal-height columns for head-to-head player cards */
[data-testid="stHorizontalBlock"]>[data-testid="column"]>div>div>div>[data-testid="stMarkdownContainer"]>div>div{{height:100%;box-sizing:border-box}}
</style>""",unsafe_allow_html=True)

# ── Load CSVs from GitHub raw ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load():
    def read(name):
        return pd.read_csv(f"{RAW_BASE}/{name}")
    return (read("cricket_batting_stats.csv"),
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
            read("cricket_bowl_innings.csv"))

with st.spinner("Loading cricket data..."):
    (batting,bowling,bat_fmt,bowl_fmt,bat_yr,bowl_yr,
     bat_ven,bat_opp,bowl_ven,bowl_opp,bvb,wvb,
     bat_form,bowl_form,bat_sim,bowl_sim,bat_inn,bowl_inn) = load()

# ── Helpers ───────────────────────────────────────────────────────────────
def avail(df,col):
    return sorted(df[col].unique().tolist(),key=lambda x:FORMATS.index(x) if x in FORMATS else 99)

def ch(fig,h=320,margin=None):
    fig.update_layout(**BASE,height=h,margin=margin or M_DEFAULT)
    st.plotly_chart(fig,**CFG)

def plot_h(fig):
    """Plot a bar_h figure without overriding its internally-computed height/margins."""
    fig.update_layout(**BASE)
    st.plotly_chart(fig,**CFG)

def bar_h(df,x,y,col,scale,title):
    max_chars = int(df[y].astype(str).str.len().max()) if len(df)>0 else 20
    lm = max(260, int(max_chars * 9 + 40))
    h  = max(500, len(df) * 68)
    xmax = float(df[x].max()) * 1.22 if len(df)>0 else 1
    fig=px.bar(df,x=x,y=y,orientation="h",color=col,color_continuous_scale=scale,title=title)
    fig.update_traces(marker_line_width=0,
                      text=pd.to_numeric(df[x], errors="coerce").round(1).fillna(0).astype(str),
                      textposition="outside",
                      textfont=dict(size=11,color=TEXT),
                      cliponaxis=False)
    fig.update_layout(**BASE,height=h,coloraxis_showscale=False,
                      margin=dict(l=lm,r=90,t=52,b=12),bargap=0.28)
    fig.update_yaxes(categoryorder="total ascending",showgrid=False,title="",
                     tickfont=dict(size=13,color=TEXT),automargin=False,
                     tickmode="linear")
    fig.update_xaxes(showgrid=True,gridcolor=GRID,title="",tickfont=dict(size=12),
                     range=[0,xmax])
    return fig

def bar_v(df,x,y,title,color,h=420):
    fig=px.bar(df,x=x,y=y,text_auto=True,title=title,color_discrete_sequence=[color])
    fig.update_traces(textposition="outside",textfont=dict(size=12,color=TEXT),
                      marker_line_width=0,width=0.6)
    fig.update_layout(**BASE,height=h,showlegend=False,
                      margin=dict(l=12,r=12,t=52,b=80))
    fig.update_xaxes(tickmode="linear",tickangle=-40,showgrid=False,
                     tickfont=dict(size=12),automargin=True)
    fig.update_yaxes(showgrid=True,gridcolor=GRID,tickfont=dict(size=12))
    return fig

def line(df,x,y,title,color,h=260):
    fig=px.line(df,x=x,y=y,markers=True,title=title)
    fig.update_traces(line=dict(color=color,width=2.5),
                      marker=dict(size=7,color=color,line=dict(width=1.5,color=BG)))
    fig.update_layout(**BASE,height=h,margin=M_DEFAULT)
    return fig

def donut(labels,values,colors,title):
    fig=go.Figure(go.Pie(labels=labels,values=values,hole=0.52,
        marker=dict(colors=colors,line=dict(color=BG,width=2)),
        textinfo="percent+label",textfont=dict(size=12,color=TEXT)))
    fig.update_layout(**BASE,height=300,title=title,showlegend=False,margin=M_DEFAULT)
    return fig

def metrics(d):
    cols=st.columns(len(d))
    for c,(k,v) in zip(cols,d.items()): c.metric(k,v)

def page_banner(emoji,title,subtitle,grad_a,grad_b,glow):
    st.markdown(f"""
<div style="background:linear-gradient(135deg,{grad_a} 0%,{grad_b} 100%);
            border-radius:16px;padding:22px 24px;margin:0 0 20px 0;
            border:1px solid {glow}44;position:relative;overflow:hidden">
  <div style="position:absolute;top:-30px;right:-30px;width:140px;height:140px;
              background:radial-gradient(circle,{glow}33 0%,transparent 70%);pointer-events:none"></div>
  <div style="display:flex;align-items:center;gap:14px">
    <div style="font-size:40px;filter:drop-shadow(0 0 8px {glow}88)">{emoji}</div>
    <div>
      <div style="color:#fff;font-size:20px;font-weight:800;letter-spacing:-0.3px">{title}</div>
      <div style="color:#aabbcc;font-size:13px;margin-top:3px">{subtitle}</div>
    </div>
  </div>
</div>""",unsafe_allow_html=True)

# ── Name alias resolution ─────────────────────────────────────────────────
NAME_ALIASES={
    "steve smith":"SPD Smith","smith":"SPD Smith",
    "hazelwood":"JR Hazlewood","josh hazelwood":"JR Hazlewood","hazlewood":"JR Hazlewood",
    "warner":"DA Warner","david warner":"DA Warner",
    "rohit":"RG Sharma","rohit sharma":"RG Sharma",
    "bumrah":"JJ Bumrah","jasprit bumrah":"JJ Bumrah",
    "starc":"MA Starc","mitchell starc":"MA Starc",
    "kohli":"V Kohli","virat kohli":"V Kohli",
    "babar":"Babar Azam","de villiers":"AB de Villiers",
    "ab de villiers":"AB de Villiers","stokes":"BA Stokes","ben stokes":"BA Stokes",
    "root":"JE Root","joe root":"JE Root",
    "anderson":"JM Anderson","james anderson":"JM Anderson",
    "broad":"SCJ Broad","stuart broad":"SCJ Broad",
    "afridi":"Shahid Afridi","shaheen":"Shaheen Shah Afridi",
    "rizwan":"Mohammad Rizwan","rashid":"Rashid Khan",
    "buttler":"JC Buttler","jos buttler":"JC Buttler",
    "maxwell":"GJ Maxwell","dhoni":"MS Dhoni",
    "sachin":"SR Tendulkar","tendulkar":"SR Tendulkar",
    "ponting":"RT Ponting","sangakkara":"KC Sangakkara","malinga":"SL Malinga",
}
def resolve(name): return NAME_ALIASES.get(name.strip().lower(),name)

# ── Wikipedia player card ─────────────────────────────────────────────────
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
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_wiki(cricsheet_name, search_name):
    """Fetch player photo + bio + born/debut from Wikipedia REST API."""
    try:
        # Use REST summary API — more reliable than action API
        wiki_title = WIKI_NAMES.get(cricsheet_name, search_name + " cricketer")
        # Step 1: search for correct page title
        search_r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":wiki_title,
                    "format":"json","utf8":1,"srlimit":3},
            timeout=8, headers={"User-Agent":"CricketAnalyticsApp/1.0"}
        )
        search_r.raise_for_status()
        results = search_r.json().get("query",{}).get("search",[])
        if not results:
            return None
        page_title = results[0]["title"]

        # Step 2: get summary via REST API (includes image + extract)
        safe_title = page_title.replace(" ","_")
        rest_r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_title}",
            timeout=8, headers={"User-Agent":"CricketAnalyticsApp/1.0"}
        )
        rest_r.raise_for_status()
        data = rest_r.json()

        img  = data.get("thumbnail",{}).get("source","")
        bio  = data.get("extract","")
        # keep max 4 sentences
        sents = [s.strip() for s in bio.split(".") if len(s.strip()) > 15]
        bio   = ". ".join(sents[:4]) + "." if sents else bio[:400]

        # Step 3: get infobox data (born, full name, debut) via action API
        info_r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action":"query","titles":page_title,"prop":"revisions",
                    "rvprop":"content","rvslots":"main","format":"json",
                    "rvsection":0},
            timeout=8, headers={"User-Agent":"CricketAnalyticsApp/1.0"}
        )
        info_r.raise_for_status()
        pages  = info_r.json().get("query",{}).get("pages",{})
        wikitext = next(iter(pages.values())).get("revisions",[{}])[0].get("slots",{}).get("main",{}).get("*","")

        import re

        def clean(val):
            # [[Link#anchor|Display Text]] → Display Text
            val = re.sub(r"\[\[[^\]|]*\|([^\]]+)\]\]", r"\1", val)
            # [[Display Text]] → Display Text
            val = re.sub(r"\[\[([^\]]+)\]\]", r"\1", val)
            val = re.sub(r"\{\{[^}]+\}\}", "", val)
            val = re.sub(r"<[^>]+>", "", val)
            val = re.sub(r"''+'", "", val)
            return val.strip().strip("|").strip()

        def extract_field(text, keys):
            """Extract field value, capturing full line so [[Link|Text]] wikilinks are preserved for clean()."""
            for key in keys:
                m = re.search(
                    r"\|\s*" + re.escape(key) + r"\s*=\s*([^\n]{2,150})",
                    text, re.IGNORECASE
                )
                if m:
                    val = clean(m.group(1))
                    # strip any leftover broken [[ fragments
                    val = re.sub(r"\[\[[^\]]*", "", val).strip().rstrip("|").strip()
                    if len(val) > 2:
                        return val
            return ""

        def extract_raw(text, keys):
            """Extract RAW field value (no cleaning) — needed for date templates like {{dts|yyyy|mm|dd}}."""
            for key in keys:
                m = re.search(r"\|\s*" + re.escape(key) + r"\s*=\s*([^\n]{2,150})",
                              text, re.IGNORECASE)
                if m:
                    return m.group(1).strip()
            return ""

        def parse_date(val):
            """Parse a date from raw wikitext including {{dts|...}} and {{birth date|...}} templates."""
            if not val: return ""
            months = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            # {{dts|yyyy|mm|dd}} or {{birth date|yyyy|mm|dd}} or {{birth date and age|yyyy|mm|dd}}
            m = re.search(r"\{\{(?:dts|birth date(?:[^|{]*)?)\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|\s*(\d{1,2})",
                          val, re.IGNORECASE)
            if m:
                try: return f"{int(m.group(3))} {months[int(m.group(2))]} {m.group(1)}"
                except: pass
            # Plain yyyy-mm-dd or yyyy|mm|dd anywhere in string
            m2 = re.search(r"(\d{4})\D+?(\d{1,2})\D+?(\d{1,2})", val)
            if m2:
                try:
                    mo = int(m2.group(2))
                    if 1 <= mo <= 12:
                        return f"{int(m2.group(3))} {months[mo]} {m2.group(1)}"
                except: pass
            # dd MonthName yyyy
            m3 = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", val)
            if m3:
                return f"{int(m3.group(1))} {m3.group(2)[:3].capitalize()} {m3.group(3)}"
            return ""

        # born — look for birth_date template e.g. {{birth date and age|1988|11|5}}
        born = ""
        bd_m = re.search(r"\{\{birth date(?:\s*and age)?\s*\|([^}]+)\}\}", wikitext, re.IGNORECASE)
        if bd_m:
            parts = [p.strip() for p in bd_m.group(1).split("|") if p.strip().isdigit()]
            if len(parts) >= 3:
                months_list = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                try: born = f"{int(parts[2])} {months_list[int(parts[1])]} {parts[0]}"
                except: pass
        if not born:
            born = extract_field(wikitext, ["birth_date","birthdate","born"])

        # Debut dates — MUST use extract_raw so {{dts|yyyy|mm|dd}} isn't stripped before parsing
        odi_debut  = parse_date(extract_raw(wikitext, ["odidebutdate","ODIdebutdate","odi_debut_date"]))
        test_debut = parse_date(extract_raw(wikitext, ["testdebutdate","Testdebutdate","test_debut_date"]))
        t20_debut  = parse_date(extract_raw(wikitext, ["t20idebutdate","T20Idebutdate","T20debutdate","t20_debut_date"]))
        any_debut  = parse_date(extract_raw(wikitext, ["debutdate","debut_date","internationaldebutdate"]))

        role   = extract_field(wikitext, ["role","batting_style","bowling_style"])
        nation = extract_field(wikitext, ["country","nationality","national_side"])

        description = data.get("description","")

        return {"title": data.get("title", page_title),
                "bio": bio, "img": img,
                "born":       born[:60]       if born       else "",
                "odi_debut":  odi_debut        if odi_debut  else any_debut,
                "test_debut": test_debut       if test_debut else any_debut,
                "t20_debut":  t20_debut        if t20_debut  else any_debut,
                "ipl_debut":  "",
                "psl_debut":  "",
                "role":       role[:80]        if role       else description[:60],
                "nation":     nation[:40]      if nation     else ""}
    except Exception as e:
        return None

def show_player_card(cricsheet_name, search_name, fmt="ODI"):
    card = get_wiki(cricsheet_name, search_name)

    # Fallback placeholder SVG avatar (always shown if no image)
    AVATAR_SVG = (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='145' "
        "viewBox='0 0 120 145'%3E%3Crect width='120' height='145' rx='12' fill='%231e2a3a'/%3E"
        "%3Ccircle cx='60' cy='50' r='28' fill='%232d3561'/%3E"
        "%3Cellipse cx='60' cy='120' rx='38' ry='28' fill='%232d3561'/%3E"
        "%3Ctext x='60' y='58' text-anchor='middle' font-size='28' fill='%236c7faa'%3E🏏%3C/text%3E"
        "%3C/svg%3E"
    )

    if not card:
        # show placeholder card with avatar if wiki fails
        display_name = cricsheet_name or search_name
        img_html = f'<img src="{AVATAR_SVG}" style="width:110px;height:132px;object-fit:cover;border-radius:12px;border:2px solid #2d3561;flex-shrink:0;">'
        st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a1f3a,#0f1117);border-radius:16px;
            padding:20px;margin:0 0 20px 0;border:1px solid #2d3561;
            display:flex;gap:18px;align-items:flex-start;min-height:180px;box-sizing:border-box">
  {img_html}
  <div style="flex:1;min-width:0">
    <div style="color:#fff;font-size:20px;font-weight:800;margin-bottom:8px">{display_name}</div>
    <div style="color:#aaa;font-size:13px;margin-top:8px">📖 Profile unavailable — Wikipedia not reachable</div>
  </div>
</div>""", unsafe_allow_html=True)
        return

    # Use Wikipedia image or fallback avatar
    img_src = card["img"] if card.get("img") else AVATAR_SVG
    img_html = f'<img src="{img_src}" style="width:110px;height:132px;object-fit:cover;border-radius:12px;border:2px solid #2d3561;flex-shrink:0;box-shadow:0 4px 20px #000a">'

    # Pick correct debut for selected format
    fmt_key = {"ODI":"odi_debut","Test":"test_debut","T20I":"t20_debut",
               "IPL":"ipl_debut","PSL":"psl_debut"}.get(fmt,"odi_debut")
    debut_date = card.get(fmt_key,"") or card.get("odi_debut","") or card.get("test_debut","")

    # Build info pills
    pills = ""
    if card["born"]:
        pills += f'<span style="background:#1e2a3a;color:#00b894;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-right:4px;margin-bottom:4px;display:inline-block">🎂 Born: {card["born"]}</span>'
    if card["nation"]:
        pills += f'<span style="background:#1e2a3a;color:#0984e3;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-right:4px;margin-bottom:4px;display:inline-block">🌍 {card["nation"]}</span>'
    if card["role"]:
        pills += f'<span style="background:#1e2a3a;color:#fdcb6e;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-right:4px;margin-bottom:4px;display:inline-block">🏏 {card["role"]}</span>'
    if debut_date:
        pills += f'<span style="background:#1e2a3a;color:#e17055;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-right:4px;margin-bottom:4px;display:inline-block">🎯 {fmt} Debut: {debut_date}</span>'

    # Truncate bio to 3 sentences for compact side-by-side layout
    bio_short = card["bio"]
    sents = [s.strip() for s in bio_short.split(".") if len(s.strip()) > 10]
    bio_display = ". ".join(sents[:3]) + "." if sents else bio_short[:280]

    st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a1f3a,#0f1117);border-radius:16px;
            padding:20px;margin:0 0 20px 0;border:1px solid #2d3561;
            display:flex;gap:16px;align-items:flex-start;min-height:200px;
            box-sizing:border-box;height:100%">
  {img_html}
  <div style="flex:1;min-width:0;overflow:hidden">
    <div style="color:#fff;font-size:18px;font-weight:800;margin-bottom:8px;line-height:1.2">{card["title"]}</div>
    <div style="margin-bottom:8px;flex-wrap:wrap;display:flex;gap:4px;line-height:1.8">{pills}</div>
    <div style="color:#8899bb;font-size:12px;line-height:1.6;overflow:hidden;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical">{bio_display}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════
st.sidebar.title("🏏 Cricket Analytics")
section=st.sidebar.radio("Navigate",[
    "🔍 Player Search","⚔️ Head to Head","🏟️ Player vs Venue",
    "🌍 Player vs Opponent","🤜 Batter vs Bowler",
    "📈 Performance Over Years","🏆 Leaderboard",
    "🤖 Similar Players","🔥 Form & Ratings"])

# ══ 1. PLAYER SEARCH ═══════════════════════════════════════════════════════
if section=="🔍 Player Search":
    st.markdown("""
<div style="background:linear-gradient(135deg,#0d1b2a 0%,#1a1f3a 50%,#0d1b2a 100%);
            border-radius:20px;padding:36px 24px 28px 24px;margin:0 0 24px 0;
            border:1px solid #2d3561;text-align:center;position:relative;overflow:hidden">
  <div style="position:absolute;top:-40px;left:-40px;width:180px;height:180px;
              background:radial-gradient(circle,#00b89455 0%,transparent 70%);pointer-events:none"></div>
  <div style="position:absolute;bottom:-40px;right:-40px;width:180px;height:180px;
              background:radial-gradient(circle,#6c5ce755 0%,transparent 70%);pointer-events:none"></div>
  <div style="position:absolute;top:30px;right:20px;width:120px;height:120px;
              background:radial-gradient(circle,#d6303133 0%,transparent 70%);pointer-events:none"></div>
  <div style="font-size:60px;line-height:1;margin-bottom:10px;filter:drop-shadow(0 0 12px #00b89466)">🏏</div>
  <h1 style="color:#ffffff;margin:0 0 6px 0;font-size:30px;font-weight:800;letter-spacing:-0.5px">Cricket Analytics</h1>
  <p style="color:#8899bb;font-size:15px;margin:0 0 22px 0">Ball-by-ball records · Every major format</p>
  <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-bottom:26px">
    <span style="background:linear-gradient(135deg,#00b894,#00cec9);color:#fff;padding:6px 16px;border-radius:20px;font-size:13px;font-weight:700;box-shadow:0 0 12px #00b89455">ODI</span>
    <span style="background:linear-gradient(135deg,#0984e3,#74b9ff);color:#fff;padding:6px 16px;border-radius:20px;font-size:13px;font-weight:700;box-shadow:0 0 12px #0984e355">Test</span>
    <span style="background:linear-gradient(135deg,#d63031,#ff7675);color:#fff;padding:6px 16px;border-radius:20px;font-size:13px;font-weight:700;box-shadow:0 0 12px #d6303155">T20I</span>
    <span style="background:linear-gradient(135deg,#e17055,#fdcb6e);color:#fff;padding:6px 16px;border-radius:20px;font-size:13px;font-weight:700;box-shadow:0 0 12px #e1705555">IPL</span>
    <span style="background:linear-gradient(135deg,#6c5ce7,#a29bfe);color:#fff;padding:6px 16px;border-radius:20px;font-size:13px;font-weight:700;box-shadow:0 0 12px #6c5ce755">PSL</span>
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;max-width:500px;margin:0 auto 22px auto">
    <div style="background:linear-gradient(135deg,#1e2a3a,#1e2130);border-radius:14px;padding:16px 8px;border:1px solid #00b89433">
      <div style="font-size:24px;margin-bottom:6px">🏏</div>
      <div style="color:#00b894;font-weight:700;font-size:14px">Batting</div>
      <div style="color:#778;font-size:11px;margin-top:3px">Runs · Avg · SR · 100s</div>
    </div>
    <div style="background:linear-gradient(135deg,#1a2a3a,#1e2130);border-radius:14px;padding:16px 8px;border:1px solid #0984e333">
      <div style="font-size:24px;margin-bottom:6px">🎳</div>
      <div style="color:#0984e3;font-weight:700;font-size:14px">Bowling</div>
      <div style="color:#778;font-size:11px;margin-top:3px">Wkts · Econ · 5-fors</div>
    </div>
    <div style="background:linear-gradient(135deg,#1e1a3a,#1e2130);border-radius:14px;padding:16px 8px;border:1px solid #6c5ce733">
      <div style="font-size:24px;margin-bottom:6px">🤖</div>
      <div style="color:#a29bfe;font-weight:700;font-size:14px">ML Insights</div>
      <div style="color:#778;font-size:11px;margin-top:3px">Form · Score · Similar</div>
    </div>
  </div>
  <p style="color:#556;font-size:13px;margin:0">
    Try: <span style="color:#00b894;font-weight:600">Babar</span> ·
         <span style="color:#0984e3;font-weight:600">Kohli</span> ·
         <span style="color:#d63031;font-weight:600">Smith</span> ·
         <span style="color:#e17055;font-weight:600">Bumrah</span> ·
         <span style="color:#6c5ce7;font-weight:600">Rashid</span>
  </p>
</div>""",unsafe_allow_html=True)

    name=st.text_input("🔍  Search player","",placeholder="Type a name e.g. Babar, Kohli, Smith...")
    if name:
        sname=resolve(name)
        ab=bat_fmt[bat_fmt["striker"].str.contains(sname,case=False,na=False)]["format"].unique().tolist()
        aw=bowl_fmt[bowl_fmt["bowler"].str.contains(sname,case=False,na=False)]["format"].unique().tolist()
        avl=sorted(set(ab+aw),key=lambda x:FORMATS.index(x) if x in FORMATS else 99)
        if not avl: st.error(f"No player found for '{name}'."); st.stop()

        fmt=st.radio("📋 Format",avl,horizontal=True)
        clr=FC.get(fmt,"#00b894")
        bat=bat_fmt[(bat_fmt["striker"].str.contains(sname,case=False,na=False))&(bat_fmt["format"]==fmt)]
        bowl=bowl_fmt[(bowl_fmt["bowler"].str.contains(sname,case=False,na=False))&(bowl_fmt["format"]==fmt)]

        display_name=bat["striker"].iloc[0] if len(bat)>0 else (bowl["bowler"].iloc[0] if len(bowl)>0 else sname)
        show_player_card(display_name,name,fmt)

        if len(bat)>0:
            p=bat.sort_values("runs",ascending=False).iloc[0]
            st.subheader(f"🏏 {p['striker']} — Batting ({fmt})")
            metrics({"Matches":int(p["matches"]),"Runs":f"{int(p['runs']):,}","Average":p["average"]})
            metrics({"Strike Rate":p["strike_rate"],"4s":int(p["fours"]),"6s":int(p["sixes"])})
            metrics({"Dismissals":int(p["dismissals"]),"Dot Ball %":f"{p['dot_pct']}%","Boundary %":f"{p['boundary_pct']}%"})
            h100=int(p["hundreds"]) if "hundreds" in p.index and pd.notna(p.get("hundreds")) else "—"
            h50 =int(p["fifties"])  if "fifties"  in p.index and pd.notna(p.get("fifties"))  else "—"
            hs  =int(p["highest"])  if "highest"  in p.index and pd.notna(p.get("highest"))  else "—"
            dk  =int(p["ducks"])    if "ducks"    in p.index and pd.notna(p.get("ducks"))    else "—"
            ps  =round(float(p["player_score"]),1) if "player_score" in p.index and pd.notna(p.get("player_score")) else "—"
            metrics({"100s":h100,"50s":h50,"Highest Score":hs,"Ducks":dk,"⭐ Player Score":ps})

            by=bat_yr[(bat_yr["striker"].str.contains(sname,case=False,na=False))&(bat_yr["format"]==fmt)].sort_values("year")
            if len(by)>1:
                ch(bar_v(by,"year","runs","Runs per Year",clr))
                c1,c2=st.columns(2)
                with c1: ch(line(by,"year","average","Batting Average",clr),260)
                with c2: ch(line(by,"year","strike_rate","Strike Rate","#fdcb6e"),260)

            fr=int(p["fours"])*4; sr=int(p["sixes"])*6; or_=max(0,int(p["runs"])-fr-sr)
            ch(donut(["Fours","Sixes","Other"],[fr,sr,or_],[clr,"#d63031","#636e72"],"Scoring Breakdown"),300)

        st.divider()
        if len(bowl)>0:
            p2=bowl.sort_values("wickets",ascending=False).iloc[0]
            st.subheader(f"🎳 {p2['bowler']} — Bowling ({fmt})")
            metrics({"Matches":int(p2["matches"]),"Wickets":int(p2["wickets"]),"Economy":p2["economy"]})
            metrics({"Average":p2["average"],"Strike Rate":p2["strike_rate"],"Dot Ball %":f"{p2['dot_pct']}%"})
            fw=int(p2["five_wkts"]) if "five_wkts" in p2.index and pd.notna(p2.get("five_wkts")) else "—"
            bb=p2.get("best_bowling","—") if "best_bowling" in p2.index else "—"
            metrics({"5-Wicket Hauls":fw,"Best Bowling":bb})

            by2=bowl_yr[(bowl_yr["bowler"].str.contains(sname,case=False,na=False))&(bowl_yr["format"]==fmt)].sort_values("year")
            if len(by2)>1:
                ch(bar_v(by2,"year","wickets","Wickets per Year",clr))
                c1,c2=st.columns(2)
                with c1: ch(line(by2,"year","economy","Economy Rate","#d63031"),260)
                with c2: ch(line(by2,"year","average","Bowling Average","#6c5ce7"),260)

        if len(bat)==0 and len(bowl)==0:
            st.warning(f"No {fmt} data for '{name}'.")

# ══ 2. HEAD TO HEAD ════════════════════════════════════════════════════════
elif section=="⚔️ Head to Head":
    page_banner("⚔️","Head to Head","Pick two players and see who dominates across formats","#1a0a2e","#2d1b4e","#6c5ce7")
    c1,c2=st.columns(2)
    n1=c1.text_input("Player 1","Kohli"); n2=c2.text_input("Player 2","Babar Azam")
    fmt=st.radio("Format",FORMATS,horizontal=True)
    if n1 and n2:
        s1=resolve(n1); s2=resolve(n2)
        b1=bat_fmt[(bat_fmt["striker"].str.contains(s1,case=False,na=False))&(bat_fmt["format"]==fmt)]
        b2=bat_fmt[(bat_fmt["striker"].str.contains(s2,case=False,na=False))&(bat_fmt["format"]==fmt)]
        if len(b1)==0 or len(b2)==0:
            st.error(f"One or both players have no {fmt} data.")
        else:
            p1=b1.iloc[0]; p2=b2.iloc[0]
            p1n=p1["striker"]; p2n=p2["striker"]
            # Show both player cards side by side
            cc1,cc2=st.columns(2)
            with cc1: show_player_card(p1n,n1,fmt)
            with cc2: show_player_card(p2n,n2,fmt)
            st.subheader(f"🏏 Batting — {fmt}")
            LABELS={"runs":"Runs","fours":"Fours","sixes":"Sixes",
                    "average":"Avg","strike_rate":"Strike Rate",
                    "dot_pct":"Dot %","boundary_pct":"Boundary %"}
            for title,ml in [("🏏 Volume",["runs","fours","sixes"]),
                              ("📈 Rates",["average","strike_rate"]),
                              ("📊 Percentages",["dot_pct","boundary_pct"])]:
                pretty=[LABELS.get(m,m) for m in ml]
                v1=[float(p1.get(m,0)) for m in ml]; v2=[float(p2.get(m,0)) for m in ml]
                xmax=max(v1+v2)*1.30 if max(v1+v2)>0 else 10
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
                                  height=max(300,len(ml)*150),
                                  margin=dict(l=150,r=120,t=52,b=12))
                fig.update_yaxes(showgrid=False,tickfont=dict(size=14),title="",automargin=True)
                fig.update_xaxes(showgrid=True,gridcolor=GRID,title="",fixedrange=True,range=[0,xmax])
                st.plotly_chart(fig,**CFG)

            by1=bat_yr[(bat_yr["striker"].str.contains(s1,case=False,na=False))&(bat_yr["format"]==fmt)].copy()
            by2y=bat_yr[(bat_yr["striker"].str.contains(s2,case=False,na=False))&(bat_yr["format"]==fmt)].copy()
            if len(by1)>0 and len(by2y)>0:
                by1["player"]=p1n; by2y["player"]=p2n
                combined = pd.concat([by1,by2y]).sort_values("year")
                fy=px.line(combined,x="year",y="runs",color="player",markers=True,
                           title=f"Runs per Year — {fmt}",
                           color_discrete_map={p1n:FC["ODI"],p2n:FC["Test"]})
                fy.update_traces(line=dict(width=2.5),marker=dict(size=8))
                fy.update_layout(**BASE,height=420,margin=dict(l=60,r=30,t=52,b=50))
                fy.update_xaxes(title="Year",tickmode="linear",dtick=2,
                                showgrid=True,gridcolor=GRID)
                fy.update_yaxes(title="Runs",showgrid=True,gridcolor=GRID)
                st.plotly_chart(fy,**CFG)

            # ── Bowling comparison ──────────────────────────────────────────
            w1=bowl_fmt[(bowl_fmt["bowler"].str.contains(s1,case=False,na=False))&(bowl_fmt["format"]==fmt)]
            w2=bowl_fmt[(bowl_fmt["bowler"].str.contains(s2,case=False,na=False))&(bowl_fmt["format"]==fmt)]
            if len(w1)>0 and len(w2)>0:
                st.subheader(f"🎳 Bowling — {fmt}")
                pw1=w1.iloc[0]; pw2=w2.iloc[0]
                BLABELS={"wickets":"Wickets","economy":"Economy","average":"Average",
                         "strike_rate":"Strike Rate","dot_pct":"Dot %"}
                for btitle,bml in [("🎳 Wickets & Economy",["wickets","economy"]),
                                   ("📊 Average & Strike Rate",["average","strike_rate"]),
                                   ("💧 Dot Ball %",["dot_pct"])]:
                    bpretty=[BLABELS.get(m,m) for m in bml]
                    bv1=[float(pw1.get(m,0)) for m in bml]
                    bv2=[float(pw2.get(m,0)) for m in bml]
                    bxmax=max(bv1+bv2)*1.30 if max(bv1+bv2)>0 else 10
                    bfig=go.Figure()
                    bfig.add_trace(go.Bar(name=pw1["bowler"],y=bpretty,x=bv1,orientation="h",
                        marker=dict(color=FC["ODI"],opacity=0.9,line=dict(width=0)),
                        text=[f"{v:.1f}" for v in bv1],textposition="outside",
                        textfont=dict(size=12,color=TEXT),cliponaxis=False))
                    bfig.add_trace(go.Bar(name=pw2["bowler"],y=bpretty,x=bv2,orientation="h",
                        marker=dict(color=FC["Test"],opacity=0.9,line=dict(width=0)),
                        text=[f"{v:.1f}" for v in bv2],textposition="outside",
                        textfont=dict(size=12,color=TEXT),cliponaxis=False))
                    bfig.update_layout(**BASE,barmode="group",title=btitle,
                                      height=max(300,len(bml)*150),
                                      margin=dict(l=150,r=120,t=52,b=12))
                    bfig.update_yaxes(showgrid=False,tickfont=dict(size=14),title="",automargin=True)
                    bfig.update_xaxes(showgrid=True,gridcolor=GRID,title="",fixedrange=True,range=[0,bxmax])
                    st.plotly_chart(bfig,**CFG)

# ══ 3. PLAYER VS VENUE ═════════════════════════════════════════════════════
elif section=="🏟️ Player vs Venue":
    page_banner("🏟️","Player vs Venue","How does a player perform at different grounds?","#0a1a1a","#0d2b2b","#00b894")
    name=st.text_input("Player name","Kohli")
    st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=(bat_ven[bat_ven["striker"].str.contains(sname,case=False,na=False)] if st_=="Batting"
             else bowl_ven[bowl_ven["bowler"].str.contains(sname,case=False,na=False)])
        if len(src)==0: st.error("Player not found!")
        else:
            fmt=st.radio("Format",avail(src,"format"),horizontal=True)
            df_v=src[src["format"]==fmt]
            if st_=="Batting":
                m=st.selectbox("Metric",["runs","average","strike_rate","fours","sixes"])
                df_v=df_v.sort_values(m,ascending=False).head(15)
                plot_h(bar_h(df_v,m,"venue",m,"Greens",f"{df_v['striker'].iloc[0]} — {m} by Venue ({fmt})"))
                st.dataframe(df_v[["venue","innings","runs","average","strike_rate"]].reset_index(drop=True))
            else:
                m=st.selectbox("Metric",["wickets","economy","average","dot_pct"])
                df_v=df_v.sort_values(m,ascending=False).head(15)
                plot_h(bar_h(df_v,m,"venue",m,"Reds",f"{df_v['bowler'].iloc[0]} — {m} by Venue ({fmt})"))
                st.dataframe(df_v[["venue","innings","wickets","economy","average"]].reset_index(drop=True))

# ══ 4. PLAYER VS OPPONENT ══════════════════════════════════════════════════
elif section=="🌍 Player vs Opponent":
    page_banner("🌍","Player vs Opponent","Find out which teams a player dominates — and which trouble them","#0a1020","#0d1e3a","#0984e3")
    name=st.text_input("Player name","Kohli")
    st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=(bat_opp[bat_opp["striker"].str.contains(sname,case=False,na=False)] if st_=="Batting"
             else bowl_opp[bowl_opp["bowler"].str.contains(sname,case=False,na=False)])
        if len(src)==0: st.error("Player not found!")
        else:
            fmt=st.radio("Format",avail(src,"format"),horizontal=True)
            df_o=src[src["format"]==fmt]
            if st_=="Batting":
                m=st.selectbox("Metric",["runs","average","strike_rate","fours","sixes"])
                df_o=df_o.sort_values(m,ascending=False)
                plot_h(bar_h(df_o,m,"opponent",m,"Blues",f"{df_o['striker'].iloc[0]} — {m} vs Teams ({fmt})"))
                st.dataframe(df_o[["opponent","innings","runs","average","strike_rate"]].reset_index(drop=True))
            else:
                m=st.selectbox("Metric",["wickets","economy","average","dot_pct"])
                df_o=df_o.sort_values(m,ascending=False)
                plot_h(bar_h(df_o,m,"opponent",m,"Purples",f"{df_o['bowler'].iloc[0]} — {m} vs Teams ({fmt})"))
                st.dataframe(df_o[["opponent","innings","wickets","economy","average"]].reset_index(drop=True))

# ══ 5. BATTER VS BOWLER ════════════════════════════════════════════════════
elif section=="🤜 Batter vs Bowler":
    page_banner("🤜","Batter vs Bowler","The ultimate matchup — who has the edge ball by ball?","#1a0a0a","#2e1010","#d63031")
    mt=st.radio("Look up a...",["Batter","Bowler"],horizontal=True)
    if mt=="Batter":
        name=st.text_input("Batter name","Babar Azam")
        if name:
            sname=resolve(name)
            src=bvb[bvb["striker"].str.contains(sname,case=False,na=False)]
            if len(src)==0: st.error("Not found!")
            else:
                fmt=st.radio("Format",avail(src,"format"),horizontal=True)
                df_m=src[src["format"]==fmt]
                m=st.selectbox("Sort by",["balls_faced","runs","strike_rate","dismissals"])
                df_m=df_m.sort_values(m,ascending=False).head(20)
                plot_h(bar_h(df_m,m,"bowler",m,"Greens",f"Top 20 bowlers faced — {m} ({fmt})"))
                st.dataframe(df_m[["bowler","balls_faced","runs","strike_rate","dismissals"]].reset_index(drop=True))
    else:
        name=st.text_input("Bowler name","Shaheen")
        if name:
            sname=resolve(name)
            src=wvb[wvb["bowler"].str.contains(sname,case=False,na=False)]
            if len(src)==0: st.error("Not found!")
            else:
                fmt=st.radio("Format",avail(src,"format"),horizontal=True)
                df_m=src[src["format"]==fmt]
                m=st.selectbox("Sort by",["wickets","economy","dot_pct","runs_given"])
                df_m=df_m.sort_values(m,ascending=(m in ["economy","dot_pct"])).head(20)
                plot_h(bar_h(df_m,m,"striker",m,"Reds",f"Top 20 batters bowled to — {m} ({fmt})"))
                st.dataframe(df_m[["striker","balls_bowled","runs_given","wickets","economy"]].reset_index(drop=True))

# ══ 6. PERFORMANCE OVER YEARS ══════════════════════════════════════════════
elif section=="📈 Performance Over Years":
    page_banner("📈","Performance Over Years","Track how a player has evolved season by season","#0a150a","#0d2a10","#00b894")
    name=st.text_input("Player name","Kohli")
    st_=st.radio("Type",["Batting","Bowling"],horizontal=True)
    if name:
        sname=resolve(name)
        src=(bat_yr[bat_yr["striker"].str.contains(sname,case=False,na=False)] if st_=="Batting"
             else bowl_yr[bowl_yr["bowler"].str.contains(sname,case=False,na=False)])
        if len(src)==0: st.error("Player not found!")
        else:
            fmt=st.radio("Format",avail(src,"format"),horizontal=True)
            by=src[src["format"]==fmt].sort_values("year")
            clr=FC.get(fmt,"#00b894")
            if st_=="Batting":
                if len(by)>1:
                    ch(bar_v(by,"year","runs","Runs per Year",clr))
                    c1,c2=st.columns(2)
                    with c1: ch(line(by,"year","average","Batting Average",clr),260)
                    with c2: ch(line(by,"year","strike_rate","Strike Rate","#fdcb6e"),260)
                else:
                    st.info("Not enough yearly data to plot trends.")
                st.dataframe(by[["year","matches","runs","average","strike_rate","fours","sixes"]].reset_index(drop=True))
            else:
                if len(by)>1:
                    ch(bar_v(by,"year","wickets","Wickets per Year",clr))
                    c1,c2=st.columns(2)
                    with c1: ch(line(by,"year","economy","Economy Rate","#d63031"),260)
                    with c2: ch(line(by,"year","average","Bowling Average","#6c5ce7"),260)
                else:
                    st.info("Not enough yearly data to plot trends.")
                st.dataframe(by[["year","matches","wickets","economy","average","dot_pct"]].reset_index(drop=True))

# ══ 7. LEADERBOARD ═════════════════════════════════════════════════════════
elif section=="🏆 Leaderboard":
    page_banner("🏆","Leaderboard","The greatest of all time — ranked by format and stat","#1a1400","#2e2400","#fdcb6e")
    fmt=st.radio("Format",FORMATS,horizontal=True)
    tab1,tab2=st.tabs(["🏏 Batting","🎳 Bowling"])
    with tab1:
        bs=bat_fmt[bat_fmt["format"]==fmt]
        c1,c2=st.columns(2)
        sb=c1.selectbox("Rank by",["runs","average","strike_rate","sixes","hundreds","player_score"])
        mr=c2.slider("Min runs",0,3000,200,100)
        tn=st.slider("Top N",5,30,15)
        lb=bs[bs["runs"]>=mr].sort_values(sb,ascending=False).head(tn).reset_index(drop=True)
        lb.insert(0,"Rank",range(1,len(lb)+1))
        plot_h(bar_h(lb,sb,"striker",sb,"Teal",f"Top {tn} {fmt} Batters — {sb}"))
        show_cols=[c for c in ["Rank","striker","matches","runs","average","strike_rate","hundreds","fifties","highest","player_score"] if c in lb.columns]
        st.dataframe(lb[show_cols].reset_index(drop=True))
    with tab2:
        ws=bowl_fmt[bowl_fmt["format"]==fmt]
        c1,c2=st.columns(2)
        sb2=c1.selectbox("Rank by",["wickets","economy","average","dot_pct","five_wkts"])
        mw=c2.slider("Min wickets",0,100,10,5)
        tn2=st.slider("Top N bowlers",5,30,15)
        lb2=ws[ws["wickets"]>=mw].sort_values(sb2,ascending=(sb2 in ["economy","average"])).head(tn2).reset_index(drop=True)
        lb2.insert(0,"Rank",range(1,len(lb2)+1))
        plot_h(bar_h(lb2,sb2,"bowler",sb2,"Sunset",f"Top {tn2} {fmt} Bowlers — {sb2}"))
        show_cols2=[c for c in ["Rank","bowler","matches","wickets","economy","average","five_wkts","best_bowling"] if c in lb2.columns]
        st.dataframe(lb2[show_cols2].reset_index(drop=True))

# ══ 8. SIMILAR PLAYERS ═════════════════════════════════════════════════════
elif section=="🤖 Similar Players":
    page_banner("🤖","Similar Players","ML-powered: find cricketers who play just like your favourite","#0a0a1a","#1a1a3a","#a29bfe")
    st.markdown("Uses **KMeans clustering + cosine similarity** on career stats to find statistically similar players.")
    st_type=st.radio("Type",["Batter","Bowler"],horizontal=True)
    name=st.text_input("Player name","Babar")
    fmt=st.radio("Format",FORMATS,horizontal=True)
    if name:
        sname=resolve(name)
        if st_type=="Batter":
            src=bat_sim[(bat_sim["striker"].str.contains(sname,case=False,na=False))&(bat_sim["format"]==fmt)]
            if len(src)==0:
                st.error(f"No ML data for '{name}' in {fmt}. They may have fewer than 200 runs.")
            else:
                p=src.iloc[0]; cluster=int(p["cluster"])
                same=bat_sim[(bat_sim["cluster"]==cluster)&(bat_sim["format"]==fmt)]
                same=same[~same["striker"].str.contains(sname,case=False,na=False)]
                same=same.sort_values("average",ascending=False).head(10)
                st.subheader(f"Players most similar to {p['striker']} in {fmt}")
                st.caption(f"⭐ Player Score: {p.get('player_score','—')} | Cluster #{cluster}")
                plot_h(bar_h(same,"average","striker","average","Purples",f"Similar batters — {fmt}"))
                st.dataframe(same[["striker","runs","average","strike_rate","boundary_pct","player_score"]].reset_index(drop=True))
        else:
            src=bowl_sim[(bowl_sim["bowler"].str.contains(sname,case=False,na=False))&(bowl_sim["format"]==fmt)]
            if len(src)==0:
                st.error(f"No ML data for '{name}' in {fmt}. They may have fewer than 20 wickets.")
            else:
                p=src.iloc[0]; cluster=int(p["cluster"])
                same=bowl_sim[(bowl_sim["cluster"]==cluster)&(bowl_sim["format"]==fmt)]
                same=same[~same["bowler"].str.contains(sname,case=False,na=False)]
                same=same.sort_values("wickets",ascending=False).head(10)
                st.subheader(f"Bowlers most similar to {p['bowler']} in {fmt}")
                plot_h(bar_h(same,"wickets","bowler","economy","Reds",f"Similar bowlers — {fmt}"))
                st.dataframe(same[["bowler","wickets","economy","average","dot_pct"]].reset_index(drop=True))

# ══ 9. FORM & RATINGS ══════════════════════════════════════════════════════
elif section=="🔥 Form & Ratings":
    page_banner("🔥","Form & Ratings","Who is on fire right now? Last 2 seasons vs career average","#1a0800","#2e1500","#e17055")
    fmt=st.radio("Format",FORMATS,horizontal=True)
    tab1,tab2,tab3=st.tabs(["🏏 Batting Form","🎳 Bowling Form","⭐ Player Scores"])

    with tab1:
        src=bat_form[bat_form["format"]==fmt].copy()
        t1,t2=st.tabs(["🔥 On Fire","📉 Struggling"])
        with t1:
            top=src[src["form_score"]>=110].sort_values("form_score",ascending=False).head(20)
            if len(top)>0:
                plot_h(bar_h(top,"form_score","striker","form_score","Oranges",f"🔥 On Fire Batters ({fmt})"))
                st.dataframe(top[["striker","form_label","form_score","recent_avg","career_avg","recent_sr","career_sr"]].reset_index(drop=True))
            else: st.info("No batters in 'On Fire' form for this format yet.")
        with t2:
            bot=src[src["form_score"]<70].sort_values("form_score").head(20)
            if len(bot)>0:
                plot_h(bar_h(bot,"form_score","striker","form_score","Blues",f"📉 Struggling Batters ({fmt})"))
                st.dataframe(bot[["striker","form_label","form_score","recent_avg","career_avg"]].reset_index(drop=True))
            else: st.info("No batters struggling in this format.")

    with tab2:
        src2=bowl_form[bowl_form["format"]==fmt].copy()
        t1,t2=st.tabs(["🔥 On Fire","📉 Struggling"])
        with t1:
            top2=src2[src2["form_score"]>=110].sort_values("form_score",ascending=False).head(20)
            if len(top2)>0:
                plot_h(bar_h(top2,"form_score","bowler","form_score","Oranges",f"🔥 On Fire Bowlers ({fmt})"))
                st.dataframe(top2[["bowler","form_label","form_score","recent_econ","career_econ","recent_avg","career_avg"]].reset_index(drop=True))
            else: st.info("No bowlers in 'On Fire' form for this format yet.")
        with t2:
            bot2=src2[src2["form_score"]<70].sort_values("form_score").head(20)
            if len(bot2)>0:
                plot_h(bar_h(bot2,"form_score","bowler","form_score","Blues",f"📉 Struggling Bowlers ({fmt})"))
                st.dataframe(bot2[["bowler","form_label","form_score","recent_econ","career_econ"]].reset_index(drop=True))
            else: st.info("No bowlers struggling in this format.")

    with tab3:
        ps=bat_sim[bat_sim["format"]==fmt].sort_values("player_score",ascending=False).head(20)
        plot_h(bar_h(ps,"player_score","striker","player_score","Teal",f"⭐ Top 20 Player Scores ({fmt})"))
        st.caption("Score = Average 30% · Strike Rate 25% · Boundary% 20% · Runs volume 15% · Non-dot% 10%")
        st.dataframe(ps[["striker","player_score","average","strike_rate","boundary_pct","runs"]].reset_index(drop=True))
