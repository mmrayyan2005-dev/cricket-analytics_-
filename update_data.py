"""
Cricket Analytics — Auto Update Script
Runs daily via GitHub Actions to download fresh Cricsheet data and push CSVs.
"""

import os, urllib.request, zipfile, shutil
import pandas as pd
import numpy as np
import requests, base64
from datetime import datetime

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_USER  = os.environ['GITHUB_USER']
GITHUB_REPO  = os.environ['GITHUB_REPO']
BRANCH       = 'main'

print(f"🏏 Cricket Analytics Update — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 60)

# ── STEP 1: Download Cricsheet Data ─────────────────────────────────────────
print("\n📥 Step 1 — Downloading Cricsheet data...")

for folder in ['odi_data','test_data','t20i_data','ipl_data','psl_data',
               'wpl_data','bbl_data','cpl_data','sa20_data','nt20_data']:
    if os.path.isdir(folder):
        shutil.rmtree(folder)

BASE = 'https://cricsheet.org/downloads/'
downloads = [
    ('odi_data',  ['odis_csv2.zip']),
    ('test_data', ['tests_csv2.zip']),
    ('t20i_data', ['t20s_csv2.zip']),
    ('ipl_data',  ['ipl_male_csv2.zip',   'ipl_csv2.zip']),
    ('psl_data',  ['psl_male_csv2.zip',   'psl_csv2.zip']),
    ('wpl_data',  ['wpl_female_csv2.zip', 'wpl_csv2.zip']),
    ('bbl_data',  ['bbl_male_csv2.zip',   'bbl_csv2.zip']),
    ('cpl_data',  ['cpl_male_csv2.zip',   'cpl_csv2.zip']),
    ('sa20_data', ['sa20_male_csv2.zip',  'sa20_csv2.zip']),
    ('nt20_data', ['nat20_male_csv2.zip', 'smat_male_csv2.zip', 'pknt20_male_csv2.zip']),
]

def try_download(folder, filenames):
    for fname in filenames:
        try:
            urllib.request.urlretrieve(BASE + fname, fname)
            os.makedirs(folder, exist_ok=True)
            with zipfile.ZipFile(fname, 'r') as z:
                z.extractall(folder)
            os.remove(fname)
            return fname
        except Exception:
            if os.path.exists(fname): os.remove(fname)
    return None

for folder, fnames in downloads:
    label = folder.replace('_data','').upper()
    print(f"  {label}...", end=' ', flush=True)
    hit = try_download(folder, fnames)
    print(f"✓ ({hit})" if hit else "⚠ skipped")

# ── STEP 2: Load & Tag ───────────────────────────────────────────────────────
print("\n📊 Step 2 — Loading data...")

def load_format(folder, label):
    if not os.path.isdir(folder): return pd.DataFrame()
    files = [f for f in os.listdir(folder) if not f.endswith('_info.csv') and f.endswith('.csv')]
    if not files: return pd.DataFrame()
    dfs = []
    for f in sorted(files):
        try: dfs.append(pd.read_csv(f'{folder}/{f}'))
        except: pass
    if not dfs: return pd.DataFrame()
    df = pd.concat(dfs, ignore_index=True)
    df['format'] = label
    print(f"  ✓ {label:8s} {df.shape[0]:,} rows")
    return df

parts = [
    load_format('odi_data/',  'ODI'),
    load_format('test_data/', 'Test'),
    load_format('t20i_data/', 'T20I'),
    load_format('ipl_data/',  'IPL'),
    load_format('psl_data/',  'PSL'),
    load_format('wpl_data/',  'WPL'),
    load_format('bbl_data/',  'BBL'),
    load_format('cpl_data/',  'CPL'),
    load_format('sa20_data/', 'SA20'),
    load_format('nt20_data/', 'NT20'),
]
df = pd.concat([p for p in parts if len(p) > 0], ignore_index=True)
print(f"\n  TOTAL: {df.shape[0]:,} rows | formats: {df['format'].unique().tolist()}")

# ── STEP 3: Clean ────────────────────────────────────────────────────────────
print("\n🧹 Step 3 — Cleaning...")
df = df.drop_duplicates()
required = ['match_id','striker','bowler','runs_off_bat','ball','start_date']
df = df.dropna(subset=required)
df = df[df['runs_off_bat'].between(0,6)]
for col in ['wides','noballs','byes','legbyes','extras']:
    df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0)
