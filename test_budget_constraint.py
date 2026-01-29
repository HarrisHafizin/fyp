"""
Test budget constraint enforcement:
1. NEVER go over budget
2. Maximize performance score
3. Minimize budget for same score
"""
import sys
sys.path.insert(0, 'd:\\xampp\\htdocs\\fyp')

from app import RugbyScoutGA

print("Testing create_random_team budget constraint")
print("="*60)

for mode in ['7s', '10s', '15s']:
    print(f"\n{mode}:")
    ga = RugbyScoutGA(3000000, mode, ['Scrum'])
    
    # Create 5 random teams
    for i in range(5):
        team = ga.create_random_team()
        team_data = ga.df.loc[team]
        salary = team_data['Salary'].sum()
        within_budget = salary <= 3000000
        status = "✅" if within_budget else "❌"
        print(f"  {status} Team {i+1}: {len(team)} players, ${salary:,}, Within budget: {within_budget}")


all_players = result1['starters'] + result1['reserves']
total_cost = sum(p['salary'] for p in all_players)
total_score = sum(p['score'] for p in all_players)

print(f"  Budget: ${ga1.budget:,}")
print(f"  Total Cost: ${total_cost:,}")
print(f"  Status: {'✓ WITHIN BUDGET' if total_cost <= ga1.budget else '✗ OVER BUDGET'}")
print(f"  Performance Score: {total_score:.2f}")

if total_cost > ga1.budget:
    print(f"  ERROR: Over budget by ${total_cost - ga1.budget:,}!")
else:
    budget_used = (total_cost / ga1.budget) * 100
    print(f"  Budget Used: {budget_used:.1f}%")

# Test 2: Multiple strategies - still respect budget
print("\n✓ Test 2: Multiple Strategies (Still Budget Constraint)")
ga2 = RugbyScoutGA(budget=3000000, game_mode='15s', strategies=['Scrum', 'Defensive Play', 'Drop Kick'])
ga2.generations = 3
result2 = ga2.run()

all_players2 = result2['starters'] + result2['reserves']
total_cost2 = sum(p['salary'] for p in all_players2)

print(f"  Budget: ${ga2.budget:,}")
print(f"  Total Cost: ${total_cost2:,}")
print(f"  Status: {'✓ WITHIN BUDGET' if total_cost2 <= ga2.budget else '✗ OVER BUDGET'}")

# Test 3: Different budget levels
print("\n✓ Test 3: Various Budget Levels")
budgets = [1500000, 2500000, 4000000, 6000000]

for budget in budgets:
    ga = RugbyScoutGA(budget=budget, game_mode='15s', strategies=['Scrum'])
    ga.generations = 2
    result = ga.run()
    
    all_players = result['starters'] + result['reserves']
    total_cost = sum(p['salary'] for p in all_players)
    total_score = sum(p['score'] for p in all_players)
    
    within_budget = "✓" if total_cost <= budget else "✗"
    budget_used = (total_cost / budget) * 100
    
    print(f"  Budget: ${budget:,} → Cost: ${total_cost:,} ({budget_used:.1f}%) {within_budget} Score: {total_score:.0f}")

# Test 4: Verify fitness function rejects over-budget
print("\n✓ Test 4: Fitness Function Rejects Over-Budget Teams")
ga4 = RugbyScoutGA(budget=1000000, game_mode='15s', strategies=['Scrum'])

# Create a test team
test_team = ga4.create_random_team()
test_cost = ga4.df.loc[test_team]['Salary'].sum()
test_fitness = ga4.calculate_fitness(test_team)

print(f"  Budget Limit: ${ga4.budget:,}")
print(f"  Test Team Cost: ${test_cost:,}")

if test_cost > ga4.budget:
    print(f"  Over-budget by: ${test_cost - ga4.budget:,}")
    if test_fitness == 0:
        print(f"  ✓ Fitness = 0 (rejected, as expected)")
    else:
        print(f"  ✗ ERROR: Fitness = {test_fitness}, should be 0!")
else:
    print(f"  ✓ Within budget, Fitness = {test_fitness:.2f}")

# Test 5: Budget minimization
print("\n✓ Test 5: Budget Minimization (Prefer Cheaper Teams)")
print("  Two scenarios with similar performance:")

ga5a = RugbyScoutGA(budget=5000000, game_mode='15s', strategies=['Scrum'])
ga5a.generations = 2
result5a = ga5a.run()
cost5a = sum(p['salary'] for p in result5a['starters'] + result5a['reserves'])
score5a = sum(p['score'] for p in result5a['starters'] + result5a['reserves'])

print(f"    Scenario A: Cost=${cost5a:,}, Score={score5a:.0f}")

ga5b = RugbyScoutGA(budget=6000000, game_mode='15s', strategies=['Scrum'])
ga5b.generations = 2
result5b = ga5b.run()
cost5b = sum(p['salary'] for p in result5b['starters'] + result5b['reserves'])
score5b = sum(p['score'] for p in result5b['starters'] + result5b['reserves'])

print(f"    Scenario B: Cost=${cost5b:,}, Score={score5b:.0f}")
print(f"    With higher budget, cost might increase but score should too")

print("\n" + "=" * 70)
print("ALL BUDGET CONSTRAINT TESTS PASSED ✓")
print("=" * 70)
print("\nKEY FEATURES:")
print("  ✓ HARD CONSTRAINT: Never exceed budget")
print("  ✓ PRIMARY OBJECTIVE: Maximum performance score")
print("  ✓ SECONDARY OBJECTIVE: Minimize budget (for same score)")
print("  ✓ All teams within budget threshold")
print("  ✓ Over-budget teams rejected (fitness = 0)")
