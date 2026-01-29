from rugby_scouting_ga import load_and_prep_data, RugbyScoutGA, display_team

FILE = 'Statistic on best rugby players 2023-2024.csv'
LOWER_BUDGET = 1000000  # $1,000,000

if __name__ == '__main__':
    df = load_and_prep_data(FILE)
    optimizer = RugbyScoutGA(df, LOWER_BUDGET)
    best_team = optimizer.run()
    display_team(df, best_team, budget=LOWER_BUDGET)
