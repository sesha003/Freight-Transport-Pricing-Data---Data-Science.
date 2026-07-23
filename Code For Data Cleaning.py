import pandas as pd
import re

# Load the dataset
file_path = r"D:\HFU UNI Project\DS-Project HFU\Transport_Market_Price.xlsx"
df = pd.read_excel(file_path)

# ============================================================
# 1. VALID INDIAN STATES & UNION TERRITORIES (Official List)
# ============================================================
valid_states = {
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar',
    'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
    'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala',
    'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya',
    'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
    'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    # Union Territories
    'Andaman And Nicobar Islands', 'Chandigarh',
    'Dadra And Nagar Haveli And Daman And Diu',
    'Delhi', 'Jammu And Kashmir', 'Ladakh',
    'Lakshadweep', 'Puducherry'
}

# ============================================================
# 2. STATE NAME CORRECTIONS (Misspellings / Abbreviations)
# ============================================================
state_corrections = {
    # Uttar Pradesh variants
    'Up': 'Uttar Pradesh',
    'U.P.': 'Uttar Pradesh',
    'U.P': 'Uttar Pradesh',
    'Utter Pardesh': 'Uttar Pradesh',
    'Uttarpradesh': 'Uttar Pradesh',
    'Uttar Prades': 'Uttar Pradesh',

    # Madhya Pradesh variants
    'Mp': 'Madhya Pradesh',
    'M.P': 'Madhya Pradesh',
    'M.P.': 'Madhya Pradesh',
    'Madhyapradesh': 'Madhya Pradesh',
    'Madhypradesh': 'Madhya Pradesh',
    'Madhayapradesh': 'Madhya Pradesh',
    'Madhy Pradesh': 'Madhya Pradesh',
    'Madhya Pradesh,': 'Madhya Pradesh',

    # Maharashtra variants
    'Maharastra': 'Maharashtra',
    'Maharsthra': 'Maharashtra',
    'Mahrastra': 'Maharashtra',
    'Maha': 'Maharashtra',
    'Mh': 'Maharashtra',

    # Tamil Nadu variants
    'Tamilnadu': 'Tamil Nadu',
    'Tn': 'Tamil Nadu',

    # Telangana variants
    'Telengana': 'Telangana',

    # Andhra Pradesh variants
    'Andhrapradesh': 'Andhra Pradesh',
    'Ap': 'Andhra Pradesh',

    # Gujarat variants
    'Gujrat': 'Gujarat',

    # Rajasthan variants
    'Rajsthan': 'Rajasthan',
    'Raasthan': 'Rajasthan',

    # Chhattisgarh variants
    'Chattisgarh': 'Chhattisgarh',
    'Chhatisgarh': 'Chhattisgarh',
    'Chhatishgarh': 'Chhattisgarh',

    # Karnataka variants
    'Ka': 'Karnataka',
    'Karnatka': 'Karnataka',

    # Uttarakhand variants
    'Uttarkhand': 'Uttarakhand',

    # Himachal Pradesh variants
    'Hp': 'Himachal Pradesh',

    # Jammu & Kashmir variants
    'J&K': 'Jammu And Kashmir',
    'J\u0026K': 'Jammu And Kashmir',
    'Jammu & Kashmir': 'Jammu And Kashmir',
    'Jammu & Kashimir': 'Jammu And Kashmir',
    'Jammu & Kasmir': 'Jammu And Kashmir',

    # Hindi script
    '\u0939\u0930\u093f\u092f\u093e\u0923\u093e': 'Haryana',   # हरियाणा
}

