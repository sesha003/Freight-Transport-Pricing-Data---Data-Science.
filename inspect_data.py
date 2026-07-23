import pandas as pd

file_path = r"D:\HFU UNI Project\DS-Project HFU\Raw Data\Transport_Market_Price.xlsx"

# Read only the state columns for speed
df = pd.read_excel(file_path, usecols=['Source_State', 'Destination_State'])

print(f"Total rows: {len(df)}")

print("\n===== SOURCE_STATE unique values =====")
src_vc = df['Source_State'].value_counts()
print(f"Unique values: {len(src_vc)}")
for val, cnt in src_vc.items():
    print(f"  {repr(val):40s}  ->  {cnt:>7,}")

print("\n===== DESTINATION_STATE unique values =====")
dst_vc = df['Destination_State'].value_counts()
print(f"Unique values: {len(dst_vc)}")
for val, cnt in dst_vc.items():
    print(f"  {repr(val):40s}  ->  {cnt:>7,}")
