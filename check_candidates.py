import pandas as pd
fp='Statistic on best rugby players 2023-2024.csv'
df=pd.read_csv(fp, encoding='ISO-8859-1')
full = (df['First-name'].astype(str).str.strip() + ' ' + df['Name'].astype(str).str.strip()).str.lower()
candidates = ['Aaron Smith','T.J. Perenara','Ben Youngs','Nic White','Gareth Davies','Alun Wyn Jones','Jonny Gray','Scott Barrett','Dane Coles','Ken Owens','Bongi Mbonambi','Leigh Halfpenny','Mike Brown','Andrew Kellaway']
for c in candidates:
    print(c, '->', ('present' if c.lower() in full.values else 'absent'))
print('\nTotal rows now:', len(df))