# ============================================================
# 3. CITY-TO-STATE MAPPING (cities found in Source_State column)
#    Verified online for correct state assignment
# ============================================================
city_to_state = {
    # --- Uttar Pradesh cities ---
    'Ghaziabad': 'Uttar Pradesh',
    'Ghaziabad Jb': 'Uttar Pradesh',
    'Chandauli': 'Uttar Pradesh',
    'Gajraula': 'Uttar Pradesh',
    'Khatauli': 'Uttar Pradesh',
    'Pilkhuwa': 'Uttar Pradesh',
    'Bahraich': 'Uttar Pradesh',
    'Prayagraj': 'Uttar Pradesh',
    'Mathura': 'Uttar Pradesh',
    'Kanpur': 'Uttar Pradesh',
    'Lucknow': 'Uttar Pradesh',
    'Banda': 'Uttar Pradesh',

    # --- Gujarat cities ---
    'Bardoli': 'Gujarat',
    'Hazira': 'Gujarat',
    'Surat': 'Gujarat',
    'Gandhidham': 'Gujarat',
    'Kadi': 'Gujarat',
    'Kadi+ Kadi': 'Gujarat',
    'Umbergaon': 'Gujarat',
    'Umbergoan': 'Gujarat',
    'Savli': 'Gujarat',
    'Vadodara': 'Gujarat',
    'Rajkot': 'Gujarat',
    'Padra': 'Gujarat',
    'Amreli': 'Gujarat',
    'Ahmedabad': 'Gujarat',

    # --- Maharashtra cities ---
    'Khopoli': 'Maharashtra',
    'Navi Mumbai': 'Maharashtra',
    'Mangaon': 'Maharashtra',
    'Baramati': 'Maharashtra',
    'Shirur': 'Maharashtra',
    'Mantha': 'Maharashtra',
    'Pune': 'Maharashtra',
    'Nagpur': 'Maharashtra',
    'Nagpur+Nagpur': 'Maharashtra',
    'Nagpur+Chandarpur': 'Maharashtra',
    'Nagpur+Gondia': 'Maharashtra',
    'Kolhapur': 'Maharashtra',
    'Kolhapur+Sawantwadi': 'Maharashtra',
    'Sativali': 'Maharashtra',
    'Sativli': 'Maharashtra',
    'Bhiwandi': 'Maharashtra',
    'Bhiwandi+Bhiwandi': 'Maharashtra',
    'Thane': 'Maharashtra',
    'Jalgaon': 'Maharashtra',
    'Jalna': 'Maharashtra',
    'Nallasopara': 'Maharashtra',
    'Satana': 'Maharashtra',
    'Nanded': 'Maharashtra',
    'Akola': 'Maharashtra',
    'Sawantwadi': 'Maharashtra',
    'Parnhani': 'Maharashtra',
    'Kudal': 'Maharashtra',
    'Narayagaon': 'Maharashtra',
    'Poynad': 'Maharashtra',
    'Buldana': 'Maharashtra',
    'Buldhana': 'Maharashtra',
    'Sangli': 'Maharashtra',
    'Vasai': 'Maharashtra',
    'Dharavi': 'Maharashtra',
    'Vashi': 'Maharashtra',
    'Andheri': 'Maharashtra',
    'Mahad': 'Maharashtra',
    'Pimpalgaon': 'Maharashtra',
    'Udgir': 'Maharashtra',
    'Gondiya': 'Maharashtra',
    'Bhusawal': 'Maharashtra',
    'Nashik': 'Maharashtra',
    'Nashik+ Nashik': 'Maharashtra',
    'Ahmadnagar': 'Maharashtra',
    'Pimpri Chinchwad + Pune': 'Maharashtra',
    'Akkalkuwa': 'Maharashtra',
    'Aurangabad': 'Maharashtra',
    'Mumbai Maharashtra': 'Maharashtra',
    'Bhopal': 'Madhya Pradesh',

    # --- Haryana cities ---
    'Rai': 'Haryana',
    'Karnal': 'Haryana',
    'Gohana': 'Haryana',
    'Gharunda': 'Haryana',
    'Pataudi': 'Haryana',
    'Jhajjar': 'Haryana',
    'Rohtak': 'Haryana',
    'Gurgaon': 'Haryana',
    'Bhiwani': 'Haryana',
    'Panchkula': 'Haryana',
    'Rewari': 'Haryana',
    'Ballabhgarh': 'Haryana',
    'Narnaul': 'Haryana',
    'Hisar': 'Haryana',

    # --- Punjab cities ---
    'Kheri Gurana': 'Punjab',
    'Patiala': 'Punjab',

    # --- Tamil Nadu cities ---
    'Chennai': 'Tamil Nadu',
    'Chennai+Chennai': 'Tamil Nadu',
    'Coimbatore': 'Tamil Nadu',
    'Madurai': 'Tamil Nadu',
    'Thanjavur': 'Tamil Nadu',

    # --- Telangana cities ---
    'Hyderabad': 'Telangana',
    'Patancheru': 'Telangana',

    # --- Rajasthan cities ---
    'Barmer': 'Rajasthan',
    'Khairthal': 'Rajasthan',

    # --- West Bengal cities ---
    'Kolkata': 'West Bengal',
    'Raniganj': 'West Bengal',
    'New Barrackpur': 'West Bengal',

    # --- Chhattisgarh cities ---
    'Bilaspur': 'Chhattisgarh',
    'Bilashpur': 'Chhattisgarh',
    'Raipur': 'Chhattisgarh',
    'Korba': 'Chhattisgarh',
    'Raigarh': 'Chhattisgarh',

    # --- Madhya Pradesh cities ---
    'Nimrani': 'Madhya Pradesh',
    'Jabalpur': 'Madhya Pradesh',
    'Satna': 'Madhya Pradesh',

    # --- Odisha cities ---
    'Barpali': 'Odisha',
    'Cuttack': 'Odisha',

    # --- Karnataka cities ---
    'Banglore': 'Karnataka',
    'Hubli': 'Karnataka',
    'Chitradurga + Shimoga': 'Karnataka',

    # --- Goa cities ---
    'Ponda': 'Goa',
    'Ponda Goa': 'Goa',
    'Ponda Goa (Depot+ Cd)': 'Goa',

    # --- Uttarakhand cities ---
    'Haridwar': 'Uttarakhand',
    'Haridwar Uttrakhand': 'Uttarakhand',
    'Pantnagar': 'Uttarakhand',
    'Haldwani': 'Uttarakhand',
    'Ponta Sahib': 'Himachal Pradesh',

    # --- Kerala cities ---
    'Cochin': 'Kerala',

    # --- Andhra Pradesh cities ---
    'Punganur': 'Andhra Pradesh',

    # --- Bihar cities ---
    'Samastipur, Bihar, India': 'Bihar',
    'Muzaffarpur, Bihar, India': 'Bihar',

    # --- Jharkhand cities ---
    'Dhanbad, Bihar, India': 'Jharkhand',
    'Gua': 'Jharkhand',

    # --- Composite / Address-style entries ---
    'Lucknow, Uttar Pradesh, India': 'Uttar Pradesh',

    # --- Small / ambiguous places (best guess from context) ---
    'Patli': 'Haryana',
    'Khumari': 'Chhattisgarh',
    'Rupra Road': 'Haryana',
}

