from rugby_scouting_ga import load_and_prep_data, RugbyScoutGA, display_team, POPULATION_SIZE, GENERATIONS

FILE = 'Statistic on best rugby players 2023-2024.csv'
BUDGET = 3000000

print('Starting debug run — POPULATION_SIZE=', POPULATION_SIZE, 'GENERATIONS=', GENERATIONS)
df = load_and_prep_data(FILE)
optimizer = RugbyScoutGA(df, BUDGET)
print('feasible:', optimizer.feasible, 'min_team_salary:', getattr(optimizer, 'min_team_salary', None))
try:
    best_team = optimizer.run()
    print('Run completed, best_team:', best_team)
    display_team(df, best_team, budget=BUDGET)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Run raised exception:', e)
