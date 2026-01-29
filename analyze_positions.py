import pandas as pd
fp='Statistic on best rugby players 2023-2024.csv'
df=pd.read_csv(fp, encoding='ISO-8859-1')
print('Total rows:', len(df))
# Normalize roughly
pos_counts = df['Position'].astype(str).str.strip().str.lower().value_counts()
print('\nRaw position counts (lowercased):')
print(pos_counts)
# Build normalized mapping same as script
def norm(p):
    p=str(p).strip().lower()
    if 'second' in p or 'lock' in p:
        return 'Lock'
    if p in ('fly', 'flyhalf', 'fly half', 'fly-half'):
        return 'Flyhalf'
    if 'center' in p or 'centre' in p:
        return 'Centre'
    if 'winger' in p:
        return 'Winger'
    if 'prop' in p:
        return 'Prop'
    if 'hooker' in p:
        return 'Hooker'
    if 'scrum' in p or 'scrumhalf' in p or 'scrum half' in p:
        return 'Scrumhalf'
    if 'fullback' in p:
        return 'Fullback'
    if 'back' in p or 'backrow' in p or 'back row' in p:
        return 'Backrow'
    return p.title()

norm_counts = df['Position'].apply(norm).value_counts()
print('\nNormalized position counts:')
print(norm_counts)

# duplicate names
full = df['First-name'].astype(str).str.strip() + ' ' + df['Name'].astype(str).str.strip()
dups = full[full.duplicated(keep=False)]
print('\nNumber of duplicate full names:', dups.nunique())
if not dups.empty:
    print('Duplicates examples:')
    print(dups.unique())

# Current max racking value (to assign new racking)
try:
    max_r = int(df['racking'].max())
except Exception:
    max_r = len(df)
print('\nMax racking:', max_r)