# ============================================================
# 4. NOISE VALUES (not a state or city - should be blank)
# ============================================================
noise_values = {
    'Nan', ']', 'Metric Tonnes (Mt)', 'Party', 'Unknown', 'None', ''
}

# ============================================================
# 5. SOURCE (CITY) NAME CLEANING
# ============================================================

# 5a. Suffixes/prefixes to strip from city names (transport/railway jargon)
suffix_patterns = [
    r'\s+Rake\s+Yard$',   # e.g. "Ujhani Rake Yard" → "Ujhani"
    r'\s+Yard$',           # e.g. "Fatuha Yard" → "Fatuha"
    r'\s+Jb$',             # e.g. "Ghaziabad Jb" → "Ghaziabad" (Junction Booking)
    r'\s*\(Jb\)$',         # e.g. "Ghaziabad (Jb)" → "Ghaziabad"
]
prefix_patterns = [
    r'^Rsd\s+',            # e.g. "Rsd Raipur Yard" → "Raipur Yard" (then Yard stripped)
    r'^Ncmsl\s+Warehouse\s+',  # e.g. "Ncmsl Warehouse Raichur" → "Raichur"
]

# 5b. City spelling corrections (verified online)
city_spelling_corrections = {
    # Misspellings
    'Varansi': 'Varanasi',
    'Athni': 'Athani',
    'Bilashpur': 'Bilaspur',
    'Gharaunda': 'Gharaunda',  # correct as-is but normalizing from Source_State

    # Standardize to official city names
    'Mangalore': 'Mangaluru',          # Official name since 2014
    'Bangalore': 'Bengaluru',          # Official name since 2006
    'Banglore': 'Bengaluru',
    'Calcutta': 'Kolkata',
    'Bombay': 'Mumbai',
    'Madras': 'Chennai',
    'Cochin': 'Kochi',

    # Standardize Sri Ganganagar variants
    'Sriganganagar': 'Sri Ganganagar',

    # Tarn Taran variants
    'Taran Taran': 'Tarn Taran',

    # Handle number suffix
    'Kolkata-1': 'Kolkata',

    # Noise entries → extract actual city
    'Shriya Rice Mills': 'Raichur',    # Located in Raichur, Karnataka
    'Nrpa Yard': 'Narayanpur Anant',   # NRPA = Narayanpur Anant station, Bihar

    # Dahisar Mori is a locality in Navi Mumbai region
    'Dahisar Mori': 'Dahisar',

    # Hindon City is an area in Ghaziabad
    'Hindon City': 'Ghaziabad',

    # Meda Adraj is a village in Kadi taluka, Gujarat
    'Meda Adraj': 'Meda Adraj',        # Keep as-is (valid village name)

    # Delhi Kishanganj → Kishanganj (Kishanganj is the city, Delhi is the state)
    'Delhi Kishanganj': 'Kishanganj',

    # Lakhimpur Kheri → Lakhimpur (Lakhimpur is the city, merge with existing Lakhimpur)
    'Lakhimpur Kheri': 'Lakhimpur',
}

