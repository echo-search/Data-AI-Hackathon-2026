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
print("🚀 CREATING ULTIMATE CARBON EMISSIONS DASHBOARD — MARCH 2026 EDITION")
print("="*90)

# ─── DATA LOADING ────────────────────────────────────────────────────────────
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

# ─── DATA PREPARATION ────────────────────────────────────────────────────────
available_years = sorted(df['Year'].dropna().unique())
available_years = [int(y) for y in available_years if y <= 2023]
latest_year = int(available_years[-1]) if available_years else 2023
earliest_year = int(available_years[0]) if available_years else 1990
countries = sorted(df['Country'].dropna().unique())

print(f"\n📊 Data Overview: Years {earliest_year}-{latest_year} | {len(countries)} Countries | {len(df)} Records")

# Region mapping (flat: country -> region, for JS regionMap)
region_mapping_flat = {}
region_groups = {
    'North America': ['United States', 'Canada', 'Mexico'],
    'Europe': ['Germany', 'United Kingdom', 'France', 'Italy', 'Spain', 'Poland', 'Netherlands', 'Turkey', 'Ukraine', 'Russia',
               'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland',
               'Greece', 'Hungary', 'Iceland', 'Ireland', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Norway', 'Portugal',
               'Romania', 'Slovakia', 'Slovenia', 'Sweden', 'Switzerland', 'Belarus', 'Montenegro', 'North Macedonia',
               'Albania', 'Bosnia and Herzegovina', 'Moldova', 'Serbia', 'Liechtenstein', 'Monaco', 'San Marino', 'Andorra'],
    'Asia': ['China', 'India', 'Japan', 'South Korea', 'Indonesia', 'Iran', 'Thailand', 'Vietnam', 'Malaysia', 'Pakistan',
             'Bangladesh', 'Myanmar', 'Nepal', 'Sri Lanka', 'Afghanistan', 'Kazakhstan', 'Uzbekistan', 'Iraq', 'Saudi Arabia',
             'Yemen', 'Syria', 'Jordan', 'Lebanon', 'Israel', 'Palestine', 'Georgia', 'Armenia', 'Azerbaijan', 'Mongolia',
             'North Korea', 'Taiwan', 'Philippines', 'Cambodia', 'Laos', 'Singapore', 'Brunei', 'Timor-Leste', 'Bhutan',
             'Maldives', 'Kyrgyzstan', 'Tajikistan', 'Turkmenistan', 'Kuwait', 'Qatar', 'United Arab Emirates', 'Bahrain', 'Oman'],
    'South America': ['Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay', 'Uruguay',
                      'Guyana', 'Suriname', 'Trinidad and Tobago'],
    'Africa': ['South Africa', 'Nigeria', 'Egypt', 'Algeria', 'Morocco', 'Angola', 'Kenya', 'Ethiopia', 'Ghana', 'Tanzania',
               'Sudan', 'Uganda', 'Mozambique', 'Madagascar', 'Cameroon', 'Côte d\'Ivoire', 'Niger', 'Burkina Faso', 'Mali',
               'Malawi', 'Zambia', 'Senegal', 'Chad', 'Somalia', 'Zimbabwe', 'Guinea', 'Rwanda', 'Benin', 'Burundi', 'Tunisia',
               'South Sudan', 'Togo', 'Eritrea', 'Sierra Leone', 'Liberia', 'Central African Republic', 'Mauritania', 'Congo',
               'Libya', 'Gabon', 'Equatorial Guinea', 'Botswana', 'Namibia', 'Lesotho', 'Eswatini', 'Djibouti', 'Comoros',
               'Cabo Verde', 'Sao Tome and Principe', 'Seychelles', 'Mauritius', 'Gambia', 'Guinea-Bissau'],
    'Oceania': ['Australia', 'New Zealand', 'Papua New Guinea', 'Fiji', 'Solomon Islands', 'Vanuatu', 'Samoa', 'Kiribati',
                'Micronesia', 'Tonga', 'Palau', 'Marshall Islands', 'Tuvalu', 'Nauru'],
    'Other': []
}
for region, clist in region_groups.items():
    for c in clist:
        region_mapping_flat[c] = region

df['Region'] = df['Country'].map(region_mapping_flat).fillna('Other')

# Yearly aggregated totals
yearly_aggregated = df.groupby('Year').agg({'CO2_mt': 'sum', 'Population_thousands': 'sum'}).reset_index()
yearly_aggregated['CO2_per_capita'] = (yearly_aggregated['CO2_mt'] * 1_000_000) / (yearly_aggregated['Population_thousands'] * 1000)
yearly_aggregated['Year'] = yearly_aggregated['Year'].astype(int)

