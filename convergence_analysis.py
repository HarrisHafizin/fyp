"""
Convergence Analysis Script for Rugby Scouting GA
Generates convergence graphs and stores fitness history for evaluation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server
import random
import os
from datetime import datetime

# Import from existing system
from strategies import STRATEGIES, get_strategy_fitness_weights, get_strategy_constraints

# ==========================================
# CONFIGURATION
# ==========================================
FILE_PATH = 'Statistic on best rugby players 2023-2024.csv'

TEAM_STRUCTURES = {
    '7s': {'Prop': 3, 'Hooker': 1, 'Lock': 1, 'Scrumhalf': 2, 'Flyhalf': 1, 'Centre': 2, 'Winger': 2},
    '10s': {'Prop': 2, 'Hooker': 1, 'Lock': 2, 'Backrow': 1, 'Scrumhalf': 3, 'Flyhalf': 1, 'Centre': 2, 'Winger': 2, 'Fullback': 1},
    '15s': {'Prop': 4, 'Hooker': 2, 'Lock': 3, 'Backrow': 5, 'Scrumhalf': 2, 'Flyhalf': 2, 'Centre': 3, 'Winger': 3, 'Fullback': 1}
}

class ConvergenceAnalysisGA:
    """
    GA with convergence tracking for analysis and visualization
    """
    
    def __init__(self, budget, game_mode='15s', strategies=None):
        self.budget = float(budget)
        self.game_mode = game_mode
        self.strategies = strategies if strategies else ['Scrum']
        self.target_structure = TEAM_STRUCTURES.get(game_mode, TEAM_STRUCTURES['15s'])
        
        # GA Parameters
        self.population_size = 100
        self.generations = 100
        self.mutation_rate = 0.2
        self.elite_size = 10
        
        # Convergence tracking
        self.fitness_history = {
            'generation': [],
            'best_fitness': [],
            'avg_fitness': [],
            'worst_fitness': [],
            'diversity': []
        }
        
        # Load data
        self.df = self._load_data()
        self.players_by_pos = self._group_by_position()
        
    def _load_data(self):
        """Load and preprocess player data"""
        try:
            df = pd.read_csv(FILE_PATH, encoding='ISO-8859-1')
        except:
            df = pd.read_csv(FILE_PATH, encoding='utf-8')
        
        df.columns = df.columns.str.strip()
        
        # Clean salary
        if 'Salary' in df.columns:
            if df['Salary'].dtype == object:
                df['Salary'] = df['Salary'].astype(str).str.replace(r'[",]', '', regex=True)
            df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce').fillna(0)
        
        # Normalize positions
        position_mapping = {
            'Prop': 'Prop', 'Hooker': 'Hooker', 'Lock': 'Lock', 'Secondrow': 'Lock',
            'Backrow': 'Backrow', 'Back row': 'Backrow', 'Scrumhalf': 'Scrumhalf',
            'Scrum': 'Scrumhalf', 'Flyhalf': 'Flyhalf', 'FlyHalf': 'Flyhalf',
            'Fly': 'Flyhalf', 'Centre': 'Centre', 'Center': 'Centre',
            'Winger': 'Winger', 'Fullback': 'Fullback',
            'Utility Back': 'Centre', 'Utility Forward': 'Backrow'
        }
        df['Position'] = df['Position'].astype(str).str.strip().map(position_mapping).fillna(df['Position'])
        
        # Calculate performance score
        current_year = 2024
        df['start_career'] = pd.to_numeric(df['start_career'], errors='coerce').fillna(2020)
        df['experience'] = current_year - df['start_career']
        
        numeric_cols = ['club_try', 'club_W', 'club_starter', 'yellow card', 'red card']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0
        
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
    
    def _group_by_position(self):
        """Group players by position"""
        players_by_pos = {}
        for pos in self.target_structure.keys():
            players_by_pos[pos] = self.df[self.df['Position'].str.lower() == pos.lower()]
        return players_by_pos
    
    def create_random_team(self):
        """Create a random team respecting structure"""
        team = []
        used = set()
        
        for pos, count in self.target_structure.items():
            candidates = self.players_by_pos.get(pos)
            if candidates is None or candidates.empty:
                candidates = self.df
            
            available = candidates[~candidates.index.isin(used)]
            if len(available) >= count:
                selected = available.sample(n=count)
            else:
                selected = candidates.sample(n=count, replace=True)
            
            for idx in selected.index:
                team.append(idx)
                used.add(idx)
        
        return team
    
    def calculate_fitness(self, team_indices):
        """Calculate fitness with budget constraint"""
        try:
            team_data = self.df.loc[team_indices]
        except:
            return 0
        
        total_salary = team_data['Salary'].sum()
        
        # Hard constraint: budget
        if total_salary > self.budget:
            return 0
        
        # Check duplicates
        if len(team_indices) != len(set(team_indices)):
            return 0
        
        # Calculate performance
        performance = team_data['Performance_Score'].sum()
        
        # ROI bonus
        utilization = total_salary / self.budget if self.budget > 0 else 0
        roi_bonus = utilization * performance * 0.1
        
        return max(1, performance + roi_bonus)
    
    def crossover(self, parent1, parent2):
        """Single point crossover"""
        cut = len(parent1) // 2
        child1 = parent1[:cut] + parent2[cut:]
        child2 = parent2[:cut] + parent1[cut:]
        return self._repair(child1), self._repair(child2)
    
    def mutate(self, team):
        """Mutation operator"""
        if random.random() < self.mutation_rate and len(team) > 0:
            idx = random.randint(0, len(team) - 1)
            player_id = team[idx]
            
            try:
                pos = self.df.loc[player_id, 'Position']
            except:
                return team
            
            candidates = self.players_by_pos.get(pos, self.df)
            available = candidates[~candidates.index.isin(team)]
            
            if not available.empty:
                new_player = random.choice(available.index.tolist())
                team[idx] = new_player
        
        return team
    
    def _repair(self, team):
        """Remove duplicates"""
        seen = set()
        new_team = []
        
        for pid in team:
            if pid not in seen:
                new_team.append(pid)
                seen.add(pid)
            else:
                # Replace with random available player
                available = self.df[~self.df.index.isin(seen)]
                if not available.empty:
                    new_pid = random.choice(available.index.tolist())
                    new_team.append(new_pid)
                    seen.add(new_pid)
        
        return new_team
    
    def calculate_diversity(self, population):
        """Calculate population diversity (unique individuals ratio)"""
        unique_teams = set()
        for team in population:
            unique_teams.add(tuple(sorted(team)))
        return len(unique_teams) / len(population) if population else 0
    
    def run(self):
        """Run GA with convergence tracking"""
        print(f"\n{'='*60}")
        print(f"CONVERGENCE ANALYSIS - Rugby Scouting GA")
        print(f"Budget: ${self.budget:,.0f} | Mode: {self.game_mode} | Strategies: {self.strategies}")
        print(f"Population: {self.population_size} | Generations: {self.generations}")
        print(f"{'='*60}\n")
        
        # Initialize population
        population = [self.create_random_team() for _ in range(self.population_size)]
        
        best_ever_fitness = 0
        best_ever_team = None
        
        for gen in range(self.generations):
            # Evaluate fitness
            fitness_scores = [(team, self.calculate_fitness(team)) for team in population]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Track statistics
            fitnesses = [f for _, f in fitness_scores]
            best_fit = max(fitnesses)
            avg_fit = np.mean(fitnesses)
            worst_fit = min(fitnesses)
            diversity = self.calculate_diversity(population)
            
            # Store history
            self.fitness_history['generation'].append(gen)
            self.fitness_history['best_fitness'].append(best_fit)
            self.fitness_history['avg_fitness'].append(avg_fit)
            self.fitness_history['worst_fitness'].append(worst_fit)
            self.fitness_history['diversity'].append(diversity)
            
            # Track best ever
            if best_fit > best_ever_fitness:
                best_ever_fitness = best_fit
                best_ever_team = fitness_scores[0][0].copy()
            
            # Print progress
            if gen % 10 == 0 or gen == self.generations - 1:
                print(f"Gen {gen:3d}: Best={best_fit:8.2f} | Avg={avg_fit:8.2f} | Diversity={diversity:.2%}")
            
            # Selection (top 50%)
            survivors = [t for t, _ in fitness_scores[:self.population_size // 2]]
            
            # Elitism
            elites = [t for t, _ in fitness_scores[:self.elite_size]]
            
            # Create new population
            new_population = elites.copy()
            
            while len(new_population) < self.population_size:
                p1 = random.choice(survivors)
                p2 = random.choice(survivors)
                c1, c2 = self.crossover(p1.copy(), p2.copy())
                new_population.append(self.mutate(c1))
                if len(new_population) < self.population_size:
                    new_population.append(self.mutate(c2))
            
            population = new_population
        
        print(f"\n{'='*60}")
        print(f"OPTIMIZATION COMPLETE")
        print(f"Best Fitness Achieved: {best_ever_fitness:.2f}")
        print(f"{'='*60}\n")
        
        return best_ever_team, best_ever_fitness
    
    def plot_convergence(self, save_path='static/images/convergence_graph.png'):
        """Generate and save convergence graph"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Genetic Algorithm Convergence Analysis\nRugby Scouting Optimization System', 
                     fontsize=14, fontweight='bold')
        
        generations = self.fitness_history['generation']
        
        # Plot 1: Fitness over generations
        ax1 = axes[0, 0]
        ax1.plot(generations, self.fitness_history['best_fitness'], 'g-', linewidth=2, label='Best Fitness')
        ax1.plot(generations, self.fitness_history['avg_fitness'], 'b-', linewidth=1.5, label='Average Fitness')
        ax1.plot(generations, self.fitness_history['worst_fitness'], 'r--', linewidth=1, alpha=0.7, label='Worst Fitness')
        ax1.fill_between(generations, self.fitness_history['worst_fitness'], 
                         self.fitness_history['best_fitness'], alpha=0.2, color='blue')
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Fitness Score')
        ax1.set_title('Fitness Progression Over Generations')
        ax1.legend(loc='lower right')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Best fitness only (zoomed)
        ax2 = axes[0, 1]
        ax2.plot(generations, self.fitness_history['best_fitness'], 'g-', linewidth=2, marker='o', 
                 markersize=3, markevery=10)
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Best Fitness Score')
        ax2.set_title('Best Fitness Convergence Curve')
        ax2.grid(True, alpha=0.3)
        
        # Annotate start and end
        ax2.annotate(f'Start: {self.fitness_history["best_fitness"][0]:.1f}', 
                     xy=(0, self.fitness_history['best_fitness'][0]),
                     xytext=(10, self.fitness_history['best_fitness'][0] + 50),
                     arrowprops=dict(arrowstyle='->', color='red'),
                     fontsize=9, color='red')
        ax2.annotate(f'End: {self.fitness_history["best_fitness"][-1]:.1f}', 
                     xy=(len(generations)-1, self.fitness_history['best_fitness'][-1]),
                     xytext=(len(generations)-20, self.fitness_history['best_fitness'][-1] - 50),
                     arrowprops=dict(arrowstyle='->', color='green'),
                     fontsize=9, color='green')
        
        # Plot 3: Diversity
        ax3 = axes[1, 0]
        ax3.plot(generations, self.fitness_history['diversity'], 'purple', linewidth=2)
        ax3.fill_between(generations, 0, self.fitness_history['diversity'], alpha=0.3, color='purple')
        ax3.set_xlabel('Generation')
        ax3.set_ylabel('Population Diversity')
        ax3.set_title('Population Diversity Over Generations')
        ax3.set_ylim(0, 1.1)
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Improvement rate
        ax4 = axes[1, 1]
        improvements = [0]
        for i in range(1, len(self.fitness_history['best_fitness'])):
            imp = self.fitness_history['best_fitness'][i] - self.fitness_history['best_fitness'][i-1]
            improvements.append(max(0, imp))
        
        ax4.bar(generations, improvements, color='teal', alpha=0.7, width=1.0)
        ax4.set_xlabel('Generation')
        ax4.set_ylabel('Fitness Improvement')
        ax4.set_title('Fitness Improvement Per Generation')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ Convergence graph saved to: {save_path}")
        return save_path
    
    def get_convergence_stats(self):
        """Get convergence statistics for report"""
        if not self.fitness_history['best_fitness']:
            return {}
        
        initial_fitness = self.fitness_history['best_fitness'][0]
        final_fitness = self.fitness_history['best_fitness'][-1]
        improvement = final_fitness - initial_fitness
        improvement_percent = (improvement / initial_fitness * 100) if initial_fitness > 0 else 0
        
        # Find convergence point (when improvement < 1% for 10 consecutive generations)
        convergence_gen = self.generations
        for i in range(10, len(self.fitness_history['best_fitness'])):
            recent = self.fitness_history['best_fitness'][i-10:i]
            if max(recent) - min(recent) < final_fitness * 0.01:
                convergence_gen = i - 10
                break
        
        return {
            'initial_fitness': initial_fitness,
            'final_fitness': final_fitness,
            'improvement': improvement,
            'improvement_percent': improvement_percent,
            'convergence_generation': convergence_gen,
            'avg_diversity': np.mean(self.fitness_history['diversity']),
            'final_diversity': self.fitness_history['diversity'][-1]
        }


