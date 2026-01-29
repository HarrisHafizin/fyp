from rugby_scouting_ga import load_and_prep_data, RugbyScoutGA, display_team

FILE = 'Statistic on best rugby players 2023-2024.csv'
BUDGET = 1900000  # $1,900,000

if __name__ == '__main__':
    df = load_and_prep_data(FILE)
    optimizer = RugbyScoutGA(df, BUDGET)
    best_team = optimizer.run()
    display_team(df, best_team, budget=BUDGET)
