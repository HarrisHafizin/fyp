# 🎯 Quick Answer: Selection & Crossover Operators Location

## ✅ Selection Operator

**📍 Location:**
- **File:** `app.py`
- **Lines:** 827-846
- **Inside Function:** `run(self)` - STEP 3

**📝 What it does:**
- **Truncation Selection** strategy
- Sorts all teams by fitness (highest first)
- Keeps only valid teams (fitness > 0 = within budget)
- Fallback: if < 10 valid teams, add top teams even if over budget

**💻 Exact Code:**
```python
# STEP 3: SELEKSI SURVIVORS (Hanya yang lepas budget constraint)
# Sort by fitness (highest first)
evaluated.sort(key=lambda x: x[1], reverse=True)

# Pilih survivors - HANYA teams yang valid (fitness > 0)
survivors = []
for ind, fit, cost in evaluated:
    if fit > 0:  # Hanya teams yang lepas kekangan Knapsack
        survivors.append(ind)

# Jika tiada valid teams, guna top teams walaupun over-budget
if len(survivors) < self.elite_size:
    for ind, fit, cost in evaluated:
        if ind not in survivors:
            survivors.append(ind)
        if len(survivors) >= self.elite_size:
            break
```

---

## ✅ Crossover Operator

**📍 Location:**
- **File:** `app.py`  
- **Lines:** 848-870
- **Inside Function:** `run(self)` - STEP 4 & 5

**📝 What it does:**
- **Single-Point Crossover** with elitism
- Preserves top 10 best teams (elite)
- Randomly selects 2 parents from survivors
- Cuts chromosomes at midpoint (position 7 or 8 for 15s)
- Creates child: `child = parent1[:cut] + parent2[cut:]`
- Applies mutation (25% probability)
- Repairs duplicates

**💻 Exact Code:**
```python
# STEP 4 & 5: CROSSOVER + MUTATION
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

---

## 🔍 Visual Flow in Code

```
run() function (Lines 768-876):
│
├─ [Line 787] Initialize population (150 teams)
│
├─ [Line 795] FOR EACH GENERATION (50 generations):
│   │
│   ├─ [Lines 800-824] STEP 2: Fitness Evaluation
│   │   └─ Calculate fitness for all 150 teams
│   │
│   ├─ [Lines 827-846] ✅ STEP 3: SELECTION OPERATOR ✅
│   │   ├─ Sort by fitness (descending)
│   │   └─ Select survivors (only valid teams)
│   │
│   └─ [Lines 848-870] ✅ STEP 4: CROSSOVER OPERATOR ✅
│       ├─ Preserve elite (top 10)
│       ├─ Select 2 parents randomly
│       ├─ Single-point crossover
│       ├─ Mutation (25% chance)
│       └─ Repair duplicates
│
└─ [Lines 876-905] Return best team found
```

---

## 📸 Screenshot Guide

### For Selection Operator:
1. Open `app.py` in VS Code
2. Press `Ctrl+G` → type `827`
3. Highlight lines **827-846**
4. Take screenshot showing:
   - Line numbers (827-846)
   - The comment "STEP 3: SELEKSI SURVIVORS"
   - The sorting code: `evaluated.sort()`
   - The loop: `for ind, fit, cost in evaluated:`
   - The fallback mechanism: `if len(survivors) < self.elite_size:`

### For Crossover Operator:
1. Open `app.py` in VS Code
2. Press `Ctrl+G` → type `848`
3. Highlight lines **848-870**
4. Take screenshot showing:
   - Line numbers (848-870)
   - The comment "STEP 4 & 5: CROSSOVER + MUTATION"
   - Elitism code: `elite = [x[0] for x in evaluated[:self.elite_size]`
   - The while loop: `while len(new_population) < self.population_size:`
   - Parent selection: `parent1 = random.choice(survivors)`
   - Crossover code: `cut_point = len(parent1) // 2`
   - Child creation: `child = list(parent1[:cut_point]) + list(parent2[cut_point:])`

---

## 📋 Key Points for Report

**Selection Operator:**
- **Type:** Truncation Selection (deterministic)
- **Selection Pressure:** High (only top 50% survive)
- **Budget Constraint:** Hard constraint (rejects fitness = 0)
- **Elite Size:** 10 (minimum survivors)

**Crossover Operator:**
- **Type:** Single-Point Crossover
- **Elitism:** Top 10 preserved unchanged
- **Cut Point:** Midpoint (len/2)
- **Parent Selection:** Random from survivors
- **Mutation Rate:** 25% (0.25)
- **Repair:** Yes (fix duplicates after crossover)

---

## 📊 Complete GA Flow Summary

```
Generation Loop (50 iterations):
│
1️⃣ EVALUATION (Lines 800-824)
   └─ Calculate fitness for all 150 teams
   
2️⃣ SELECTION (Lines 827-846) ← ✅ SELECTION OPERATOR
   └─ Keep only valid teams (fitness > 0)
   
3️⃣ CROSSOVER (Lines 848-870) ← ✅ CROSSOVER OPERATOR
   ├─ Elitism: Preserve top 10
   ├─ Choose 2 parents randomly
   ├─ Cut at midpoint
   └─ Combine: child = parent1[:cut] + parent2[cut:]
   
4️⃣ MUTATION (Lines 866-867)
   └─ Call _mutate() with 25% probability
   
5️⃣ REPAIR (Line 870)
   └─ Fix duplicates via repair_team()
```

---

**Updated:** January 25, 2026  
**For:** Chapter 4 Report Documentation  
**Reference:** Section 4.2.2.D - Genetic Operators
