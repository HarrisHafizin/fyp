from flask import Flask, render_template, request, jsonify
import pandas as pd
import random
import numpy as np
import traceback
import requests
from strategies import STRATEGIES, get_strategy_fitness_weights, get_strategy_constraints, apply_strategy_bonus
from api_config import RUGBY_API_CONFIG, POPULAR_LEAGUES, DEFAULT_SEASON

app = Flask(__name__)

# ==========================================
# RUGBY API HELPER FUNCTIONS
# ==========================================
def get_api_headers():
    """Get headers for Rugby API requests"""
    return {'x-apisports-key': RUGBY_API_CONFIG['api_key']}

def fetch_from_rugby_api(endpoint, params=None):
    """Generic function to fetch data from Rugby API"""
    try:
        url = f"{RUGBY_API_CONFIG['base_url']}/{endpoint}"
        response = requests.get(url, headers=get_api_headers(), params=params, timeout=10)
        data = response.json()
        return data
    except Exception as e:
        print(f"API Error: {e}")
        return {'error': str(e), 'results': 0, 'response': []}

# ==========================================
# HELPER FUNCTIONS FOR STRATEGY COMBINATION
# ==========================================
def combine_strategy_weights(strategy_names):
    """
    Combine weights from multiple strategies by averaging them
    Returns normalized combined weights dictionary
    """
    if not strategy_names or len(strategy_names) == 0:
        strategy_names = ['Scrum']  # Default
    
    combined_weights = {}
    total_strategies = len(strategy_names)
    
    for strategy_name in strategy_names:
        weights = get_strategy_fitness_weights(strategy_name)
        for attribute, weight in weights.items():
            if attribute not in combined_weights:
                combined_weights[attribute] = 0
            combined_weights[attribute] += weight
    
    # Average the weights
    for attribute in combined_weights:
        combined_weights[attribute] = combined_weights[attribute] / total_strategies
    
    # Normalize to sum to 1.0
    total = sum(combined_weights.values())
    if total > 0:
        for attribute in combined_weights:
            combined_weights[attribute] = combined_weights[attribute] / total
    
    return combined_weights

def combine_strategy_constraints(strategy_names):
    """
    Combine constraints from multiple strategies (most restrictive wins)
    """
    if not strategy_names or len(strategy_names) == 0:
        strategy_names = ['Scrum']
    
    combined_constraints = {}
    
    for strategy_name in strategy_names:
        constraints = get_strategy_constraints(strategy_name)
        for constraint_key, constraint_val in constraints.items():
            if constraint_key not in combined_constraints:
                # For _min constraints, take the maximum (most restrictive)
                if '_min' in constraint_key or '_max' in constraint_key:
                    combined_constraints[constraint_key] = constraint_val
                else:
                    combined_constraints[constraint_key] = constraint_val
            else:
                # For minimum constraints, keep the higher minimum
                if '_min' in constraint_key:
                    combined_constraints[constraint_key] = max(combined_constraints[constraint_key], constraint_val)
                # For maximum constraints, keep the lower maximum
                elif '_max' in constraint_key:
                    combined_constraints[constraint_key] = min(combined_constraints[constraint_key], constraint_val)
    
    return combined_constraints

def get_preferred_positions_from_strategies(strategy_names):
    """
    Get consolidated preferred positions from multiple strategies
    """
    if not strategy_names or len(strategy_names) == 0:
        strategy_names = ['Scrum']
    
    all_preferred = []
    for strategy_name in strategy_names:
        strategy = STRATEGIES.get(strategy_name, {})
        preferred = strategy.get('preferred_positions', [])
        all_preferred.extend(preferred)
    
    # Return unique positions, maintaining order
    return list(dict.fromkeys(all_preferred))

# ==========================================
# CONFIGURATION
# ==========================================
FILE_PATH = 'Statistic on best rugby players 2023-2024.csv'

# Dynamic Team Structures based on Game Format (for GA recruitment)
TEAM_STRUCTURES = {
    '7s': { 
        'Prop': 3, 'Hooker': 1, 'Lock': 1,
        'Scrumhalf': 2, 'Flyhalf': 1, 'Centre': 2, 'Winger': 2 
    },
    '10s': {
        'Prop': 2, 'Hooker': 1, 'Lock': 2, 'Backrow': 1,
        'Scrumhalf': 3, 'Flyhalf': 1, 'Centre': 2, 'Winger': 2, 'Fullback': 1
    },
    '15s': {
        'Prop': 4, 'Hooker': 2, 'Lock': 3, 'Backrow': 5,
        'Scrumhalf': 2, 'Flyhalf': 2, 'Centre': 3, 'Winger': 3, 'Fullback': 1
    }
}

# Starter Position Requirements (actual rugby formation)
STARTER_POSITIONS = {
    '7s': {
        'Prop': 1, 'Hooker': 1, 'Lock': 1,
        'Scrumhalf': 1, 'Flyhalf': 1, 'Centre': 1, 'Winger': 1
    },
    '10s': {
        'Prop': 2, 'Hooker': 1, 'Lock': 1, 'Backrow': 1,
        'Scrumhalf': 1, 'Flyhalf': 1, 'Centre': 1, 'Winger': 1, 'Fullback': 1
    },
    '15s': {
        'Prop': 2, 'Hooker': 1, 'Lock': 2, 'Backrow': 3,
        'Scrumhalf': 1, 'Flyhalf': 1, 'Centre': 2, 'Winger': 2, 'Fullback': 1
    }
}

