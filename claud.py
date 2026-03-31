import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
import json
import math
import random
import numpy as np
from datetime import datetime

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*90)
print("🚀 CREATING ULTIMATE CARBON EMISSIONS DASHBOARD WITH ENHANCED FEATURES")
print("="*90)

# Auto-detect CO2 file
co2_folder = 'co2-emissions'
co2_files = [f for f in os.listdir(co2_folder) if f.endswith('.csv') and 'co2' in f.lower()] if os.path.exists(co2_folder) else []
if not co2_files:
    print("⚠️ Warning: No CO2 file found. Using synthetic data for demonstration.")
    np.random.seed(42)
    countries_list = [
        'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria',
        'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan',
        'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia',
        'Cameroon', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica',
        'Côte d\'Ivoire', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador',
        'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France',
        'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau',
        'Guyana', 'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland',
        'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan',
        'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar',
        'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia',
        'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal',
        'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan',
        'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar',
        'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia',
        'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa',
        'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Taiwan',
        'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan',
        'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City',
        'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe'
    ]
    years = list(range(1990, 2024))
    synthetic_data = []
    for country in countries_list:
        base_emission = np.random.uniform(0.1, 8000)
        growth_rate = np.random.uniform(-0.03, 0.08)
        for year in years:
            emission = base_emission * (1 + growth_rate) ** (year - 1990) + np.random.normal(0, base_emission * 0.08)
            population = np.random.uniform(10000, 1.4e9)
            synthetic_data.append({
                'Country': country, 'Year': year,
                'CO2_mt': max(0.01, emission),
                'Population_thousands': population / 1000
            })
    df = pd.DataFrame(synthetic_data)
    df['CO2_per_capita'] = (df['CO2_mt'] * 1_000_000) / (df['Population_thousands'] * 1000)
    co2_files = ['synthetic_data.csv']
else:
    try:
        co2_path = os.path.join(co2_folder, co2_files[0])
        co2 = pd.read_csv(co2_path, encoding='utf-8')
        pop = pd.read_csv('energy-intensity/population-population-people-in-thousands.csv', encoding='utf-8')
        for df_ in [co2, pop]:
            df_.replace('--', pd.NA, inplace=True)
            for col in df_.columns:
                if col.isdigit():
                    df_[col] = pd.to_numeric(df_[col], errors='coerce')
        def melt_df(df_, value_name):
            if 'Code' in df_.columns:
                df_ = df_.drop(columns=['Code'])
            id_vars = [c for c in df_.columns if not str(c).isdigit()]
            long = pd.melt(df_, id_vars=id_vars, var_name='Year', value_name=value_name)
            long['Year'] = pd.to_numeric(long['Year'], errors='coerce')
            return long
        co2_long = melt_df(co2, 'CO2_mt')
        pop_long = melt_df(pop, 'Population_thousands')
        df = co2_long.merge(pop_long, on=['Country', 'Year'], how='left')
        exclude = ['USSR', 'Yugoslavia', 'Czechoslovakia', 'East Germany', 'WORL', 'AFRC', 'EU27', 'OECD', 'OPEC']
        df = df[~df['Country'].isin(exclude)]
        df['CO2_per_capita'] = (df['CO2_mt'] * 1_000_000) / (df['Population_thousands'] * 1000)
        df = df.dropna(subset=['CO2_mt', 'Population_thousands', 'CO2_per_capita'])
        df = df[df['CO2_per_capita'] > 0]
        df = df[df['CO2_mt'] > 0]
    except Exception as e:
        print(f"⚠️ Data load error ({e}). Using synthetic data.")
        np.random.seed(42)
        countries_list = [
            'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria',
            'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan',
            'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia',
            'Cameroon', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica',
            'Côte d\'Ivoire', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador',
            'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France',
            'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau',
            'Guyana', 'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland',
            'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan',
            'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar',
            'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia',
            'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal',
            'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan',
            'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar',
            'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia',
            'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa',
            'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Taiwan',
            'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan',
            'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City',
            'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe'
        ]
        years = list(range(1990, 2024))
        synthetic_data = []
        for country in countries_list:
            base_emission = np.random.uniform(0.1, 8000)
            growth_rate = np.random.uniform(-0.03, 0.08)
            for year in years:
                emission = base_emission * (1 + growth_rate) ** (year - 1990) + np.random.normal(0, base_emission * 0.08)
                population = np.random.uniform(10000, 1.4e9)
                synthetic_data.append({
                    'Country': country, 'Year': year,
                    'CO2_mt': max(0.01, emission),
                    'Population_thousands': population / 1000
                })
        df = pd.DataFrame(synthetic_data)
        df['CO2_per_capita'] = (df['CO2_mt'] * 1_000_000) / (df['Population_thousands'] * 1000)

available_years = sorted(df['Year'].dropna().unique())
available_years = [int(y) for y in available_years if y <= 2023]
latest_year = int(available_years[-1]) if available_years else 2023
earliest_year = int(available_years[0]) if available_years else 1990
countries = sorted(df['Country'].dropna().unique())

print(f"\n📊 Data Overview: Years {earliest_year}-{latest_year} | {len(countries)} Countries | {len(df)} Records")

yearly_aggregated = df.groupby('Year').agg({'CO2_mt': 'sum', 'Population_thousands': 'sum'}).reset_index()
yearly_aggregated['CO2_per_capita'] = (yearly_aggregated['CO2_mt'] * 1_000_000) / (yearly_aggregated['Population_thousands'] * 1000)
yearly_aggregated['Year'] = yearly_aggregated['Year'].astype(int)
yearly_aggregated['CO2_mt'] = yearly_aggregated['CO2_mt'].astype(float)
yearly_aggregated['Population_thousands'] = yearly_aggregated['Population_thousands'].astype(float)
yearly_aggregated['CO2_per_capita'] = yearly_aggregated['CO2_per_capita'].astype(float)

top_countries = df.groupby('Country')['CO2_mt'].max().nlargest(20).index.tolist()

growth_data = []
for country in countries:
    country_df = df[df['Country'] == country].sort_values('Year')
    if len(country_df) >= 2:
        first_co2 = float(country_df['CO2_mt'].iloc[0])
        last_co2 = float(country_df['CO2_mt'].iloc[-1])
        growth_rate = float(((last_co2 - first_co2) / first_co2 * 100) if first_co2 > 0 else 0)
        growth_data.append({'Country': country, 'Growth_Rate': growth_rate, 'First_CO2': first_co2,
                            'Last_CO2': last_co2, 'First_Year': int(country_df['Year'].iloc[0]),
                            'Last_Year': int(country_df['Year'].iloc[-1])})
growth_df = pd.DataFrame(growth_data).sort_values('Growth_Rate', ascending=False)

yearly_country_data = []
for country in countries:
    country_df = df[df['Country'] == country].sort_values('Year')
    for _, row in country_df.iterrows():
        yearly_country_data.append({'Country': country, 'Year': int(row['Year']),
                                    'CO2_mt': float(row['CO2_mt']), 'CO2_per_capita': float(row['CO2_per_capita'])})

global_stats = {
    'peak_emissions': float(yearly_aggregated['CO2_mt'].max()),
    'peak_year': int(yearly_aggregated.loc[yearly_aggregated['CO2_mt'].idxmax(), 'Year']) if len(yearly_aggregated) > 0 else 0,
    'avg_growth_rate': float(growth_df['Growth_Rate'].mean()) if len(growth_df) > 0 else 0,
    'total_countries': int(len(countries)),
    'total_emissions_all_time': float(df['CO2_mt'].sum())
}

