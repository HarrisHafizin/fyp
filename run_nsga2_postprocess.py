import pandas as pd
from rugby_scouting_ga import load_and_prep_data, display_team

BUDGET = 3000000
IN = 'pareto_front.csv'
OUT = 'pareto_front_feasible.csv'

df = pd.read_csv(IN)
# filter feasible
feasible = df[df['salary'] <= BUDGET].copy()
# drop duplicate team encodings
feasible = feasible.drop_duplicates(subset=['team', 'salary', 'score']).reset_index(drop=True)
feasible = feasible.sort_values(['salary', 'score'], ascending=[True, False])
feasible.to_csv(OUT, index=False)

print(f"Pareto total: {len(df)}, feasible (<= ${BUDGET:,}): {len(feasible)} — saved to {OUT}")
print(feasible.head(10))

# display best score among feasible
if not feasible.empty:
    best = feasible.loc[feasible['score'].idxmax()]
    print('\nBest feasible by score:')
    df_all = load_and_prep_data('Statistic on best rugby players 2023-2024.csv')
    team_indices = list(map(int, best['team'].split('|')))
    display_team(df_all, team_indices, budget=BUDGET)
else:
    print('No feasible Pareto solutions found (check budget).')
