"""
Baseline Algorithms for Rugby Team Optimization Comparison
Implements: Greedy, Random Search, and Hill Climbing algorithms
"""

import pandas as pd
import numpy as np
import random
from typing import List, Tuple, Dict

class BaselineOptimizers:
    """
    Collection of baseline optimization algorithms for comparison with GA
    """
    
    def __init__(self, df: pd.DataFrame, budget: int, game_mode: str = '15s'):
        self.df = df
        self.budget = budget
        self.game_mode = game_mode
        
        # Team structure requirements
        self.team_structures = {
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
        
        self.required_positions = self.team_structures[game_mode]
        self.total_players = sum(self.required_positions.values())
        
    def calculate_fitness(self, team_indices: List[int]) -> float:
        """Calculate fitness score for a team"""
        try:
            team_data = self.df.loc[team_indices]
        except KeyError:
            return 0
        
        total_salary = team_data['Salary'].sum()
        
        # Hard constraint: budget
        if total_salary > self.budget:
            return 0
        
        # Check duplicates
        if len(team_indices) != len(set(team_indices)):
            return 0
        
        # Performance score
        performance_score = team_data['Performance_Score'].sum()
        
        # ROI bonus
        budget_utilization = total_salary / self.budget
        roi_bonus = budget_utilization * performance_score * 0.10
        
        final_fitness = performance_score + roi_bonus
        return max(1, final_fitness)
    
    def is_valid_team(self, team_indices: List[int]) -> bool:
        """Check if team meets all position requirements"""
        try:
            team_data = self.df.loc[team_indices]
        except KeyError:
            return False
        
        # Check salary constraint
        if team_data['Salary'].sum() > self.budget:
            return False
        
        # Check duplicates
        if len(team_indices) != len(set(team_indices)):
            return False
        
        # Check position requirements
        position_counts = team_data['Position'].value_counts().to_dict()
        for position, required in self.required_positions.items():
            if position_counts.get(position, 0) < required:
                return False
        
        return True
    
    # =========================================================================
    # ALGORITHM 1: GREEDY VALUE-BASED SELECTION
    # =========================================================================
    
    def greedy_optimization(self) -> Tuple[List[int], float, Dict]:
        """
        Greedy algorithm: Select players with best Performance/Salary ratio
        
        Algorithm:
        1. Calculate value ratio (Performance/Salary) for each player
        2. Sort players by this ratio (best value first)
        3. For each position, select highest-rated available players
        4. Continue until budget exhausted or all positions filled
        
        Time Complexity: O(n log n) - dominated by sorting
        
        Returns:
            - team_indices: List of selected player indices
            - fitness: Fitness score of the team
            - stats: Statistics about the optimization
        """
        print("🔍 Running Greedy Optimization...")
        
        # Calculate value ratio for each player
        df_copy = self.df.copy()
        df_copy['value_ratio'] = df_copy['Performance_Score'] / df_copy['Salary']
        
        # Sort by value ratio (best first)
        df_sorted = df_copy.sort_values('value_ratio', ascending=False)
        
        team_indices = []
        used_positions = {pos: 0 for pos in self.required_positions.keys()}
        total_salary = 0
        
        # Greedy selection
        for idx, row in df_sorted.iterrows():
            position = row['Position']
            
            # Check if we need more players in this position
            if position in used_positions:
                if used_positions[position] < self.required_positions[position]:
                    # Check if adding this player keeps us within budget
                    if total_salary + row['Salary'] <= self.budget:
                        team_indices.append(idx)
                        used_positions[position] += 1
                        total_salary += row['Salary']
            
            # Check if team is complete
            if len(team_indices) == self.total_players:
                break
        
        # Calculate fitness
        fitness = self.calculate_fitness(team_indices) if len(team_indices) == self.total_players else 0
        
        # Statistics
        stats = {
            'algorithm': 'Greedy',
            'team_size': len(team_indices),
            'total_salary': total_salary,
            'budget_utilization': (total_salary / self.budget) * 100,
            'fitness': fitness,
            'valid': self.is_valid_team(team_indices) if len(team_indices) == self.total_players else False
        }
        
        print(f"✓ Greedy completed: Fitness = {fitness:.2f}, Budget = ${total_salary:,}")
        return team_indices, fitness, stats
    
    # =========================================================================
    # ALGORITHM 2: RANDOM SEARCH
    # =========================================================================
    
    def random_search_optimization(self, iterations: int = 1000) -> Tuple[List[int], float, Dict]:
        """
        Random Search: Generate random valid teams and keep the best
        
        Algorithm:
        1. Generate random team satisfying position requirements
        2. Check if valid (budget + positions)
        3. Keep track of best team found
        4. Repeat for N iterations
        
        Time Complexity: O(iterations × n) where n = team size
        
        Args:
            iterations: Number of random teams to generate
            
        Returns:
            - team_indices: List of selected player indices (best found)
            - fitness: Fitness score of the best team
            - stats: Statistics about the optimization
        """
        print(f"🎲 Running Random Search ({iterations} iterations)...")
        
        best_team = None
        best_fitness = 0
        valid_teams_found = 0
        
        for i in range(iterations):
            # Generate random team
            team_indices = self._generate_random_team()
            
            if team_indices and self.is_valid_team(team_indices):
                valid_teams_found += 1
                fitness = self.calculate_fitness(team_indices)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_team = team_indices
                    print(f"  New best at iteration {i+1}: Fitness = {best_fitness:.2f}")
        
        team_data = self.df.loc[best_team] if best_team else pd.DataFrame()
        total_salary = team_data['Salary'].sum() if not team_data.empty else 0
        
        # Statistics
        stats = {
            'algorithm': 'Random Search',
            'iterations': iterations,
            'valid_teams_found': valid_teams_found,
            'success_rate': (valid_teams_found / iterations) * 100,
            'team_size': len(best_team) if best_team else 0,
            'total_salary': total_salary,
            'budget_utilization': (total_salary / self.budget) * 100 if total_salary > 0 else 0,
            'fitness': best_fitness,
            'valid': best_team is not None
        }
        
        print(f"✓ Random Search completed: Best Fitness = {best_fitness:.2f}, Valid teams = {valid_teams_found}/{iterations}")
        return best_team if best_team else [], best_fitness, stats
    
    def _generate_random_team(self) -> List[int]:
        """Generate a random team satisfying position requirements"""
        team_indices = []
        
        for position, count in self.required_positions.items():
            # Get all players in this position
            position_players = self.df[self.df['Position'] == position].index.tolist()
            
            if len(position_players) < count:
                return None  # Not enough players for this position
            
            # Randomly select required number of players
            selected = random.sample(position_players, count)
            team_indices.extend(selected)
        
        return team_indices
    
    # =========================================================================
    # ALGORITHM 3: HILL CLIMBING
    # =========================================================================
    
    def hill_climbing_optimization(self, max_iterations: int = 500, 
                                   restarts: int = 5) -> Tuple[List[int], float, Dict]:
        """
        Hill Climbing: Local search optimization with random restarts
        
        Algorithm:
        1. Start with random valid team (or greedy solution)
        2. Generate neighbors by swapping one player
        3. If neighbor is better, move to it
        4. Repeat until no improvement (local optimum)
        5. Restart from new random position
        6. Keep best solution across all restarts
        
        Time Complexity: O(restarts × max_iterations × n²) 
        where n = number of players per position
        
        Args:
            max_iterations: Maximum iterations per restart
            restarts: Number of random restarts
            
        Returns:
            - team_indices: List of selected player indices (best found)
            - fitness: Fitness score of the best team
            - stats: Statistics about the optimization
        """
        print(f"⛰️  Running Hill Climbing ({restarts} restarts, {max_iterations} max iterations each)...")
        
        global_best_team = None
        global_best_fitness = 0
        total_improvements = 0
        total_iterations = 0
        
        for restart in range(restarts):
            print(f"\n  Restart {restart + 1}/{restarts}:")
            
            # Initialize with random team
            current_team = self._generate_random_team()
            if not current_team or not self.is_valid_team(current_team):
                print(f"    Failed to generate valid initial team")
                continue
            
            current_fitness = self.calculate_fitness(current_team)
            local_improvements = 0
            
            for iteration in range(max_iterations):
                total_iterations += 1
                
                # Generate neighbors (swap one player at a time)
                neighbors = self._generate_neighbors(current_team)
                
                # Find best neighbor
                best_neighbor = None
                best_neighbor_fitness = current_fitness
                
                for neighbor in neighbors:
                    if self.is_valid_team(neighbor):
                        neighbor_fitness = self.calculate_fitness(neighbor)
                        if neighbor_fitness > best_neighbor_fitness:
                            best_neighbor = neighbor
                            best_neighbor_fitness = neighbor_fitness
                
                # If found better neighbor, move to it
                if best_neighbor and best_neighbor_fitness > current_fitness:
                    current_team = best_neighbor
                    current_fitness = best_neighbor_fitness
                    local_improvements += 1
                    total_improvements += 1
                    print(f"    Iteration {iteration + 1}: Improved to {current_fitness:.2f}")
                else:
                    # Local optimum reached
                    print(f"    Local optimum reached at iteration {iteration + 1}: Fitness = {current_fitness:.2f}")
                    break
            
            # Update global best
            if current_fitness > global_best_fitness:
                global_best_fitness = current_fitness
                global_best_team = current_team
                print(f"  ✓ New global best: {global_best_fitness:.2f}")
        
        team_data = self.df.loc[global_best_team] if global_best_team else pd.DataFrame()
        total_salary = team_data['Salary'].sum() if not team_data.empty else 0
        
        # Statistics
        stats = {
            'algorithm': 'Hill Climbing',
            'restarts': restarts,
            'total_iterations': total_iterations,
            'total_improvements': total_improvements,
            'team_size': len(global_best_team) if global_best_team else 0,
            'total_salary': total_salary,
            'budget_utilization': (total_salary / self.budget) * 100 if total_salary > 0 else 0,
            'fitness': global_best_fitness,
            'valid': global_best_team is not None
        }
        
        print(f"\n✓ Hill Climbing completed: Best Fitness = {global_best_fitness:.2f}, Improvements = {total_improvements}")
        return global_best_team if global_best_team else [], global_best_fitness, stats
    
    def _generate_neighbors(self, team_indices: List[int]) -> List[List[int]]:
        """
        Generate neighbor solutions by swapping one player
        
        For each player in team, try swapping with another player 
        of the same position not in the team
        """
        neighbors = []
        team_data = self.df.loc[team_indices]
        
        for i, player_idx in enumerate(team_indices):
            player_position = self.df.loc[player_idx, 'Position']
            
            # Get all players in same position not in current team
            available = self.df[
                (self.df['Position'] == player_position) & 
                (~self.df.index.isin(team_indices))
            ].index.tolist()
            
            # Create neighbors by swapping
            for swap_idx in available[:5]:  # Limit to 5 swaps per player to avoid too many neighbors
                neighbor = team_indices.copy()
                neighbor[i] = swap_idx
                neighbors.append(neighbor)
        
        return neighbors


def run_comparison(df: pd.DataFrame, budget: int = 10000000, game_mode: str = '15s'):
    """
    Run all baseline algorithms and compare results
    """
    print("=" * 80)
    print("BASELINE ALGORITHMS COMPARISON")
    print("=" * 80)
    print(f"Dataset: {len(df)} players")
    print(f"Budget: ${budget:,}")
    print(f"Game Mode: {game_mode}")
    print("=" * 80)
    
    optimizer = BaselineOptimizers(df, budget, game_mode)
    
    results = {}
    
    # 1. Greedy
    print("\n" + "=" * 80)
    team1, fitness1, stats1 = optimizer.greedy_optimization()
    results['Greedy'] = stats1
    
    # 2. Random Search
    print("\n" + "=" * 80)
    team2, fitness2, stats2 = optimizer.random_search_optimization(iterations=1000)
    results['Random Search'] = stats2
    
    # 3. Hill Climbing
    print("\n" + "=" * 80)
    team3, fitness3, stats3 = optimizer.hill_climbing_optimization(max_iterations=500, restarts=5)
    results['Hill Climbing'] = stats3
    
    # Print comparison
    print("\n" + "=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    print(f"\n{'Algorithm':<20} {'Fitness':<12} {'Budget Used':<15} {'Utilization':<12} {'Valid':<8}")
    print("-" * 80)
    
    for algo_name, stats in results.items():
        print(f"{algo_name:<20} {stats['fitness']:<12.2f} ${stats['total_salary']:<14,} "
              f"{stats['budget_utilization']:<11.1f}% {'✓' if stats['valid'] else '✗':<8}")
    
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    # Load dataset and preprocess (same as app.py)
    print("Loading dataset...")
    FILE_PATH = 'Statistic on best rugby players 2023-2024.csv'
    
    try:
        df = pd.read_csv(FILE_PATH, encoding='latin1')
    except:
        try:
            df = pd.read_csv(FILE_PATH, encoding='utf-8')
        except:
            df = pd.read_csv(FILE_PATH, encoding='cp1252')
    
    df.columns = df.columns.str.strip()
    
    # Clean salary
    salary_col = [c for c in df.columns if 'Salary' in c][0]
    if df[salary_col].dtype == object:
        df[salary_col] = df[salary_col].astype(str).str.replace(r'[",]', '', regex=True)
        df[salary_col] = pd.to_numeric(df[salary_col], errors='coerce').fillna(0)
    df.rename(columns={salary_col: 'Salary'}, inplace=True)
    
    # Clean positions
    if 'Position' in df.columns:
        df['Position'] = df['Position'].astype(str).str.strip()
        position_mapping = {
            'Prop': 'Prop', 'Hooker': 'Hooker', 'Lock': 'Lock',
            'Secondrow': 'Lock', 'Backrow': 'Backrow', 'Back row': 'Backrow',
            'Scrumhalf': 'Scrumhalf', 'Scrum': 'Scrumhalf',
            'Flyhalf': 'Flyhalf', 'FlyHalf': 'Flyhalf', 'Fly': 'Flyhalf',
            'Centre': 'Centre', 'Center': 'Centre',
            'Winger': 'Winger', 'Fullback': 'Fullback',
        }
        df['Position'] = df['Position'].map(position_mapping).fillna(df['Position'])
    
    # Calculate performance score
    current_year = 2024
    df['start_career'] = pd.to_numeric(df['start_career'], errors='coerce').fillna(2020)
    df['experience'] = current_year - df['start_career']
    
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
    
    # Run comparison
    results = run_comparison(df, budget=10000000, game_mode='15s')
    
    print("\n✓ Comparison completed!")
