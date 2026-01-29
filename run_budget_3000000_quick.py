import rugby_scouting_ga as r
from rugby_scouting_ga import load_and_prep_data, RugbyScoutGA, display_team

# Reduce population and generations for a faster run to get a result quickly
r.POPULATION_SIZE = 30
r.GENERATIONS = 50

FILE = 'Statistic on best rugby players 2023-2024.csv'
BUDGET = 3000000

if __name__ == '__main__':
    df = load_and_prep_data(FILE)
    optimizer = RugbyScoutGA(df, BUDGET)
    best_team = optimizer.run()
    display_team(df, best_team, budget=BUDGET)