df['bowler_runs'] = df['runs_off_bat'] + df['wides'] + df['noballs']
df['start_date']  = pd.to_datetime(df['start_date'], errors='coerce')
df = df.dropna(subset=['start_date'])
df['over']       = df['ball'].astype(str).str.split('.').str[0].astype(int)
df['total_runs'] = df['runs_off_bat'] + df['extras']
df['is_wicket']  = df['wicket_type'].notna().astype(int)
df['is_wide']    = (df['wides'] > 0).astype(int)
df['is_noball']  = (df['noballs'] > 0).astype(int)
df['is_dot']     = ((df['runs_off_bat']==0)&(df['is_wide']==0)&(df['is_noball']==0)).astype(int)
df['year']       = df['start_date'].dt.year
valid = df.groupby('match_id')['ball'].count()
df = df[df['match_id'].isin(valid[valid>=6].index)]
print(f"  ✓ {df.shape[0]:,} clean rows")

# ── STEP 4: Innings Tables ───────────────────────────────────────────────────
print("\n📋 Step 4 — Building innings tables...")
bat_innings = df[df['is_wide']==0].groupby(
    ['match_id','striker','batting_team','bowling_team','venue','start_date','format']
).agg(
    runs=('runs_off_bat','sum'), balls_faced=('runs_off_bat','count'),
    fours=('runs_off_bat', lambda x:(x==4).sum()),
    sixes=('runs_off_bat', lambda x:(x==6).sum()),
    dismissed=('is_wicket','max'),
).reset_index()
bat_innings['strike_rate'] = ((bat_innings['runs']/bat_innings['balls_faced'].replace(0,1))*100).round(2)
bat_innings['year'] = pd.to_datetime(bat_innings['start_date']).dt.year

bowl_innings = df[df['is_wide']==0].groupby(
    ['match_id','bowler','batting_team','bowling_team','venue','start_date','format']
).agg(
    balls=('bowler_runs','count'), runs_given=('bowler_runs','sum'),
    wickets=('is_wicket','sum'), dot_balls=('is_dot','sum'),
).reset_index()
bowl_innings['overs']   = (bowl_innings['balls']/6).round(1)
bowl_innings['economy'] = ((bowl_innings['runs_given']/bowl_innings['balls'].replace(0,1))*6).round(2)
bowl_innings['year']    = pd.to_datetime(bowl_innings['start_date']).dt.year
print(f"  ✓ bat_innings: {bat_innings.shape} | bowl_innings: {bowl_innings.shape}")

# ── STEP 5: Career Stats ─────────────────────────────────────────────────────
print("\n🏏 Step 5 — Career stats...")

def build_batting(data, group_cols=['striker']):
    bat = data.groupby(group_cols).agg(
        matches=('match_id','nunique'), runs=('runs_off_bat','sum'),
        balls_faced=('is_wide', lambda x:(x==0).sum()),
        dismissals=('is_wicket','sum'), dot_balls=('is_dot','sum'),
        fours=('runs_off_bat', lambda x:(x==4).sum()),
        sixes=('runs_off_bat', lambda x:(x==6).sum()),
    ).reset_index()
    bat['average']      = (bat['runs']/bat['dismissals'].replace(0,1)).round(2)
    bat['strike_rate']  = ((bat['runs']/bat['balls_faced'].replace(0,1))*100).round(2)
    bat['dot_pct']      = ((bat['dot_balls']/bat['balls_faced'].replace(0,1))*100).round(2)
    bat['boundary_pct'] = (((bat['fours']+bat['sixes'])/bat['balls_faced'].replace(0,1))*100).round(2)
    return bat.sort_values('runs', ascending=False)

