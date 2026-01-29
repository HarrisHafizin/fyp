import sys
sys.path.insert(0, 'd:\\xampp\\htdocs\\fyp')

from app import RugbyScoutGA

print("Testing Score Quality for All Formats")
print("="*70)

# Test 7s
print("\n7️⃣s FORMAT")
print("-"*70)
ga_7s = RugbyScoutGA(budget=3000000, game_mode='7s', strategies=['Scrum'])

# Check team composition
sample_team = ga_7s.create_random_team()
sample_team_data = ga_7s.df.loc[sample_team]
sample_salary = sample_team_data['Salary'].sum()
sample_fitness = ga_7s.calculate_fitness(sample_team)

print(f"Sample team salary: ${sample_salary:,}")
print(f"Sample team fitness: {sample_fitness:.2f}")
print(f"Budget utilization: {(sample_salary/3000000)*100:.1f}%")

# Run full GA
result_7s = ga_7s.run()
total_salary = sum(p['salary'] for p in result_7s['starters'] + result_7s['reserves'])
total_score = sum(p['score'] for p in result_7s['starters'] + result_7s['reserves'])

print(f"\nBest team salary: ${total_salary:,}")
print(f"Best team score: {total_score:.2f}")
print(f"Budget utilization: {(total_salary/3000000)*100:.1f}%")
print(f"Budget remaining: ${3000000 - total_salary:,}")

print("\n" + "="*70)

# Test 10s
print("\n🔟s FORMAT")
print("-"*70)
ga_10s = RugbyScoutGA(budget=3000000, game_mode='10s', strategies=['Scrum'])

# Check team composition
sample_team = ga_10s.create_random_team()
sample_team_data = ga_10s.df.loc[sample_team]
sample_salary = sample_team_data['Salary'].sum()
sample_fitness = ga_10s.calculate_fitness(sample_team)

print(f"Sample team salary: ${sample_salary:,}")
print(f"Sample team fitness: {sample_fitness:.2f}")
print(f"Budget utilization: {(sample_salary/3000000)*100:.1f}%")

# Run full GA
result_10s = ga_10s.run()
total_salary = sum(p['salary'] for p in result_10s['starters'] + result_10s['reserves'])
total_score = sum(p['score'] for p in result_10s['starters'] + result_10s['reserves'])

print(f"\nBest team salary: ${total_salary:,}")
print(f"Best team score: {total_score:.2f}")
print(f"Budget utilization: {(total_salary/3000000)*100:.1f}%")
print(f"Budget remaining: ${3000000 - total_salary:,}")

print("\n" + "="*70)

# Test 15s
print("\n1️⃣5️⃣s FORMAT")
print("-"*70)
ga_15s = RugbyScoutGA(budget=3000000, game_mode='15s', strategies=['Scrum'])

# Check team composition
sample_team = ga_15s.create_random_team()
sample_team_data = ga_15s.df.loc[sample_team]
sample_salary = sample_team_data['Salary'].sum()
sample_fitness = ga_15s.calculate_fitness(sample_team)

print(f"Sample team salary: ${sample_salary:,}")
print(f"Sample team fitness: {sample_fitness:.2f}")
print(f"Budget utilization: {(sample_salary/3000000)*100:.1f}%")

# Run full GA
result_15s = ga_15s.run()
total_salary = sum(p['salary'] for p in result_15s['starters'] + result_15s['reserves'])
total_score = sum(p['score'] for p in result_15s['starters'] + result_15s['reserves'])

print(f"\nBest team salary: ${total_salary:,}")
print(f"Best team score: {total_score:.2f}")
print(f"Budget utilization: {(total_salary/3000000)*100:.1f}%")
print(f"Budget remaining: ${3000000 - total_salary:,}")

print("\n" + "="*70)
print("\n⚠️ Analysis:")
print("  If 7s/10s scores are much lower than 15s while budget available is high,")
print("  then GA is not exploring enough or fitness function has issues.")
