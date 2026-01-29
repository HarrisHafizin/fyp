"""
Test Rugby API Connection
--------------------------
Fail ini untuk test sama ada API key anda berfungsi atau tidak.

ARAHAN:
1. Gantikan 'YOUR_API_KEY_HERE' dengan API key sebenar anda
2. Run fail ini: python test_rugby_api.py
"""

import requests

# ===========================================
# GANTIKAN DENGAN API KEY ANDA
# ===========================================
API_KEY = "bd24706d9ec6f4b97e1c4486bbccdf51"  # <-- TUKAR INI!
# ===========================================

BASE_URL = "https://v1.rugby.api-sports.io"

def test_connection():
    """Test basic API connection"""
    print("=" * 50)
    print("🏉 TESTING RUGBY API CONNECTION")
    print("=" * 50)
    
    headers = {
        'x-apisports-key': API_KEY
    }
    
    # Test 1: Check Account Status
    print("\n📡 Test 1: Checking Account Status...")
    try:
        response = requests.get(f"{BASE_URL}/status", headers=headers)
        data = response.json()
        
        if 'response' in data:
            account = data['response'].get('account', {})
            subscription = data['response'].get('subscription', {})
            requests_info = data['response'].get('requests', {})
            
            print(f"   ✅ Connection Successful!")
            print(f"   📧 Email: {account.get('email', 'N/A')}")
            print(f"   📦 Plan: {subscription.get('plan', 'N/A')}")
            print(f"   📊 Requests Today: {requests_info.get('current', 0)}/{requests_info.get('limit_day', 0)}")
        else:
            print(f"   ❌ Error: {data.get('errors', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection Failed: {e}")
        return False
    
    return True

def test_get_countries():
    """Test getting list of countries"""
    print("\n📡 Test 2: Getting Countries...")
    
    headers = {'x-apisports-key': API_KEY}
    
    try:
        response = requests.get(f"{BASE_URL}/countries", headers=headers)
        data = response.json()
        
        if data.get('results', 0) > 0:
            countries = data['response'][:5]  # First 5 countries
            print(f"   ✅ Found {data['results']} countries!")
            print(f"   📍 Sample countries:")
            for country in countries:
                print(f"      - {country.get('name', 'N/A')} ({country.get('code', 'N/A')})")
        else:
            print(f"   ⚠️ No countries found")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_get_leagues():
    """Test getting list of leagues"""
    print("\n📡 Test 3: Getting Rugby Leagues...")
    
    headers = {'x-apisports-key': API_KEY}
    
    try:
        response = requests.get(f"{BASE_URL}/leagues", headers=headers)
        data = response.json()
        
        if data.get('results', 0) > 0:
            leagues = data['response'][:5]  # First 5 leagues
            print(f"   ✅ Found {data['results']} leagues!")
            print(f"   🏆 Sample leagues:")
            for league in leagues:
                print(f"      - {league.get('name', 'N/A')} ({league.get('country', {}).get('name', 'N/A')})")
        else:
            print(f"   ⚠️ No leagues found")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_get_teams():
    """Test getting teams from a league"""
    print("\n📡 Test 4: Getting Rugby Teams...")
    
    headers = {'x-apisports-key': API_KEY}
    params = {
        'league': 3,  # Example: Super Rugby
        'season': 2023
    }
    
    try:
        response = requests.get(f"{BASE_URL}/teams", headers=headers, params=params)
        data = response.json()
        
        if data.get('results', 0) > 0:
            teams = data['response'][:5]  # First 5 teams
            print(f"   ✅ Found {data['results']} teams!")
            print(f"   🏉 Sample teams:")
            for team in teams:
                print(f"      - {team.get('name', 'N/A')} (ID: {team.get('id', 'N/A')})")
        else:
            print(f"   ⚠️ No teams found for this league/season")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Main function"""
    if API_KEY == "YOUR_API_KEY_HERE":
        print("=" * 50)
        print("⚠️  PERHATIAN!")
        print("=" * 50)
        print("\nSila tukar 'YOUR_API_KEY_HERE' dengan API key sebenar anda!")
        print("\nLangkah:")
        print("1. Buka fail test_rugby_api.py")
        print("2. Cari baris: API_KEY = \"YOUR_API_KEY_HERE\"")
        print("3. Gantikan dengan API key anda dari dashboard")
        print("4. Run semula: python test_rugby_api.py")
        return
    
    # Run tests
    if test_connection():
        test_get_countries()
        test_get_leagues()
        test_get_teams()
    
    print("\n" + "=" * 50)
    print("🏁 TEST COMPLETED!")
    print("=" * 50)
    print("\nJika semua test ✅, API key anda berfungsi dengan baik!")
    print("Seterusnya kita boleh integrate ke dalam sistem Rugby Genius.")

if __name__ == "__main__":
    main()