region_mapping = {
    'North America': ['United States', 'Canada', 'Mexico'],
    'Europe': ['Germany', 'United Kingdom', 'France', 'Italy', 'Spain', 'Poland', 'Netherlands', 'Turkey', 'Ukraine', 'Russia', 'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Norway', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Sweden', 'Switzerland'],
    'Asia': ['China', 'India', 'Japan', 'South Korea', 'Indonesia', 'Iran', 'Thailand', 'Vietnam', 'Malaysia', 'Pakistan', 'Bangladesh', 'Myanmar', 'Nepal', 'Sri Lanka', 'Afghanistan', 'Kazakhstan', 'Uzbekistan', 'Iraq', 'Saudi Arabia', 'Yemen', 'Syria', 'Jordan', 'Lebanon', 'Israel', 'Palestine', 'Cyprus', 'Georgia', 'Armenia', 'Azerbaijan', 'Mongolia', 'North Korea', 'Taiwan', 'Philippines', 'Cambodia', 'Laos', 'Singapore', 'Brunei', 'Timor-Leste'],
    'South America': ['Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay', 'Uruguay', 'Guyana', 'Suriname'],
    'Africa': ['South Africa', 'Nigeria', 'Egypt', 'Algeria', 'Morocco', 'Angola', 'Kenya', 'Ethiopia', 'Ghana', 'Tanzania', 'Sudan', 'Uganda', 'Mozambique', 'Madagascar', 'Cameroon', 'Côte d\'Ivoire', 'Niger', 'Burkina Faso', 'Mali', 'Malawi', 'Zambia', 'Senegal', 'Chad', 'Somalia', 'Zimbabwe', 'Guinea', 'Rwanda', 'Benin', 'Burundi', 'Tunisia', 'South Sudan', 'Togo', 'Eritrea', 'Sierra Leone', 'Liberia', 'Central African Republic', 'Mauritania', 'Congo', 'Libya'],
    'Oceania': ['Australia', 'New Zealand', 'Papua New Guinea', 'Fiji', 'Solomon Islands', 'Vanuatu', 'Samoa', 'Kiribati', 'Micronesia', 'Tonga', 'Palau', 'Marshall Islands', 'Tuvalu', 'Nauru'],
    'Middle East': ['Saudi Arabia', 'United Arab Emirates', 'Qatar', 'Kuwait', 'Oman', 'Bahrain', 'Iran', 'Iraq', 'Jordan', 'Lebanon', 'Syria', 'Yemen']
}

df['Region'] = 'Other'
for region, countries_list in region_mapping.items():
    df.loc[df['Country'].isin(countries_list), 'Region'] = region

yearly_data_js = [{'Year': int(r['Year']), 'Total_CO2': float(r['CO2_mt']),
                   'Total_Population': float(r['Population_thousands']), 'Per_Capita': float(r['CO2_per_capita'])}
                  for _, r in yearly_aggregated.iterrows()]

race_data_js = []
for year in available_years:
    year_data = [d for d in yearly_country_data if d['Year'] == year]
    sorted_data = sorted(year_data, key=lambda x: x['CO2_mt'], reverse=True)[:15]
    race_data_js.append({'Year': year, 'Data': sorted_data})

growth_by_year = []
for country in countries:
    country_df = df[df['Country'] == country].sort_values('Year')
    if len(country_df) >= 2:
        for i in range(1, len(country_df)):
            year = int(country_df['Year'].iloc[i])
            prev_co2 = float(country_df['CO2_mt'].iloc[i-1])
            curr_co2 = float(country_df['CO2_mt'].iloc[i])
            growth = ((curr_co2 - prev_co2) / prev_co2 * 100) if prev_co2 > 0 else 0
            growth_by_year.append({'Country': country, 'Year': year, 'Growth_Rate': growth, 'CO2_mt': curr_co2})

growth_race_data = []
for year in available_years:
    year_data = [d for d in growth_by_year if d['Year'] == year]
    sorted_data = sorted(year_data, key=lambda x: x['Growth_Rate'], reverse=True)[:10]
    growth_race_data.append({'Year': year, 'Data': sorted_data})

map_data_js = [{'Country': str(r['Country']), 'Year': int(r['Year']),
                'CO2_mt': float(r['CO2_mt']), 'CO2_per_capita': float(r['CO2_per_capita'])}
               for _, r in df.iterrows() if int(r['Year']) in available_years]

region_country_mapping = {}
for region, clist in region_mapping.items():
    for c in clist:
        region_country_mapping[c] = region

sankey_data_js = []
for year in available_years:
    year_data = [d for d in yearly_country_data if d['Year'] == year]
    top_emitters = sorted(year_data, key=lambda x: x['CO2_mt'], reverse=True)[:15]
    region_totals = {}
    for emitter in top_emitters:
        region = region_country_mapping.get(emitter['Country'], 'Other')
        region_totals[region] = region_totals.get(region, 0) + emitter['CO2_mt']
    sankey_data_js.append({'Year': year, 'Regions': region_totals, 'TopEmitters': top_emitters})

comparison_data_js = []
for country in countries:
    country_df = df[df['Country'] == country].sort_values('Year')
    if len(country_df) >= 2:
        years_list = [int(r['Year']) for _, r in country_df.iterrows()]
        co2_list = [float(r['CO2_mt']) for _, r in country_df.iterrows()]
        pc_list = [float(r['CO2_per_capita']) for _, r in country_df.iterrows()]
        comparison_data_js.append({
            'Country': country, 'Years': years_list, 'CO2': co2_list, 'PerCapita': pc_list,
            'First_Year': years_list[0], 'Last_Year': years_list[-1],
            'First_CO2': co2_list[0], 'Last_CO2': co2_list[-1],
            'CO2_Change': co2_list[-1] - co2_list[0],
            'CO2_Pct_Change': ((co2_list[-1] - co2_list[0]) / co2_list[0] * 100) if co2_list[0] > 0 else 0,
            'First_Per_Capita': pc_list[0], 'Last_Per_Capita': pc_list[-1],
            'Per_Capita_Change': pc_list[-1] - pc_list[0],
            'Per_Capita_Pct_Change': ((pc_list[-1] - pc_list[0]) / pc_list[0] * 100) if pc_list[0] > 0 else 0
        })

print("✅ Data preparation complete!")

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carbon Emissions Analytics Platform</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg:        #0a0d14;
            --surface:   #111520;
            --surface2:  #161c2d;
            --border:    rgba(255,255,255,0.07);
            --accent1:   #ff6b35;
            --accent2:   #f7c948;
            --accent3:   #3bffc8;
            --accent4:   #a78bfa;
            --accent5:   #f472b6;
            --text:      #e8ecf4;
            --muted:     #6b7a99;
            --glow1:     rgba(255,107,53,0.35);
            --glow2:     rgba(247,201,72,0.3);
            --glow3:     rgba(59,255,200,0.3);
            --glow4:     rgba(167,139,250,0.3);
            --radius:    16px;
            --radius-lg: 24px;
        }

        * { margin:0; padding:0; box-sizing:border-box; }

        body {
            font-family: 'DM Sans', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ─── ANIMATED NOISE / GRID BACKGROUND ─────────────────── */
        body::before {
            content:'';
            position:fixed; inset:0; z-index:0;
            background-image:
                repeating-linear-gradient(0deg,  transparent, transparent 59px, rgba(255,255,255,0.025) 60px),
                repeating-linear-gradient(90deg, transparent, transparent 59px, rgba(255,255,255,0.025) 60px);
            pointer-events:none;
        }

        .app-wrap { position:relative; z-index:1; max-width:1640px; margin:0 auto; padding:24px; }

        /* ─── HEADER ────────────────────────────────────────────── */
        .hero {
            position:relative;
            border-radius: var(--radius-lg);
            overflow:hidden;
            padding: 56px 48px 48px;
            margin-bottom: 28px;
            background: linear-gradient(135deg, #0f1629 0%, #1a0a2e 40%, #0d1f1a 100%);
            border: 1px solid var(--border);
        }
        .hero-glow {
            position:absolute; border-radius:50%; filter:blur(80px); pointer-events:none;
        }
        .hero-glow.a { width:400px;height:400px; top:-120px;left:-80px;  background:var(--glow1); }
        .hero-glow.b { width:350px;height:350px; top:-80px; right:-60px; background:var(--glow4); }
        .hero-glow.c { width:300px;height:300px; bottom:-80px;left:40%;  background:var(--glow3); opacity:.5; }

        .hero-badge {
            display:inline-flex; align-items:center; gap:8px;
            background:rgba(255,107,53,0.15); border:1px solid rgba(255,107,53,0.4);
            color:var(--accent1); padding:6px 14px; border-radius:999px;
            font-size:12px; font-weight:600; letter-spacing:1.5px; text-transform:uppercase;
            margin-bottom:20px;
        }
        .hero-badge span { width:6px;height:6px;background:var(--accent1);border-radius:50%;
            animation:pulse 1.6s ease-in-out infinite; }

        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(1.4)} }

        .hero h1 {
            font-family:'Syne',sans-serif; font-weight:800;
            font-size:clamp(2rem,4vw,3.4rem); line-height:1.1;
            background: linear-gradient(135deg, #fff 0%, var(--accent2) 50%, var(--accent1) 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            background-clip:text; margin-bottom:14px;
        }
        .hero p { color:var(--muted); font-size:15px; max-width:600px; line-height:1.7; }

        /* ─── STATS BANNER ──────────────────────────────────────── */
        .kpi-row {
            display:grid;
            grid-template-columns: repeat(auto-fit, minmax(220px,1fr));
            gap:16px; margin-bottom:28px;
        }
        .kpi-card {
            position:relative; overflow:hidden;
            background:var(--surface); border:1px solid var(--border);
            border-radius: var(--radius); padding:24px 22px;
            transition: transform .25s, box-shadow .25s;
        }
        .kpi-card:hover { transform:translateY(-4px); }
        .kpi-card::before {
            content:''; position:absolute; top:0;left:0;right:0; height:3px;
            border-radius:var(--radius) var(--radius) 0 0;
        }
        .kpi-card:nth-child(1)::before { background:linear-gradient(90deg,var(--accent1),var(--accent2)); box-shadow:0 0 16px var(--glow1); }
        .kpi-card:nth-child(2)::before { background:linear-gradient(90deg,var(--accent3),#00d4ff); box-shadow:0 0 16px var(--glow3); }
        .kpi-card:nth-child(3)::before { background:linear-gradient(90deg,var(--accent4),var(--accent5)); box-shadow:0 0 16px var(--glow4); }
        .kpi-card:nth-child(4)::before { background:linear-gradient(90deg,var(--accent2),var(--accent1)); box-shadow:0 0 16px var(--glow2); }
        .kpi-card:hover:nth-child(1) { box-shadow:0 8px 32px var(--glow1); }
        .kpi-card:hover:nth-child(2) { box-shadow:0 8px 32px var(--glow3); }
        .kpi-card:hover:nth-child(3) { box-shadow:0 8px 32px var(--glow4); }
        .kpi-card:hover:nth-child(4) { box-shadow:0 8px 32px var(--glow2); }

        .kpi-label { font-size:11px; letter-spacing:1.4px; text-transform:uppercase; color:var(--muted); margin-bottom:10px; }
        .kpi-value { font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:700; line-height:1; }
        .kpi-card:nth-child(1) .kpi-value { color:var(--accent1); }
        .kpi-card:nth-child(2) .kpi-value { color:var(--accent3); }
        .kpi-card:nth-child(3) .kpi-value { color:var(--accent4); }
        .kpi-card:nth-child(4) .kpi-value { color:var(--accent2); }
        .kpi-unit { font-size:12px; color:var(--muted); margin-top:6px; }

        /* ─── TABS ──────────────────────────────────────────────── */
        .tab-nav {
            display:flex; gap:4px; overflow-x:auto; padding-bottom:2px;
            margin-bottom:24px; scrollbar-width:none;
        }
        .tab-nav::-webkit-scrollbar { display:none; }

        .tab-btn {
            flex-shrink:0; padding:10px 20px;
            background:var(--surface); border:1px solid var(--border);
            border-radius:999px; color:var(--muted);
            font-family:'DM Sans',sans-serif; font-size:13px; font-weight:500;
            cursor:pointer; white-space:nowrap;
            transition: all .22s; letter-spacing:.3px;
        }
        .tab-btn:hover { border-color:rgba(255,255,255,0.18); color:var(--text); }
        .tab-btn.active {
            background:linear-gradient(135deg,var(--accent1),var(--accent2));
            border-color:transparent; color:#000; font-weight:700;
            box-shadow:0 4px 18px var(--glow1);
        }

        /* ─── TAB CONTENT ───────────────────────────────────────── */
        .tab-content { display:none; animation: tabIn .35s ease; }
        .tab-content.active { display:block; }
        @keyframes tabIn {
            from { opacity:0; transform:translateY(14px); }
            to   { opacity:1; transform:translateY(0);    }
        }

        /* ─── SECTION HEADER ────────────────────────────────────── */
        .section-header {
            display:flex; align-items:center; gap:12px;
            margin-bottom:20px;
        }
        .section-icon {
            width:40px;height:40px; border-radius:10px;
            display:flex; align-items:center; justify-content:center;
            font-size:18px;
        }
        .section-header h2 { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700; }
        .section-header p  { font-size:13px; color:var(--muted); margin-top:2px; }

        /* ─── CONTROLS PANEL ────────────────────────────────────── */
        .ctrl-panel {
            background:var(--surface); border:1px solid var(--border);
            border-radius:var(--radius); padding:20px 22px;
            display:flex; flex-wrap:wrap; gap:16px; align-items:flex-end;
            margin-bottom:20px;
        }
        .ctrl-group { flex:1; min-width:160px; }
        .ctrl-group label {
            display:block; font-size:11px; letter-spacing:1.2px;
            text-transform:uppercase; color:var(--muted); margin-bottom:8px;
        }
        select, input[type="text"] {
            width:100%; padding:10px 14px;
            background:var(--surface2); border:1px solid var(--border);
            border-radius:10px; color:var(--text);
            font-family:'DM Sans',sans-serif; font-size:14px;
            transition: border-color .2s, box-shadow .2s; appearance:none;
        }
        select:focus, input[type="text"]:focus {
            outline:none; border-color:var(--accent1);
            box-shadow:0 0 0 3px rgba(255,107,53,0.15);
        }

        .btn {
            width:100%; padding:10px 20px;
            background:linear-gradient(135deg,var(--accent1),var(--accent2));
            border:none; border-radius:10px;
            color:#000; font-family:'DM Sans',sans-serif;
            font-size:14px; font-weight:700; cursor:pointer;
            transition: transform .2s, box-shadow .2s; letter-spacing:.3px;
        }
        .btn:hover { transform:translateY(-2px); box-shadow:0 6px 20px var(--glow1); }
        .btn:active { transform:translateY(0); }
        .btn.secondary {
            background:var(--surface2); color:var(--text); border:1px solid var(--border);
            box-shadow:none;
        }
        .btn.secondary:hover { border-color:rgba(255,255,255,0.2); box-shadow:none; }

        /* ─── SLIDER CONTROL ────────────────────────────────────── */
        .slider-row {
            display:flex; align-items:center; gap:16px; margin-bottom:20px;
        }
        .slider-row input[type="range"] {
            flex:1; -webkit-appearance:none; appearance:none;
            height:5px; border-radius:999px;
            background:linear-gradient(90deg,var(--accent1),var(--accent2));
            outline:none; border:none; cursor:pointer;
        }
        .slider-row input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance:none; width:18px;height:18px;
            border-radius:50%; background:var(--accent2);
            box-shadow:0 0 8px var(--glow2); cursor:pointer;
        }
        .slider-year-badge {
            font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:700;
            color:var(--accent2); min-width:68px; text-align:right;
        }
        .speed-label { font-size:12px; color:var(--muted); text-align:center; margin-top:4px; }

        /* ─── CHART CARD ────────────────────────────────────────── */
        .chart-card {
            background:var(--surface); border:1px solid var(--border);
            border-radius:var(--radius); overflow:hidden;
            margin-bottom:20px; padding:4px;
        }

        /* ─── INFO STRIP ────────────────────────────────────────── */
        .info-strip {
            background:var(--surface2); border:1px solid var(--border);
            border-left:3px solid var(--accent3); border-radius:var(--radius);
            padding:14px 18px; font-size:13px; color:var(--muted); line-height:1.6;
            margin-top:16px;
        }
        .info-strip strong { color:var(--accent3); }

        /* ─── STAT CARDS (trend/rankings bottom) ────────────────── */
        .metric-row {
            display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
            gap:14px; margin-top:18px;
        }
        .metric-card {
            background:var(--surface); border:1px solid var(--border);
            border-radius:var(--radius); padding:20px;
            text-align:center; transition:transform .22s;
        }
        .metric-card:hover { transform:translateY(-3px); }
        .metric-card .m-label { font-size:11px; text-transform:uppercase; letter-spacing:1.2px; color:var(--muted); margin-bottom:10px; }
        .metric-card .m-value { font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:700; }
        .metric-card.c1 .m-value { color:var(--accent1); }
        .metric-card.c2 .m-value { color:var(--accent3); }
        .metric-card.c3 .m-value { color:var(--accent4); }
        .metric-card.c4 .m-value { color:var(--accent2); }
        .up   { color:var(--accent1) !important; }
        .down { color:var(--accent3) !important; }

        /* ─── COMPARISON STATS ──────────────────────────────────── */
        .cmp-panel {
            background:var(--surface); border:1px solid var(--border);
            border-radius:var(--radius); padding:24px; margin-top:18px;
        }
        .cmp-panel h3 { font-family:'Syne',sans-serif; font-size:1rem; font-weight:700;
            text-align:center; margin-bottom:20px; color:var(--text); }
        .cmp-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; }
        .cmp-metric {
            background:var(--surface2); border:1px solid var(--border);
            border-radius:12px; padding:16px; text-align:center;
        }
        .cmp-metric .cv { font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:700; color:var(--accent1); }
        .cmp-metric .cl { font-size:11px; color:var(--muted); margin-top:5px; letter-spacing:.5px; }

        /* ─── TABLE ─────────────────────────────────────────────── */
        .search-wrap { position:relative; margin-bottom:16px; }
        .search-wrap input {
            padding:12px 16px 12px 44px;
            border-radius:12px; font-size:14px;
        }
        .search-icon {
            position:absolute; left:14px; top:50%; transform:translateY(-50%);
            color:var(--muted); font-size:16px; pointer-events:none;
        }
        .tbl-wrap {
            background:var(--surface); border:1px solid var(--border);
            border-radius:var(--radius); overflow:hidden; max-height:560px; overflow-y:auto;
        }
        .tbl-wrap::-webkit-scrollbar { width:6px; }
        .tbl-wrap::-webkit-scrollbar-track { background:var(--surface2); }
        .tbl-wrap::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.1); border-radius:3px; }

        table { width:100%; border-collapse:collapse; }
        thead th {
            background:var(--surface2); padding:13px 16px;
            font-size:11px; text-transform:uppercase; letter-spacing:1.2px;
            color:var(--muted); text-align:left; font-weight:600;
            position:sticky; top:0; z-index:5; border-bottom:1px solid var(--border);
        }
        tbody td {
            padding:11px 16px; border-bottom:1px solid var(--border);
            font-size:14px; color:var(--text);
        }
        tbody tr { transition: background .15s; cursor:pointer; }
        tbody tr:hover { background:rgba(255,107,53,0.07); }
        tbody tr:last-child td { border-bottom:none; }

        .rank-pill {
            display:inline-flex; align-items:center; justify-content:center;
            width:28px;height:28px; border-radius:50%;
            background:linear-gradient(135deg,var(--accent1),var(--accent2));
            color:#000; font-weight:700; font-size:11px;
        }
        .badge-up   { color:var(--accent1); font-weight:600; }
        .badge-down { color:var(--accent3); font-weight:600; }

        /* ─── RESPONSIVE ─────────────────────────────────────────── */
        @media(max-width:768px){
            .app-wrap { padding:14px; }
            .hero { padding:32px 22px; }
            .hero h1 { font-size:1.8rem; }
            .kpi-row { grid-template-columns:repeat(2,1fr); }
        }
    </style>
