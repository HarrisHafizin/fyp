import pandas as pd
import random
import numpy as np

# ==========================================
# KEPERLUAN SISTEM (SYSTEM REQUIREMENTS)
# ==========================================
# 1. Python Version: 3.10, 3.11, atau 3.12 (Disarankan)
# 2. Libraries Wajib:
#    Sila buka Command Prompt (CMD) dan taip arahan ini:
#    pip install pandas numpy

# ==========================================
# 1. KONFIGURASI & PENGURUSAN DATA
# ==========================================

FILE_PATH = 'Statistic on best rugby players 2023-2024.csv'
BUDGET_LIMIT = 5000000  # Contoh: Bajet 5 Juta
POPULATION_SIZE = 50    # Jumlah pasukan dalam satu generasi
GENERATIONS = 100       # Berapa kali evolusi berlaku
MUTATION_RATE = 0.1     # Kebarangkalian tukar pemain
SALARY_PENALTY_FACTOR = 50  # Scaling penalty to prefer cheaper teams (higher -> stronger penalty)

# Struktur Pasukan Ragbi (15 Pemain) berdasarkan data CSV
# Kita akan pastikan GA memilih pemain mengikut slot ini supaya pasukan seimbang.
TEAM_STRUCTURE = {
    'Prop': 2,
    'Hooker': 1,
    'Lock': 2,
    'Backrow': 3,
    'Scrumhalf': 1,
    'Flyhalf': 1,
    'Centre': 2,
    'Winger': 2,
    'Fullback': 1
}