# ==========================================
# GENETIC ALGORITHM LOGIC (MULTI-MODE WITH MULTIPLE STRATEGIES)
# ==========================================
class RugbyScoutGA:
    def __init__(self, budget, game_mode, strategies=None, locked_players=None):
        """
        Initialize GA dengan support untuk Locked Players (Complete My Team mode)
        
        Args:
            budget: Budget maksimum untuk team
            game_mode: '7s', '10s', atau '15s'
            strategies: List strategi yang dipilih
            locked_players: List of player indices yang WAJIB ada dalam team (locked)
        """
        self.budget = float(budget)
        self.game_mode = game_mode
        
        # Handle locked players
        self.locked_players = locked_players if locked_players else []
        
        # Handle strategies - can be list or single string
        if strategies is None:
            strategies = ['Scrum']
        elif isinstance(strategies, str):
            strategies = [strategies]
        
        self.strategies = strategies  # Now accepts list of strategies
        self.target_structure = TEAM_STRUCTURES.get(game_mode, TEAM_STRUCTURES['15s'])
        
        self.df = self.load_data()
        self.population_size = 150  # Beratus kromosom untuk exploration yang lebih baik
        self.generations = 50  # Lebih banyak generations untuk optimization
        self.mutation_rate = 0.25  # Kadar mutasi untuk explore kombinasi baru
        self.elite_size = 10  # Simpan top 10 terbaik setiap generasi 
        
        # Combine weights and constraints from multiple strategies
        self.strategy_weights = combine_strategy_weights(strategies)
        self.strategy_constraints = combine_strategy_constraints(strategies)
        self.preferred_positions = get_preferred_positions_from_strategies(strategies)
        
        self.players_by_pos = {}
        all_positions = set(self.target_structure.keys())
        
        for pos in all_positions:
            filtered = self.df[self.df['Position'].str.lower() == pos.lower()]
            self.players_by_pos[pos] = filtered

    def load_data(self):
        try:
            df = pd.read_csv(FILE_PATH, encoding='ISO-8859-1')
        except:
            try:
                df = pd.read_csv(FILE_PATH, encoding='utf-8')
            except:
                df = pd.read_csv(FILE_PATH, encoding='cp1252')

        df.columns = df.columns.str.strip()
        
        salary_col = [c for c in df.columns if 'Salary' in c][0] 
        if df[salary_col].dtype == object:
            df[salary_col] = df[salary_col].astype(str).str.replace(r'[",]', '', regex=True)
            df[salary_col] = pd.to_numeric(df[salary_col], errors='coerce').fillna(0)
        df.rename(columns={salary_col: 'Salary'}, inplace=True)

        if 'Position' in df.columns:
            df['Position'] = df['Position'].astype(str).str.strip()
            # Standardize position names (handle inconsistencies)
            position_mapping = {
                'Prop': 'Prop',
                'Hooker': 'Hooker',
                'Lock': 'Lock',
                'Secondrow': 'Lock',
                'Backrow': 'Backrow',
                'Back row': 'Backrow',
                'Scrumhalf': 'Scrumhalf',
                'Scrum': 'Scrumhalf',
                'Flyhalf': 'Flyhalf',
                'FlyHalf': 'Flyhalf',
                'Fly': 'Flyhalf',
                'Centre': 'Centre',
                'Center': 'Centre',
                'Winger': 'Winger',
                'Fullback': 'Fullback',
                'Utility Back': 'Centre',
                'Utility Forward': 'Backrow',
            }
            df['Position'] = df['Position'].map(position_mapping).fillna(df['Position'])
        
        current_year = 2024
        df['start_career'] = pd.to_numeric(df['start_career'], errors='coerce').fillna(2020)
        df['experience'] = current_year - df['start_career']
        
        # --- PEMBERSIHAN DATA TAMBAHAN ---
        # Pastikan data fizikal dan prestasi wujud dan adalah nombor
        numeric_cols = ['age', 'weight', 'tall(m)', 'club_try', 'club_W', 'club_starter', 'yellow card', 'red card']
        for col in numeric_cols:
            if col not in df.columns:
                df[col] = 0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['Performance_Score'] = (
            (df['experience'] * 1.0) + 
            (df['club_try'] * 5.0) + 
            (df['club_W'] * 3.0) +
            (df['club_starter'] * 2.0) +
            (df['yellow card'] * -10.0) +
            (df['red card'] * -25.0)
        )
        df['Performance_Score'] = df['Performance_Score'].apply(lambda x: max(x, 1))
        return df

    def create_random_team(self):
        """
        Create a random team with support for LOCKED PLAYERS.
        
        Jika ada locked players:
        1. Masukkan locked players dahulu
        2. Lengkapkan baki posisi dengan pemain lain
        """
        team_indices = []
        used_indices = set()
        current_salary = 0.0
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: Add locked players first (if any)
        # ═══════════════════════════════════════════════════════════
        positions_filled = {pos: 0 for pos in self.target_structure.keys()}
        
        for locked_idx in self.locked_players:
            if locked_idx in self.df.index:
                locked_player = self.df.loc[locked_idx]
                player_pos = locked_player['Position']
                
                # Check if this position still needs players
                if player_pos in positions_filled:
                    if positions_filled[player_pos] < self.target_structure.get(player_pos, 0):
                        team_indices.append(locked_idx)
                        used_indices.add(locked_idx)
                        current_salary += locked_player['Salary']
                        positions_filled[player_pos] += 1
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: Fill remaining positions with random players
        # ═══════════════════════════════════════════════════════════
        for pos, total_count in self.target_structure.items():
            already_filled = positions_filled.get(pos, 0)
            remaining_count = total_count - already_filled
            
            if remaining_count <= 0:
                continue
                
            candidates = self.players_by_pos.get(pos)
            if candidates is None or candidates.empty:
                continue
            
            # Get candidates not yet used
            available = candidates[~candidates.index.isin(used_indices)]
            
            # Shuffle for random selection (not just cheapest)
            available_list = list(available.index)
            random.shuffle(available_list)
            
            selected_count = 0
            for idx in available_list:
                if selected_count >= remaining_count:
                    break
                    
                row = available.loc[idx]
                new_salary = current_salary + row['Salary']
                
                # Only add if it keeps us within budget
                if new_salary <= self.budget:
                    team_indices.append(idx)
                    used_indices.add(idx)
                    current_salary = new_salary
                    selected_count += 1
            
            # If we couldn't fill all positions within budget, add cheapest anyway
            # (this ensures we have a team, fitness function will reject if over budget)
            if selected_count < remaining_count:
                # Sort remaining by salary (cheapest first) for fallback
                remaining_players = available[~available.index.isin(used_indices)].sort_values('Salary')
                for idx, row in remaining_players.iterrows():
                    if selected_count >= remaining_count:
                        break
                    if idx not in used_indices:
                        team_indices.append(idx)
                        used_indices.add(idx)
                        current_salary += row['Salary']
                        selected_count += 1
        
        return team_indices

    def calculate_fitness(self, team_indices):
        """
        FITNESS FUNCTION dengan KNAPSACK INTEGRATION
        
        Objektif:
        1. MAKSIMUMKAN Performance Score (berdasarkan strategy)
        2. MINIMUMKAN Budget Usage (ROI bonus)
        
        Kekangan Knapsack (HARD CONSTRAINT):
        - Jika Total_Salary > User_Budget → FITNESS = 0 (GAGAL/REJECTED)
        """
        try:
            team_data = self.df.loc[team_indices]
        except KeyError: 
            return 0  # Invalid indices
        
        total_salary = team_data['Salary'].sum()
        
        # ═══════════════════════════════════════════════════════════
        # KEKANGAN KNAPSACK: HARD CONSTRAINT
        # Jika jumlah gaji > bajet, kromosom ini GAGAL
        # ═══════════════════════════════════════════════════════════
        if total_salary > self.budget:
            return 0  # ❌ GAGAL - Langgar kekangan budget
        
        # Check for duplicate players (tidak boleh pemain sama)
        if len(team_indices) != len(set(team_indices)): 
            return 0  # ❌ GAGAL - Pemain duplikat
        
        # ═══════════════════════════════════════════════════════════
        # HITUNG PERFORMANCE SCORE (Berdasarkan Strategy)
        # ═══════════════════════════════════════════════════════════
        performance_score = self._calculate_strategy_fitness(team_data)
        
        # ═══════════════════════════════════════════════════════════
        # ROI BONUS: Reward untuk efficiency (lebih murah = bonus)
        # Formula: Lebih tinggi utilization, lebih tinggi bonus
        # Ini menggalakkan GA cari team yang POWER tapi MURAH
        # ═══════════════════════════════════════════════════════════
        budget_utilization = total_salary / self.budget  # 0.0 to 1.0
        
        # Bonus calculation:
        # - Jika guna 100% budget → bonus = 10% of performance_score
        # - Jika guna 50% budget → bonus = 5% of performance_score
        # Ini encourage team yang maximize budget usage efficiently
        roi_bonus = budget_utilization * performance_score * 0.10
        
        # ═══════════════════════════════════════════════════════════
        # FINAL FITNESS = Performance Score + ROI Bonus
        # ═══════════════════════════════════════════════════════════
        final_fitness = performance_score + roi_bonus
        
        return max(1, final_fitness)  # Minimum fitness = 1 untuk valid teams
    
    def _calculate_strategy_fitness(self, team_data):
        """Calculate fitness score based on selected strategy"""
        if not self.strategy_weights:
            # Fallback to basic performance score if no strategy
            return team_data['Performance_Score'].sum()
        
        total_score = 0.0
        
        # Apply strategy-specific weights
        for attribute, weight in self.strategy_weights.items():
            if weight == 0:
                continue
            
            if attribute == 'Performance_Score':
                score_contribution = team_data['Performance_Score'].sum() * weight
                total_score += score_contribution
            
            elif attribute == 'weight':
                # Penalize extreme weight values based on constraints
                min_weight = self.strategy_constraints.get('weight_min', 80)
                max_weight = self.strategy_constraints.get('weight_max', 120)
                
                weight_scores = []
                for w in team_data['weight']:
                    if min_weight <= w <= max_weight:
                        weight_scores.append(w)
                    else:
                        # Penalty for out-of-range weight
                        penalty = abs(w - max(min_weight, min(max_weight, w))) / 10
                        weight_scores.append(max(1, w - penalty))
                
                score_contribution = sum(weight_scores) * weight / 100
                total_score += score_contribution
            
            elif attribute == 'height':
                # Favor ideal height range
                min_height = self.strategy_constraints.get('height_min', 1.70)
                max_height = self.strategy_constraints.get('height_max', 2.05)
                
                height_scores = []
                for h in team_data['tall(m)']:
                    if min_height <= h <= max_height:
                        height_scores.append(h * 100)  # Scale height
                    else:
                        penalty = abs(h - max(min_height, min(max_height, h))) * 10
                        height_scores.append(max(1, (h * 100) - penalty))
                
                score_contribution = sum(height_scores) * weight / 100
                total_score += score_contribution
            
            elif attribute in ['starter', 'club_starter', 'national_match']:
                # Experience/starter appearances
                col_name = attribute
                if col_name in team_data.columns:
                    score_contribution = team_data[col_name].sum() * weight / 10
                    total_score += score_contribution
            
            elif attribute in ['club_points', 'National_Points', 'club_try']:
                # Try and point scoring
                col_map = {
                    'club_points': 'club_points',
                    'National_Points': 'National_Points',
                    'club_try': 'club_try'
                }
                col_name = col_map.get(attribute, attribute)
                if col_name in team_data.columns:
                    score_contribution = team_data[col_name].sum() * weight * 2
                    total_score += score_contribution
            
            elif attribute == 'age':
                # Age-based scoring
                age_scores = []
                for age in team_data['age']:
                    # Prefer mature players (18-35)
                    if 18 <= age <= 35:
                        age_scores.append(age)
                    else:
                        penalty = abs(age - max(18, min(35, age))) * 2
                        age_scores.append(max(1, age - penalty))
                
                score_contribution = sum(age_scores) * weight / 10
                total_score += score_contribution
            
            elif attribute in ['yellow_card', 'red_card']:
                # Discipline penalty (minimize cards)
                col_map = {
                    'yellow_card': 'yellow card',
                    'red_card': 'red card'
                }
                col_name = col_map.get(attribute, attribute)
                if col_name in team_data.columns:
                    # Penalize high card count
                    cards = team_data[col_name].sum()
                    score_contribution = max(0, 100 - (cards * 50)) * weight
                    total_score += score_contribution
        
        # Apply position preference bonus from all selected strategies
        position_bonus = 0
        for idx, row in team_data.iterrows():
            # Check if player position is in any of the preferred positions
            player_position = row.get('Position', '').strip()
            if player_position in self.preferred_positions:
                position_bonus += 1  # Add bonus for each player in preferred position
        
        position_score = (position_bonus / len(team_data)) * 10 if len(team_data) > 0 else 0
        total_score += position_score
        
        return max(1, total_score)

    def _mutate(self, child):
        """
        MUTATION OPERATOR
        
        Tukar satu pemain secara rawak dengan pemain lain dari posisi sama.
        PENTING: Locked players TIDAK BOLEH dimutasi!
        
        Strategi Mutation:
        1. Pilih random position dalam team (BUKAN locked player)
        2. Ganti pemain itu dengan pemain lain dari posisi sama
        3. 50% chance pilih pemain dengan higher score, 50% chance random
        """
        if len(child) == 0:
            return child
        
        # Get indices yang BOLEH dimutasi (bukan locked players)
        mutable_indices = [i for i, player_idx in enumerate(child) 
                          if player_idx not in self.locked_players]
        
        if not mutable_indices:
            return child  # Semua pemain locked, tak boleh mutate
        
        # Pilih index rawak untuk dimutasi (dari yang boleh dimutasi sahaja)
        mutate_idx = random.choice(mutable_indices)
        original_player_idx = child[mutate_idx]
        
        # Dapatkan posisi pemain asal
        try:
            original_position = self.df.loc[original_player_idx, 'Position']
        except KeyError:
            return child
        
        # Cari pemain lain dari posisi sama
        candidates = self.players_by_pos.get(original_position)
        if candidates is None or candidates.empty:
            return child
        
        # Filter pemain yang belum ada dalam team
        available = candidates[~candidates.index.isin(child)]
        if available.empty:
            return child
        
        # 50% chance: pilih pemain dengan Performance_Score lebih tinggi
        # 50% chance: pilih secara rawak (untuk exploration)
        if random.random() < 0.5:
            # Greedy: pilih pemain dengan score tertinggi
            available_sorted = available.sort_values('Performance_Score', ascending=False)
            new_player_idx = available_sorted.index[0]
        else:
            # Random: untuk exploration
            new_player_idx = random.choice(available.index.tolist())
        
        # Ganti pemain
        child[mutate_idx] = new_player_idx
        
        return child

    def repair_team(self, team_indices):
        """
        Repair team by replacing duplicates with better alternative players.
        PENTING: Locked players tidak akan diganti!
        """
        seen = set()
        new_team = []
        target_list = []
        for pos, count in self.target_structure.items():
            target_list.extend([pos] * count)
            
        if len(team_indices) != len(target_list):
            return self.create_random_team()

        # Add locked players to seen first (they cannot be replaced)
        for locked_idx in self.locked_players:
            seen.add(locked_idx)

        for i, idx in enumerate(team_indices):
            required_pos = target_list[i]
            
            # If this is a locked player, keep it no matter what
            if idx in self.locked_players:
                new_team.append(idx)
                continue
                
            if idx in seen:
                # Duplicate found - replace with better player of same position
                candidates = self.players_by_pos.get(required_pos)
                if candidates is not None:
                    # Don't pick locked players or already used players
                    available = candidates[~candidates.index.isin(seen)]
                    if not available.empty:
                        # Sort by Performance_Score descending (best players first)
                        available_sorted = available.sort_values('Performance_Score', ascending=False)
                        new_idx = available_sorted.index[0]
                        new_team.append(new_idx)
                        seen.add(new_idx)
                    else:
                        new_team.append(idx)
                else:
                    new_team.append(idx)
            else:
                new_team.append(idx)
                seen.add(idx)
        return new_team
    def organize_starters_by_position(self, team_df, num_starters):
        """
        Organize starters by exact position requirements from STARTER_POSITIONS.
        Selects EXACTLY the required number per position for proper rugby formation.
        Remaining players become reserves.
        """
        # Get exact position requirements for starters in this game mode
        position_requirements = STARTER_POSITIONS.get(self.game_mode, STARTER_POSITIONS['15s'])
        
        starters = []
        reserves = []
        used_indices = set()
        
        # Group players by position
        players_by_position = {}
        for idx, row in team_df.iterrows():
            pos = row['Position']
            if pos not in players_by_position:
                players_by_position[pos] = []
            players_by_position[pos].append((idx, row))
        
        # Fill starters based on EXACT position requirements
        for position in position_requirements:
            required_count = position_requirements[position]
            selected_count = 0
            
            if position in players_by_position:
                for idx, row in players_by_position[position]:
                    if selected_count >= required_count:
                        break
                    
                    # Calculate Moneyball-style Value Metrics
                    perf_score = row['Performance_Score']
                    salary = row['Salary']
                    value_score = round((perf_score / (salary / 100000)) * 10, 1) if salary > 0 else 0
                    
                    # Determine market value status
                    if value_score >= 15:
                        market_value = 'undervalued'
                        efficiency_grade = 'A'
                    elif value_score >= 10:
                        market_value = 'good-value'
                        efficiency_grade = 'B'
                    elif value_score >= 5:
                        market_value = 'fair-value'
                        efficiency_grade = 'C'
                    else:
                        market_value = 'overpriced'
                        efficiency_grade = 'D'
                    
                    # Helper to safely convert values (handles NaN)
                    def safe_int(val, default=0):
                        try:
                            if pd.isna(val):
                                return default
                            return int(val)
                        except (ValueError, TypeError):
                            return default
                    
                    def safe_height(val, default=0.0):
                        try:
                            if pd.isna(val):
                                return default
                            result = float(val)
                            if result > 3:  # If > 3, assume it's in cm
                                result = result / 100
                            return round(result, 2)
                        except (ValueError, TypeError):
                            return default
                    
                    player_data = {
                        'name': f"{row.get('First-name', '')} {row.get('Name', '')}",
                        'position': row['Position'],
                        'salary': salary,
                        'score': round(perf_score, 2),
                        'club': row.get('club', 'Unknown'),
                        'country': row.get('Nationality', 'Unknown'),
                        'age': safe_int(row.get('age', 0)),
                        'height': safe_height(row.get('tall(m)', 0)),
                        'weight': safe_int(row.get('weight', 0)),
                        # Extended statistics from CSV
                        'tries': safe_int(row.get('club_try', 0)),
                        'club_matches': safe_int(row.get('club-match', 0)),
                        'club_wins': safe_int(row.get('club_W', 0)),
                        'yellow_cards': safe_int(row.get('yellow card', 0)),
                        'red_cards': safe_int(row.get('red card', 0)),
                        'experience': safe_int(row.get('experience', 0)),
                        # Moneyball Metrics
                        'value_score': value_score,
                        'market_value': market_value,
                        'efficiency_grade': efficiency_grade
                    }
                    starters.append(player_data)
                    used_indices.add(idx)
                    selected_count += 1
        
        # All remaining players become reserves
        for position in players_by_position:
            for idx, row in players_by_position[position]:
                if idx not in used_indices:
                    # Calculate Moneyball-style Value Metrics for reserves too
                    perf_score = row['Performance_Score']
                    salary = row['Salary']
                    value_score = round((perf_score / (salary / 100000)) * 10, 1) if salary > 0 else 0
                    
                    # Determine market value status
                    if value_score >= 15:
                        market_value = 'undervalued'
                        efficiency_grade = 'A'
                    elif value_score >= 10:
                        market_value = 'good-value'
                        efficiency_grade = 'B'
                    elif value_score >= 5:
                        market_value = 'fair-value'
                        efficiency_grade = 'C'
                    else:
                        market_value = 'overpriced'
                        efficiency_grade = 'D'
                    
                    # Helper to safely convert values (handles NaN)
                    def safe_int(val, default=0):
                        try:
                            if pd.isna(val):
                                return default
                            return int(val)
                        except (ValueError, TypeError):
                            return default
                    
                    def safe_height(val, default=0.0):
                        try:
                            if pd.isna(val):
                                return default
                            result = float(val)
                            if result > 3:  # If > 3, assume it's in cm
                                result = result / 100
                            return round(result, 2)
                        except (ValueError, TypeError):
                            return default
                    
                    player_data = {
                        'name': f"{row.get('First-name', '')} {row.get('Name', '')}",
                        'position': row['Position'],
                        'salary': salary,
                        'score': round(perf_score, 2),
                        'club': row.get('club', 'Unknown'),
                        'country': row.get('Nationality', 'Unknown'),
                        'age': safe_int(row.get('age', 0)),
                        'height': safe_height(row.get('tall(m)', 0)),
                        'weight': safe_int(row.get('weight', 0)),
                        # Extended statistics from CSV
                        'tries': safe_int(row.get('club_try', 0)),
                        'club_matches': safe_int(row.get('club-match', 0)),
                        'club_wins': safe_int(row.get('club_W', 0)),
                        'yellow_cards': safe_int(row.get('yellow card', 0)),
                        'red_cards': safe_int(row.get('red card', 0)),
                        'experience': safe_int(row.get('experience', 0)),
                        # Moneyball Metrics
                        'value_score': value_score,
                        'market_value': market_value,
                        'efficiency_grade': efficiency_grade
                    }
                    reserves.append(player_data)
        
        return starters, reserves

    def run(self):
        """
        GENETIC ALGORITHM dengan KNAPSACK INTEGRATION
        
        Aliran:
        1. POPULASI: Menjana beratus kombinasi pemain (kromosom)
        2. PENILAIAN: Semak setiap kromosom - jika gaji > bajet → fitness = 0
        3. SELEKSI: Pilih survivors (hanya yang lepas kekangan budget)
        4. CROSSOVER: Gabung 2 parent untuk hasilkan child
        5. MUTATION: Tukar random player untuk explore kombinasi baru
        6. REPEAT untuk semua generations
        """
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: JANA POPULASI AWAL (Beratus kromosom)
        # ═══════════════════════════════════════════════════════════
        print(f"🧬 Menjana {self.population_size} kromosom awal...")
        population = [self.create_random_team() for _ in range(self.population_size)]
        
        best_team_indices = None
        best_fitness = -1
        best_team_cost = float('inf')
        minimum_team_cost = float('inf')
        
        # Track statistics
        valid_teams_per_gen = []

        for gen in range(self.generations):
            # ═══════════════════════════════════════════════════════════
            # STEP 2: PENILAIAN FITNESS (Knapsack Check)
            # ═══════════════════════════════════════════════════════════
            evaluated = []
            valid_count = 0
            
            for individual in population:
                fitness = self.calculate_fitness(individual)
                team_cost = self.df.loc[individual]['Salary'].sum()
                
                # Track jika valid (fitness > 0 = lepas kekangan budget)
                if fitness > 0:
                    valid_count += 1
                    minimum_team_cost = min(minimum_team_cost, team_cost)
                    
                    # Update best team (maksimum fitness, minimum cost)
                    if fitness > best_fitness:
                        best_fitness = fitness
                        best_team_indices = individual
                        best_team_cost = team_cost
                    elif fitness == best_fitness and team_cost < best_team_cost:
                        best_team_indices = individual
                        best_team_cost = team_cost
                
                evaluated.append((individual, fitness, team_cost))
            
            valid_teams_per_gen.append(valid_count)
            
            # ═══════════════════════════════════════════════════════════
            # STEP 3: SELEKSI SURVIVORS (Hanya yang lepas budget constraint)
            # ═══════════════════════════════════════════════════════════
            # Sort by fitness (highest first)
            evaluated.sort(key=lambda x: x[1], reverse=True)
            
            # Pilih survivors - HANYA teams yang valid (fitness > 0)
            survivors = []
            for ind, fit, cost in evaluated:
                if fit > 0:  # Hanya teams yang lepas kekangan Knapsack
                    survivors.append(ind)
            
            # Jika tiada valid teams, guna top teams walaupun over-budget
            # (untuk elak GA stuck)
            if len(survivors) < self.elite_size:
                for ind, fit, cost in evaluated:
                    if ind not in survivors:
                        survivors.append(ind)
                    if len(survivors) >= self.elite_size:
                        break
            
            # ═══════════════════════════════════════════════════════════
            # STEP 4 & 5: CROSSOVER + MUTATION
            # ═══════════════════════════════════════════════════════════
            new_population = []
            
            # ELITISM: Simpan top performers terus ke generasi seterusnya
            elite = [x[0] for x in evaluated[:self.elite_size] if x[1] > 0]
            new_population.extend(elite)
            
            # Jana anak-anak baru melalui crossover & mutation
            while len(new_population) < self.population_size:
                # CROSSOVER: Pilih 2 parents secara rawak
                parent1 = random.choice(survivors)
                parent2 = random.choice(survivors)
                
                # Single-point crossover
                cut_point = len(parent1) // 2
                child = list(parent1[:cut_point]) + list(parent2[cut_point:])
                
                # MUTATION: Tukar random player dengan kemungkinan mutation_rate
                if random.random() < self.mutation_rate:
                    child = self._mutate(child)
                
                # Repair child untuk pastikan valid structure
                child = self.repair_team(child)
                new_population.append(child)
            
            population = new_population
            
            # Progress logging setiap 10 generasi
            if gen % 10 == 0:
                print(f"  Gen {gen}: Valid teams = {valid_count}/{self.population_size}, Best fitness = {best_fitness:.1f}")

        print(f"✅ GA selesai! Best fitness = {best_fitness:.1f}, Cost = ${best_team_cost:,.0f}")
        
        # Return best valid team found
        if best_team_indices is None:
            best_team_indices = self.create_random_team()
        
        best_team_df = self.df.loc[best_team_indices]
        actual_cost = best_team_df['Salary'].sum()
        
        # Determine number of starters based on game mode
        if self.game_mode == '7s':
            num_starters = 7
        elif self.game_mode == '10s':
            num_starters = 10
        else:  # 15s
            num_starters = 15
        
        # Organize starters by position
        starters, reserves = self.organize_starters_by_position(best_team_df, num_starters)
        
        # Store minimum budget info for API response
        self.minimum_budget = minimum_team_cost if minimum_team_cost != float('inf') else actual_cost
        self.actual_cost = actual_cost
        
        return {'starters': starters, 'reserves': reserves}