def build_bowling(data, group_cols=['bowler']):
    bowl = data.groupby(group_cols).agg(
        matches=('match_id','nunique'),
        balls=('is_wide', lambda x:(x==0).sum()),
        runs_given=('bowler_runs','sum'), wickets=('is_wicket','sum'),
        dot_balls=('is_dot','sum'), wides=('is_wide','sum'), noballs=('is_noball','sum'),
    ).reset_index()
    bowl['overs']       = (bowl['balls']/6).round(1)
    bowl['economy']     = ((bowl['runs_given']/bowl['balls'].replace(0,1))*6).round(2)
    bowl['average']     = (bowl['runs_given']/bowl['wickets'].replace(0,1)).round(2)
    bowl['dot_pct']     = ((bowl['dot_balls']/bowl['balls'].replace(0,1))*100).round(2)
    bowl['strike_rate'] = (bowl['balls']/bowl['wickets'].replace(0,1)).round(2)
    return bowl.sort_values('wickets', ascending=False)

batting           = build_batting(df)
bowling           = build_bowling(df)
batting_by_format = build_batting(df, ['striker','format'])
bowling_by_format = build_bowling(df, ['bowler','format'])

bat_milestones = bat_innings.groupby(['striker','format']).agg(
    hundreds=('runs', lambda x:(x>=100).sum()),
    fifties=('runs',  lambda x:((x>=50)&(x<100)).sum()),
    highest=('runs','max'), ducks=('runs', lambda x:(x==0).sum()),
).reset_index()
bowl_milestones = bowl_innings.groupby(['bowler','format']).agg(
    five_wkts=('wickets', lambda x:(x>=5).sum()),
    four_wkts=('wickets', lambda x:(x==4).sum()),
).reset_index()
best_fig = bowl_innings.sort_values(['wickets','runs_given'],ascending=[False,True])
best_fig = best_fig.groupby(['bowler','format']).first()[['wickets','runs_given']].reset_index()
best_fig['best_bowling'] = best_fig['wickets'].astype(str)+'/'+best_fig['runs_given'].astype(str)
bowl_milestones = bowl_milestones.merge(best_fig[['bowler','format','best_bowling']], on=['bowler','format'], how='left')
batting_by_format = batting_by_format.merge(bat_milestones, on=['striker','format'], how='left')
bowling_by_format = bowling_by_format.merge(bowl_milestones, on=['bowler','format'], how='left')
print(f"  ✓ batting_by_format: {batting_by_format.shape} | bowling_by_format: {bowling_by_format.shape}")

# ── STEP 6: Yearly / Venue / Opponent / Matchup ──────────────────────────────
print("\n📈 Step 6 — Yearly/venue/opponent tables...")

batting_yearly = df.groupby(['striker','year','format']).agg(
    runs=('runs_off_bat','sum'), balls_faced=('is_wide',lambda x:(x==0).sum()),
    dismissals=('is_wicket','sum'), matches=('match_id','nunique'),
    fours=('runs_off_bat',lambda x:(x==4).sum()), sixes=('runs_off_bat',lambda x:(x==6).sum()),
).reset_index()
batting_yearly['average']     = (batting_yearly['runs']/batting_yearly['dismissals'].replace(0,1)).round(2)
batting_yearly['strike_rate'] = ((batting_yearly['runs']/batting_yearly['balls_faced'].replace(0,1))*100).round(2)

