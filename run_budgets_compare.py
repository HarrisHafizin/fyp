from rugby_scouting_ga import load_and_prep_data, RugbyScoutGA, display_team

FILE = 'Statistic on best rugby players 2023-2024.csv'
BUDGETS = [2700000, 3000000]

if __name__ == '__main__':
    df = load_and_prep_data(FILE)
    for b in BUDGETS:
        print('\n' + '='*60)
        print(f'Running optimizer with BUDGET = ${b:,}')
        print('='*60)
        optimizer = RugbyScoutGA(df, b)
        best_team = optimizer.run()
        display_team(df, best_team, budget=b)