</head>
<body>
<div class="app-wrap">

    <!-- HERO HEADER -->
    <header class="hero">
        <div class="hero-glow a"></div>
        <div class="hero-glow b"></div>
        <div class="hero-glow c"></div>
        <div class="hero-badge"><span></span>Live Analytics Platform</div>
        <h1>Carbon Emissions<br>Intelligence Dashboard</h1>
        <p>227 nations · 33 years · Interactive world map · Animated races · Dual comparison · Sankey flows</p>
    </header>

    <!-- KPI BANNER -->
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-label">Global CO₂ (Latest Year)</div>
            <div class="kpi-value" id="kpi1">—</div>
            <div class="kpi-unit">Million Tonnes</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Countries Tracked</div>
            <div class="kpi-value" id="kpi2">—</div>
            <div class="kpi-unit">Nations Worldwide</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Data Range</div>
            <div class="kpi-value" id="kpi3">—</div>
            <div class="kpi-unit">Year Span</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Peak Emissions Year</div>
            <div class="kpi-value" id="kpi4">—</div>
            <div class="kpi-unit">Historical Maximum</div>
        </div>
    </div>

    <!-- TAB NAV -->
    <nav class="tab-nav">
        <button class="tab-btn active" onclick="switchTab('worldmap')">🗺 World Map</button>
        <button class="tab-btn" onclick="switchTab('animation')">🏁 Emission Race</button>
        <button class="tab-btn" onclick="switchTab('growthrace')">📈 Growth Race</button>
        <button class="tab-btn" onclick="switchTab('compare')">⚖ Country Compare</button>
        <button class="tab-btn" onclick="switchTab('trends')">📉 Trend Analysis</button>
        <button class="tab-btn" onclick="switchTab('heatmap')">🔥 Heat Calendar</button>
        <button class="tab-btn" onclick="switchTab('sankey')">🌊 Emissions Flow</button>
        <button class="tab-btn" onclick="switchTab('rankings')">🏆 Rankings</button>
        <button class="tab-btn" onclick="switchTab('data')">📋 All Data</button>
    </nav>

    <!-- WORLD MAP -->
    <div id="worldmap" class="tab-content active">
        <div class="section-header">
            <div class="section-icon" style="background:rgba(255,107,53,.15)">🗺</div>
            <div><h2>Interactive World Map</h2><p>Hover any country for details · Click to drill into trend analysis</p></div>
        </div>
        <div class="ctrl-panel">
            <div class="ctrl-group"><label>Year</label><select id="mapYearSelect"></select></div>
            <div class="ctrl-group"><label>Metric</label>
                <select id="mapMetricSelect">
                    <option value="co2">Total CO₂ (Mt)</option>
                    <option value="per_capita">Per Capita (t)</option>
                </select>
            </div>
            <div class="ctrl-group"><label>&nbsp;</label><button class="btn" onclick="updateMap()">Update Map</button></div>
        </div>
        <div class="chart-card"><div id="worldMapContainer" style="height:580px"></div></div>
        <div class="info-strip"><strong>Tip:</strong> Click any country on the map to jump directly to its trend analysis.</div>
    </div>

    <!-- EMISSION RACE -->
    <div id="animation" class="tab-content">
        <div class="section-header">
            <div class="section-icon" style="background:rgba(247,201,72,.15)">🏁</div>
            <div><h2>Animated Emissions Race</h2><p>Top 15 emitters competing year by year</p></div>
        </div>
        <div class="ctrl-panel">
            <div class="ctrl-group">
                <label>Speed (ms/frame)</label>
                <input type="range" id="animationSpeed" min="400" max="2000" value="1000" step="100"
                       style="width:100%;margin-top:6px" oninput="document.getElementById('speedValue').innerText=this.value+'ms'">
                <div class="speed-label" id="speedValue">1000ms</div>
            </div>
            <div class="ctrl-group"><label>&nbsp;</label><button class="btn" onclick="startRaceAnimation()" id="racePlayBtn">▶ Start Race</button></div>
            <div class="ctrl-group"><label>&nbsp;</label><button class="btn secondary" onclick="resetRaceAnimation()">↺ Reset</button></div>
        </div>
        <div class="slider-row">
            <input type="range" id="raceYearSlider" min="0" max="0" step="1" oninput="updateRaceYear(this.value)">
            <span class="slider-year-badge" id="raceYearDisplay">—</span>
        </div>
        <div class="chart-card"><div id="raceChart" style="height:580px"></div></div>
        <div class="info-strip"><strong>Animated Bar Race:</strong> Each frame represents one year. Use the slider to jump to any year.</div>
    </div>

    <!-- GROWTH RACE -->
    <div id="growthrace" class="tab-content">
        <div class="section-header">
            <div class="section-icon" style="background:rgba(59,255,200,.15)">📈</div>
            <div><h2>Growth Rate Race</h2><p>Who's growing emissions fastest year over year?</p></div>
        </div>
        <div class="ctrl-panel">
            <div class="ctrl-group">
                <label>Speed (ms/frame)</label>
                <input type="range" id="growthSpeed" min="400" max="2000" value="1000" step="100"
                       style="width:100%;margin-top:6px" oninput="document.getElementById('growthSpeedValue').innerText=this.value+'ms'">
                <div class="speed-label" id="growthSpeedValue">1000ms</div>
            </div>
            <div class="ctrl-group"><label>&nbsp;</label><button class="btn" onclick="startGrowthRaceAnimation()" id="growthRacePlayBtn">▶ Start Race</button></div>
            <div class="ctrl-group"><label>&nbsp;</label><button class="btn secondary" onclick="resetGrowthRaceAnimation()">↺ Reset</button></div>
        </div>
        <div class="slider-row">
            <input type="range" id="growthYearSlider" min="0" max="0" step="1" oninput="updateGrowthYear(this.value)">
            <span class="slider-year-badge" id="growthYearDisplay">—</span>
        </div>
        <div class="chart-card"><div id="growthRaceChart" style="height:580px"></div></div>
        <div class="info-strip"><strong>Growth Race:</strong> <span style="color:#ff6b35">Red bars</span> = increasing · <span style="color:#3bffc8">Teal bars</span> = decreasing emissions.</div>
    </div>

    <!-- DUAL COMPARE -->
    <div id="compare" class="tab-content">
        <div class="section-header">
            <div class="section-icon" style="background:rgba(167,139,250,.15)">⚖</div>
            <div><h2>Dual Country Comparison</h2><p>Side-by-side emissions journey with full metrics</p></div>
        </div>
        <div class="ctrl-panel">
            <div class="ctrl-group"><label>First Country</label><select id="country1Select"></select></div>
            <div class="ctrl-group"><label>Second Country</label><select id="country2Select"></select></div>
            <div class="ctrl-group"><label>&nbsp;</label><button class="btn" onclick="updateDualComparison()">Compare →</button></div>
        </div>
        <div class="chart-card"><div id="dualComparisonChart" style="height:460px"></div></div>
        <div id="dualComparisonStats" class="cmp-panel" style="display:none"></div>
        <div class="info-strip"><strong>Tip:</strong> Both total emissions and growth metrics are shown below the chart.</div>
    </div>

    <!-- TRENDS -->
    <div id="trends" class="tab-content">
        <div class="section-header">
            <div class="section-icon" style="background:rgba(244,114,182,.15)">📉</div>
            <div><h2>Trend Analysis</h2><p>Actual data + trend line + 3-year moving average</p></div>
        </div>
        <div class="ctrl-panel">
            <div class="ctrl-group"><label>Country</label><select id="trendCountrySelect"></select></div>
            <div class="ctrl-group"><label>&nbsp;</label><button class="btn" onclick="updateTrendAnalysis()">Analyse →</button></div>
        </div>
        <div class="chart-card"><div id="trendChart" style="height:440px"></div></div>
        <div id="trendStats" class="metric-row"></div>
        <div class="info-strip"><strong>Analysis includes:</strong> raw emissions, linear trend line, and 3-year centred moving average.</div>
    </div>

    <!-- HEAT CALENDAR -->
    <div id="heatmap" class="tab-content">
        <div class="section-header">
            <div class="section-icon" style="background:rgba(255,107,53,.15)">🔥</div>
            <div><h2>Heat Calendar</h2><p>Year-over-year emissions intensity comparison</p></div>
        </div>
        <div class="ctrl-panel">
            <div class="ctrl-group"><label>Country</label><select id="heatCountrySelect"></select></div>
            <div class="ctrl-group">
                <label>Start Year</label><select id="heatYearStart"></select>
            </div>
            <div class="ctrl-group">
                <label>End Year</label><select id="heatYearEnd"></select>
            </div>
            <div class="ctrl-group"><label>&nbsp;</label><button class="btn" onclick="updateHeatCalendar()">Generate →</button></div>
        </div>
        <div class="chart-card"><div id="heatCalendarChart" style="height:520px"></div></div>
        <div class="info-strip"><strong>Heat Calendar:</strong> Darker cells indicate higher emission years. Diagonal = baseline year.</div>
    </div>

    <!-- SANKEY -->
    <div id="sankey" class="tab-content">
        <div class="section-header">
            <div class="section-icon" style="background:rgba(59,255,200,.15)">🌊</div>
            <div><h2>Emissions Flow (Sankey)</h2><p>Global → Region → Top Emitters flow diagram</p></div>
        </div>
        <div class="ctrl-panel">
            <div class="ctrl-group"><label>Year</label><select id="sankeyYearSelect"></select></div>
            <div class="ctrl-group"><label>&nbsp;</label><button class="btn" onclick="updateSankeyDiagram()">Generate Flow →</button></div>
        </div>
        <div class="slider-row">
            <input type="range" id="sankeyYearSlider" min="0" max="0" step="1" oninput="updateSankeyYear(this.value)">
            <span class="slider-year-badge" id="sankeyYearDisplay">—</span>
        </div>
        <div class="chart-card"><div id="sankeyChart" style="height:580px"></div></div>
        <div class="info-strip"><strong>Flow Diagram:</strong> Width of each path is proportional to CO₂ emissions in that year.</div>
    </div>

    <!-- RANKINGS -->
    <div id="rankings" class="tab-content">
        <div class="section-header">
            <div class="section-icon" style="background:rgba(247,201,72,.15)">🏆</div>
            <div><h2>Country Rankings</h2><p>Ranked by total emissions, per capita, or growth rate</p></div>
        </div>
        <div class="ctrl-panel">
            <div class="ctrl-group"><label>Year</label><select id="rankYearSelect"></select></div>
            <div class="ctrl-group"><label>Metric</label>
                <select id="rankMetric">
                    <option value="co2">Total CO₂ Emissions</option>
                    <option value="per_capita">Per Capita CO₂</option>
                    <option value="growth">Growth Rate (%)</option>
                </select>
            </div>
            <div class="ctrl-group"><label>Show Top</label>
                <select id="topNSelect">
                    <option value="10">Top 10</option>
                    <option value="20">Top 20</option>
                    <option value="30">Top 30</option>
                    <option value="50">Top 50</option>
                </select>
            </div>
            <div class="ctrl-group"><label>&nbsp;</label><button class="btn" onclick="updateRankings()">Update →</button></div>
        </div>
        <div class="chart-card"><div id="rankingsChart" style="height:500px"></div></div>
        <div id="rankingsStats" class="metric-row"></div>
    </div>

    <!-- ALL DATA -->
    <div id="data" class="tab-content">
        <div class="section-header">
            <div class="section-icon" style="background:rgba(59,255,200,.15)">📋</div>
            <div><h2>All Data</h2><p>Search and explore complete country-level dataset</p></div>
        </div>
        <div class="search-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" placeholder="Search any country…" oninput="filterDataTable()">
        </div>
        <div class="tbl-wrap">
            <table id="dataTable">
                <thead>
                    <tr>
                        <th>#</th><th>Country</th><th>First Year</th><th>Last Year</th>
                        <th>CO₂ Change (Mt)</th><th>Change (%)</th>
                        <th>Per Capita Chg (t)</th><th>Trend</th>
                    </tr>
                </thead>
                <tbody id="dataTableBody"></tbody>
            </table>
        </div>
    </div>

