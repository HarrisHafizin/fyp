from app import RugbyScoutGA

print("Testing Score Quality with Increased GA Parameters")
print("="*70)

for mode in ['7s', '10s', '15s']:
    print(f"\n{mode.upper()} FORMAT")
    print("-"*70)
    
    ga = RugbyScoutGA(budget=3000000, game_mode=mode, strategies=['Scrum'])
    result = ga.run()
    
    total_salary = sum(p['salary'] for p in result['starters'] + result['reserves'])
    total_score = sum(p['score'] for p in result['starters'] + result['reserves'])
    
    print(f"Starters: {len(result['starters'])} | Reserves: {len(result['reserves'])}")
    print(f"Total Cost: ${total_salary:,}")
    print(f"Total Score: {total_score:.2f}")
    print(f"Budget Used: {(total_salary/3000000)*100:.1f}%")
    print(f"Budget Remaining: ${3000000 - total_salary:,}")
    print(f"Within Budget: {'✅ YES' if total_salary <= 3000000 else '❌ NO'}")

print("\n" + "="*70)
print("✅ All formats should:")
print("  - Respect budget constraint")
print("  - Have good performance scores")
print("  - Use budget efficiently")