# ==========================================
# ROUTES
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/players', methods=['GET'])
def get_all_players():
    """
    API endpoint untuk dapatkan semua pemain untuk search functionality.
    Digunakan dalam "Complete My Team" mode.
    """
    try:
        # Load data
        try:
            df = pd.read_csv(FILE_PATH, encoding='ISO-8859-1')
        except:
            try:
                df = pd.read_csv(FILE_PATH, encoding='utf-8')
            except:
                df = pd.read_csv(FILE_PATH, encoding='cp1252')
        
        df.columns = df.columns.str.strip()
        
        # Process salary
        salary_col = [c for c in df.columns if 'Salary' in c][0]
        if df[salary_col].dtype == object:
            df[salary_col] = df[salary_col].astype(str).str.replace(r'[",]', '', regex=True)
            df[salary_col] = pd.to_numeric(df[salary_col], errors='coerce').fillna(0)
        df.rename(columns={salary_col: 'Salary'}, inplace=True)
        
        # Calculate Performance Score
        current_year = 2026
        df['start_career'] = pd.to_numeric(df['start_career'], errors='coerce').fillna(2020)
        df['experience'] = current_year - df['start_career']
        
        numeric_cols = ['club_try', 'club_W', 'club_starter', 'yellow card', 'red card']
        for col in numeric_cols:
            if col not in df.columns:
                df[col] = 0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['Performance_Score'] = (
            (df['experience'] * 1.0) + 
            (df['club_try'] * 5.0) + 
            (df['club_W'] * 3.0) +
            (df['club_starter'] * 2.0) +
            (df['yellow card'] * -10.0) +
            (df['red card'] * -25.0)
        )
        df['Performance_Score'] = df['Performance_Score'].apply(lambda x: max(x, 1))
        
        # Build player list for API response
        players = []
        for idx, row in df.iterrows():
            players.append({
                'id': str(idx),  # String ID for consistency
                'name': f"{row.get('First-name', '')} {row.get('Name', '')}".strip(),
                'position': row.get('Position', 'Unknown'),
                'salary': int(row['Salary']),
                'score': round(row['Performance_Score'], 1),
                'club': row.get('club', 'Unknown'),
                'country': row.get('Nationality', 'Unknown'),
                'age': int(row.get('Age', 0)) if pd.notna(row.get('Age')) else None,
                'height': float(row.get('Height', 0)) if pd.notna(row.get('Height')) else None,
                'weight': int(row.get('Weight', 0)) if pd.notna(row.get('Weight')) else None,
                'start_career': int(row.get('start_career', 2020)) if pd.notna(row.get('start_career')) else None,
                'tries': int(row.get('club_try', 0)) if pd.notna(row.get('club_try')) else 0,
                'wins': int(row.get('club_W', 0)) if pd.notna(row.get('club_W')) else 0
            })
        
        return jsonify({'players': players})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/players', methods=['POST'])