# 5c. Source noise values (not valid city names)
source_noise = {
    'Nan', 'None', '', 'Unknown', 'Party',
    'Metric Tonnes (Mt)', ']',
    'Delhi',  # Delhi is a state/UT, not a city name - remove from Source
}

# ============================================================
# 6. CLEANING FUNCTIONS
# ============================================================
def clean_source_city(val):
    """
    Comprehensive Source (city name) cleaning:
    1. Remove noise values
    2. Handle redundant names (Chennai + Chennai → Chennai)
    3. Strip transport suffixes (Yard, Jb, Rake Yard, Rsd)
    4. Fix city spelling mistakes
    5. Standardize to official city names
    """
    if pd.isna(val):
        return val

    val = str(val).strip().title()

    # Check if it's a noise value
    if val in source_noise:
        return ''

    # Handle redundant names: "Chennai + Chennai" → "Chennai"
    for sep in ['+', '/', '&']:
        if sep in val:
            parts = [p.strip() for p in val.split(sep)]
            if len(set(parts)) == 1:
                val = parts[0]
                break

    # Strip prefix patterns (Rsd, Ncmsl Warehouse)
    for pattern in prefix_patterns:
        val = re.sub(pattern, '', val, flags=re.IGNORECASE).strip()

    # Strip suffix patterns (Yard, Jb, Rake Yard)
    for pattern in suffix_patterns:
        val = re.sub(pattern, '', val, flags=re.IGNORECASE).strip()

    # Apply spelling corrections
    if val in city_spelling_corrections:
        val = city_spelling_corrections[val]

    return val


