import sys
sys.path.insert(0, 'd:\\xampp\\htdocs\\fyp')

from app import RugbyScoutGA, STARTER_POSITIONS

print("="*60)
print("Testing 10s format")
print("="*60)

ga_10s = RugbyScoutGA(budget=3000000, game_mode='10s', strategies=['Scrum'])
result_10s = ga_10s.run()

print(f"Starters: {len(result_10s['starters'])} players")
print(f"Reserves: {len(result_10s['reserves'])} players")
positions = {}
for p in result_10s['starters']:
    pos = p['position']
    positions[pos] = positions.get(pos, 0) + 1

print("\nRequired vs Actual:")
for pos in STARTER_POSITIONS['10s']:
    required = STARTER_POSITIONS['10s'][pos]
    actual = positions.get(pos, 0)
    match = "✅" if actual == required else "❌"
    print(f"  {match} {pos}: {required} required, {actual} actual")

print("\n" + "="*60)
print("Testing 15s format")
print("="*60)

ga_15s = RugbyScoutGA(budget=3000000, game_mode='15s', strategies=['Scrum'])
result_15s = ga_15s.run()

print(f"Starters: {len(result_15s['starters'])} players")
print(f"Reserves: {len(result_15s['reserves'])} players")
positions = {}
for p in result_15s['starters']:
    pos = p['position']
    positions[pos] = positions.get(pos, 0) + 1

print("\nRequired vs Actual:")
for pos in STARTER_POSITIONS['15s']:
    required = STARTER_POSITIONS['15s'][pos]
    actual = positions.get(pos, 0)
    match = "✅" if actual == required else "❌"
    print(f"  {match} {pos}: {required} required, {actual} actual")