def calculate_manual_ideal_fitness(df, budget, game_mode='15s'):
    """
    Calculate the IDEAL fitness if we manually select the best players
    (greedy approach - highest performance score within budget)
    Used for accuracy calculation
    """
    structure = TEAM_STRUCTURES.get(game_mode, TEAM_STRUCTURES['15s'])
    
    # Group by position
    players_by_pos = {}
    for pos in structure.keys():
        players_by_pos[pos] = df[df['Position'].str.lower() == pos.lower()].copy()
    
    # Greedy selection: for each position, pick highest performance players within budget
    selected = []
    used_indices = set()
    remaining_budget = budget
    
    # Sort positions by required count (fill harder positions first)
    sorted_positions = sorted(structure.items(), key=lambda x: len(players_by_pos.get(x[0], [])))
    
    for pos, count in sorted_positions:
        candidates = players_by_pos.get(pos, df)
        if candidates.empty:
            candidates = df
        
        # Filter available and affordable
        available = candidates[~candidates.index.isin(used_indices)]
        available = available[available['Salary'] <= remaining_budget]
        
        # Sort by performance score (descending)
        available = available.sort_values('Performance_Score', ascending=False)
        
        selected_count = 0
        for idx, row in available.iterrows():
            if selected_count >= count:
                break
            if row['Salary'] <= remaining_budget:
                selected.append(idx)
                used_indices.add(idx)
                remaining_budget -= row['Salary']
                selected_count += 1
        
        # If not enough players selected, pick cheapest available
        if selected_count < count:
            remaining = df[~df.index.isin(used_indices)].sort_values('Salary')
            for idx, row in remaining.iterrows():
                if selected_count >= count:
                    break
                selected.append(idx)
                used_indices.add(idx)
                selected_count += 1
    
    # Calculate ideal fitness
    if selected:
        team_data = df.loc[selected]
        total_salary = team_data['Salary'].sum()
        performance = team_data['Performance_Score'].sum()
        
        if total_salary <= budget:
            utilization = total_salary / budget if budget > 0 else 0
            roi_bonus = utilization * performance * 0.1
            return performance + roi_bonus
    
    return 0