</div><!-- /app-wrap -->

<script>
    /* ── DATA ─────────────────────────────────────────────────── */
    const yearlyData       = """ + json.dumps(yearly_data_js) + """;
    const raceData         = """ + json.dumps(race_data_js) + """;
    const growthRaceData   = """ + json.dumps(growth_race_data) + """;
    const comparisonData   = """ + json.dumps(comparison_data_js) + """;
    const mapData          = """ + json.dumps(map_data_js) + """;
    const sankeyData       = """ + json.dumps(sankey_data_js) + """;
    const globalStats      = """ + json.dumps(global_stats) + """;
    const regionMapping    = """ + json.dumps(region_mapping) + """;

    const allYears     = yearlyData.map(d=>d.Year).sort((a,b)=>a-b);
    const allCountries = [...new Set(comparisonData.map(d=>d.Country))].sort();

    let raceInterval  = null;
    let growthInterval = null;

    /* ── PLOTLY THEME ─────────────────────────────────────────── */
    const DARK_LAYOUT = {
        paper_bgcolor:'rgba(0,0,0,0)',
        plot_bgcolor :'rgba(0,0,0,0)',
        font: { family:"'DM Sans',sans-serif", color:'#e8ecf4', size:12 },
        xaxis: { gridcolor:'rgba(255,255,255,0.06)', zerolinecolor:'rgba(255,255,255,0.1)' },
        yaxis: { gridcolor:'rgba(255,255,255,0.06)', zerolinecolor:'rgba(255,255,255,0.1)' },
        margin: { l:130, r:30, t:60, b:50 }
    };

    const PALETTE = ['#ff6b35','#f7c948','#3bffc8','#a78bfa','#f472b6',
                     '#38bdf8','#fb923c','#34d399','#818cf8','#e879f9',
                     '#facc15','#4ade80','#60a5fa','#c084fc','#f87171'];

    const PLOTLY_CFG = { responsive:true, displayModeBar:false };

    /* ── INIT ─────────────────────────────────────────────────── */
    function init() {
        populateDropdowns();
        updateKPIs();
        updateMap();
        updateRankings();
        updateTrendAnalysis();
        updateHeatCalendar();
        updateSankeyDiagram();
        if (raceData.length)       { drawRaceChart(raceData[0]);       setupRaceSlider();       }
        if (growthRaceData.length) { drawGrowthRaceChart(growthRaceData[0]); setupGrowthRaceSlider(); }
        setupSankeySlider();
        populateDataTable();
    }

    /* ── KPIs ─────────────────────────────────────────────────── */
    function updateKPIs() {
        const latestYear = Math.max(...allYears);
        const d = yearlyData.find(d=>d.Year===latestYear);
        if (d) document.getElementById('kpi1').innerText = Math.round(d.Total_CO2).toLocaleString();
        document.getElementById('kpi2').innerText = allCountries.length;
        document.getElementById('kpi3').innerText = Math.min(...allYears)+' – '+Math.max(...allYears);
        document.getElementById('kpi4').innerText = globalStats.peak_year || '—';
    }

    /* ── DROPDOWNS ────────────────────────────────────────────── */
    function populateDropdowns() {
        const ids = ['mapYearSelect','rankYearSelect','sankeyYearSelect','heatYearStart','heatYearEnd'];
        ids.forEach(id => {
            const el = document.getElementById(id);
            allYears.forEach(y => { el.innerHTML += `<option value="${y}">${y}</option>`; });
        });
        document.getElementById('mapYearSelect').value   = allYears.at(-1);
        document.getElementById('rankYearSelect').value  = allYears.at(-1);
        document.getElementById('sankeyYearSelect').value= allYears.at(-1);
        document.getElementById('heatYearStart').value   = allYears[0];
        document.getElementById('heatYearEnd').value     = allYears.at(-1);

        ['country1Select','country2Select','trendCountrySelect','heatCountrySelect'].forEach(id => {
            const el = document.getElementById(id);
            allCountries.forEach(c => { el.innerHTML += `<option value="${c}">${c}</option>`; });
        });
        document.getElementById('country2Select').value =
            allCountries.length > 1 ? allCountries[1] : allCountries[0];
    }

    /* ── TAB SWITCH ───────────────────────────────────────────── */
    function switchTab(name) {
        [raceInterval, growthInterval].forEach(t => { if (t) clearInterval(t); });
        raceInterval = growthInterval = null;
        document.getElementById('racePlayBtn').innerText  = '▶ Start Race';
        document.getElementById('growthRacePlayBtn').innerText = '▶ Start Race';

        document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
        document.getElementById(name).classList.add('active');
        document.querySelectorAll('.tab-btn')
            .forEach(b=>{ if(b.getAttribute('onclick').includes("'"+name+"'")) b.classList.add('active'); });

        if (name==='rankings') updateRankings();
        if (name==='heatmap')  updateHeatCalendar();
        if (name==='sankey')   updateSankeyDiagram();
        if (name==='worldmap') updateMap();
        if (name==='trends')   updateTrendAnalysis();
        if (name==='compare')  updateDualComparison();
    }

    /* ── WORLD MAP ────────────────────────────────────────────── */
    function updateMap() {
        const year   = +document.getElementById('mapYearSelect').value;
        const metric = document.getElementById('mapMetricSelect').value;
        const yd     = mapData.filter(d=>d.Year===year);
        const vals   = yd.map(d=> metric==='co2' ? d.CO2_mt : d.CO2_per_capita);

        Plotly.newPlot('worldMapContainer', [{
            type:'choropleth', locationmode:'country names',
            locations: yd.map(d=>d.Country), z: vals,
            text: yd.map(d=>`<b>${d.Country}</b><br>Total: ${d.CO2_mt.toFixed(1)} Mt<br>Per Capita: ${d.CO2_per_capita.toFixed(2)} t`),
            colorscale: metric==='co2'
                ? [[0,'#0d1117'],[0.25,'#7f1d1d'],[0.5,'#dc2626'],[0.75,'#f97316'],[1,'#fde68a']]
                : [[0,'#042f2e'],[0.25,'#0f766e'],[0.5,'#14b8a6'],[0.75,'#a78bfa'],[1,'#f472b6']],
            colorbar:{ title:{ text: metric==='co2'?'Mt CO₂':'t/person', side:'right' },
                       tickfont:{color:'#6b7a99'}, titlefont:{color:'#6b7a99'} },
            marker:{ line:{ color:'rgba(255,255,255,0.08)', width:0.6 } },
            hovertemplate:'%{text}<extra></extra>'
        }], {
            ...DARK_LAYOUT,
            title:{ text:`<b>Carbon Emissions — ${year}</b>`, font:{size:18,color:'#e8ecf4'}, x:.5 },
            margin:{l:0,r:0,t:54,b:0},
            geo:{ bgcolor:'rgba(0,0,0,0)', showframe:false, showcoastlines:true,
                  coastlinecolor:'rgba(255,255,255,0.12)',
                  projection:{type:'natural earth'},
                  showland:true, landcolor:'#1a2035',
                  showocean:true, oceancolor:'#0d1422',
                  showcountries:true, countrycolor:'rgba(255,255,255,0.08)' }
        }, PLOTLY_CFG);

        document.getElementById('worldMapContainer').on('plotly_click', data=>{
            const country = data.points?.[0]?.location;
            if (!country) return;
            switchTab('trends');
            const sel = document.getElementById('trendCountrySelect');
            if ([...sel.options].some(o=>o.value===country)) {
                sel.value = country; updateTrendAnalysis();
            }
        });
    }

    /* ── RACE CHART ───────────────────────────────────────────── */
    function setupRaceSlider() {
        const s = document.getElementById('raceYearSlider');
        s.max = raceData.length-1; s.value = 0;
        document.getElementById('raceYearDisplay').innerText = raceData[0].Year;
    }
    function updateRaceYear(v) {
        const idx = +v;
        drawRaceChart(raceData[idx]);
        document.getElementById('raceYearDisplay').innerText = raceData[idx].Year;
    }
    function drawRaceChart(frame) {
        const sorted = [...frame.Data].sort((a,b)=>a.CO2_mt-b.CO2_mt);
        Plotly.newPlot('raceChart',[{
            x: sorted.map(d=>d.CO2_mt),
            y: sorted.map(d=>d.Country),
            type:'bar', orientation:'h',
            marker:{ color: sorted.map((_,i)=>PALETTE[i%PALETTE.length]),
                     line:{color:'rgba(0,0,0,0.4)',width:1} },
            text: sorted.map(d=>d.CO2_mt.toFixed(1)+' Mt'),
            textposition:'outside',
            textfont:{ color:'#6b7a99', size:11 }
        }],{
            ...DARK_LAYOUT,
            title:{ text:`<b>Top 15 CO₂ Emitters — ${frame.Year}</b>`,
                    font:{size:18,color:'#e8ecf4'}, x:.5 },
            xaxis:{ ...DARK_LAYOUT.xaxis, title:'Million Tonnes CO₂',
                    range:[0, sorted.at(-1)?.CO2_mt*1.25||100] },
            yaxis:{ ...DARK_LAYOUT.yaxis, automargin:true }
        }, PLOTLY_CFG);
    }
    function startRaceAnimation() {
        if (raceInterval) { clearInterval(raceInterval); raceInterval=null;
            document.getElementById('racePlayBtn').innerText='▶ Start Race'; return; }
        let idx = +document.getElementById('raceYearSlider').value;
        const speed = +document.getElementById('animationSpeed').value;
        document.getElementById('racePlayBtn').innerText = '⏸ Pause';
        function step() {
            if (idx >= raceData.length) { clearInterval(raceInterval); raceInterval=null;
                document.getElementById('racePlayBtn').innerText='▶ Start Race'; return; }
            drawRaceChart(raceData[idx]);
            document.getElementById('raceYearSlider').value = idx;
            document.getElementById('raceYearDisplay').innerText = raceData[idx].Year;
            idx++;
        }
        step(); raceInterval = setInterval(step, speed);
    }
    function resetRaceAnimation() {
        if (raceInterval) { clearInterval(raceInterval); raceInterval=null; }
        drawRaceChart(raceData[0]);
        document.getElementById('raceYearSlider').value = 0;
        document.getElementById('raceYearDisplay').innerText = raceData[0].Year;
        document.getElementById('racePlayBtn').innerText = '▶ Start Race';
    }

    /* ── GROWTH RACE ──────────────────────────────────────────── */
    function setupGrowthRaceSlider() {
        const s = document.getElementById('growthYearSlider');
        s.max = growthRaceData.length-1; s.value=0;
        document.getElementById('growthYearDisplay').innerText = growthRaceData[0].Year;
    }
    function updateGrowthYear(v) {
        const idx=+v; drawGrowthRaceChart(growthRaceData[idx]);
        document.getElementById('growthYearDisplay').innerText = growthRaceData[idx].Year;
    }
    function drawGrowthRaceChart(frame) {
        const sorted=[...frame.Data].sort((a,b)=>a.Growth_Rate-b.Growth_Rate);
        Plotly.newPlot('growthRaceChart',[{
            x: sorted.map(d=>d.Growth_Rate),
            y: sorted.map(d=>d.Country),
            type:'bar', orientation:'h',
            marker:{ color:sorted.map(d=>d.Growth_Rate>=0?'#ff6b35':'#3bffc8'),
                     opacity:.85, line:{color:'rgba(0,0,0,0.3)',width:1} },
            text: sorted.map(d=>(d.Growth_Rate>=0?'+':'')+d.Growth_Rate.toFixed(1)+'%'),
            textposition:'outside', textfont:{color:'#6b7a99',size:11}
        }],{
            ...DARK_LAYOUT,
            title:{ text:`<b>Fastest Growing Emissions — ${frame.Year}</b>`,
                    font:{size:18,color:'#e8ecf4'}, x:.5 },
            xaxis:{ ...DARK_LAYOUT.xaxis, title:'Year-on-Year Growth Rate (%)' },
            yaxis:{ ...DARK_LAYOUT.yaxis, automargin:true }
        }, PLOTLY_CFG);
    }
    function startGrowthRaceAnimation() {
        if (growthInterval) { clearInterval(growthInterval); growthInterval=null;
            document.getElementById('growthRacePlayBtn').innerText='▶ Start Race'; return; }
        let idx=+document.getElementById('growthYearSlider').value;
        const speed=+document.getElementById('growthSpeed').value;
        document.getElementById('growthRacePlayBtn').innerText='⏸ Pause';
        function step() {
            if (idx>=growthRaceData.length) { clearInterval(growthInterval); growthInterval=null;
                document.getElementById('growthRacePlayBtn').innerText='▶ Start Race'; return; }
            drawGrowthRaceChart(growthRaceData[idx]);
            document.getElementById('growthYearSlider').value=idx;
            document.getElementById('growthYearDisplay').innerText=growthRaceData[idx].Year;
            idx++;
        }
        step(); growthInterval=setInterval(step,speed);
    }
    function resetGrowthRaceAnimation() {
        if (growthInterval) { clearInterval(growthInterval); growthInterval=null; }
        drawGrowthRaceChart(growthRaceData[0]);
        document.getElementById('growthYearSlider').value=0;
        document.getElementById('growthYearDisplay').innerText=growthRaceData[0].Year;
        document.getElementById('growthRacePlayBtn').innerText='▶ Start Race';
    }

    /* ── DUAL COMPARE ─────────────────────────────────────────── */
    function updateDualComparison() {
        const c1 = document.getElementById('country1Select').value;
        const c2 = document.getElementById('country2Select').value;
        const d1 = comparisonData.find(d=>d.Country===c1);
        const d2 = comparisonData.find(d=>d.Country===c2);
        if (!d1||!d2) return;

        Plotly.newPlot('dualComparisonChart',[
            { x:d1.Years, y:d1.CO2, type:'scatter', mode:'lines+markers', name:c1,
              line:{color:'#ff6b35',width:3}, marker:{size:7,color:'#ff6b35',
              line:{color:'#fff',width:1.5}} },
            { x:d2.Years, y:d2.CO2, type:'scatter', mode:'lines+markers', name:c2,
              line:{color:'#3bffc8',width:3}, marker:{size:7,color:'#3bffc8',
              line:{color:'#fff',width:1.5}} }
        ], {
            ...DARK_LAYOUT,
            title:{ text:`<b>${c1}</b> vs <b>${c2}</b> — CO₂ Emissions`,
                    font:{size:17,color:'#e8ecf4'}, x:.5 },
            xaxis:{ ...DARK_LAYOUT.xaxis, title:'Year' },
            yaxis:{ ...DARK_LAYOUT.yaxis, title:'Million Tonnes CO₂' },
            hovermode:'x unified',
            legend:{ bgcolor:'rgba(0,0,0,0)', bordercolor:'rgba(255,255,255,.1)',
                     borderwidth:1, font:{color:'#e8ecf4'} }
        }, PLOTLY_CFG);

        const statsEl = document.getElementById('dualComparisonStats');
        statsEl.style.display='block';
        const sign = v => v>0?'+':'';
        const cls  = v => v>0?'up':'down';
        statsEl.innerHTML = `
        <h3>Detailed Comparison</h3>
        <div class="cmp-grid">
            <div class="cmp-metric"><div class="cv ${cls(d1.CO2_Change)}">${sign(d1.CO2_Change)}${d1.CO2_Change.toFixed(1)} Mt</div><div class="cl">${c1} — CO₂ Change</div></div>
            <div class="cmp-metric"><div class="cv ${cls(d2.CO2_Change)}">${sign(d2.CO2_Change)}${d2.CO2_Change.toFixed(1)} Mt</div><div class="cl">${c2} — CO₂ Change</div></div>
            <div class="cmp-metric"><div class="cv ${cls(d1.CO2_Pct_Change)}">${sign(d1.CO2_Pct_Change)}${d1.CO2_Pct_Change.toFixed(1)}%</div><div class="cl">${c1} — Growth Rate</div></div>
            <div class="cmp-metric"><div class="cv ${cls(d2.CO2_Pct_Change)}">${sign(d2.CO2_Pct_Change)}${d2.CO2_Pct_Change.toFixed(1)}%</div><div class="cl">${c2} — Growth Rate</div></div>
            <div class="cmp-metric"><div class="cv">${d1.Last_Per_Capita.toFixed(2)} t</div><div class="cl">${c1} — Latest Per Capita</div></div>
            <div class="cmp-metric"><div class="cv">${d2.Last_Per_Capita.toFixed(2)} t</div><div class="cl">${c2} — Latest Per Capita</div></div>
        </div>`;
    }

    /* ── TREND ANALYSIS ───────────────────────────────────────── */
    function updateTrendAnalysis() {
        const country = document.getElementById('trendCountrySelect').value;
        const d = comparisonData.find(x=>x.Country===country);
        if (!d) return;

        const n=d.Years.length, sx=d.Years.reduce((a,b)=>a+b,0), sy=d.CO2.reduce((a,b)=>a+b,0);
        const sxy=d.Years.reduce((s,x,i)=>s+x*d.CO2[i],0), sx2=d.Years.reduce((s,x)=>s+x*x,0);
        const slope=(n*sxy-sx*sy)/(n*sx2-sx*sx), intercept=(sy-slope*sx)/n;
        const trend=d.Years.map(x=>slope*x+intercept);
        const ma=d.CO2.map((_,i)=> i===0||i===d.CO2.length-1?d.CO2[i]:(d.CO2[i-1]+d.CO2[i]+d.CO2[i+1])/3);

        Plotly.newPlot('trendChart',[
            { x:d.Years, y:d.CO2, type:'scatter', mode:'lines+markers', name:'Actual',
              line:{color:'#f7c948',width:2.5}, marker:{size:6,color:'#f7c948',
              line:{color:'rgba(0,0,0,0.4)',width:1}},
              fill:'tozeroy', fillcolor:'rgba(247,201,72,0.07)' },
            { x:d.Years, y:trend, type:'scatter', mode:'lines', name:'Trend',
              line:{color:'#ff6b35',width:2.5,dash:'dash'} },
            { x:d.Years, y:ma, type:'scatter', mode:'lines', name:'3-yr MA',
              line:{color:'#3bffc8',width:2} }
        ],{
            ...DARK_LAYOUT,
            title:{ text:`<b>${country}</b> — Trend Analysis`,
                    font:{size:17,color:'#e8ecf4'}, x:.5 },
            xaxis:{ ...DARK_LAYOUT.xaxis, title:'Year' },
            yaxis:{ ...DARK_LAYOUT.yaxis, title:'Million Tonnes CO₂' },
            hovermode:'x unified',
            legend:{ bgcolor:'rgba(0,0,0,0)',bordercolor:'rgba(255,255,255,.1)',
                     borderwidth:1,font:{color:'#e8ecf4'} }
        }, PLOTLY_CFG);

        const s=v=>(v>0?'+':'')+v.toFixed(1);
        document.getElementById('trendStats').innerHTML = `
        <div class="metric-card c1"><div class="m-label">Total Change (${d.First_Year}–${d.Last_Year})</div>
            <div class="m-value ${d.CO2_Change>0?'up':'down'}">${s(d.CO2_Change)} Mt</div></div>
        <div class="metric-card c2"><div class="m-label">Overall Change %</div>
            <div class="m-value ${d.CO2_Pct_Change>0?'up':'down'}">${s(d.CO2_Pct_Change)}%</div></div>
        <div class="metric-card c3"><div class="m-label">Trend Direction</div>
            <div class="m-value" style="font-size:1.3rem">${slope>0?'↑ Rising':'↓ Falling'}</div></div>
        <div class="metric-card c4"><div class="m-label">Latest Per Capita</div>
            <div class="m-value">${d.Last_Per_Capita.toFixed(2)} t</div></div>`;
    }

    /* ── HEAT CALENDAR ────────────────────────────────────────── */
    function updateHeatCalendar() {
        const country = document.getElementById('heatCountrySelect').value;
        const y0 = +document.getElementById('heatYearStart').value;
        const y1 = +document.getElementById('heatYearEnd').value;
        const d  = comparisonData.find(x=>x.Country===country);
        if (!d) return;

        const years = d.Years.filter(y=>y>=y0&&y<=y1);
        const vals  = d.CO2.filter((_,i)=>d.Years[i]>=y0&&d.Years[i]<=y1);
        const z     = years.map(()=>vals);

        Plotly.newPlot('heatCalendarChart',[{
            z, x:years, y:years, type:'heatmap',
            colorscale:[[0,'#042f2e'],[0.25,'#065f46'],[0.5,'#f59e0b'],[0.75,'#dc2626'],[1,'#fde68a']],
            showscale:true,
            colorbar:{ title:{text:'CO₂ (Mt)',side:'right'},
                       tickfont:{color:'#6b7a99'}, titlefont:{color:'#6b7a99'} },
            hovertemplate:'Year: %{x}<br>Emissions: %{z:.1f} Mt<extra></extra>'
        }],{
            ...DARK_LAYOUT,
            title:{ text:`<b>${country}</b> — Emissions Heat Calendar`,
                    font:{size:17,color:'#e8ecf4'}, x:.5 },
            xaxis:{ ...DARK_LAYOUT.xaxis, title:'Year', tickangle:-45 },
            yaxis:{ ...DARK_LAYOUT.yaxis, title:'Year', autorange:'reversed' },
            margin:{l:80,r:40,t:60,b:80}
        }, PLOTLY_CFG);
    }

    /* ── SANKEY ───────────────────────────────────────────────── */
    function setupSankeySlider() {
        const s=document.getElementById('sankeyYearSlider');
        s.max=sankeyData.length-1; s.value=sankeyData.length-1;
        if (sankeyData.length) {
            document.getElementById('sankeyYearDisplay').innerText=sankeyData.at(-1).Year;
            drawSankeyChart(sankeyData.at(-1));
        }
    }
    function updateSankeyYear(v) {
        const idx=+v; drawSankeyChart(sankeyData[idx]);
        document.getElementById('sankeyYearDisplay').innerText=sankeyData[idx].Year;
        document.getElementById('sankeyYearSelect').value=sankeyData[idx].Year;
    }
    function updateSankeyDiagram() {
        const year=+document.getElementById('sankeyYearSelect').value;
        const d=sankeyData.find(x=>x.Year===year);
        if (!d) return;
        drawSankeyChart(d);
        const idx=sankeyData.findIndex(x=>x.Year===year);
        document.getElementById('sankeyYearSlider').value=idx;
        document.getElementById('sankeyYearDisplay').innerText=year;
    }
    const rcMap={};
    Object.entries(regionMapping).forEach(([r,cs])=>cs.forEach(c=>rcMap[c]=r));

    function drawSankeyChart(frame) {
        const regions=Object.keys(frame.Regions);
        const emitters=frame.TopEmitters;
        const nodes=['Global',...regions,...emitters.map(e=>e.Country)];
        const ni={};nodes.forEach((n,i)=>ni[n]=i);
        const src=[],tgt=[],val=[],lc=[];
        const nodeColors=['#f7c948',...regions.map((_,i)=>PALETTE[i+1]),
                          ...emitters.map((_,i)=>PALETTE[i%PALETTE.length])];

        regions.forEach(r=>{
            const v=frame.Regions[r];
            if (v>0){ src.push(ni['Global']); tgt.push(ni[r]); val.push(v);
                      lc.push('rgba(247,201,72,0.25)'); }
        });
        emitters.forEach(e=>{
            const r=rcMap[e.Country]||'Other';
            if (ni[r]!==undefined) {
                src.push(ni[r]); tgt.push(ni[e.Country]); val.push(e.CO2_mt);
                lc.push('rgba(255,107,53,0.2)');
            }
        });

        Plotly.newPlot('sankeyChart',[{
            type:'sankey', orientation:'h',
            node:{ pad:18, thickness:22,
                   line:{color:'rgba(255,255,255,0.1)',width:0.5},
                   label:nodes,
                   color:nodeColors.map(c=>c||'#a78bfa'),
                   font:{color:'#e8ecf4',size:11} },
            link:{ source:src, target:tgt, value:val, color:lc }
        }],{
            ...DARK_LAYOUT,
            title:{ text:`<b>Emissions Flow — ${frame.Year}</b>`,
                    font:{size:17,color:'#e8ecf4'}, x:.5 },
            margin:{l:20,r:20,t:60,b:20},
            font:{color:'#e8ecf4',size:11}
        }, PLOTLY_CFG);
    }

    /* ── RANKINGS ─────────────────────────────────────────────── */
    function updateRankings() {
        const year   = +document.getElementById('rankYearSelect').value;
        const metric = document.getElementById('rankMetric').value;
        const topN   = +document.getElementById('topNSelect').value;

        let sorted;
        if (metric==='co2')
            sorted = [...comparisonData].sort((a,b)=>b.Last_CO2-a.Last_CO2);
        else if (metric==='per_capita')
            sorted = [...comparisonData].sort((a,b)=>b.Last_Per_Capita-a.Last_Per_Capita);
        else
            sorted = [...comparisonData].sort((a,b)=>b.CO2_Pct_Change-a.CO2_Pct_Change);

        const top    = sorted.slice(0,topN);
        const vals   = top.map(d=> metric==='co2'?d.Last_CO2: metric==='per_capita'?d.Last_Per_Capita:d.CO2_Pct_Change);
        const names  = top.map(d=>d.Country);
        const colors = vals.map((v,i)=>`hsl(${20+i*(280/topN)},80%,55%)`);

        const unitLabel = metric==='co2'?'Million Tonnes CO₂': metric==='per_capita'?'Tonnes / Capita':'Growth Rate (%)';

        Plotly.newPlot('rankingsChart',[{
            x:vals, y:names, type:'bar', orientation:'h',
            marker:{ color:colors, opacity:.85,
                     line:{color:'rgba(0,0,0,0.3)',width:0.8} },
            text:vals.map(v=>v.toFixed(1)), textposition:'outside',
            textfont:{color:'#6b7a99',size:11}
        }],{
            ...DARK_LAYOUT,
            title:{ text:`<b>Top ${topN} Countries by ${unitLabel}</b>`,
                    font:{size:16,color:'#e8ecf4'}, x:.5 },
            xaxis:{ ...DARK_LAYOUT.xaxis, title:unitLabel },
            yaxis:{ ...DARK_LAYOUT.yaxis, automargin:true },
            height: Math.max(400, topN*34),
            margin:{ l:150,r:60,t:60,b:50 }
        }, PLOTLY_CFG);

        document.getElementById('rankingsStats').innerHTML = `
        <div class="metric-card c1"><div class="m-label">Top Country</div>
            <div class="m-value" style="font-size:1.1rem">${names[0]||'—'}</div></div>
        <div class="metric-card c2"><div class="m-label">Top Value</div>
            <div class="m-value">${vals[0]?.toFixed(1)||'—'}</div></div>
        <div class="metric-card c3"><div class="m-label">Countries Analysed</div>
            <div class="m-value">${sorted.length}</div></div>`;
    }

    /* ── DATA TABLE ───────────────────────────────────────────── */
    function populateDataTable() {
        const tbody = document.getElementById('dataTableBody');
        tbody.innerHTML='';
        comparisonData.forEach((d,i)=>{
            const up = d.CO2_Pct_Change>0;
            const row = tbody.insertRow();
            row.innerHTML = `
                <td><span class="rank-pill">${i+1}</span></td>
                <td><b>${d.Country}</b></td>
                <td>${d.First_Year}</td>
                <td>${d.Last_Year}</td>
                <td class="${up?'badge-up':'badge-down'}">${up?'+':''}${d.CO2_Change.toFixed(1)}</td>
                <td class="${up?'badge-up':'badge-down'}">${up?'+':''}${d.CO2_Pct_Change.toFixed(1)}%</td>
                <td>${d.Per_Capita_Change>0?'+':''}${d.Per_Capita_Change.toFixed(2)}</td>
                <td>${up?'↑ Rising':'↓ Falling'}</td>`;
            row.onclick=()=>{
                switchTab('trends');
                const s=document.getElementById('trendCountrySelect');
                if([...s.options].some(o=>o.value===d.Country)){
                    s.value=d.Country; updateTrendAnalysis();
                }
            };
        });
    }
    function filterDataTable() {
        const q = document.getElementById('searchInput').value.toLowerCase();
        [...document.getElementById('dataTableBody').rows]
            .forEach(r=>{ r.style.display=r.textContent.toLowerCase().includes(q)?'':'none'; });
    }

    init();