# yearlyTotals for JS (used by updateKPIs)
yearly_totals_js = [
    {
        'Year': int(r['Year']),
        'Total_CO2': float(r['CO2_mt']),
        'Per_Capita': float(r['CO2_per_capita'])
    }
    for _, r in yearly_aggregated.iterrows()
]

# compData — per-country time series + summary stats
comp_data_js = []
country_time_series = {}
for country in countries:
    cdf = df[df['Country'] == country].sort_values('Year')
    if len(cdf) < 2:
        continue
    yrs = [int(y) for y in cdf['Year'].tolist()]
    co2 = [float(v) for v in cdf['CO2_mt'].tolist()]
    pc  = [float(v) for v in cdf['CO2_per_capita'].tolist()]
    country_time_series[country] = {'years': yrs, 'co2': co2, 'pc': pc}
    comp_data_js.append({
        'Country': country,
        'Years': yrs,
        'CO2': co2,
        'PerCapita': pc,
        'First_Year': yrs[0],
        'Last_Year': yrs[-1],
        'First_CO2': co2[0],
        'Last_CO2': co2[-1],
        'CO2_Change': co2[-1] - co2[0],
        'CO2_Pct_Change': ((co2[-1] - co2[0]) / co2[0] * 100) if co2[0] > 0 else 0,
        'First_Per_Capita': pc[0],
        'Last_Per_Capita': pc[-1],
        'Per_Capita_Change': pc[-1] - pc[0],
        'Per_Capita_Pct_Change': ((pc[-1] - pc[0]) / pc[0] * 100) if pc[0] > 0 else 0,
    })

# mapData — all country-year records
map_data_js = [
    {
        'Country': str(r['Country']),
        'Year': int(r['Year']),
        'CO2_mt': float(r['CO2_mt']),
        'CO2_per_capita': float(r['CO2_per_capita'])
    }
    for _, r in df.iterrows()
    if int(r['Year']) in available_years
]

# raceData — top N emitters per year (sorted desc, all countries kept)
race_data_js = []
for year in available_years:
    year_rows = [d for d in map_data_js if d['Year'] == year]
    sorted_rows = sorted(year_rows, key=lambda x: x['CO2_mt'], reverse=True)
    race_data_js.append({
        'Year': year,
        'Data': [{'Country': d['Country'], 'CO2_mt': d['CO2_mt'], 'CO2_per_capita': d['CO2_per_capita']} for d in sorted_rows]
    })

# growthRaceData — year-on-year growth for all countries
country_yearly_data = {}
for entry in map_data_js:
    c = entry['Country']
    if c not in country_yearly_data:
        country_yearly_data[c] = {}
    country_yearly_data[c][entry['Year']] = entry['CO2_mt']

growth_race_data_js = []
for year in available_years[1:]:
    prev_year = year - 1
    frame_data = []
    for country in countries:
        cy = country_yearly_data.get(country, {})
        if year in cy and prev_year in cy and cy[prev_year] > 0:
            gr = (cy[year] - cy[prev_year]) / cy[prev_year] * 100
            frame_data.append({'Country': country, 'Growth_Rate': float(gr), 'CO2_mt': float(cy[year])})
    growth_race_data_js.append({'Year': year, 'Data': frame_data})

# sankeyData — Global -> Region -> Top Emitters per year
sankey_data_js = []
for year in available_years:
    year_rows = [d for d in map_data_js if d['Year'] == year]
    top_emitters = sorted(year_rows, key=lambda x: x['CO2_mt'], reverse=True)[:15]
    region_totals = {}
    for e in top_emitters:
        region = region_mapping_flat.get(e['Country'], 'Other')
        region_totals[region] = region_totals.get(region, 0) + e['CO2_mt']
    sankey_data_js.append({
        'Year': year,
        'Regions': region_totals,
        'TopEmitters': [{'Country': e['Country'], 'CO2_mt': e['CO2_mt']} for e in top_emitters]
    })

# globalStats
peak_row = yearly_aggregated.loc[yearly_aggregated['CO2_mt'].idxmax()]
global_stats_js = {
    'peak_year': int(peak_row['Year']),
    'total_countries': int(len(countries))
}

all_years_js = available_years
all_countries_js = sorted([d['Country'] for d in comp_data_js])

print("✅ Data preparation complete!")
print(f"   compData: {len(comp_data_js)} countries")
print(f"   mapData: {len(map_data_js)} records")
print(f"   raceData: {len(race_data_js)} frames")
print(f"   growthRaceData: {len(growth_race_data_js)} frames")
print(f"   sankeyData: {len(sankey_data_js)} frames")