def run_accuracy_test(budget=5000000, game_mode='15s', strategies=None, num_runs=5):
    """
    Run accuracy test comparing GA output vs manual ideal
    """
    print("\n" + "="*70)
    print("ACCURACY & VALIDATION TEST")
    print("="*70)
    
    # Load data for manual calculation
    try:
        df = pd.read_csv(FILE_PATH, encoding='ISO-8859-1')
    except:
        df = pd.read_csv(FILE_PATH, encoding='utf-8')
    
    df.columns = df.columns.str.strip()
    
    if 'Salary' in df.columns:
        if df['Salary'].dtype == object:
            df['Salary'] = df['Salary'].astype(str).str.replace(r'[",]', '', regex=True)
        df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce').fillna(0)
    
    position_mapping = {
        'Prop': 'Prop', 'Hooker': 'Hooker', 'Lock': 'Lock', 'Secondrow': 'Lock',
        'Backrow': 'Backrow', 'Scrumhalf': 'Scrumhalf', 'Flyhalf': 'Flyhalf',
        'Fly': 'Flyhalf', 'Centre': 'Centre', 'Center': 'Centre',
        'Winger': 'Winger', 'Fullback': 'Fullback',
        'Utility Back': 'Centre', 'Utility Forward': 'Backrow'
    }
    df['Position'] = df['Position'].astype(str).str.strip().map(position_mapping).fillna(df['Position'])
    
    df['start_career'] = pd.to_numeric(df['start_career'], errors='coerce').fillna(2020)
    df['experience'] = 2024 - df['start_career']
    
    for col in ['club_try', 'club_W', 'club_starter', 'yellow card', 'red card']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0
    
    df['Performance_Score'] = (
        (df['experience'] * 1.0) + (df['club_try'] * 5.0) + (df['club_W'] * 3.0) +
        (df['club_starter'] * 2.0) + (df['yellow card'] * -10.0) + (df['red card'] * -25.0)
    )
    df['Performance_Score'] = df['Performance_Score'].apply(lambda x: max(x, 1))
    
    # Calculate manual ideal
    manual_ideal = calculate_manual_ideal_fitness(df, budget, game_mode)
    print(f"\nManual Ideal Fitness (Greedy Best): {manual_ideal:.2f}")
    
    # Run GA multiple times
    ga_results = []
    for run in range(num_runs):
        print(f"\n--- Run {run + 1}/{num_runs} ---")
        ga = ConvergenceAnalysisGA(budget, game_mode, strategies)
        _, fitness = ga.run()
        ga_results.append(fitness)
        print(f"GA Fitness: {fitness:.2f}")
    
    # Calculate accuracy
    avg_ga_fitness = np.mean(ga_results)
    best_ga_fitness = max(ga_results)
    worst_ga_fitness = min(ga_results)
    
    accuracy_avg = (avg_ga_fitness / manual_ideal * 100) if manual_ideal > 0 else 0
    accuracy_best = (best_ga_fitness / manual_ideal * 100) if manual_ideal > 0 else 0
    
    print("\n" + "="*70)
    print("ACCURACY RESULTS")
    print("="*70)
    print(f"Manual Ideal Fitness:     {manual_ideal:.2f}")
    print(f"GA Average Fitness:       {avg_ga_fitness:.2f}")
    print(f"GA Best Fitness:          {best_ga_fitness:.2f}")
    print(f"GA Worst Fitness:         {worst_ga_fitness:.2f}")
    print(f"GA Std Deviation:         {np.std(ga_results):.2f}")
    print("-"*70)
    print(f"ACCURACY (Average):       {accuracy_avg:.2f}%")
    print(f"ACCURACY (Best Run):      {accuracy_best:.2f}%")
    print("="*70)
    
    return {
        'manual_ideal': manual_ideal,
        'ga_average': avg_ga_fitness,
        'ga_best': best_ga_fitness,
        'ga_worst': worst_ga_fitness,
        'ga_std': np.std(ga_results),
        'accuracy_avg': accuracy_avg,
        'accuracy_best': accuracy_best,
        'all_runs': ga_results
    }


