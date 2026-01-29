import sys
sys.path.insert(0, 'd:\\xampp\\htdocs\\fyp')

from app import RugbyScoutGA

print("Testing position standardization...")

# Create GA instance for 7s
ga_7s = RugbyScoutGA(budget=3000000, game_mode='7s', strategies=['Scrum'])
print(f"\n✅ 7s initialized")
print(f"Data loaded: {len(ga_7s.df)} players")
print(f"Position types in data: {ga_7s.df['Position'].unique()}")

# Check if positions in STARTER_POSITIONS exist in data
from app import STARTER_POSITIONS
print(f"\n7s requirements: {STARTER_POSITIONS['7s']}")
print(f"Required positions exist in data:")
for pos, count in STARTER_POSITIONS['7s'].items():
    count_in_data = len(ga_7s.df[ga_7s.df['Position'] == pos])
    print(f"  {pos}: {count} needed, {count_in_data} available")

print("\n" + "="*50)
print("Running GA for 7s...")
try:
    result = ga_7s.run()
    print(f"✅ GA completed successfully")
    print(f"Starters: {len(result['starters'])} players")
    print(f"Reserves: {len(result['reserves'])} players")
    print("\nStarters by position:")
    positions = {}
    for p in result['starters']:
        pos = p['position']
        positions[pos] = positions.get(pos, 0) + 1
    for pos, count in sorted(positions.items()):
        print(f"  {pos}: {count}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