# ─── HTML DASHBOARD ───────────────────────────────────────────────────────────
# Build the Python-injected data block that replaces the JS generateData() IIFE.
# All other HTML/CSS/JS from the updated dashboard is preserved exactly.

python_data_injection = """
/* ════════════════════════════════════════
   PYTHON-INJECTED DATA (replaces synthetic generateData)
   Generated by claud.py on """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """
════════════════════════════════════════ */
window.ALL_YEARS = """ + json.dumps(all_years_js) + """;
window.ALL_COUNTRIES = """ + json.dumps(all_countries_js) + """;
window.DATA = {
  compData:      """ + json.dumps(comp_data_js) + """,
  mapData:       """ + json.dumps(map_data_js) + """,
  raceData:      """ + json.dumps(race_data_js) + """,
  growthRaceData:""" + json.dumps(growth_race_data_js) + """,
  sankeyData:    """ + json.dumps(sankey_data_js) + """,
  yearlyTotals:  """ + json.dumps(yearly_totals_js) + """,
  regionMap:     """ + json.dumps(region_mapping_flat) + """,
  globalStats:   """ + json.dumps(global_stats_js) + """
};
"""

# Read the updated HTML template
with open('updated_dashboard_31-3-2026.html', 'r', encoding='utf-8') as f:
    html_template = f.read()

# Replace the generateData IIFE with Python-injected data.
# The IIFE runs from (function generateData(){ to the closing })();
gen_start = html_template.find('(function generateData(){')
gen_end_marker = '})();\n\n/* ════ COLOR PALETTE'
gen_end_pos = html_template.find(gen_end_marker)
if gen_start != -1 and gen_end_pos != -1:
    # Find the exact end of the IIFE (the }) line)
    iife_close = html_template.find('})();', gen_end_pos) + len('})();')
    html_content = html_template[:gen_start] + python_data_injection + html_template[iife_close:]
    print("✅ Replaced generateData() IIFE with Python-injected data")
else:
    # Fallback: inject before first <script> closing tag section
    html_content = html_template
    print("⚠️ Could not locate generateData IIFE — using template as-is")

# ─── OUTPUT ───────────────────────────────────────────────────────────────────
output_path = "carbon_emissions_dashboard_2026.html"
with open(output_path, "w", encoding='utf-8') as f:
    f.write(html_content)

# Also export comparison data as CSV
comparison_df = pd.DataFrame([{
    'Country': d['Country'],
    'First_Year': d['First_Year'],
    'Last_Year': d['Last_Year'],
    'CO2_Change_Mt': round(d['CO2_Change'], 2),
    'CO2_Pct_Change': round(d['CO2_Pct_Change'], 2),
    'Last_CO2_Mt': round(d['Last_CO2'], 2),
    'Last_Per_Capita_t': round(d['Last_Per_Capita'], 3),
} for d in comp_data_js])
comparison_df.to_csv('ultimate_emissions_comparison.csv', index=False)

print(f"\n✅ UPGRADED DASHBOARD → {output_path}")
print("✅ Comparison data   → ultimate_emissions_comparison.csv")
print("\n🎨 NEW FEATURES IN THIS EDITION (updated_dashboard_31-3-2026.html):")
print("   • 🌗 Dark / Light theme toggle — persistent across all tabs")
print("   • 🌍 Animated World Map — auto-plays with ▶/⏸/⏮/⏭ controls + progress bar")
print("   • 🔵 Bubble map mode — country-color bubbles sized by emissions")
print("   • 🎨 Consistent per-country colors (MASTER_PALETTE locked to each country)")
print("   • 💬 Rich hover tooltip — sparkline, rank badge, YoY %, region, global share")
print("   • 👁 At a Glance tab — card grid for every country, sortable & filterable")
print("   • 👣 Carbon Footprint tab — SVG footprint, 2007→2023 rank shift, animated treemap")
print("   • 📊 Improvers vs Worseners — top 10 countries that improved / worsened since 2007")
print("   • 🏁 Bar Races — all countries, configurable Top N (15/25/50/All)")
print("   • 📏 Dynamic chart height — scales with number of countries shown")
print("   • 🖱 Click-anywhere-to-trends — every chart navigates to Trend Analysis on click")
print("   • ✨ Smoother animations — Plotly.react() for incremental updates")
print("   • Refined CSS: CSS variable theming, dual :root selectors, sharper spacing")