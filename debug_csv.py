import pandas as pd

fp = 'Statistic on best rugby players 2023-2024.csv'
try:
    df = pd.read_csv(fp, encoding='ISO-8859-1')
except Exception as e:
    print('Error reading CSV:', e)
    raise

print('\nDtypes for key columns:')
print(df[['club_starter','club_try','club_W','yellow card','red card']].dtypes)

print('\nRows 100-114:')
print(df.loc[100:114])

# Show if any non-numeric values exist in these columns
for col in ['club_starter','club_try','club_W','yellow card','red card','start_career']:
    bad = df.loc[100:114, col].apply(lambda x: not (isinstance(x, (int, float))))
    print(f"Column {col} has non-numeric types in rows: {df.loc[100:114, col][bad].index.tolist()}")
