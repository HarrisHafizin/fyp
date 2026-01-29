import pandas as pd

curr_fp='Statistic on best rugby players 2023-2024.csv'
bak_fp='Statistic on best rugby players 2023-2024.csv.bak'

curr = pd.read_csv(curr_fp, encoding='ISO-8859-1')
bak = pd.read_csv(bak_fp, encoding='ISO-8859-1')

curr['full_name'] = curr['First-name'].astype(str).str.strip() + ' ' + curr['Name'].astype(str).str.strip()
bak['full_name'] = bak['First-name'].astype(str).str.strip() + ' ' + bak['Name'].astype(str).str.strip()

# Build map from backup full_name -> salary if >0
salary_map = {}
for _, row in bak.iterrows():
    fn = row['full_name']
    sal = row.get('Salary', 0)
    try:
        sval = int(float(sal))
    except:
        try:
            sval = int(str(sal).replace(',','').replace('"','').strip())
        except:
            sval = 0
    if sval > 0:
        salary_map[fn.lower()] = sval

repaired = []
for idx, row in curr.iterrows():
    if int(row.get('Salary',0)) == 0:
        fn = row['full_name'].lower()
        if fn in salary_map:
            curr.at[idx,'Salary'] = salary_map[fn]
            repaired.append((idx, row['full_name'], salary_map[fn]))

curr.to_csv(curr_fp, index=False, encoding='ISO-8859-1')

print('Repaired salary entries:')
for t in repaired:
    print(t)

print('\nRemaining zero salaries:', (curr['Salary']==0).sum())
