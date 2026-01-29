import pandas as pd

df = pd.read_csv('Statistic on best rugby players 2023-2024.csv')

# Map inconsistent position names to standard names
position_mapping = {
    'Prop': 'Prop',
    'Prop ': 'Prop',
    'Hooker': 'Hooker',
    'Hooker ': 'Hooker',
    'Lock': 'Lock',
    'Secondrow': 'Lock',
    'Secondrow ': 'Lock',
    'Backrow': 'Backrow',
    'Backrow ': 'Backrow',
    'Back row': 'Backrow',
    'Scrumhalf': 'Scrumhalf',
    'Scrumhalf ': 'Scrumhalf',
    'Scrum': 'Scrumhalf',
    'Flyhalf': 'Flyhalf',
    'FlyHalf ': 'Flyhalf',
    'Fly': 'Flyhalf',
    'Centre': 'Centre',
    'Center': 'Centre',
    'Center ': 'Centre',
    'Centre ': 'Centre',
    'Winger': 'Winger',
    'Winger ': 'Winger',
    'Fullback': 'Fullback',
    'Fullback ': 'Fullback',
    'Utility Back': 'Centre',
    'Utility Back ': 'Centre',
    'Utility Forward': 'Backrow',
    'Utility Forward ': 'Backrow',
}

df['Position'] = df['Position'].map(position_mapping)
df = df.dropna(subset=['Position'])

print('Standardized positions:')
print(df['Position'].value_counts())