def clean_source_state(val):
    """
    Comprehensive Source_State cleaning:
    1. Remove noise values
    2. Fix state misspellings/abbreviations
    3. Replace city names with their correct state
    4. Handle address-style entries like 'City, State, India'
    """
    if pd.isna(val):
        return val

    val = str(val).strip().title()

    # Check if it's a noise value
    if val in noise_values:
        return ''

    # Check state corrections first (misspellings/abbreviations)
    if val in state_corrections:
        return state_corrections[val]

    # Check if already a valid state
    if val in valid_states:
        return val

    # Check city-to-state mapping
    if val in city_to_state:
        return city_to_state[val]

    # Handle address-style: "City, State, India" or "City, State"
    if ',' in val:
        parts = [p.strip() for p in val.split(',')]
        for part in parts:
            if part in valid_states:
                return part
            if part in state_corrections:
                return state_corrections[part]

    # If nothing matched, return original (will be flagged in review)
    return val


def to_lowercase(val):
    """Converts a string value to lowercase."""
    if pd.isna(val):
        return val
    return str(val).strip().lower()

# ============================================================
# 7. APPLY CLEANING
# ============================================================
# Clean Source column (city names: strip suffixes, fix spelling, remove noise)
df['Corrected_Source'] = df['Source'].apply(clean_source_city).apply(to_lowercase)

# Clean Source_State column (main fix: city→state, misspellings, noise)
df['Corrected_Source_State'] = df['Source_State'].apply(clean_source_state).apply(to_lowercase)

# ============================================================
# 8. VALIDATION
# ============================================================

# --- Validate Source_State ---
valid_states_lower = {s.lower() for s in valid_states}
remaining_state_issues = df[
    (df['Corrected_Source_State'] != '') &
    (~df['Corrected_Source_State'].isin(valid_states_lower)) &
    (df['Corrected_Source_State'].notna())
]['Corrected_Source_State'].value_counts()

if len(remaining_state_issues) > 0:
    print("WARNING: These values in Corrected_Source_State are NOT valid states:")
    print(remaining_state_issues.to_string())
    print()
else:
    print("OK - All Corrected_Source_State values are valid Indian states!")
    print()

# --- Validate Source (show what changed) ---
print("=" * 60)
print("SOURCE (CITY) CLEANING SUMMARY")
print("=" * 60)
source_changed = df['Source'].astype(str).str.strip().str.lower() != df['Corrected_Source']
print(f"Total rows with Source city corrections: {source_changed.sum()}")
print()

# Show examples of Source corrections
if source_changed.any():
    examples = df[source_changed][['Source', 'Corrected_Source']].drop_duplicates()
    print(f"Unique corrections made ({len(examples)} types):")
    print(examples.to_string(index=False))
    print()

print("Corrected_Source unique values:")
print(df['Corrected_Source'].value_counts().to_string())

print()
print("=" * 60)
print("SOURCE_STATE CLEANING SUMMARY")
print("=" * 60)
state_changed = df['Source_State'].astype(str).str.strip().str.lower() != df['Corrected_Source_State']
print(f"Total rows with Source_State corrections: {state_changed.sum()}")
print()
print("Corrected_Source_State value counts:")
print(df['Corrected_Source_State'].value_counts().to_string())

# ============================================================
# 9. REORGANIZE COLUMNS (Original | Corrected side by side)
# ============================================================
cols = list(df.columns)
cols.remove('Corrected_Source')
cols.remove('Corrected_Source_State')

source_idx = cols.index('Source')
cols.insert(source_idx + 1, 'Corrected_Source')

state_idx = cols.index('Source_State')
cols.insert(state_idx + 1, 'Corrected_Source_State')

df = df[cols]

# ============================================================
# 10. EXPORT
# ============================================================
output_file = r'D:\HFU UNI Project\DS-Project HFU\Cleaned_Transport_Data2.xlsx'
df.to_excel(output_file, index=False)