import time
import random
import pandas as pd
from rugby_scouting_ga import load_and_prep_data, RugbyScoutGA, display_team, TEAM_STRUCTURE

FILE = 'Statistic on best rugby players 2023-2024.csv'
BUDGET = 3000000
POPULATION = 40
GENERATIONS = 60
ATTEMPTS = 50  # attempts used in randomized budget-compliant sampling (smaller -> faster)
OUT_CSV = 'pareto_front.csv'

# Objectives: minimize [-total_score, total_salary] i.e. f1 = -score (to minimize), f2 = salary

def evaluate(optimizer, team):
    df = optimizer.df
    team_data = df.loc[team]
    total_salary = int(team_data['Salary'].sum())
    total_score = float(team_data['Performance_Score'].sum())
    return (-total_score, total_salary)  # minimize these


def dominates(a, b):
    # a and b are objective tuples (f1, f2) to be minimized
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def nondominated_sort(pop_objs):
    # pop_objs: list of (obj_tuple)
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
    # last front may be empty
    return [front for front in fronts if front]


def crowding_distance(front, pop_objs):
    # front: list of indices
    dist = {i: 0.0 for i in front}
    num_obj = len(pop_objs[0])
    for m in range(num_obj):
        front_sorted = sorted(front, key=lambda idx: pop_objs[idx][m])
        fmin = pop_objs[front_sorted[0]][m]
        fmax = pop_objs[front_sorted[-1]][m]
        # set extremes to large distance
        dist[front_sorted[0]] = float('inf')
        dist[front_sorted[-1]] = float('inf')
        if fmax == fmin:
            continue
        for i in range(1, len(front_sorted)-1):
            prevv = pop_objs[front_sorted[i-1]][m]
            nextv = pop_objs[front_sorted[i+1]][m]
            dist[front_sorted[i]] += (nextv - prevv) / (fmax - fmin)
    return dist


def tournament_selection(pop, ranks, distances):
    a, b = random.randrange(len(pop)), random.randrange(len(pop))
    # compare ranks (lower is better), then crowding distance (higher is better)
    if ranks[a] < ranks[b]:
        return pop[a]
    if ranks[b] < ranks[a]:
        return pop[b]
    # same rank
    if distances.get(a, 0) >= distances.get(b, 0):
        return pop[a]
    return pop[b]


if __name__ == '__main__':
    df = load_and_prep_data(FILE)
    optimizer = RugbyScoutGA(df, BUDGET)

    if not optimizer.feasible:
        print('Dataset/budget infeasible — NSGA-II cannot proceed.')
        raise SystemExit(1)

    # Fill initial population with budget-compliant teams
    pop = []
    attempts_fill = 0
    while len(pop) < POPULATION and attempts_fill < POPULATION * 20:
        team = optimizer.generate_budget_compliant_team(randomize=True, attempts=ATTEMPTS)
        if team is None:
            break
        if team not in pop:
            pop.append(team)
        attempts_fill += 1
    # fallback: fill with random teams
    while len(pop) < POPULATION:
        pop.append(optimizer.create_random_team())

    print(f"Initial population size: {len(pop)}")

    # Evaluate objectives
    pop_objs = [evaluate(optimizer, team) for team in pop]

    start = time.time()
    for gen in range(GENERATIONS):
        # create offspring population
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

        # nondominated sort
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
            # need to select some individuals from current front by crowding distance
            last_front = fronts[current]
            distances = crowding_distance(last_front, combined_objs)
            # sort by distance desc
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
            # report current best (by score)
            scores = [(-o[0], o[1]) for o in pop_objs]  # (score, salary)
            best = max(scores, key=lambda s: s[0])
            print(f"Generasi {gen}: Best score = {best[0]:.2f}, salary = ${best[1]:,}")

    elapsed = time.time() - start
    print(f"NSGA-II finished in {elapsed:.1f}s")

    # Compute final Pareto front
    final_objs = [evaluate(optimizer, t) for t in pop]
    fronts = nondominated_sort(final_objs)
    pareto_idx = fronts[0]
    pareto = []
    for idx in pareto_idx:
        sc, sal = final_objs[idx]
        pareto.append({'score': -sc, 'salary': sal, 'team': '|'.join(map(str, pop[idx]))})

    pareto_df = pd.DataFrame(pareto).sort_values(['score', 'salary'], ascending=[False, True])
    pareto_df.to_csv(OUT_CSV, index=False)

    print(f"Pareto front size: {len(pareto_df)} — saved to {OUT_CSV}")
    # print top 5 Pareto solutions
    print(pareto_df.head(10))

    # Also display the team with highest score on the Pareto front
    best_idx = pareto_df['score'].idxmax()
    best_row = pareto_df.loc[best_idx]
    best_team_indices = list(map(int, best_row['team'].split('|')))

    print('\nBest Pareto solution (highest score among Pareto front):')
    display_team(df, best_team_indices, budget=BUDGET)

    # Mark todo as completed
    print('\nFinished short NSGA-II demo.')
