# Chapter 4 Code Reference Guide - Exact Line Numbers

Panduan ini menyenaraikan SEMUA code references yang disebutkan dalam Chapter 4 report dengan **line numbers yang spesifik** untuk screenshot dan penerangan.

---

## 📁 Section 4.2.1: Data Preprocessing

### **Reference 1: Load Data Function**
- **File:** `app.py`
- **Lines:** 194-223
- **Function:** `load_data(self)`
- **Penerangan:** 
  - CSV loading dengan multiple encoding support (ISO-8859-1, UTF-8, CP1252)
  - Data cleaning untuk salary (buang quotes dan commas)
  - Position normalization (standardize nama posisi)
  - Experience calculation (tahun semasa - start_career)
  - Performance Score calculation

**Code untuk screenshot:**
```python
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
```

### **Reference 2: Position Mapping**
- **File:** `app.py`
- **Lines:** 210-227
- **Penerangan:**
  - Standardize position names untuk handle inconsistencies
  - Map sinonim ke nama standard (e.g., "Fly" → "Flyhalf", "Center" → "Centre")
  - Fallback untuk unknown positions

**Code untuk screenshot:**
```python
if 'Position' in df.columns:
    df['Position'] = df['Position'].astype(str).str.strip()
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
```

### **Reference 3: Performance Score Calculation**
- **File:** `app.py`
- **Lines:** 236-245
- **Penerangan:**
  - Weighted formula untuk nilai prestasi pemain
  - Experience (×1.0) + Tries (×5.0) + Wins (×3.0) + Starts (×2.0)
  - Penalty untuk cards: Yellow (-10.0), Red (-25.0)
  - Minimum score = 1 (avoid negative values)

**Code untuk screenshot:**
```python
df['Performance_Score'] = (
    (df['experience'] * 1.0) + 
    (df['club_try'] * 5.0) + 
    (df['club_W'] * 3.0) +
    (df['club_starter'] * 2.0) +
    (df['yellow card'] * -10.0) +
    (df['red card'] * -25.0)
)
df['Performance_Score'] = df['Performance_Score'].apply(lambda x: max(x, 1))
```

---

## 📁 Section 4.2.2: Implementation of Genetic Algorithm

### **A. Chromosome Representation**

**Reference 4: Team Structure Definition**
- **File:** `app.py`
- **Lines:** 111-126
- **Constant:** `TEAM_STRUCTURES`
- **Penerangan:**
  - Define struktur pasukan untuk 7s, 10s, 15s
  - Setiap posisi ada quota (berapa orang diperlukan)
  - Used untuk initialize population dan validate teams

**Code untuk screenshot:**
```python
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
```

### **B. Initialization Process**

**Reference 5: Create Random Team Function**
- **File:** `app.py`
- **Lines:** 248-319
- **Function:** `create_random_team(self)`
- **Penerangan:**
  - Support untuk locked players (Complete My Team mode)
  - Budget-aware initialization - pilih dari cheapest players first
  - Fallback mechanism jika budget tidak mencukupi

**Code untuk screenshot (STEP 1 - Locked Players):**
```python
def create_random_team(self):
    team_indices = []
    used_indices = set()
    current_salary = 0.0
    
    # STEP 1: Add locked players first (if any)
    positions_filled = {pos: 0 for pos in self.target_structure.keys()}
    
    for locked_idx in self.locked_players:
        if locked_idx in self.df.index:
            locked_player = self.df.loc[locked_idx]
            player_pos = locked_player['Position']
            
            if player_pos in positions_filled:
                if positions_filled[player_pos] < self.target_structure.get(player_pos, 0):
                    team_indices.append(locked_idx)
                    used_indices.add(locked_idx)
                    current_salary += locked_player['Salary']
                    positions_filled[player_pos] += 1
```

**Code untuk screenshot (STEP 2 - Fill Remaining Positions):**
```python
    # STEP 2: Fill remaining positions with random players
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
```

### **C. Fitness Function Design**

**Reference 6: Calculate Fitness Function**
- **File:** `app.py`
- **Lines:** 321-357
- **Function:** `calculate_fitness(self, team_indices)`
- **Penerangan:**
  - **HARD CONSTRAINT:** Budget violation = fitness 0 (Knapsack problem)
  - Check for duplicate players
  - Calculate strategy-based performance score
  - ROI bonus untuk encourage budget efficiency

