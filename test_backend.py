import requests
import json

# Test 7s format
payload_7s = {
    "budget": 3000000,
    "mode": "7s",
    "strategies": ["Scrum"]
}

print("Testing 7s format...")
response = requests.post('http://localhost:5000/optimize', json=payload_7s)
data = response.json()

if 'starters' in data:
    print(f"✅ 7s Starters: {len(data['starters'])} players")
    for p in data['starters']:
        print(f"  - {p['position']}: {p['name']}")
else:
    print("❌ Error:", data)

print("\n" + "="*50 + "\n")

# Test 10s format
payload_10s = {
    "budget": 3000000,
    "mode": "10s",
    "strategies": ["Scrum"]
}

print("Testing 10s format...")
response = requests.post('http://localhost:5000/optimize', json=payload_10s)
data = response.json()

if 'starters' in data:
    print(f"✅ 10s Starters: {len(data['starters'])} players")
    positions = {}
    for p in data['starters']:
        pos = p['position']
        positions[pos] = positions.get(pos, 0) + 1
    
    for pos, count in sorted(positions.items()):
        print(f"  - {pos}: {count}")
else:
    print("❌ Error:", data)

print("\n" + "="*50 + "\n")

# Test 15s format
payload_15s = {
    "budget": 3000000,
    "mode": "15s",
    "strategies": ["Scrum"]
}

print("Testing 15s format...")
response = requests.post('http://localhost:5000/optimize', json=payload_15s)
data = response.json()

if 'starters' in data:
    print(f"✅ 15s Starters: {len(data['starters'])} players")
    positions = {}
    for p in data['starters']:
        pos = p['position']
        positions[pos] = positions.get(pos, 0) + 1
    
    for pos, count in sorted(positions.items()):
        print(f"  - {pos}: {count}")
else:
    print("❌ Error:", data)
