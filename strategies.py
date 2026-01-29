"""
Rugby Strategy Configuration & Attribute Mapping
Based on Basic Play, Tactical Play, and Contingency Play strategies
"""

# ==========================================
# STRATEGY DEFINITIONS
# ==========================================

STRATEGIES = {
    # =====================
    # BASIC PLAY STRATEGIES
    # =====================
    'Scrum': {
        'category': 'Basic Play',
        'description': 'Focus on scrum stability and set-piece dominance',
        'key_attributes': ['weight', 'height', 'Position'],
        'preferred_positions': ['Prop', 'Hooker', 'Secondrow'],
        'fitness_weights': {
            'weight': 0.30,           # Heavy weight preferred
            'height': 0.20,           # Tall preferred
            'starter': 0.25,          # Experience as starter
            'club_points': 0.10,      # Club performance
            'National_Points': 0.15   # National performance
        },
        'constraints': {
            'weight_min': 105,        # kg
            'height_min': 1.80,       # meters
            'height_max': 2.05,       # meters
            'min_starters_required': 5
        }
    },
    
    'Lineout': {
        'category': 'Basic Play',
        'description': 'Focus on lineout execution and jumping ability',
        'key_attributes': ['height', 'starter', 'Position'],
        'preferred_positions': ['Secondrow', 'Backrow'],
        'fitness_weights': {
            'height': 0.35,           # Height is critical for lineout
            'starter': 0.30,          # Game experience
            'club_points': 0.20,      # Club consistency
            'weight': 0.10,           # Some weight needed
            'National_Points': 0.05
        },
        'constraints': {
            'height_min': 1.95,       # meters
            'min_starters_required': 6
        }
    },
    
    'Ruck': {
        'category': 'Basic Play',
        'description': 'Focus on ruck dominance and ball security',
        'key_attributes': ['weight', 'starter', 'Position'],
        'preferred_positions': ['Backrow', 'Prop', 'Hooker'],
        'fitness_weights': {
            'weight': 0.30,           # Body mass for ruck
            'starter': 0.35,          # Experience crucial
            'club_points': 0.20,      # Consistency
            'height': 0.10,           # Some height
            'National_Points': 0.05
        },
        'constraints': {
            'weight_min': 100,        # kg
            'weight_max': 120,        # kg - balanced
            'min_starters_required': 6
        }
    },
    
    'Tackle': {
        'category': 'Basic Play',
        'description': 'Focus on defensive strength and tackling ability',
        'key_attributes': ['weight', 'height', 'Position'],
        'preferred_positions': ['Secondrow', 'Backrow'],
        'fitness_weights': {
            'weight': 0.35,           # Heavy for tackles
            'height': 0.30,           # Height advantage
            'starter': 0.20,          # Experience
            'club_points': 0.10,      # Consistency
            'National_Points': 0.05
        },
        'constraints': {
            'weight_min': 80,         # kg
            'height_min': 1.85,       # meters
            'yellow_card_max': 2,     # Discipline
            'red_card_max': 0
        }
    },
    
    # =====================
    # TACTICAL PLAY STRATEGIES
    # =====================
    'Pick and Go': {
        'category': 'Tactical Play',
        'description': 'Short-range attacking through forwards',
        'key_attributes': ['weight', 'height', 'starter', 'club_starter'],
        'preferred_positions': ['Prop', 'Hooker', 'Backrow'],
        'fitness_weights': {
            'weight': 0.25,           # Some bulk needed
            'height': 0.15,           # Less critical
            'club_starter': 0.30,     # Club experience key
            'starter': 0.20,          # National experience
            'club_points': 0.10
        },
        'constraints': {
            'weight_min': 100,        # kg
            'club_starter_min': 15,   # At least 15 club matches started
            'min_starters_required': 6
        }
    },
    
    'Grubber Kick': {
        'category': 'Tactical Play',
        'description': 'Ground-level kicking for territorial gain',
        'key_attributes': ['weight', 'age', 'club_points'],
        'preferred_positions': ['Flyhalf', 'Scrumhalf'],
        'fitness_weights': {
            'weight': 0.15,           # Light and quick
            'age': 0.15,              # Experience
            'club_points': 0.35,      # Kicking accuracy via points
            'National_Points': 0.20,  # National performance
            'starter': 0.15
        },
        'constraints': {
            'weight_max': 95,         # kg
            'height_min': 1.70,       # meters
            'height_max': 1.85,       # meters
            'club_points_min': 10     # Proven kicker
        }
    },
    
    'Drop Kick': {
        'category': 'Tactical Play',
        'description': 'Precision kicking for field position',
        'key_attributes': ['age', 'club_points', 'national_points', 'starter'],
        'preferred_positions': ['Flyhalf'],
        'fitness_weights': {
            'age': 0.20,              # Experience critical
            'club_points': 0.25,      # Club kicking performance
            'National_Points': 0.30,  # National kicking performance
            'starter': 0.25           # Match experience
        },
        'constraints': {
            'age_min': 28,            # Mature kickers
            'club_points_min': 20,    # High scoring
            'national_points_min': 10,
            'starter_min': 10         # Minimum national caps
        }
    },
    
    'Cross Kick': {
        'category': 'Tactical Play',
        'description': 'Cross-field kicking for wing attacks',
        'key_attributes': ['height', 'starter', 'national_min', 'club_min'],
        'preferred_positions': ['Flyhalf'],
        'fitness_weights': {
            'height': 0.20,           # Field vision
            'starter': 0.25,          # Game awareness
            'National_Points': 0.30,  # National performance
            'club_points': 0.25       # Club consistency
        },
        'constraints': {
            'height_min': 1.75,       # meters
            'height_max': 1.85,       # meters
            'starter_min': 10,        # National experience
            'club_points_min': 15
        }
    },
    
    'Quick Tap': {
        'category': 'Tactical Play',
        'description': 'Quick tactical tapping for advantage',
        'key_attributes': ['weight', 'age', 'club_try', 'national_min', 'starter'],
        'preferred_positions': ['Scrumhalf', 'Fullback'],
        'fitness_weights': {
            'weight': 0.15,           # Lighter and quicker
            'age': 0.15,              # Experience
            'club_try': 0.25,         # Try-scoring ability
            'National_Points': 0.25,  # National performance
            'starter': 0.20
        },
        'constraints': {
            'weight_max': 90,         # kg
            'age_max': 25,            # Younger/quicker players
            'club_try_min': 3,        # Try scorers
            'starter_min': 6
        }
    },
    
    'Maul': {
        'category': 'Tactical Play',
        'description': 'Ball-carrying through contact',
        'key_attributes': ['weight', 'height', 'club_starter'],
        'preferred_positions': ['Prop', 'Secondrow', 'Hooker'],
        'fitness_weights': {
            'weight': 0.35,           # Heavy for maul
            'height': 0.25,           # Physical presence
            'club_starter': 0.20,     # Match time
            'starter': 0.15,          # National experience
            'club_points': 0.05
        },
        'constraints': {
            'weight_min': 105,        # kg
            'height_min': 1.85,       # meters
            'club_starter_min': 15
        }
    },
    
    'Defensive Play': {
        'category': 'Tactical Play',
        'description': 'Strong defensive formation and positioning',
        'key_attributes': ['weight', 'height', 'yellow_card', 'red_card', 'club_min', 'national_min'],
        'preferred_positions': ['Backrow', 'Lock', 'Hooker'],
        'fitness_weights': {
            'weight': 0.30,           # Defensive mass
            'height': 0.25,           # Physical presence
            'club_Min': 0.20,         # Match time
            'national_match': 0.15,   # National experience
            'starter': 0.10
        },
        'constraints': {
            'weight_min': 103,        # kg
            'height_min': 1.85,       # meters
            'yellow_card_max': 0,     # No yellow cards
            'red_card_max': 0         # No red cards
        }
    },
    
    # =====================
    # CONTINGENCY PLAY STRATEGIES
    # =====================
    'Side Step': {
        'category': 'Contingency Play',
        'description': 'Evasion and agility-based attack',
        'key_attributes': ['weight', 'height', 'starter', 'national_min', 'club_min'],
        'preferred_positions': ['Wing', 'Fullback'],
        'fitness_weights': {
            'weight': 0.20,           # Lighter for agility
            'height': 0.15,           # Vision
            'starter': 0.30,          # Match experience
            'national_match': 0.20,   # National experience
            'club_points': 0.15
        },
        'constraints': {
            'weight_max': 90,         # kg
            'height_min': 1.70,       # meters
            'height_max': 1.83,       # meters
            'starter_min': 6
        }
    },
    
    'Quick Tap (Contingency)': {
        'category': 'Contingency Play',
        'description': 'Quick tap for penalty advantage',
        'key_attributes': ['weight', 'height', 'age', 'national_min', 'starter'],
        'preferred_positions': ['Scrumhalf', 'Wing'],
        'fitness_weights': {
            'weight': 0.15,           # Light and quick
            'height': 0.15,           # Field vision
            'age': 0.20,              # Decision-making experience
            'starter': 0.30,          # Match experience
            'National_Points': 0.20
        },
        'constraints': {
            'weight_max': 90,         # kg
            'height_min': 1.70,       # meters
            'height_max': 1.85,       # meters
            'starter_min': 6
        }
    },
    
    'Chip Kick': {
        'category': 'Contingency Play',
        'description': 'High-arcing kick for space creation',
        'key_attributes': ['weight', 'height', 'starter'],
        'preferred_positions': ['Flyhalf', 'Fullback'],
        'fitness_weights': {
            'weight': 0.15,           # Light for balance
            'height': 0.20,           # Field vision
            'starter': 0.35,          # Match experience
            'National_Points': 0.20,  # National kicking
            'club_points': 0.10
        },
        'constraints': {
            'weight_min': 90,         # kg
            'weight_max': 100,        # kg
            'height_min': 1.75,       # meters
            'height_max': 1.85,       # meters
            'starter_min': 2
        }
    },
    
    '22m Opponent Scrum': {
        'category': 'Contingency Play',
        'description': 'Defensive scrum in danger zone',
        'key_attributes': ['weight', 'height', 'starter'],
        'preferred_positions': ['Prop', 'Hooker'],
        'fitness_weights': {
            'weight': 0.35,           # Heavy for scrum
            'height': 0.30,           # Physical presence
            'starter': 0.25,          # Experience
            'club_points': 0.10
        },
        'constraints': {
            'weight_min': 105,        # kg
            'weight_max': 200,        # kg
            'height_min': 1.80,       # meters
            'height_max': 2.00,       # meters
            'starter_min': 10         # Experience crucial
        }
    }
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_strategy_by_name(strategy_name):
    """Get strategy configuration by name"""
    return STRATEGIES.get(strategy_name, None)

def get_strategies_by_category(category):
    """Get all strategies in a category"""
    return {name: config for name, config in STRATEGIES.items() 
            if config['category'] == category}

def get_all_categories():
    """Get all strategy categories"""
    return list(set(config['category'] for config in STRATEGIES.values()))

def validate_strategy(strategy_name):
    """Check if strategy exists"""
    return strategy_name in STRATEGIES

def get_strategy_fitness_weights(strategy_name):
    """Get fitness weights for a specific strategy"""
    strategy = get_strategy_by_name(strategy_name)
    return strategy['fitness_weights'] if strategy else {}

def get_strategy_constraints(strategy_name):
    """Get constraints for a specific strategy"""
    strategy = get_strategy_by_name(strategy_name)
    return strategy['constraints'] if strategy else {}

def get_preferred_positions(strategy_name):
    """Get preferred positions for a strategy"""
    strategy = get_strategy_by_name(strategy_name)
    return strategy['preferred_positions'] if strategy else []

def apply_strategy_bonus(player_score, player_data, strategy_name):
    """
    Apply position preference bonus to player score based on strategy
    """
    strategy = get_strategy_by_name(strategy_name)
    if not strategy:
        return player_score
    
    preferred_positions = strategy['preferred_positions']
    player_position = player_data.get('Position', '').strip()
    
    # Give 15% bonus if player is in preferred position
    if player_position in preferred_positions:
        return player_score * 1.15
    
    return player_score

# ==========================================
# STRATEGY DESCRIPTIONS FOR UI
# ==========================================

STRATEGY_DESCRIPTIONS = {
    'Basic Play': 'Fundamental rugby strategies based on set pieces and core skills',
    'Tactical Play': 'Advanced tactical approaches for different game situations',
    'Contingency Play': 'Adaptive strategies for emergency or pressure situations'
}