**Code untuk screenshot:**
```python
def calculate_fitness(self, team_indices):
    try:
        team_data = self.df.loc[team_indices]
    except KeyError: 
        return 0  # Invalid indices
    
    total_salary = team_data['Salary'].sum()
    
    # ═══ KEKANGAN KNAPSACK: HARD CONSTRAINT ═══
    # Jika jumlah gaji > bajet, kromosom ini GAGAL
    if total_salary > self.budget:
        return 0  # ❌ GAGAL - Langgar kekangan budget
    
    # Check for duplicate players (tidak boleh pemain sama)
    if len(team_indices) != len(set(team_indices)): 
        return 0  # ❌ GAGAL - Pemain duplikat
    
    # ═══ HITUNG PERFORMANCE SCORE (Berdasarkan Strategy) ═══
    performance_score = self._calculate_strategy_fitness(team_data)
    
    # ═══ ROI BONUS: Reward untuk efficiency ═══
    budget_utilization = total_salary / self.budget  # 0.0 to 1.0
    roi_bonus = budget_utilization * performance_score * 0.10
    
    # ═══ FINAL FITNESS = Performance Score + ROI Bonus ═══
    final_fitness = performance_score + roi_bonus
    
    return max(1, final_fitness)
```

**Reference 7: Strategy Fitness Calculation**
- **File:** `app.py`
- **Lines:** 359-450
- **Function:** `_calculate_strategy_fitness(self, team_data)`
- **Penerangan:**
  - Apply strategy-specific weights dari strategies.py
  - Handle different attributes: weight, height, age, tries, cards
  - Position preference bonus

**Code untuk screenshot (Strategy Weights Application):**
```python
def _calculate_strategy_fitness(self, team_data):
    if not self.strategy_weights:
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
            min_weight = self.strategy_constraints.get('weight_min', 80)
            max_weight = self.strategy_constraints.get('weight_max', 120)
            
            weight_scores = []
            for w in team_data['weight']:
                if min_weight <= w <= max_weight:
                    weight_scores.append(w)
                else:
                    penalty = abs(w - max(min_weight, min(max_weight, w))) / 10
                    weight_scores.append(max(1, w - penalty))
            
            score_contribution = sum(weight_scores) * weight / 100
            total_score += score_contribution
```

### **D. Genetic Operators**

**Reference 8: Selection Operator**
- **File:** `app.py`
- **Lines:** 827-846
- **Location:** Inside `run()` function - STEP 3
- **Penerangan:**
  - **Truncation Selection** - pilih top performers sahaja
  - Sort population by fitness (highest first)
  - Pilih HANYA teams yang valid (fitness > 0 = lepas budget constraint)
  - Fallback mechanism jika tiada valid teams (ambil top teams walaupun over-budget)
  - Elite size = 10 (minimum survivors)

**Code untuk screenshot:**
```python
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
```

**Reference 9: Crossover Operator**
- **File:** `app.py`
- **Lines:** 848-870
- **Location:** Inside `run()` function - STEP 4 & 5
- **Penerangan:**
  - **Single-Point Crossover** dengan elitism
  - Simpan elite (top 10) terus ke next generation
  - Pilih 2 parents secara random dari survivors
  - Cut chromosome di midpoint (position 7/8 untuk 15s)
  - Gabungkan: child = parent1[:cut] + parent2[cut:]
  - Apply mutation dengan probability 25%
  - Repair child untuk fix duplicates

**Code untuk screenshot:**
```python
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
```

**Reference 10: Mutation Operator**
- **File:** `app.py`
- **Lines:** 452-504
- **Function:** `_mutate(self, child)`
- **Penerangan:**
  - Position-preserving mutation (ganti dengan pemain dari posisi sama)
  - 50% greedy (pilih higher performance), 50% random
  - Locked players TIDAK BOLEH dimutasi

**Code untuk screenshot:**
```python
def _mutate(self, child):
    if len(child) == 0:
        return child
    
    # Get indices yang BOLEH dimutasi (bukan locked players)
    mutable_indices = [i for i, player_idx in enumerate(child) 
                      if player_idx not in self.locked_players]
    if not mutable_indices:
        return child  # Semua pemain locked, tak boleh mutate
    # Pilih index rawak untuk dimutasi
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
```

**Reference 11: Repair Team Function**
- **File:** `app.py`
- **Lines:** 506-548
- **Function:** `repair_team(self, team_indices)`
- **Penerangan:**
  - Fix duplicate players after crossover
  - Replace duplicates dengan better players (sort by Performance_Score)
  - Locked players tidak akan diganti

**Code untuk screenshot:**
```python
def repair_team(self, team_indices):
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
            # Duplicate found - replace with better player
            candidates = self.players_by_pos.get(required_pos)
            if candidates is not None:
                available = candidates[~candidates.index.isin(seen)]
                if not available.empty:
                    # Sort by Performance_Score descending
                    available_sorted = available.sort_values('Performance_Score', ascending=False)
                    new_idx = available_sorted.index[0]
                    new_team.append(new_idx)
                    seen.add(new_idx)
```