def load_and_prep_data(filepath):
    """
    Membaca CSV, membersihkan data gaji, dan mengira Skor Prestasi.
    """
    try:
        # Cuba baca dengan 'utf-8' dulu (standard)
        df = pd.read_csv(filepath)
    except UnicodeDecodeError:
        # Jika error (seperti 0xa0), guna encoding 'ISO-8859-1' (biasa untuk Excel)
        print("Format Excel dikesan, menukar mod pembacaan...")
        df = pd.read_csv(filepath, encoding='ISO-8859-1')
    except FileNotFoundError:
        print(f"Ralat: Fail '{filepath}' tidak dijumpai.")
        return None

    # 1. Bersihkan Data Gaji (Buang quote " dan koma ,)
    # Contoh: "620,000" -> 620000
    if 'Salary' in df.columns and df['Salary'].dtype == object:
        df['Salary'] = df['Salary'].astype(str).str.replace(r'[",]', '', regex=True)
    df['Salary'] = pd.to_numeric(df.get('Salary', pd.Series()), errors='coerce').fillna(0)

    # Pastikan lajur-lajur yang digunakan untuk kiraan adalah numeric — jika ada teks/ruangan kosong, tukar ke 0
    numeric_cols = ['start_career', 'club_try', 'club_W', 'club_starter', 'yellow card', 'red card', 'club_D', 'club_L', 'club_points', 'National_min']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[",]', '', regex=True), errors='coerce').fillna(0)

    # 2. Kira 'Performance Score' (Fungsi Kecergasan Individu)
    # Formula: (Experience) + (Tries * 5) + (Wins * 2) - (Yellow Cards * 10)
    # Ini adalah logik 'Scouting' untuk menilai pemain.
    
    # Anggap tahun semasa 2024 untuk kira experience
    current_year = 2024
    df['experience'] = current_year - df['start_career']
    
    # Formula Heuristik (Boleh diubah mengikut strategi manager)
    df['Performance_Score'] = (
        (df['experience'] * 1) + 
        (df['club_try'] * 5) + 
        (df['club_W'] * 3) +
        (df['club_starter'] * 2) - 
        (df['yellow card'] * 10) -
        (df['red card'] * 20)
    )
    
    # Pastikan skor tidak negatif (pilihan)
    df['Performance_Score'] = df['Performance_Score'].apply(lambda x: max(x, 1))

    # Bersihkan & normalkan nama posisi supaya seragam (buang whitespace & peta sinonim)
    def normalize_position(pos):
        p = str(pos).strip().lower()
        if 'second' in p or 'lock' in p:
            return 'Lock'
        if p in ('fly', 'flyhalf', 'fly half', 'fly-half'):
            return 'Flyhalf'
        if 'center' in p or 'centre' in p:
            return 'Centre'
        if 'winger' in p:
            return 'Winger'
        if 'prop' in p:
            return 'Prop'
        if 'hooker' in p:
            return 'Hooker'
        if 'scrum' in p or 'scrumhalf' in p or 'scrum half' in p:
            return 'Scrumhalf'
        if 'fullback' in p:
            return 'Fullback'
        if 'back' in p or 'backrow' in p or 'back row' in p:
            return 'Backrow'
        # Fallback: Title case the original
        return str(pos).strip().title()

    df['Position'] = df['Position'].apply(normalize_position)

    return df

# ==========================================
# 2. LOGIK GENETIC ALGORITHM
# ==========================================

class RugbyScoutGA:
    def __init__(self, dataframe, budget):
        self.df = dataframe
        self.budget = budget
        # Asingkan pemain ikut posisi untuk memudahkan pemilihan
        self.players_by_pos = {pos: self.df[self.df['Position'] == pos] for pos in TEAM_STRUCTURE.keys()}
        
        # Check adakah data cukup untuk setiap posisi
        for pos, count in TEAM_STRUCTURE.items():
            available = len(self.players_by_pos.get(pos, []))
            if available < count:
                print(f"AMARAN: Data tidak cukup untuk posisi {pos}. Perlukan {count}, ada {available}.")

        # Kira gaji minimum untuk pasukan (ambil pemain termurah bagi setiap posisi)
        self.min_team_salary = 0
        infeasible = False
        for pos, count in TEAM_STRUCTURE.items():
            candidates = self.players_by_pos.get(pos)
            if candidates is None or candidates.empty or len(candidates) < count:
                infeasible = True
                break
            cheapest = candidates.nsmallest(count, 'Salary')
            self.min_team_salary += int(cheapest['Salary'].sum())

        if infeasible:
            print("AMARAN: Tidak cukup pemain untuk membentuk pasukan lengkap berdasarkan struktur TEAM_STRUCTURE.")
            self.feasible = False
        else:
            self.feasible = True
            if self.min_team_salary > self.budget:
                print(f"AMARAN: Bajet ${self.budget:,} terlalu rendah — gaji minimum untuk membentuk pasukan ialah ${self.min_team_salary:,}.")
                self.feasible = False
            else:
                print(f"Nota: Gaji minimum pasukan yang mungkin ialah ${self.min_team_salary:,}.")

    def generate_budget_compliant_team(self, randomize=True, attempts=1000):
        """Try to build a team that strictly respects the budget.
        Strategy:
         - Build per-position candidate pools sorted by ascending salary
         - Randomly choose from the cheaper subset to allow variation but ensure total salary <= budget
         - If no sampled combination fits after attempts, fall back to the deterministic cheapest assignment
        Returns a list of player indices or None when impossible.
        """
        total_slots = sum(TEAM_STRUCTURE.values())

        # Precompute sorted pools
        pools = {}
        for pos, count in TEAM_STRUCTURE.items():
            candidates = self.players_by_pos.get(pos)
            if candidates is None or candidates.empty:
                pools[pos] = self.df.sort_values('Salary')  # fallback to whole pool
            else:
                pools[pos] = candidates.sort_values('Salary')

        # Quick check: cheapest deterministic assignment
        cheapest_team = []
        for pos, count in TEAM_STRUCTURE.items():
            pool = pools[pos]
            if len(pool) < count:
                return None
            cheapest_team.extend(pool.head(count).index.tolist())
        cheapest_salary = int(self.df.loc[cheapest_team]['Salary'].sum())
        if cheapest_salary <= self.budget:
            # If randomize, try to produce varied teams under budget
            if randomize:
                for _ in range(attempts):
                    team = []
                    used = set()
                    for pos, count in TEAM_STRUCTURE.items():
                        pool = pools[pos]
                        # select from the cheapest K (to avoid very expensive picks); K is min(len, 5+count)
                        K = min(len(pool), 5 + count)
                        choices = pool.head(K).index.tolist()
                        # sample unique for this position
                        sel = []
                        attempts_pos = 0
                        while len(sel) < count and attempts_pos < 20:
                            candidate = random.choice(choices)
                            if candidate not in used:
                                sel.append(candidate)
                                used.add(candidate)
                            attempts_pos += 1
                        if len(sel) < count:
                            # fill with cheapest available
                            for c in pool.head(count*2).index:
                                if c not in used and len(sel) < count:
                                    sel.append(c); used.add(c)
                        team.extend(sel)
                    total_salary = int(self.df.loc[team]['Salary'].sum())
                    if total_salary <= self.budget and len(team) == total_slots:
                        return [int(i) for i in team]
            # deterministic cheapest works
            return [int(i) for i in cheapest_team]

        # No feasible team possible
        return None

    def create_random_team(self):
        """Wrapper to create a random team; prefer budget-compliant teams when possible."""
        team = self.generate_budget_compliant_team(randomize=True)
        if team is None:
            # if no budget-compliant team possible, fall back to older robust method (non-budgeted)
            # This should rarely happen because feasibility is checked at init
            team = []
            selected_ids = set()
            total_slots = sum(TEAM_STRUCTURE.values())

            for pos, count in TEAM_STRUCTURE.items():
                candidates = self.players_by_pos.get(pos)

                if candidates is None or candidates.empty:
                    candidates = self.df

                available = candidates.index.difference(pd.Index(list(selected_ids)))
                if len(available) >= count:
                    chosen = self.df.loc[available].sample(n=count, replace=False)
                else:
                    chosen = candidates.sample(n=count, replace=True)

                for idx in chosen.index:
                    if idx in selected_ids:
                        alt = candidates.index.difference(pd.Index(list(selected_ids)))
                        if not alt.empty:
                            idx = alt[0]
                    team.append(int(idx))
                    selected_ids.add(int(idx))

            if len(team) < total_slots:
                remaining = total_slots - len(team)
                available = self.df.index.difference(pd.Index(list(selected_ids)))
                if len(available) >= remaining:
                    extra = self.df.loc[available].sample(n=remaining, replace=False)
                else:
                    extra = self.df.sample(n=remaining, replace=True)
                team.extend([int(i) for i in extra.index.tolist()])

        return team

    def calculate_fitness(self, team_indices):
        """
        Mengira kecergasan pasukan.
        Multi-objective style: maximize performance score but penalize higher team salary so optimizer
        prefers cheaper teams when scores are comparable.
        Jika Gaji > Bajet, Fitness = 0 (Hukuman).
        """
        team_data = self.df.loc[team_indices]
        total_salary = int(team_data['Salary'].sum())
        total_score = float(team_data['Performance_Score'].sum())

        if total_salary > self.budget:
            return 0  # Pasukan ini gagal (over budget)

        # Penalty proportional to fraction of budget used (scaled)
        penalty = (total_salary / self.budget) * SALARY_PENALTY_FACTOR
        fitness = total_score - penalty
        # Ensure non-negative fitness (optional)
        return max(fitness, 0)

    def crossover(self, parent1, parent2):
        """
        Melakukan crossover (kacukan) antara dua pasukan.
        Kita guna Single Point Crossover, tapi mesti hati-hati dengan posisi.
        Cara mudah: Ambil separuh pemain dari Parent 1, separuh dari Parent 2.
        """
        # Kerana struktur posisi tetap, kita boleh potong di tengah
        cut_point = len(parent1) // 2
        child1 = parent1[:cut_point] + parent2[cut_point:]
        child2 = parent2[:cut_point] + parent1[cut_point:]
        
        # Perbaiki duplikasi dan pastikan saiz pasukan betul
        child1 = self.fix_duplicates(child1)
        child2 = self.fix_duplicates(child2)
        return child1, child2

    def mutate(self, team_indices):
        """
        Mutasi: Tukar seorang pemain dengan pemain lain dari posisi yang SAMA.
        Tujuannya untuk cari opsyen lebih murah atau lebih perform.
        """
        if random.random() < MUTATION_RATE and len(team_indices) > 0:
            # Pilih satu slot rawak dalam team untuk ditukar
            idx_to_change = random.randint(0, len(team_indices) - 1)
            player_id = team_indices[idx_to_change]
            
            # Cari posisi pemain tersebut
            player_pos = self.df.loc[player_id]['Position']
            
            # Cari pengganti dari pool posisi yang sama (exclude current and already in team)
            candidates = self.players_by_pos.get(player_pos, self.df)
            available = candidates.index.difference(pd.Index(team_indices))
            
            if not available.empty:
                new_player_id = available.to_series().sample(1).iloc[0]
            else:
                # fallback: pick any different player
                alt = self.df.index.difference(pd.Index([player_id]))
                if not alt.empty:
                    new_player_id = alt.to_series().sample(1).iloc[0]
                else:
                    new_player_id = player_id  # no change possible
            
            team_indices[idx_to_change] = int(new_player_id)
            
        # Ensure no duplicates and proper team size/positions
        team_indices = self.fix_duplicates(team_indices)
        return team_indices

    def fix_duplicates(self, team_indices):
        """Ensure no duplicate player indices in team. Replaces duplicates with other candidates from same position when possible."""
        seen = set()
        new_team = []

        for pid in team_indices:
            pid = int(pid)
            if pid not in seen:
                new_team.append(pid)
                seen.add(pid)
            else:
                # duplicate — find replacement from same position not in seen
                try:
                    pos = self.df.loc[pid]['Position']
                except Exception:
                    pos = None
                candidates = self.players_by_pos.get(pos, self.df)
                alt = candidates.index.difference(pd.Index(list(seen)))
                if not alt.empty:
                    new_pid = int(alt[0])
                else:
                    # pick any not seen
                    alt2 = self.df.index.difference(pd.Index(list(seen)))
                    if not alt2.empty:
                        new_pid = int(alt2[0])
                    else:
                        new_pid = pid  # give up
                new_team.append(new_pid)
                seen.add(new_pid)

        # Fill missing slots if any
        total_slots = sum(TEAM_STRUCTURE.values())
        if len(new_team) < total_slots:
            remaining = total_slots - len(new_team)
            available = self.df.index.difference(pd.Index(list(seen)))
            if len(available) >= remaining:
                sample = self.df.loc[available].sample(n=remaining, replace=False)
            else:
                sample = self.df.sample(n=remaining, replace=True)
            new_team.extend([int(i) for i in sample.index.tolist()])

        return new_team

    def run(self):
        # 1. Initial Population
        population = [self.create_random_team() for _ in range(POPULATION_SIZE)]

        print(f"Mula mengoptimumkan skuad ragbi (Bajet: ${self.budget:,})...")
        if not self.feasible:
            print("Bajet/current dataset tidak membenarkan pembentukan pasukan yang lengkap dalam had ini. Tamat run.")
            return None

        for gen in range(GENERATIONS):
            # 2. Evaluate Fitness
            scores = [(individual, self.calculate_fitness(individual)) for individual in population]
            
            # Sort by fitness (Highest first)
            scores.sort(key=lambda x: x[1], reverse=True)
            
            # Simpan statistik
            best_team_gen = scores[0]
            if gen % 10 == 0:
                print(f"Generasi {gen}: Skor Terbaik = {best_team_gen[1]:.2f}")

            # 3. Selection (Top 50% survive)
            survivors = [x[0] for x in scores[:POPULATION_SIZE//2]]
            
            # 4. Crossover & Mutation
            new_population = []
            while len(new_population) < POPULATION_SIZE:
                p1 = random.choice(survivors)
                p2 = random.choice(survivors)
                c1, c2 = self.crossover(p1, p2)
                new_population.append(self.mutate(c1))
                new_population.append(self.mutate(c2))
            
            population = new_population

        # Return best team found in final generation
        final_scores = [(ind, self.calculate_fitness(ind)) for ind in population]
        best_team_indices = max(final_scores, key=lambda x: x[1])[0]
        return best_team_indices

# ==========================================
# 3. PAPARAN KEPUTUSAN
# ==========================================

def display_team(df, team_indices, budget=None):
    if team_indices is None:
        print("\nTiada pasukan sah dibentuk (bajet terhad atau data tidak mencukupi).")
        return

    team_data = df.loc[team_indices]
    total_salary = team_data['Salary'].sum()
    total_score = team_data['Performance_Score'].sum()
    
    print("\n" + "="*50)
    print("      HASIL OPTIMASI SCOUTING (DREAM TEAM)")
    print("="*50)
    print(f"{'Posisi':<15} {'Nama':<25} {'Gaji ($)':<15} {'Skor':<10}")
    print("-" * 65)
    
    for _, player in team_data.iterrows():
        name = f"{player['First-name']} {player['Name']}"
        print(f"{player['Position']:<15} {name:<25} {player['Salary']:<15,.0f} {player['Performance_Score']:.1f}")
        
    print("-" * 65)
    use_budget = BUDGET_LIMIT if budget is None else budget
    print(f"TOTAL GAJI  : ${total_salary:,.0f} (Bajet: ${use_budget:,.0f})")
    print(f"BAKI BAJET  : ${use_budget - total_salary:,.0f}")
    print(f"TOTAL SKOR  : {total_score:.2f}")
    print("="*50)

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    # Load Data
    df = load_and_prep_data(FILE_PATH)
    
    if df is not None:
        # Check posisi apa yang ada dalam CSV awak untuk update TEAM_STRUCTURE jika perlu
        # print("Posisi yang wujud:", df['Position'].unique())
        
        # Jalankan GA
        optimizer = RugbyScoutGA(df, BUDGET_LIMIT)
        best_team_indices = optimizer.run()
        
        # Tunjuk Result
        display_team(df, best_team_indices)     