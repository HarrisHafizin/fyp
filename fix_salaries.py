import pandas as pd
import re

fp='Statistic on best rugby players 2023-2024.csv'
df=pd.read_csv(fp, encoding='ISO-8859-1')
pattern = re.compile(r'"?\s*(\d{1,3}(?:,\d{3})+)(?:\.\d+)?\s*"?')
fixed = []
for idx, row in df[df['Salary'].isna() | (df['Salary']==0)].iterrows():
    found = False
    for col in df.columns:
        val = row[col]
        if isinstance(val, str):
            m = pattern.search(val)
            if m:
                num = m.group(1).replace(',','')
                try:
                    sal = int(num)
                except:
                    continue
                df.at[idx,'Salary'] = sal
                # remove the numeric substring from the original cell to avoid duplication
                newval = pattern.sub('', val).strip().strip('"')
                # if nothing left, set to 0
                if newval == '':
                    newval = 0
                df.at[idx,col] = newval
                fixed.append((idx, col, sal))
                found = True
                break
    if not found:
        # no formatted number found — leave as 0
        df.at[idx,'Salary'] = 0
        fixed.append((idx, None, 0))

# Coerce Salary to numeric
df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce').fillna(0).astype(int)

# Save a backup and write fixed CSV
backup = fp + '.bak'
open(backup,'w',encoding='ISO-8859-1').write(open(fp,'r',encoding='ISO-8859-1').read())
df.to_csv(fp, index=False, encoding='ISO-8859-1')

print('Fixed rows:')
for t in fixed:
    print(' idx:', t[0], 'from col:', t[1], '-> salary set to:', t[2])

# Verify
bad = df[df['Salary'].isna() | (df['Salary']==0)]
print('\nRemaining bad salaries:', len(bad))
print(bad[['racking','First-name','Name','Position','Salary']])
