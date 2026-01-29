import pandas as pd

df = pd.read_csv('Statistic on best rugby players 2023-2024.csv')
print('Unique positions:')
print(df['Position'].unique())
print('\nPosition counts:')
print(df['Position'].value_counts())

# Check starter positions totals
STARTER_POSITIONS = {
    '7s': {
        'Prop': 1, 'Hooker': 1, 'Lock': 1,
        'Scrumhalf': 1, 'Flyhalf': 1, 'Centre': 1, 'Winger': 1
    },
    '10s': {
        'Prop': 2, 'Hooker': 1, 'Lock': 1, 'Backrow': 1,
        'Scrumhalf': 1, 'Flyhalf': 1, 'Centre': 1, 'Winger': 1, 'Fullback': 1
    },
    '15s': {
        'Prop': 2, 'Hooker': 1, 'Lock': 2, 'Backrow': 3,
        'Scrumhalf': 1, 'Flyhalf': 1, 'Centre': 2, 'Winger': 2, 'Fullback': 1
    }
}

print('\n\n=== STARTER POSITIONS TOTALS ===')
for format_name, positions in STARTER_POSITIONS.items():
    total = sum(positions.values())
    print(f'{format_name}: {total} starters')
    print(f'  {positions}')
