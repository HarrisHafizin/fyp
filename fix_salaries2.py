import pandas as pd
import re

fp='Statistic on best rugby players 2023-2024.csv'
with open(fp,'r',encoding='ISO-8859-1') as f:
    lines = f.readlines()

df = pd.read_csv(fp, encoding='ISO-8859-1')

pattern = re.compile(r'"(\d{1,3}(?:,\d{3})+)"')  # quoted numbers like "700,000"

fixed = []
for idx, row in df[df['Salary'].isna() | (df['Salary']==0)].iterrows():
    raw = lines[idx]
    # look for quoted big-number first
    m = pattern.findall(raw)
    candidate = None
    if m:
        # take the last quoted number
        candidate = m[-1].replace(',','')
    else:
        # find all bare numbers and pick the last reasonably large one
        nums = re.findall(r'(\d{5,7})', raw)
        if nums:
            candidate = nums[-1]
    if candidate:
        try:
            val = int(candidate)
            if val < 10000:
                # too small — probably not salary
                val = 0
        except:
            val = 0
    else:
        val = 0
    df.at[idx,'Salary'] = val
    fixed.append((idx, val))

# cast Salary to int
df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce').fillna(0).astype(int)

# Save changes (no backup since you requested repair only)
df.to_csv(fp, index=False, encoding='ISO-8859-1')

print('Fixed rows:')
for t in fixed:
    print(' idx:', t[0], '-> salary set to:', t[1])

bad = df[df['Salary']==0]
print('\nRemaining zero salaries:', len(bad))
print(bad[['racking','First-name','Name','Position','Salary']].head(20))
