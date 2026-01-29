import time
import random
import pandas as pd
from rugby_scouting_ga import load_and_prep_data, RugbyScoutGA, display_team

FILE = 'Statistic on best rugby players 2023-2024.csv'
BUDGET = 3000000
POPULATION = 80
GENERATIONS = 150
ATTEMPTS = 50
OUT_CSV = 'pareto_front_long.csv'
OUT_FEAS = 'pareto_front_long_feasible.csv'
OUT_LEX = 'pareto_lexico_best.csv'

# Reuse functions from run_nsga2: evaluate, dominates, nondominated_sort, crowding_distance

def evaluate(optimizer, team):
    df = optimizer.df
    team_data = df.loc[team]
    total_salary = int(team_data['Salary'].sum())
    total_score = float(team_data['Performance_Score'].sum())
    return (-total_score, total_salary)  # minimize


def dominates(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def nondominated_sort(pop_objs):
    S = [set() for _ in range(len(pop_objs))]
    n = [0] * len(pop_objs)
    fronts = [[]]
    for p in range(len(pop_objs)):
        for q in range(len(pop_objs)):
            if p == q:
                continue
            if dominates(pop_objs[p], pop_objs[q]):
                S[p].add(q)
            elif dominates(pop_objs[q], pop_objs[p]):
                n[p] += 1
        if n[p] == 0:
            fronts[0].append(p)
    i = 0
    while fronts[i]:
        Q = []
        for p in fronts[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    Q.append(q)
        i += 1
        fronts.append(Q)
    return [front for front in fronts if front]


def crowding_distance(front, pop_objs):
    dist = {i: 0.0 for i in front}
    num_obj = len(pop_objs[0])
    for m in range(num_obj):
        front_sorted = sorted(front, key=lambda idx: pop_objs[idx][m])
        fmin = pop_objs[front_sorted[0]][m]
        fmax = pop_objs[front_sorted[-1]][m]
        dist[front_sorted[0]] = float('inf')
        dist[front_sorted[-1]] = float('inf')
        if fmax == fmin:
            continue
        for i in range(1, len(front_sorted)-1):
            prevv = pop_objs[front_sorted[i-1]][m]
            nextv = pop_objs[front_sorted[i+1]][m]
            dist[front_sorted[i]] += (nextv - prevv) / (fmax - fmin)
    return dist


if __name__ == '__main__':
    df = load_and_prep_data(FILE)
    optimizer = RugbyScoutGA(df, BUDGET)

    if not optimizer.feasible:
        print('Dataset/budget infeasible — cannot proceed.')
        raise SystemExit(1)

    print(f"Starting long NSGA-II: POP={POPULATION}, GEN={GENERATIONS}, attempts={ATTEMPTS}")

    # Initial population
    pop = []
    attempts_fill = 0
    while len(pop) < POPULATION and attempts_fill < POPULATION * 40:
        team = optimizer.generate_budget_compliant_team(randomize=True, attempts=ATTEMPTS)
        if team is None:
            break
        if team not in pop:
            pop.append(team)
        attempts_fill += 1
    while len(pop) < POPULATION:
        pop.append(optimizer.create_random_team())

    print(f"Initial pop: {len(pop)}")
    pop_objs = [evaluate(optimizer, team) for team in pop]

    start = time.time()
    for gen in range(GENERATIONS):
        offspring = []
        while len(offspring) < POPULATION:
            p1 = random.choice(pop)
            p2 = random.choice(pop)
            c1, c2 = optimizer.crossover(p1, p2)
            o1 = optimizer.mutate(c1)
            o2 = optimizer.mutate(c2)
            offspring.append(o1)
            offspring.append(o2)
        offspring = offspring[:POPULATION]

        combined = pop + offspring
        combined_objs = [evaluate(optimizer, t) for t in combined]

        fronts = nondominated_sort(combined_objs)
        new_pop = []
        ranks = [None] * len(combined)
        current = 0
        while len(new_pop) + len(fronts[current]) <= POPULATION:
            for idx in fronts[current]:
                new_pop.append(combined[idx])
                ranks[idx] = current
            current += 1
            if current >= len(fronts):
                break
        if len(new_pop) < POPULATION:
            last_front = fronts[current]
            distances = crowding_distance(last_front, combined_objs)
            sorted_last = sorted(last_front, key=lambda idx: distances[idx], reverse=True)
            for idx in sorted_last:
                if len(new_pop) < POPULATION:
                    new_pop.append(combined[idx])
                    ranks[idx] = current
                else:
                    break
        pop = new_pop
        pop_objs = [evaluate(optimizer, team) for team in pop]

        if gen % 10 == 0:
            scores = [(-o[0], o[1]) for o in pop_objs]
            best = max(scores, key=lambda s: s[0])
            print(f"Gen {gen}: Best score = {best[0]:.2f}, salary = ${best[1]:,}")

    elapsed = time.time() - start
    print(f"Finished NSGA-II in {elapsed:.1f}s")

    # Save full pareto front from final population
    final_objs = [evaluate(optimizer, t) for t in pop]
    fronts = nondominated_sort(final_objs)
    pareto_idx = fronts[0]
    pareto = []
    for idx in pareto_idx:
        sc, sal = final_objs[idx]
        pareto.append({'score': -sc, 'salary': sal, 'team': '|'.join(map(str, pop[idx]))})

    pareto_df = pd.DataFrame(pareto).sort_values(['score', 'salary'], ascending=[False, True])
    pareto_df.to_csv(OUT_CSV, index=False)
    print(f"Pareto front saved to {OUT_CSV} (size {len(pareto_df)})")

    # Filter feasible
    feasible = pareto_df[pareto_df['salary'] <= BUDGET].copy()
    feasible = feasible.drop_duplicates(subset=['team', 'salary', 'score']).reset_index(drop=True)
    feasible = feasible.sort_values(['score', 'salary'], ascending=[False, True]).reset_index(drop=True)
    feasible.to_csv(OUT_FEAS, index=False)
    print(f"Feasible Pareto solutions (<= ${BUDGET:,}): {len(feasible)} saved to {OUT_FEAS}")

    if feasible.empty:
        print('No budget-feasible Pareto solutions.')
        raise SystemExit(0)

    # Lexicographic selection: pick highest score, then lowest salary among ties
    max_score = feasible['score'].max()
    best_by_score = feasible[feasible['score'] == max_score]
    best_lex = best_by_score.loc[best_by_score['salary'].idxmin()]

    # Save lexicographic best
    pd.DataFrame([best_lex]).to_csv(OUT_LEX, index=False)
    print('Lexicographic best saved to', OUT_LEX)

    # Display chosen team
    team_indices = list(map(int, best_lex['team'].split('|')))
    print('\nLexicographic best (highest score, then lowest salary):')
    display_team(df, team_indices, budget=BUDGET)

    print('\nDone.')
