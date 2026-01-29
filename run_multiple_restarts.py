import time
import rugby_scouting_ga as r
from rugby_scouting_ga import load_and_prep_data, RugbyScoutGA, display_team

FILE = 'Statistic on best rugby players 2023-2024.csv'
BUDGET = 3000000
RESTARTS = 3
POP = 30
GEN = 70

r.POPULATION_SIZE = POP
r.GENERATIONS = GEN

if __name__ == '__main__':
    df = load_and_prep_data(FILE)
    best = None
    best_fit = -1

    for i in range(RESTARTS):
        start = time.time()
        print('\n' + '='*50)
        print(f'Restart {i+1}/{RESTARTS} — POP={POP}, GEN={GEN}')
        print('='*50)
        optimizer = RugbyScoutGA(df, BUDGET)
        # Limit randomized attempts to speed up initial population generation when budget is tight
        # Use a small attempt budget to avoid expensive population-building (keeps runs fast)
        optimizer.generate_budget_compliant_team = lambda randomize=True, attempts=None: RugbyScoutGA.generate_budget_compliant_team(optimizer, randomize=randomize, attempts=50)
        # Seed randomness per restart for reproducibility
        import random as _rnd
        _rnd.seed(i+123)
        team = optimizer.run()
        if team is None:
            print('No feasible team for this restart (budget/data).')
            continue
        fit = optimizer.calculate_fitness(team)
        elapsed = time.time() - start
        print(f'Restart {i+1} finished in {elapsed:.1f}s — Fitness: {fit:.2f}')
        if fit > best_fit:
            best_fit = fit
            best = (i+1, fit, team, optimizer)

    print('\n' + '='*50)
    if best is None:
        print('No feasible solutions found across restarts.')
    else:
        print(f'Best run: Restart #{best[0]} with fitness {best[1]:.2f}')
        display_team(df, best[2], budget=BUDGET)
    print('='*50)
