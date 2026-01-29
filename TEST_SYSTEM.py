#!/usr/bin/env python3
"""
Test script to verify the entire Rugby Scout system is working correctly.
Run this to diagnose any issues with the backend or API.
"""

import requests
import time
import sys

print("="*80)
print("RUGBY SCOUT ELITE - SYSTEM VERIFICATION TEST")
print("="*80)

tests_passed = 0
tests_failed = 0

def test(name, func):
    """Run a test and track results"""
    global tests_passed, tests_failed
    print(f"\n[TEST] {name}")
    try:
        func()
        print("  Status: PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"  Status: FAILED - {str(e)}")
        tests_failed += 1
    except Exception as e:
        print(f"  Status: ERROR - {str(e)}")
        tests_failed += 1

# Test 1: Homepage loads
def test_homepage():
    response = requests.get('http://localhost:5000/', timeout=5)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert len(response.text) > 10000, "Homepage content too small"
    print(f"  Homepage loads successfully ({len(response.text)} bytes)")

test("1. Homepage Load", test_homepage)

# Test 2: API responds to optimization request
def test_api_basic():
    response = requests.post('http://localhost:5000/optimize',
        json={'budget': 7000000, 'mode': '15s', 'strategies': ['Scrum']},
        timeout=60
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data['status'] == 'success', f"Expected success, got {data['status']}"
    assert 'starters' in data, "Missing starters in response"
    assert 'reserves' in data, "Missing reserves in response"
    assert 'total_cost' in data, "Missing total_cost in response"
    assert 'total_score' in data, "Missing total_score in response"
    print(f"  API returns valid response with {len(data['starters'])} starters and {len(data['reserves'])} reserves")

test("2. API Basic Response", test_api_basic)

# Test 3: Budget constraint enforcement
def test_budget_constraint():
    response = requests.post('http://localhost:5000/optimize',
        json={'budget': 7000000, 'mode': '15s', 'strategies': ['Scrum']},
        timeout=60
    )
    data = response.json()
    
    # Check that team is within budget (or marked as over-budget if too low)
    total_cost = data['total_cost']
    budget = data['budget']
    
    if total_cost > budget:
        # System marks it as over-budget
        assert data['is_over_budget'] == True, "Should mark as over-budget"
        assert 'minimum_budget' in data, "Should provide minimum_budget info"
        print(f"  Budget constraint detected: Cost ${total_cost:,} > Budget ${budget:,}")
        print(f"  Minimum budget returned: ${data['minimum_budget']:,}")
    else:
        # Team is within budget
        assert data['is_over_budget'] == False, "Should not mark as over-budget"
        print(f"  Team within budget: ${total_cost:,} <= ${budget:,}")

test("3. Budget Constraint Enforcement", test_budget_constraint)

# Test 4: Multiple strategies
def test_multiple_strategies():
    strategies = ['Scrum', 'Defensive Play', 'Attack Focus']
    response = requests.post('http://localhost:5000/optimize',
        json={'budget': 8000000, 'mode': '10s', 'strategies': strategies},
        timeout=60
    )
    data = response.json()
    assert data['status'] == 'success', "API should handle multiple strategies"
    assert data['strategies'] == strategies, "Strategies should match request"
    print(f"  Multiple strategies work: {strategies}")
    print(f"  Team score: {data['total_score']}")

test("4. Multiple Strategies Support", test_multiple_strategies)

# Test 5: Different game formats
def test_game_formats():
    formats = {
        '7s': 7,
        '10s': 10,
        '15s': 15
    }
    
    for mode, expected_starters in formats.items():
        response = requests.post('http://localhost:5000/optimize',
            json={'budget': 5000000, 'mode': mode, 'strategies': ['Scrum']},
            timeout=60
        )
        data = response.json()
        assert data['status'] == 'success', f"Failed for {mode}"
        assert len(data['starters']) == expected_starters, f"Wrong starter count for {mode}"
        print(f"  {mode} format: {len(data['starters'])} starters, {len(data['reserves'])} reserves")

test("5. Game Formats (7s, 10s, 15s)", test_game_formats)

# Test 6: Analytics data
def test_analytics():
    response = requests.post('http://localhost:5000/optimize',
        json={'budget': 7000000, 'mode': '15s', 'strategies': ['Scrum']},
        timeout=60
    )
    data = response.json()
    assert 'analytics' in data, "Missing analytics"
    analytics = data['analytics']
    assert 'avg_age' in analytics, "Missing avg_age"
    assert 'avg_weight' in analytics, "Missing avg_weight"
    assert 'avg_height' in analytics, "Missing avg_height"
    assert 'attack_potential' in analytics, "Missing attack_potential"
    print(f"  Analytics: Age={analytics['avg_age']} yrs, Weight={analytics['avg_weight']} kg, Height={analytics['avg_height']} m")

test("6. Analytics Data", test_analytics)

# Test 7: Performance (response time)
def test_performance():
    start = time.time()
    response = requests.post('http://localhost:5000/optimize',
        json={'budget': 7000000, 'mode': '15s', 'strategies': ['Scrum']},
        timeout=60
    )
    elapsed = time.time() - start
    assert elapsed < 30, f"Response took too long: {elapsed:.1f}s"
    print(f"  Response time: {elapsed:.1f} seconds")

test("7. Performance Check", test_performance)

# Summary
print("\n" + "="*80)
print(f"RESULTS: {tests_passed} PASSED, {tests_failed} FAILED")
print("="*80)

if tests_failed == 0:
    print("\nAll tests PASSED! The system is working correctly.")
    print("\nYou can now:")
    print("  1. Open http://localhost:5000 in your browser")
    print("  2. Select strategies (or leave default)")
    print("  3. Choose game format (7s, 10s, or 15s)")
    print("  4. Set budget (slider)")
    print("  5. Click 'RUN AI SCOUTING'")
    print("  6. Wait for results to display (loading bar will show progress)")
    sys.exit(0)
else:
    print(f"\nSome tests FAILED. Please check the error messages above.")
    sys.exit(1)
