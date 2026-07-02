# Cricket Analytics Dashboard

A multi-format cricket stats and ML dashboard covering ODI, Test, T20I, IPL, and PSL,
built on ball-by-ball data from [Cricsheet](https://cricsheet.org).

## How it fits together

There are three moving parts. Understanding this flow is the key to understanding
the whole project:

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│   pipeline.py    │ ───> │  GitHub repo      │ ───> │  cricket_dashboard.py│
│  (data pipeline) │      │  (CSV storage)    │      │  (Streamlit app)     │
└─────────────────┘      └──────────────────┘      └─────────────────────┘
   Downloads raw            Stores the cleaned         Reads the CSVs and
   Cricsheet data,          stats/ML tables as          renders all the
   cleans it, computes      CSV files (acts as a        charts, player
   stats + ML tables         lightweight database)       cards, hot/cold
                                                          lists, etc.
```

**Why a GitHub repo instead of a real database?** It's free, versioned (you can
see every past update in the commit history), and Streamlit can read CSVs
straight from `raw.githubusercontent.com` with zero setup — no database
credentials to manage in the dashboard itself.

## 1. `pipeline.py` — the data pipeline

This used to be a Colab notebook you had to open and re-run by hand every time
you wanted fresh data. It's now a standalone script that:

1. Downloads the latest ball-by-ball CSVs from Cricsheet for each format
2. Cleans and validates the data — **and logs every row it drops and why**
   (see `pipeline_run.log` after each run)
3. Builds all stats tables (career, yearly, venue, opponent, head-to-head)
4. Runs the ML step (player clustering, form ratings, player scores)
5. Pushes all resulting CSVs to your GitHub data repo
6. Writes `last_updated.txt` so the dashboard can show when data was last refreshed

### Running it manually
```bash
export GITHUB_TOKEN=your_personal_access_token
export GITHUB_USER=your_github_username
export GITHUB_REPO=cricket-data
python pipeline.py
```

### Running it automatically (recommended — no more manual reruns)
See `.github/workflows/update_data.yml`. It runs every Sunday at 03:00 UTC
automatically, or you can trigger it manually from the **Actions** tab on
GitHub anytime you want fresh data immediately.

**One-time setup for automation:**
1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Add a new repository secret named `DATA_PUSH_TOKEN` with your GitHub
   Personal Access Token (`repo` scope) as the value
3. That's it — the workflow file already references this secret

## 2. `cricket_dashboard.py` — the Streamlit app

Reads the 18 CSVs pushed by the pipeline (in parallel, for speed) and renders:
- Player search with Wikipedia-sourced bio cards
- Hot list / Cold list (in-form and out-of-form players)
- Player scores (0-100 composite rating)
- Format-by-format breakdowns (ODI/Test/T20I/IPL/PSL)

### A note on player profile data
Player bios and birth dates come from a live Wikipedia lookup at
`get_wiki()`. This can fail to find the right page for players with common
names or nicknames. If a profile is missing data, check the **"🔧 Data
diagnostics"** panel at the bottom of the app — it now logs exactly which
lookups failed and why, so you can add a manual name mapping to the
`WIKI_NAMES` dictionary near the top of the file.

### A note on load speed
On Streamlit Community Cloud's free tier, the app "sleeps" after a period
of inactivity and takes 20-40 seconds to wake up on the next visit — this
is a platform limitation, not a bug in this code. Once awake, data loads
are cached for 1 hour (`@st.cache_data(ttl=3600)`) and fetched in parallel,
so normal usage should feel fast.

## Known limitations (be upfront about these if presenting this project)
- Player age/bio data depends on Wikipedia having a matching, well-formatted
  page — coverage isn't 100% for lesser-known players
- Free-tier Streamlit hosting means occasional cold-start delays
- Cricsheet data has its own update cadence; this pipeline is only as fresh
  as Cricsheet's latest release