if __name__ == "__main__":
    # Run convergence analysis
    print("\n" + "="*70)
    print("RUNNING CONVERGENCE ANALYSIS")
    print("="*70)
    
    # Budget increased to accommodate 25 players (15s mode with reserves)
    # Average salary ~$350K × 25 players = ~$8.75M minimum
    ga = ConvergenceAnalysisGA(
        budget=10000000,  # $10M budget for realistic team building
        game_mode='15s',
        strategies=['Scrum', 'Lineout']
    )
    
    best_team, best_fitness = ga.run()
    
    # Generate convergence graph
    graph_path = ga.plot_convergence()
    
    # Get statistics
    stats = ga.get_convergence_stats()
    print("\nConvergence Statistics:")
    print(f"  Initial Fitness:      {stats['initial_fitness']:.2f}")
    print(f"  Final Fitness:        {stats['final_fitness']:.2f}")
    print(f"  Improvement:          {stats['improvement']:.2f} ({stats['improvement_percent']:.1f}%)")
    print(f"  Converged at Gen:     {stats['convergence_generation']}")
    print(f"  Average Diversity:    {stats['avg_diversity']:.2%}")
    
    # Run accuracy test
    accuracy_results = run_accuracy_test(budget=10000000, game_mode='15s', num_runs=5)
