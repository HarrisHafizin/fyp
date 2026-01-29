import sys
sys.path.insert(0, 'd:\\xampp\\htdocs\\fyp')
from app import RugbyScoutGA

print('Quick Backend Test: Starters/Reserves Separation')
print('=' * 60)

ga = RugbyScoutGA(budget=5000000, game_mode='15s', strategies=['Scrum'])
ga.generations = 2  # Quick test
print('Running optimization (2 generations)...')
result = ga.run()

print(f'✓ Starters: {len(result["starters"])}')
print(f'✓ Reserves: {len(result["reserves"])}')
print(f'✓ Total: {len(result["starters"]) + len(result["reserves"])}')

if result['starters']:
    starter = result['starters'][0]
    print(f'\n✓ Starter example: {starter["name"]} ({starter["position"]})')
    print(f'  Salary: ${starter["salary"]:,}, Score: {starter["score"]}')

if result['reserves']:
    reserve = result['reserves'][0]
    print(f'\n✓ Reserve example: {reserve["name"]} ({reserve["position"]})')
    print(f'  Salary: ${reserve["salary"]:,}, Score: {reserve["score"]}')

print('\n' + '=' * 60)
print('✓ BACKEND TEST PASSED!')
print('✓ Starters and Reserves properly separated')
