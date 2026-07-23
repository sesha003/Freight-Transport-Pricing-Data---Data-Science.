import pandas as pd, re

df = pd.read_excel(r"D:\HFU UNI Project\DS-Project HFU\Transport_Market_Price.xlsx")

valid_states = {'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal','Andaman And Nicobar Islands','Chandigarh','Dadra And Nagar Haveli And Daman And Diu','Delhi','Jammu And Kashmir','Ladakh','Lakshadweep','Puducherry'}
state_corrections = {'Up':'Uttar Pradesh','U.P.':'Uttar Pradesh','Mp':'Madhya Pradesh','M.P.':'Madhya Pradesh','Maharastra':'Maharashtra','Mh':'Maharashtra','Tamilnadu':'Tamil Nadu','Tn':'Tamil Nadu','Telengana':'Telangana','Ap':'Andhra Pradesh','Gujrat':'Gujarat','Rajsthan':'Rajasthan','Chattisgarh':'Chhattisgarh','Ka':'Karnataka','Hp':'Himachal Pradesh','J&K':'Jammu And Kashmir','हरियाणा':'Haryana'}
city_to_state = {'Ghaziabad':'Uttar Pradesh','Lucknow':'Uttar Pradesh','Kanpur':'Uttar Pradesh','Surat':'Gujarat','Ahmedabad':'Gujarat','Vadodara':'Gujarat','Pune':'Maharashtra','Nagpur':'Maharashtra','Nashik':'Maharashtra','Kolhapur':'Maharashtra','Chennai':'Tamil Nadu','Coimbatore':'Tamil Nadu','Hyderabad':'Telangana','Kolkata':'West Bengal','Raipur':'Chhattisgarh','Bhopal':'Madhya Pradesh','Gurgaon':'Haryana','Rohtak':'Haryana','Banglore':'Karnataka','Haridwar':'Uttarakhand','Ponda':'Goa'}
noise_values = {'Nan',']','Metric Tonnes (Mt)','Party','Unknown','None',''}; source_noise = {'Nan','None','','Unknown','Party','Metric Tonnes (Mt)',']','Delhi'}
suffix_patterns = [r'\s+Rake\s+Yard$',r'\s+Yard$',r'\s+Jb$',r'\s*\(Jb\)$']; prefix_patterns = [r'^Rsd\s+',r'^Ncmsl\s+Warehouse\s+']
city_spelling = {'Varansi':'Varanasi','Banglore':'Bengaluru','Bangalore':'Bengaluru','Calcutta':'Kolkata','Bombay':'Mumbai','Madras':'Chennai','Cochin':'Kochi','Kolkata-1':'Kolkata','Hindon City':'Ghaziabad','Lakhimpur Kheri':'Lakhimpur'}