### **E. Evolution Loop**

**Reference 12: Main GA Run Function**
- **File:** `app.py`
- **Lines:** 768-876
- **Function:** `run(self)`
- **Penerangan:**
  - Generate initial population (150 chromosomes)
  - Loop untuk 50 generations
  - Evaluation → Selection → Crossover → Mutation → Elitism
  - Track best team and statistics

**Code untuk screenshot (Initialization & Tracking):**
```python
def run(self):
    # STEP 1: JANA POPULASI AWAL (Beratus kromosom)
    print(f"🧬 Menjana {self.population_size} kromosom awal...")
    population = [self.create_random_team() for _ in range(self.population_size)]
    
    best_team_indices = None
    best_fitness = -1
    best_team_cost = float('inf')
    minimum_team_cost = float('inf')
    
    # Track statistics
    valid_teams_per_gen = []
```

**Code untuk screenshot (Generational Loop):**
```python
    for gen in range(self.generations):
        # STEP 2: PENILAIAN FITNESS (Knapsack Check)
        evaluated = []
        valid_count = 0
        
        for individual in population:
            fitness = self.calculate_fitness(individual)
            team_cost = self.df.loc[individual]['Salary'].sum()
            
            # Track jika valid (fitness > 0 = lepas kekangan budget)
            if fitness > 0:
                valid_count += 1
                minimum_team_cost = min(minimum_team_cost, team_cost)
                
                # Update best team
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_team_indices = individual
                    best_team_cost = team_cost
                elif fitness == best_fitness and team_cost < best_team_cost:
                    best_team_indices = individual
                    best_team_cost = team_cost
            
            evaluated.append((individual, fitness, team_cost))
        
        valid_teams_per_gen.append(valid_count)
```

**Code untuk screenshot (Selection):**
```python
        # STEP 3: SELEKSI SURVIVORS
        evaluated.sort(key=lambda x: x[1], reverse=True)
        
        # Pilih survivors - HANYA teams yang valid (fitness > 0)
        survivors = []
        for ind, fit, cost in evaluated:
            if fit > 0:
                survivors.append(ind)
        
        # Fallback jika tiada valid teams
        if len(survivors) < self.elite_size:
            for ind, fit, cost in evaluated:
                if ind not in survivors:
                    survivors.append(ind)
                if len(survivors) >= self.elite_size:
                    break
```

**Code untuk screenshot (Crossover & Mutation):**
```python
        # STEP 4 & 5: CROSSOVER + MUTATION
        new_population = []
        
        # ELITISM: Simpan top performers
        elite = [x[0] for x in evaluated[:self.elite_size] if x[1] > 0]
        new_population.extend(elite)
        
        # Jana anak-anak baru melalui crossover & mutation
        while len(new_population) < self.population_size:
            # CROSSOVER: Pilih 2 parents
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            
            # Single-point crossover
            cut_point = len(parent1) // 2
            child = list(parent1[:cut_point]) + list(parent2[cut_point:])
            
            # MUTATION
            if random.random() < self.mutation_rate:
                child = self._mutate(child)
            
            # Repair child
            child = self.repair_team(child)
            new_population.append(child)
        
        population = new_population
```

---

## 📁 Section 4.3: User Interface

**Reference 13: Flask Route - Optimize Endpoint**
- **File:** `app.py`
- **Lines:** 1152-1217
- **Route:** `/optimize`
- **Penerangan:**
  - Main API endpoint untuk optimization
  - Receive budget, mode, strategies, locked_players
  - Call GA dan return results dengan analytics

**Code untuk screenshot:**
```python
@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.json
        budget = data.get('budget', 5000000)
        mode = data.get('mode', '15s')
        strategies = data.get('strategies', ['Scrum'])
        build_mode = data.get('build_mode', 'scratch')
        locked_players = data.get('locked_players', [])
        
        # Ensure budget is integer
        budget = int(budget) if isinstance(budget, str) else int(budget)
        
        # Ensure strategies is a list
        if isinstance(strategies, str):
            strategies = [strategies]
        
        # Ensure locked_players is a list of integers
        locked_players = [int(p) for p in locked_players] if locked_players else []
        
        print(f"Processing: Budget=${budget}, Mode={mode}, Strategies={' + '.join(strategies)}")
        print(f"Build Mode: {build_mode_display}, Locked Players: {len(locked_players)}")
        
        ga = RugbyScoutGA(budget, mode, strategies, locked_players)
        team_result = ga.run()
        
        starters = team_result['starters']
        reserves = team_result['reserves']
        
        total_cost = sum(p['salary'] for p in starters + reserves)
        total_score = sum(p['score'] for p in starters + reserves)
```

