"""
Test strategy selection - verify max performance score and min budget
"""
import sys
sys.path.insert(0, 'd:\\xampp\\htdocs\\fyp')

from app import RugbyScoutGA

print("Testing Strategy Selection & Optimization")
print("="*60)

# Test 1: Scrum strategy (heavy, tall players)
print("\n1️⃣ Testing SCRUM Strategy (prefer heavy/tall)")
ga_scrum = RugbyScoutGA(budget=3000000, game_mode='15s', strategies=['Scrum'])
result_scrum = ga_scrum.run()

print(f"Total Score: {result_scrum.get('total_score', 'N/A')}")
print(f"Total Cost: ${result_scrum.get('total_cost', 0):,}")
print(f"Budget Used: {(result_scrum.get('total_cost', 0) / 3000000 * 100):.1f}%")
print(f"Minimum Budget: ${result_scrum.get('minimum_budget', 0):,}")

print("\nStarters sample:")
for i, p in enumerate(result_scrum['starters'][:5]):
    print(f"  {i+1}. {p['name']}: {p['position']} - ${p['salary']:,} - Score {p['score']}")

print("\n" + "="*60)
print("\n2️⃣ Testing LINEOUT Strategy (prefer tall)")
ga_lineout = RugbyScoutGA(budget=3000000, game_mode='15s', strategies=['Lineout'])
result_lineout = ga_lineout.run()

print(f"Total Score: {result_lineout.get('total_score', 'N/A')}")
print(f"Total Cost: ${result_lineout.get('total_cost', 0):,}")
print(f"Budget Used: {(result_lineout.get('total_cost', 0) / 3000000 * 100):.1f}%")
print(f"Minimum Budget: ${result_lineout.get('minimum_budget', 0):,}")

print("\nStarters sample:")
for i, p in enumerate(result_lineout['starters'][:5]):
    print(f"  {i+1}. {p['name']}: {p['position']} - ${p['salary']:,} - Score {p['score']}")

print("\n" + "="*60)
print("\n✅ Both should:")
print("  - Maximize performance score for selected strategy")
print("  - Minimize budget usage while meeting strategy requirements")
print("  - Different strategies = different player selections")
