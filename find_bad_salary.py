import pandas as pd
fp='Statistic on best rugby players 2023-2024.csv'
df=pd.read_csv(fp, encoding='ISO-8859-1')
bad = df[df['Salary'].isna() | (df['Salary']==0)]
print('Count bad salaries:', len(bad))
print(bad[['racking','First-name','Name','Position','Salary']])
with open(fp,'r',encoding='ISO-8859-1') as f:
    lines = f.readlines()
print('\nRaw lines for bad rows:')
for idx in bad.index:
    start = max(0, idx-1)
    end = min(len(lines), idx+2)
    print('\n--- line index', idx, '---')
    for i in range(start, end):
        print(i+1, repr(lines[i]))
