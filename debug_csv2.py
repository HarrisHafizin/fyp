import pandas as pd

fp = 'Statistic on best rugby players 2023-2024.csv'
df = pd.read_csv(fp, encoding='ISO-8859-1')
print('Columns:', list(df.columns))
for idx in range(100,115):
    print('\nRow', idx)
    row = df.loc[idx]
    for col in ['racking','First-name','Name','Position','yellow card','red card','Salary']:
        val = row[col]
        print(f"{col}: ({type(val).__name__}) -> {val}")
