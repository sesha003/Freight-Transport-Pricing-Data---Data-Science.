"""
Analyze Source_State & Destination_State columns in Transport_Market_Price.xlsx
to find city names used instead of valid Indian state names,
and generate a premium dark-themed chart.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import sys

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

matplotlib.rcParams['font.family'] = 'Segoe UI'

# ──────────────────────────────────────────────────────────────────────────
# 1. OFFICIAL INDIAN STATES & UNION TERRITORIES (normalized to lowercase)
# ──────────────────────────────────────────────────────────────────────────
VALID_STATES = {
    'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar',
    'chhattisgarh', 'goa', 'gujarat', 'haryana', 'himachal pradesh',
    'jharkhand', 'karnataka', 'kerala', 'madhya pradesh', 'maharashtra',
    'manipur', 'meghalaya', 'mizoram', 'nagaland', 'odisha',
    'punjab', 'rajasthan', 'sikkim', 'tamil nadu', 'telangana',
    'tripura', 'uttar pradesh', 'uttarakhand', 'west bengal',
    # Union Territories
    'andaman and nicobar islands', 'chandigarh', 'dadra and nagar haveli',
    'dadra and nagar haveli and daman and diu', 'daman and diu',
    'delhi', 'jammu and kashmir', 'jammu & kashmir', 'ladakh',
    'lakshadweep', 'puducherry',
}

# Common misspellings / abbreviations that are still STATES (not cities)
STATE_ALIASES = {
    # Misspellings
    'gujrat', 'gujjrat', 'gujatat', 'rajsthan', 'rajsthn',
    'chhatisgarh', 'chattisgarh', 'chhatishgarh',
    'andhrapradesh', 'madhyapradesh', 'uttarpradesh', 'maharastra',
    'madhypradesh', 'utter pardesh', 'uttarkhand', 'maharsthra',
    'telengana', 'tamilnadu', 'harayana',
    'uttrakhand', 'uttara khand', 'uttat pradesh',
    'madhayapradesh', 'madhy pradesh', 'madhya pradsh', 'madhya predesh',
    'karataka', 'karantaka', 'karnat', 'kerela',
    'aasam', 'orissa', 'odhisa',
    'panjab', 'punajb', 'punjub',
    'himichal pradesh',
    'jharkahnd', 'jharkahnd',
    'west bangal',
    # Abbreviations
    'j&k', 'jk', 'up', 'mp', 'm.p', 'wb', 'mh', 'cg', 'gj', 'hr',
    'rj', 'r.j.', 'ka', 'k.a', 'br', 'tn', 'kl01', 'k.l', 'del',
    'jammu & kashimir', 'jammu & kasmir', 'jammu kashmir', 'jammu @ kashmir',
    'kashmir',
    # Other state-level references
    'jammu', 'himachal', 'pondicherry', 'nepal',
    'haryana|',
}

# Entries that are neither states nor cities (junk / other data)
JUNK_VALUES = {
    'metric tonnes (mt)', 'direct party',
    # Codes / IDs
    'hu0245', 'hu0259', 'hu0266', 'hu0271', 'hu0274', 'hu0286', 'hu0292',
    'hgl005',
    # Compound entries like "Samastipur, Bihar, India"
}

# ──────────────────────────────────────────────────────────────────────────
# 2. LOAD DATA
# ──────────────────────────────────────────────────────────────────────────
print("Loading Excel file (this may take a minute for ~50MB)...")
file_path = r"D:\HFU UNI Project\DS-Project HFU\Raw Data\Transport_Market_Price.xlsx"
df = pd.read_excel(file_path, usecols=['Source_State', 'Destination_State'])
print(f"Loaded {len(df):,} rows.\n")

# ──────────────────────────────────────────────────────────────────────────
# 3. CLASSIFY each unique value in both state columns
# ──────────────────────────────────────────────────────────────────────────
def classify_value(val):
    """Return 'state', 'city', or 'junk'."""
    if pd.isna(val):
        return 'junk'
    cleaned = str(val).strip().lower().replace('\xa0', '').rstrip('|')
    if cleaned in VALID_STATES or cleaned in STATE_ALIASES:
        return 'state'
    if cleaned in JUNK_VALUES:
        return 'junk'
    # Check if it contains comma (e.g. "Samastipur, Bihar, India") - junk/address
    if ',' in cleaned:
        return 'junk'
    # Alphanumeric codes (e.g. HU0292, HGL005)
    import re
    if re.match(r'^[a-z]{2,3}\d{2,}$', cleaned):
        return 'junk'
    # Everything else that doesn't match a known state -> treat as city
    return 'city'

# Analyze both columns
city_records = []  # list of (city_name, column, row_count)

for col_name in ['Source_State', 'Destination_State']:
    vc = df[col_name].value_counts()
    for val, count in vc.items():
        category = classify_value(val)
        if category == 'city':
            city_records.append({
                'city_name': str(val).strip(),
                'column': col_name,
                'row_count': count
            })

city_df = pd.DataFrame(city_records)

if city_df.empty:
    print("No city names found in state columns!")
    exit()

# ──────────────────────────────────────────────────────────────────────────
# 4. AGGREGATE: total rows affected per city (across both columns)
# ──────────────────────────────────────────────────────────────────────────
# Normalize city names to title case for grouping similar entries
city_df['city_normalized'] = city_df['city_name'].str.strip().str.upper()
city_agg = city_df.groupby('city_normalized').agg(
    total_rows=('row_count', 'sum'),
    original_forms=('city_name', lambda x: ', '.join(sorted(set(x)))),
    columns_affected=('column', lambda x: ' & '.join(sorted(set(x))))
).reset_index()
city_agg = city_agg.sort_values('total_rows', ascending=False).reset_index(drop=True)

# Print summary
total_city_rows = city_agg['total_rows'].sum()
total_rows = len(df)
print(f"{'='*70}")
print(f"  SUMMARY: City names found in State columns")
print(f"{'='*70}")
print(f"  Total rows in dataset       : {total_rows:>10,}")
print(f"  Rows with city (not state)  : {total_city_rows:>10,}")
print(f"  Unique city names found     : {len(city_agg):>10}")
print(f"  Percentage affected         : {total_city_rows/total_rows*100:>9.2f}%")
print(f"{'='*70}\n")

print(f"{'City Name':<25} {'Rows':>8}  {'Appears In':<35}  Original Forms")
print("-" * 100)
for _, row in city_agg.iterrows():
    print(f"{row['city_normalized']:<25} {row['total_rows']:>8,}  "
          f"{row['columns_affected']:<35}  {row['original_forms']}")

# ──────────────────────────────────────────────────────────────────────────
# 5. CHART — Premium dark-themed horizontal bar chart
# ──────────────────────────────────────────────────────────────────────────

# Take top 30 cities for readability
top_n = min(30, len(city_agg))
plot_df = city_agg.head(top_n).iloc[::-1]  # reverse for horizontal bars

fig, ax = plt.subplots(figsize=(16, max(10, top_n * 0.42)))

# Dark theme
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#161b22')

# Gradient-like color palette
gradient_colors = plt.cm.plasma(np.linspace(0.2, 0.85, top_n))

y_pos = np.arange(top_n)
bars = ax.barh(y_pos, plot_df['total_rows'].values,
               color=gradient_colors, edgecolor='#30363d',
               linewidth=0.8, height=0.7, zorder=3)

# Subtle grid
ax.xaxis.grid(True, linestyle='--', alpha=0.15, color='#8b949e', zorder=0)
ax.yaxis.grid(False)

# Labels on bars
for i, (bar, rows) in enumerate(zip(bars, plot_df['total_rows'].values)):
    width = bar.get_width()
    # Row count inside bar (if bar is wide enough) or outside
    if width > max(plot_df['total_rows'].values) * 0.15:
        ax.text(width - max(plot_df['total_rows'].values) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f'{rows:,}', va='center', ha='right',
                fontsize=9, color='white', fontweight='bold', zorder=5)
    else:
        ax.text(width + max(plot_df['total_rows'].values) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f'{rows:,}', va='center', ha='left',
                fontsize=9, color='#e6edf3', fontweight='bold', zorder=5)

# Y-axis labels
ax.set_yticks(y_pos)
ax.set_yticklabels(plot_df['city_normalized'].values,
                   fontsize=10, color='#e6edf3', fontweight='600')
ax.set_xlabel('Number of Rows Affected', fontsize=12, color='#8b949e',
              labelpad=12, fontweight='500')

# Title
ax.set_title('City Names Found in State Column\n'
             '(These should be state names, not cities)',
             fontsize=17, color='#58a6ff', fontweight='bold', pad=20,
             loc='left')

# Subtitle
ax.text(0.0, 1.02,
        f'Total: {total_city_rows:,} rows affected  •  '
        f'{len(city_agg)} unique cities  •  '
        f'{total_city_rows/total_rows*100:.1f}% of all data',
        transform=ax.transAxes, fontsize=10, color='#f0883e',
        fontweight='500', va='bottom')

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='x', colors='#8b949e')
ax.tick_params(axis='y', length=0)
ax.set_xlim(0, max(plot_df['total_rows'].values) * 1.18)

plt.tight_layout(rect=[0, 0, 1, 0.96])

# ── Save ──
output_path = r"D:\HFU UNI Project\DS-Project HFU\city_names_in_state_column.png"
plt.savefig(output_path, dpi=200, bbox_inches='tight',
            facecolor=fig.get_facecolor(), edgecolor='none')
print(f"\n✅ Chart saved to: {output_path}")
plt.show()