bowling_yearly = df.groupby(['bowler','year','format']).agg(
    balls=('is_wide',lambda x:(x==0).sum()), runs_given=('bowler_runs','sum'),
    wickets=('is_wicket','sum'), matches=('match_id','nunique'), dot_balls=('is_dot','sum'),
).reset_index()
bowling_yearly['economy']     = ((bowling_yearly['runs_given']/bowling_yearly['balls'].replace(0,1))*6).round(2)
bowling_yearly['average']     = (bowling_yearly['runs_given']/bowling_yearly['wickets'].replace(0,1)).round(2)
bowling_yearly['strike_rate'] = (bowling_yearly['balls']/bowling_yearly['wickets'].replace(0,1)).round(2)
bowling_yearly['dot_pct']     = ((bowling_yearly['dot_balls']/bowling_yearly['balls'].replace(0,1))*100).round(2)

batting_venue = df.groupby(['striker','venue','format']).agg(
    innings=('match_id','nunique'), runs=('runs_off_bat','sum'),
    balls_faced=('is_wide',lambda x:(x==0).sum()), dismissals=('is_wicket','sum'),
    fours=('runs_off_bat',lambda x:(x==4).sum()), sixes=('runs_off_bat',lambda x:(x==6).sum()),
).reset_index()
batting_venue['average']     = (batting_venue['runs']/batting_venue['dismissals'].replace(0,1)).round(2)
batting_venue['strike_rate'] = ((batting_venue['runs']/batting_venue['balls_faced'].replace(0,1))*100).round(2)

batting_opponent = df.groupby(['striker','bowling_team','format']).agg(
    innings=('match_id','nunique'), runs=('runs_off_bat','sum'),
    balls_faced=('is_wide',lambda x:(x==0).sum()), dismissals=('is_wicket','sum'),
    fours=('runs_off_bat',lambda x:(x==4).sum()), sixes=('runs_off_bat',lambda x:(x==6).sum()),
).reset_index()
batting_opponent['average']     = (batting_opponent['runs']/batting_opponent['dismissals'].replace(0,1)).round(2)
batting_opponent['strike_rate'] = ((batting_opponent['runs']/batting_opponent['balls_faced'].replace(0,1))*100).round(2)
batting_opponent.rename(columns={'bowling_team':'opponent'}, inplace=True)

bowling_venue = df.groupby(['bowler','venue','format']).agg(
    innings=('match_id','nunique'), balls=('is_wide',lambda x:(x==0).sum()),
    runs_given=('bowler_runs','sum'), wickets=('is_wicket','sum'), dot_balls=('is_dot','sum'),
).reset_index()
bowling_venue['economy'] = ((bowling_venue['runs_given']/bowling_venue['balls'].replace(0,1))*6).round(2)
bowling_venue['average'] = (bowling_venue['runs_given']/bowling_venue['wickets'].replace(0,1)).round(2)
bowling_venue['dot_pct'] = ((bowling_venue['dot_balls']/bowling_venue['balls'].replace(0,1))*100).round(2)

bowling_opponent = df.groupby(['bowler','batting_team','format']).agg(
    innings=('match_id','nunique'), balls=('is_wide',lambda x:(x==0).sum()),
    runs_given=('bowler_runs','sum'), wickets=('is_wicket','sum'), dot_balls=('is_dot','sum'),
).reset_index()
bowling_opponent['economy'] = ((bowling_opponent['runs_given']/bowling_opponent['balls'].replace(0,1))*6).round(2)
bowling_opponent['average'] = (bowling_opponent['runs_given']/bowling_opponent['wickets'].replace(0,1)).round(2)
bowling_opponent['dot_pct'] = ((bowling_opponent['dot_balls']/bowling_opponent['balls'].replace(0,1))*100).round(2)
bowling_opponent.rename(columns={'batting_team':'opponent'}, inplace=True)