area_to_district = {('bavla','gujarat'):'ahmedabad',('changodar','gujarat'):'ahmedabad',('nandasana','gujarat'):'mehsana',('linch','gujarat'):'mehsana',('kuvadva','gujarat'):'rajkot',('bhimasar','gujarat'):'kachchh',('meda adraj','gujarat'):'gandhinagar',('vadsar','gujarat'):'gandhinagar',('hazira','gujarat'):'surat',('barota','haryana'):'sonipat',('barwala','haryana'):'hisar',('cheeka','haryana'):'kaithal',('gharaunda','haryana'):'karnal',('gohana','haryana'):'sonipat',('jundla','haryana'):'karnal',('kundli','haryana'):'sonipat',('patli','haryana'):'gurgaon',('rai','haryana'):'sonipat',('taraori','haryana'):'karnal',('anekal','karnataka'):'bengaluru urban',('hoskote','karnataka'):'bengaluru rural',('yeshwanthpur','karnataka'):'bengaluru urban',('karatagi','karnataka'):'koppal',('munoli','karnataka'):'belagavi',('dahisar','maharashtra'):'mumbai suburban',('khopoli','maharashtra'):'raigad',('taloja','maharashtra'):'raigad',('jiyagaon','madhya pradesh'):'dewas',('malanpur','madhya pradesh'):'bhind',('salkani','madhya pradesh'):'raisen',('udaipura','madhya pradesh'):'raisen',('mandideep','madhya pradesh'):'raisen',('nimrani','madhya pradesh'):'khargone',('farah','uttar pradesh'):'mathura',('gajraula','uttar pradesh'):'amroha',('kuberpur','uttar pradesh'):'agra',('mohanlalganj','uttar pradesh'):'lucknow',('khatauli','uttar pradesh'):'muzaffarnagar',('pilkhuwa','uttar pradesh'):'hapur',('sikandrabad','uttar pradesh'):'bulandshahr',('ujhani','uttar pradesh'):'budaun',('hariawan','uttar pradesh'):'hardoi',('bhimsen','uttar pradesh'):'kanpur nagar',('chaukhandi','uttar pradesh'):'kanpur nagar',('fatuha','bihar'):'patna',('kudra','bihar'):'kaimur',('mohania','bihar'):'kaimur',('nokha','bihar'):'rohtas',('nrpa','bihar'):'muzaffarpur',('kheri gurana','punjab'):'patiala',('shambhu','punjab'):'patiala',('sunam','punjab'):'sangrur',('gummidipoondi','tamil nadu'):'tiruvallur',('gulabganj','rajasthan'):'sirohi',('jhalrapatan','rajasthan'):'jhalawar',('kanakpura','rajasthan'):'jaipur',('mantralayam','andhra pradesh'):'kurnool',('narela','delhi'):'delhi',('kishanganj','delhi'):'delhi',('west medinipur','west bengal'):'paschim medinipur',('rairangpur','odisha'):'mayurbhanj'}

def clean_source_city(val):
    if pd.isna(val): return val
    val = str(val).strip().title()
    if val in source_noise: return ''
    for sep in ['+','/','\&']:
        if sep in val:
            parts = [p.strip() for p in val.split(sep)]
            if len(set(parts)) == 1: val = parts[0]; break
    for p in prefix_patterns: val = re.sub(p,'',val,flags=re.IGNORECASE).strip()
    for p in suffix_patterns: val = re.sub(p,'',val,flags=re.IGNORECASE).strip()
    return city_spelling.get(val, val)

def clean_source_state(val):
    if pd.isna(val): return val
    val = str(val).strip().title()
    if val in noise_values: return ''
    if val in state_corrections: return state_corrections[val]
    if val in valid_states: return val
    if val in city_to_state: return city_to_state[val]
    if ',' in val:
        for part in [p.strip() for p in val.split(',')]:
            if part in valid_states: return part
            if part in state_corrections: return state_corrections[part]
    return val

to_lowercase = lambda v: v if pd.isna(v) else str(v).strip().lower()
df['Corrected_Source'] = df['Source'].apply(clean_source_city).apply(to_lowercase)
df['Corrected_Source_State'] = df['Source_State'].apply(clean_source_state).apply(to_lowercase)

for (old, st), new in area_to_district.items():
    if old != new:
        mask = (df['Corrected_Source'] == old) & (df['Corrected_Source_State'] == st)
        if mask.any(): df.loc[mask, 'Corrected_Source'] = new; print(f"  {old} ({st}) -> {new} ({mask.sum()} rows)")

valid_lower = {s.lower() for s in valid_states}; bad = df[(df['Corrected_Source_State'] != '') & (~df['Corrected_Source_State'].isin(valid_lower)) & (df['Corrected_Source_State'].notna())]['Corrected_Source_State'].value_counts(); print('OK – All valid!' if len(bad) == 0 else f'WARNING:\n{bad}')
cols = list(df.columns); cols.remove('Corrected_Source'); cols.remove('Corrected_Source_State'); cols.insert(cols.index('Source') + 1, 'Corrected_Source'); cols.insert(cols.index('Source_State') + 1, 'Corrected_Source_State')
df[cols].to_excel(r'D:\HFU UNI Project\DS-Project HFU\Cleaned_Transport_Data2.xlsx', index=False)
