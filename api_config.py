"""
Rugby API Configuration
-----------------------
Simpan API credentials di sini.
JANGAN commit fail ini ke GitHub jika ada sensitive data!
"""

# API-Sports Rugby API Configuration
RUGBY_API_CONFIG = {
    'api_key': 'a929b192e5e96d5692ddfbf3bc649daa',  # Your API Key
    'base_url': 'https://v1.rugby.api-sports.io',
    'plan': 'Free',
    'daily_limit': 100
}

# Default League IDs for quick access
POPULAR_LEAGUES = {
    'super_rugby': 3,
    'six_nations': 6,
    'rugby_world_cup': 1,
    'premiership': 4,
    'top_14': 5,
    'pro14': 7
}

# Default Season
DEFAULT_SEASON = 2023