batter_vs_bowler = df.groupby(['striker','bowler','format']).agg(
    balls_faced=('is_wide',lambda x:(x==0).sum()), runs=('runs_off_bat','sum'),
    dismissals=('is_wicket','sum'), fours=('runs_off_bat',lambda x:(x==4).sum()),
    sixes=('runs_off_bat',lambda x:(x==6).sum()), dot_balls=('is_dot','sum'),
).reset_index()
batter_vs_bowler['strike_rate'] = ((batter_vs_bowler['runs']/batter_vs_bowler['balls_faced'].replace(0,1))*100).round(2)
batter_vs_bowler['average']     = (batter_vs_bowler['runs']/batter_vs_bowler['dismissals'].replace(0,1)).round(2)
batter_vs_bowler = batter_vs_bowler[batter_vs_bowler['balls_faced']>=10]

bowler_vs_batter = df.groupby(['bowler','striker','format']).agg(
    balls_bowled=('is_wide',lambda x:(x==0).sum()), runs_given=('bowler_runs','sum'),
    wickets=('is_wicket','sum'), dot_balls=('is_dot','sum'),
    fours_given=('runs_off_bat',lambda x:(x==4).sum()),
    sixes_given=('runs_off_bat',lambda x:(x==6).sum()),
).reset_index()
bowler_vs_batter['economy']     = ((bowler_vs_batter['runs_given']/bowler_vs_batter['balls_bowled'].replace(0,1))*6).round(2)
bowler_vs_batter['strike_rate'] = (bowler_vs_batter['balls_bowled']/bowler_vs_batter['wickets'].replace(0,1)).round(2)
bowler_vs_batter['dot_pct']     = ((bowler_vs_batter['dot_balls']/bowler_vs_batter['balls_bowled'].replace(0,1))*100).round(2)
bowler_vs_batter = bowler_vs_batter[bowler_vs_batter['balls_bowled']>=10]
print("  ✓ All tables built")

# ── STEP 7: ML — Similarity + Form + Player Score ───────────────────────────
print("\n🤖 Step 7 — ML...")
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

bat_ml = batting_by_format.copy()
features = ['average','strike_rate','boundary_pct','dot_pct','runs']
bat_ml = bat_ml.dropna(subset=features)
bat_ml = bat_ml[bat_ml['runs'] >= 200]
scaler = StandardScaler()
X = scaler.fit_transform(bat_ml[features])
bat_ml['cluster'] = KMeans(n_clusters=8, random_state=42, n_init=10).fit_predict(X)

bowl_ml = bowling_by_format.copy()
bfeatures = ['economy','average','dot_pct','strike_rate','wickets']
bowl_ml = bowl_ml.dropna(subset=bfeatures)
bowl_ml = bowl_ml[bowl_ml['wickets'] >= 20]
Xb = scaler.fit_transform(bowl_ml[bfeatures])
bowl_ml['cluster'] = KMeans(n_clusters=8, random_state=42, n_init=10).fit_predict(Xb)

latest_year = batting_yearly['year'].max()
recent = batting_yearly[batting_yearly['year'] >= latest_year-1].groupby(['striker','format']).agg(
    recent_runs=('runs','sum'), recent_avg=('average','mean'), recent_sr=('strike_rate','mean')
).reset_index()
career_avg = batting_by_format[['striker','format','average','strike_rate']].copy()
career_avg.columns = ['striker','format','career_avg','career_sr']
form = recent.merge(career_avg, on=['striker','format'], how='left')
form['form_score'] = ((form['recent_avg']/form['career_avg'].replace(0,1))*50 +
                      (form['recent_sr']/form['career_sr'].replace(0,1))*50).round(1)
form['form_label'] = pd.cut(form['form_score'],
    bins=[0,60,85,110,999], labels=['📉 Poor','😐 Average','✅ Good','🔥 On Fire'])

