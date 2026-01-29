import pandas as pd

fp = 'Statistic on best rugby players 2023-2024.csv'
df = pd.read_csv(fp, encoding='ISO-8859-1')

# Build full name
df['full_name'] = df['First-name'].astype(str).str.strip() + ' ' + df['Name'].astype(str).str.strip()

# Find duplicated full names
dups = df[df.duplicated('full_name', keep=False)].sort_values('full_name')
if dups.empty:
    print('No duplicate full names found.')
else:
    print('Duplicate full names found:')
    to_drop = []
    for name, group in dups.groupby('full_name'):
        print('\nName:', name)
        for idx, row in group.iterrows():
            print('  idx:', idx, 'racking:', row['racking'], 'source row:', row.to_dict())
        # Keep the first occurrence (lowest index), drop others that are >=100 (likely added)
        first_idx = group.index.min()
        for idx in group.index:
            if idx != first_idx and idx >= 100:
                to_drop.append(idx)

    # Remove duplicates that were appended
    if to_drop:
        print('\nRemoving appended duplicate indices:', to_drop)
        df2 = df.drop(index=to_drop)
        df2 = df2.drop(columns=['full_name'])
        df2.to_csv(fp, index=False, encoding='ISO-8859-1')
        print('File updated, duplicates removed.')
    else:
        print('\nNo appended duplicates to remove (duplicates exist but none are from the appended region).')