</script>
</body>
</html>"""

output_path = "carbon_emissions_upgraded_dashboard.html"
with open(output_path, "w", encoding='utf-8') as f:
    f.write(html_content)

comparison_df = pd.DataFrame(comparison_data_js)
comparison_df.to_csv('ultimate_emissions_comparison.csv', index=False)

print(f"\n✅ UPGRADED DASHBOARD → {output_path}")
print("✅ Comparison data   → ultimate_emissions_comparison.csv")
print("\n🎨 VISUAL UPGRADES APPLIED:")
print("   • Deep dark theme — near-black surface, grid texture background")
print("   • Syne + DM Sans font pairing — editorial, distinctive")
print("   • Vivid accent palette: flame orange, golden yellow, teal, violet, pink")
print("   • Glow KPI cards with per-card top-border gradient & hover box-shadow")
print("   • Pill-style tab bar with gradient active state + glow")
print("   • All charts: transparent backgrounds matched to dark theme")
print("   • Custom map colorscale: dark navy → red → amber")
print("   • Sankey: coloured nodes, translucent amber/coral links")
print("   • Bar races: per-country PALETTE colours, dark plot bg")
print("   • Trend chart: area fill under actual line, tri-colour legend")
print("   • Heat calendar: teal-to-amber-to-red scale")
print("   • Rankings: HSL rainbow gradient across bars")
print("   • Table: dark rows, orange rank pills, colour-coded rise/fall badges")
print("   • Animated hero badge pulse, tab fade-in, card hover lifts")