def add_player():
    """
    API endpoint to add a new player to the CSV database
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'position', 'club', 'nationality', 'salary']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Load existing data
        try:
            df = pd.read_csv(FILE_PATH, encoding='ISO-8859-1')
        except:
            try:
                df = pd.read_csv(FILE_PATH, encoding='utf-8')
            except:
                df = pd.read_csv(FILE_PATH, encoding='cp1252')
        
        df.columns = df.columns.str.strip()
        
        # Create new player row
        new_player = {
            'First-name': data.get('first_name', ''),
            'Name': data.get('last_name', ''),
            'Position': data.get('position', ''),
            'club': data.get('club', ''),
            'Nationality': data.get('nationality', ''),
            'Age': data.get('age'),
            'Height': data.get('height'),
            'Weight': data.get('weight'),
            'start_career': data.get('start_career'),
            'club_try': data.get('tries', 0),
            'club_W': data.get('wins', 0),
            'club_starter': 0,
            'yellow card': 0,
            'red card': 0
        }
        
        # Find salary column and set salary
        salary_col = [c for c in df.columns if 'Salary' in c][0]
        new_player[salary_col] = data.get('salary', 0)
        
        # Append new player
        new_df = pd.DataFrame([new_player])
        df = pd.concat([df, new_df], ignore_index=True)
        
        # Save back to CSV
        df.to_csv(FILE_PATH, index=False, encoding='ISO-8859-1')
        
        return jsonify({
            'success': True,
            'message': 'Player added successfully',
            'player_id': str(len(df) - 1)
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/players/<player_id>', methods=['PUT'])
def update_player(player_id):
    """
    API endpoint to update an existing player
    """
    try:
        data = request.json
        player_idx = int(player_id)
        
        # Load existing data
        try:
            df = pd.read_csv(FILE_PATH, encoding='ISO-8859-1')
        except:
            try:
                df = pd.read_csv(FILE_PATH, encoding='utf-8')
            except:
                df = pd.read_csv(FILE_PATH, encoding='cp1252')
        
        df.columns = df.columns.str.strip()
        
        # Check if player exists
        if player_idx < 0 or player_idx >= len(df):
            return jsonify({'success': False, 'error': 'Player not found'}), 404
        
        # Update player data
        if data.get('first_name'):
            df.at[player_idx, 'First-name'] = data.get('first_name')
        if data.get('last_name'):
            df.at[player_idx, 'Name'] = data.get('last_name')
        if data.get('position'):
            df.at[player_idx, 'Position'] = data.get('position')
        if data.get('club'):
            df.at[player_idx, 'club'] = data.get('club')
        if data.get('nationality'):
            df.at[player_idx, 'Nationality'] = data.get('nationality')
        if data.get('age') is not None:
            df.at[player_idx, 'Age'] = data.get('age')
        if data.get('height') is not None:
            df.at[player_idx, 'Height'] = data.get('height')
        if data.get('weight') is not None:
            df.at[player_idx, 'Weight'] = data.get('weight')
        if data.get('start_career') is not None:
            df.at[player_idx, 'start_career'] = data.get('start_career')
        if data.get('tries') is not None:
            df.at[player_idx, 'club_try'] = data.get('tries')
        if data.get('wins') is not None:
            df.at[player_idx, 'club_W'] = data.get('wins')
        
        # Find salary column and update salary
        salary_col = [c for c in df.columns if 'Salary' in c][0]
        if data.get('salary') is not None:
            df.at[player_idx, salary_col] = data.get('salary')
        
        # Save back to CSV
        df.to_csv(FILE_PATH, index=False, encoding='ISO-8859-1')
        
        return jsonify({
            'success': True,
            'message': 'Player updated successfully'
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/players/<player_id>', methods=['DELETE'])
def delete_player(player_id):
    """
    API endpoint to delete a player
    """
    try:
        player_idx = int(player_id)
        
        # Load existing data
        try:
            df = pd.read_csv(FILE_PATH, encoding='ISO-8859-1')
        except:
            try:
                df = pd.read_csv(FILE_PATH, encoding='utf-8')
            except:
                df = pd.read_csv(FILE_PATH, encoding='cp1252')
        
        df.columns = df.columns.str.strip()
        
        # Check if player exists
        if player_idx < 0 or player_idx >= len(df):
            return jsonify({'success': False, 'error': 'Player not found'}), 404
        
        # Delete player
        df = df.drop(index=player_idx).reset_index(drop=True)
        
        # Save back to CSV
        df.to_csv(FILE_PATH, index=False, encoding='ISO-8859-1')
        
        return jsonify({
            'success': True,
            'message': 'Player deleted successfully'
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.json
        budget = data.get('budget', 5000000)
        mode = data.get('mode', '15s')
        strategies = data.get('strategies', ['Scrum'])  # Can be array or single strategy
        build_mode = data.get('build_mode', 'scratch')  # 'scratch' or 'complete'
        locked_players = data.get('locked_players', [])  # List of player IDs to lock
        
        # Ensure budget is integer (fix for JavaScript string values)
        budget = int(budget) if isinstance(budget, str) else int(budget)
        
        # Ensure strategies is a list
        if isinstance(strategies, str):
            strategies = [strategies]
        
        # Ensure locked_players is a list of integers
        locked_players = [int(p) for p in locked_players] if locked_players else []
        
        strategies_display = ' + '.join(strategies)
        build_mode_display = "Complete Team" if build_mode == 'complete' else "From Scratch"
        print(f"Processing: Budget=${budget}, Mode={mode}, Strategies={strategies_display}")
        print(f"Build Mode: {build_mode_display}, Locked Players: {len(locked_players)}")
        
        ga = RugbyScoutGA(budget, mode, strategies, locked_players)  # Pass locked_players
        team_result = ga.run()  # Now returns dict with 'starters' and 'reserves'
        
        starters = team_result['starters']
        reserves = team_result['reserves']
        
        total_cost = sum(p['salary'] for p in starters + reserves)
        total_score = sum(p['score'] for p in starters + reserves)
        
        # --- PENGIRAAN STATISTIK PASUKAN (ANALYTICS) ---
        all_players = starters + reserves
        
        # Safe calculations with NaN handling
        def safe_avg(players, key):
            values = [p[key] for p in players if p.get(key) and not (isinstance(p[key], float) and pd.isna(p[key]))]
            return sum(values) / len(values) if values else 0
        
        avg_age = safe_avg(all_players, 'age')
        avg_weight = safe_avg(all_players, 'weight')
        
        # Height needs special handling - normalize to meters if in cm
        heights = []
        for p in all_players:
            h = p.get('height', 0)
            if h and not (isinstance(h, float) and pd.isna(h)):
                # If height > 3, assume it's in cm and convert to meters
                if h > 3:
                    h = h / 100
                heights.append(h)
        avg_height = sum(heights) / len(heights) if heights else 0
        
        total_attack_power = sum(p.get('tries', 0) for p in all_players)
        
        # Check if over budget and provide minimum budget info
        is_over_budget = total_cost > budget
        minimum_budget = ga.minimum_budget if hasattr(ga, 'minimum_budget') else total_cost
        
        # Convert numpy types to Python types for JSON serialization
        minimum_budget = int(minimum_budget) if hasattr(minimum_budget, 'item') else int(minimum_budget)

        response = {
            'status': 'success',
            'starters': starters,  # Main team
            'reserves': reserves,  # Bench
            'total_cost': total_cost,
            'total_score': round(total_score, 2),
            'budget': budget,
            'mode': mode,
            'strategies': strategies,  # Include strategies array in response
            'is_over_budget': is_over_budget,
            'minimum_budget': minimum_budget,
            'analytics': {
                'avg_age': round(avg_age, 1),
                'avg_weight': round(avg_weight, 1),
                'avg_height': round(avg_height, 2),
                'attack_potential': total_attack_power
            }
        }
        
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==========================================
# RUGBY API ENDPOINTS (LIVE DATA)
# ==========================================

@app.route('/api/rugby/status')
def api_rugby_status():
    """Check API connection status and quota"""
    data = fetch_from_rugby_api('status')
    
    # Check for API errors (invalid/expired key)
    if 'errors' in data and data['errors']:
        return jsonify({
            'status': 'error',
            'message': 'API Key issue: ' + str(list(data['errors'].values())[0] if data['errors'] else 'Unknown error'),
            'errors': data['errors']
        })
    
    if 'response' in data and isinstance(data['response'], list) and len(data['response']) > 0:
        resp = data['response'][0] if isinstance(data['response'], list) else data['response']
        return jsonify({
            'status': 'connected',
            'account': resp.get('account', {}),
            'subscription': resp.get('subscription', {}),
            'requests': resp.get('requests', {})
        })
    elif 'response' in data and isinstance(data['response'], dict):
        return jsonify({
            'status': 'connected',
            'account': data['response'].get('account', {}),
            'subscription': data['response'].get('subscription', {}),
            'requests': data['response'].get('requests', {})
        })
    return jsonify({'status': 'error', 'message': 'Could not connect to API or API key expired'})

@app.route('/api/rugby/countries')
def api_rugby_countries():
    """Get list of rugby countries"""
    data = fetch_from_rugby_api('countries')
    return jsonify({
        'status': 'success',
        'count': data.get('results', 0),
        'countries': data.get('response', [])
    })

@app.route('/api/rugby/leagues')
def api_rugby_leagues():
    """Get list of rugby leagues/competitions"""
    country = request.args.get('country', None)
    season = request.args.get('season', None)
    
    params = {}
    if country:
        params['country'] = country
    if season:
        params['season'] = season
    
    data = fetch_from_rugby_api('leagues', params)
    
    # Check for API errors
    if 'errors' in data and data['errors']:
        return jsonify({
            'status': 'error',
            'message': 'API Error: ' + str(list(data['errors'].values())[0] if data['errors'] else 'Unknown'),
            'leagues': []
        })
    
    return jsonify({
        'status': 'success',
        'count': data.get('results', 0),
        'leagues': data.get('response', [])
    })

@app.route('/api/rugby/teams')
def api_rugby_teams():
    """Get teams from a specific league"""
    league_id = request.args.get('league', 3)  # Default: Super Rugby
    season = request.args.get('season', DEFAULT_SEASON)
    search = request.args.get('search', None)
    
    params = {'league': league_id, 'season': season}
    if search:
        params['search'] = search
    
    data = fetch_from_rugby_api('teams', params)
    return jsonify({
        'status': 'success',
        'count': data.get('results', 0),
        'teams': data.get('response', [])
    })

@app.route('/api/rugby/team/<int:team_id>')
def api_rugby_team_detail(team_id):
    """Get detailed info about a specific team"""
    data = fetch_from_rugby_api('teams', {'id': team_id})
    if data.get('results', 0) > 0:
        return jsonify({
            'status': 'success',
            'team': data['response'][0]
        })
    return jsonify({'status': 'error', 'message': 'Team not found'})

@app.route('/api/rugby/standings')
def api_rugby_standings():
    """Get league standings"""
    league_id = request.args.get('league', 3)
    season = request.args.get('season', DEFAULT_SEASON)
    
    data = fetch_from_rugby_api('standings', {
        'league': league_id,
        'season': season
    })
    return jsonify({
        'status': 'success',
        'count': data.get('results', 0),
        'standings': data.get('response', [])
    })

@app.route('/api/rugby/games')
def api_rugby_games():
    """Get games/matches"""
    league_id = request.args.get('league', None)
    season = request.args.get('season', DEFAULT_SEASON)
    team_id = request.args.get('team', None)
    date = request.args.get('date', None)
    
    params = {'season': season}
    if league_id:
        params['league'] = league_id
    if team_id:
        params['team'] = team_id
    if date:
        params['date'] = date
    
    data = fetch_from_rugby_api('games', params)
    return jsonify({
        'status': 'success',
        'count': data.get('results', 0),
        'games': data.get('response', [])
    })

@app.route('/api/rugby/team-stats')
def api_rugby_team_stats():
    """Get team statistics for a season"""
    team_id = request.args.get('team')
    league_id = request.args.get('league', 3)
    season = request.args.get('season', DEFAULT_SEASON)
    
    if not team_id:
        return jsonify({'status': 'error', 'message': 'Team ID required'})
    
    data = fetch_from_rugby_api('teams/statistics', {
        'team': team_id,
        'league': league_id,
        'season': season
    })
    return jsonify({
        'status': 'success',
        'statistics': data.get('response', {})
    })

@app.route('/api/rugby/h2h')
def api_rugby_h2h():
    """Get head-to-head between two teams"""
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    
    if not team1 or not team2:
        return jsonify({'status': 'error', 'message': 'Both team IDs required'})
    
    data = fetch_from_rugby_api('games/h2h', {'h2h': f"{team1}-{team2}"})
    return jsonify({
        'status': 'success',
        'count': data.get('results', 0),
        'matches': data.get('response', [])
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)