**Reference 12: HTML Template - Main Interface**
- **File:** `templates/index.html`
- **Lines:** 1-50 (Header section)
- **Penerangan:**
  - Bunga Raya themed header
  - Budget input field
  - Game mode selector (7s/10s/15s)

**Reference 13: Strategy Selection Interface**
- **File:** `templates/index.html`
- **Lines:** Check strategy selection section
- **Penerangan:**
  - Multiple strategy selection with tooltips
  - Categories: Offensive, Defensive, Balanced

---

## 📁 Section 4.4: Evaluation Results

**Reference 14: Convergence Analysis Script**
- **File:** `convergence_analysis.py`
- **Lines:** 1-100 (Main ConvergenceAnalysisGA class)
- **Penerangan:**
  - Extended GA class dengan convergence tracking
  - Plot 4 graphs: Fitness Progression, Best Fitness, Diversity, Improvement Rate
  - Generate static/images/convergence_graph.png

**Reference 15: Accuracy Test**
- **File:** `convergence_analysis.py`
- **Lines:** 200-250 (run_accuracy_test function)
- **Penerangan:**
  - Compare GA vs Manual Ideal (Greedy baseline)
  - Run 5 times untuk statistical validation
  - Calculate accuracy percentage

---

## 📁 Strategies System

**Reference 16: Strategy Definitions**
- **File:** `strategies.py`
- **Lines:** 1-150
- **Penerangan:**
  - Define all 9 strategies (Scrum Power, Running Rugby, etc.)
  - Fitness weights per strategy
  - Constraints (weight_min, height_min, etc.)

**Code untuk screenshot:**
```python
STRATEGIES = {
    'Scrum': {
        'name': 'Scrum Power',
        'description': 'Dominasi melalui kuasa scrum',
        'fitness_weights': {
            'weight': 0.30,
            'height': 0.15,
            'Performance_Score': 0.40,
            'starter': 0.15
        },
        'constraints': {
            'weight_min': 95,
            'height_min': 1.80
        },
        'preferred_positions': ['Prop', 'Hooker', 'Lock']
    },
    # ... more strategies
}
```

---

## 🎯 Quick Reference Summary

| Section | File | Lines | Purpose |
|---------|------|-------|---------|
| 4.2.1 Data Preprocessing | app.py | 194-245 | Load, clean, calculate performance |
| 4.2.2.A Chromosome | app.py | 111-126 | Team structure definition |
| 4.2.2.B Initialization | app.py | 248-319 | Create random team with budget-aware |
| 4.2.2.C Fitness | app.py | 321-450 | Calculate fitness + strategy weights |
| 4.2.2.D Selection | app.py | 827-846 | Truncation selection (Top 50%) |
| 4.2.2.D Crossover | app.py | 848-870 | Single-point crossover + elitism |
| 4.2.2.D Mutation | app.py | 452-504 | Position-preserving mutation |
| 4.2.2.D Repair | app.py | 506-548 | Fix duplicates after crossover |
| 4.2.2.E Evolution Loop | app.py | 768-876 | Main GA run function |
| 4.3 API Endpoint | app.py | 1152-1217 | Flask optimize route |
| 4.4 Convergence | convergence_analysis.py | 1-250 | Tracking & graphing |
| Strategies | strategies.py | 1-150 | Strategy definitions |

---

## 📸 Screenshot Tips

**Untuk setiap code reference:**

1. **Buka file** dalam VS Code
2. **Navigate to line number** (Ctrl+G)
3. **Highlight code block** yang disebutkan
4. **Screenshot** dengan line numbers visible (kiri side bar)
5. **Crop** untuk focus pada relevant code
6. **Annotate** jika perlu (arrow, highlight important lines)

**Recommended Screenshot Tool:** 
- Windows Snipping Tool (Win+Shift+S)
- VS Code Screenshot Extension
- ShareX (for advanced annotations)

**Formatting Tips:**
- Font size: 12-14pt (readable in report)
- Theme: Light theme (better for printing)
- Line numbers: ON
- Minimap: OFF (untuk save space)

---

## ✅ Verification Checklist

Semak bahawa setiap screenshot ada:
- [ ] Line numbers visible di sebelah kiri
- [ ] File name/path di title bar atau caption
- [ ] Code readable (tidak blur)
- [ ] Proper indentation preserved
- [ ] Complete function/code block (jangan potong separuh)
- [ ] Comments included (jika ada dalam original code)

---

**Generated:** January 25, 2026  
**Purpose:** Chapter 4 Report Code Documentation  
**Total References:** 16 code blocks across 3 main files