latest_yr2 = bowling_yearly['year'].max()
recent_bowl = bowling_yearly[bowling_yearly['year'] >= latest_yr2-1].groupby(['bowler','format']).agg(
    recent_wkts=('wickets','sum'), recent_econ=('economy','mean'), recent_avg=('average','mean')
).reset_index()
career_bowl = bowling_by_format[['bowler','format','economy','average']].copy()
career_bowl.columns = ['bowler','format','career_econ','career_avg']
bowl_form = recent_bowl.merge(career_bowl, on=['bowler','format'], how='left')
bowl_form['form_score'] = ((bowl_form['career_econ']/bowl_form['recent_econ'].replace(0,1))*50 +
                           (bowl_form['career_avg']/bowl_form['recent_avg'].replace(0,1))*50).round(1)
bowl_form['form_label'] = pd.cut(bowl_form['form_score'],
    bins=[0,60,85,110,999], labels=['📉 Poor','😐 Average','✅ Good','🔥 On Fire'])

def compute_player_score(row):
    score = (
        min(row.get('average',0)/80,1)*30 +
        min(row.get('strike_rate',0)/180,1)*25 +
        min(row.get('boundary_pct',0)/30,1)*20 +
        min(row.get('runs',0)/10000,1)*15 +
        (1 - min(row.get('dot_pct',100)/70,1))*10
    )
    return round(score*100, 1)

batting_by_format['player_score'] = batting_by_format.apply(compute_player_score, axis=1)
bat_ml['player_score'] = bat_ml.apply(compute_player_score, axis=1)
print("  ✓ ML done")

# ── STEP 8: Push to GitHub ───────────────────────────────────────────────────
print(f"\n🚀 Step 8 — Pushing to GitHub ({GITHUB_USER}/{GITHUB_REPO})...")

def push_csv(df, filename):
    url = f'https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{filename}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    content_b64 = base64.b64encode(df.to_csv(index=False).encode('utf-8')).decode('utf-8')
    payload = {'message': f'Auto-update {filename} — {datetime.now().strftime("%Y-%m-%d")}',
               'content': content_b64, 'branch': BRANCH}
    if sha: payload['sha'] = sha
    resp = requests.put(url, headers=headers, json=payload)
    if resp.status_code in (200,201):
        print(f"  ✓ {filename} — {len(df):,} rows")
    else:
        print(f"  ✗ {filename} FAILED: {resp.status_code} {resp.json().get('message')}")

files = {
    'cricket_batting_stats.csv'    : batting,
    'cricket_bowling_stats.csv'    : bowling,
    'cricket_batting_by_format.csv': batting_by_format,
    'cricket_bowling_by_format.csv': bowling_by_format,
    'cricket_batting_yearly.csv'   : batting_yearly,
    'cricket_bowling_yearly.csv'   : bowling_yearly,
    'cricket_batting_venue.csv'    : batting_venue,
    'cricket_batting_opponent.csv' : batting_opponent,
    'cricket_bowling_venue.csv'    : bowling_venue,
    'cricket_bowling_opponent.csv' : bowling_opponent,
    'cricket_batter_vs_bowler.csv' : batter_vs_bowler,
    'cricket_bowler_vs_batter.csv' : bowler_vs_batter,
    'cricket_bat_innings.csv'      : bat_innings,
    'cricket_bowl_innings.csv'     : bowl_innings,
    'cricket_bat_form_ratings.csv' : form,
    'cricket_bowl_form_ratings.csv': bowl_form,
    'cricket_bat_similarity.csv'   : bat_ml[['striker','format','cluster','average','strike_rate','boundary_pct','dot_pct','runs','player_score']],
    'cricket_bowl_similarity.csv'  : bowl_ml[['bowler','format','cluster','wickets','economy','average','dot_pct']],
}

# Push last_updated timestamp
ts_df = pd.DataFrame({'last_updated': [datetime.now().strftime('%Y-%m-%d %H:%M UTC')]})
files['last_updated.txt'] = ts_df

for fname, df_out in files.items():
    push_csv(df_out, fname)

print(f"\n✅ Done — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
