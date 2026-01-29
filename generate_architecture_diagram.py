"""
System Architecture Diagram Generator
Rugby Scouting Strategy Optimization using Genetic Algorithm
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set up the figure with high DPI for quality
fig, ax = plt.subplots(1, 1, figsize=(20, 28), dpi=150)
ax.set_xlim(0, 100)
ax.set_ylim(0, 140)
ax.axis('off')
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('#f8f9fa')

# Color scheme
colors = {
    'header': '#1a237e',      # Dark blue
    'layer1': '#e3f2fd',      # Light blue (UI)
    'layer2': '#fff3e0',      # Light orange (Backend)
    'layer3': '#e8f5e9',      # Light green (Data)
    'layer4': '#fce4ec',      # Light pink (Strategy)
    'layer5': '#ede7f6',      # Light purple (GA)
    'layer6': '#e0f2f1',      # Light teal (Output)
    'box': '#ffffff',
    'border': '#37474f',
    'text': '#212121',
    'arrow': '#455a64',
    'highlight': '#c62828',   # Red for important
    'code': '#1565c0',        # Blue for code references
}

def draw_layer_box(y_start, y_end, color, title, subtitle=""):
    """Draw a layer background box"""
    rect = FancyBboxPatch((2, y_start), 96, y_end - y_start,
                          boxstyle="round,pad=0.02,rounding_size=0.5",
                          facecolor=color, edgecolor=colors['border'],
                          linewidth=2, alpha=0.7)
    ax.add_patch(rect)
    ax.text(5, y_end - 1.5, title, fontsize=12, fontweight='bold', 
            color=colors['header'], family='monospace')
    if subtitle:
        ax.text(5, y_end - 3.5, subtitle, fontsize=9, color=colors['code'], 
                family='monospace', style='italic')

def draw_box(x, y, width, height, text, subtext="", color='white', text_size=9):
    """Draw a component box"""
    rect = FancyBboxPatch((x, y), width, height,
                          boxstyle="round,pad=0.02,rounding_size=0.3",
                          facecolor=color, edgecolor=colors['border'],
                          linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2 + 0.8, text, fontsize=text_size, 
            fontweight='bold', ha='center', va='center', color=colors['text'])
    if subtext:
        ax.text(x + width/2, y + height/2 - 1.2, subtext, fontsize=7, 
                ha='center', va='center', color=colors['code'], family='monospace')

def draw_arrow(start, end, color=None):
    """Draw an arrow between points"""
    if color is None:
        color = colors['arrow']
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color, lw=2))

def draw_process_box(x, y, width, height, step_num, title, code_ref, details=None):
    """Draw a GA process step box"""
    # Main box
    rect = FancyBboxPatch((x, y), width, height,
                          boxstyle="round,pad=0.02,rounding_size=0.3",
                          facecolor='#ffffff', edgecolor=colors['highlight'],
                          linewidth=2)
    ax.add_patch(rect)
    
    # Step number circle
    circle = plt.Circle((x + 3, y + height - 2), 1.5, color=colors['highlight'], zorder=5)
    ax.add_patch(circle)
    ax.text(x + 3, y + height - 2, step_num, fontsize=10, fontweight='bold',
            ha='center', va='center', color='white', zorder=6)
    
    # Title
    ax.text(x + 7, y + height - 2, title, fontsize=10, fontweight='bold',
            va='center', color=colors['text'])
    
    # Code reference
    ax.text(x + 2, y + height - 4.5, f"📍 {code_ref}", fontsize=7,
            color=colors['code'], family='monospace')
    
    # Details
    if details:
        for i, detail in enumerate(details):
            ax.text(x + 3, y + height - 6.5 - (i * 1.8), f"• {detail}", 
                   fontsize=7, color=colors['text'])

# ==================== MAIN TITLE ====================
ax.text(50, 138, "SYSTEM ARCHITECTURE", fontsize=20, fontweight='bold',
        ha='center', color=colors['header'])
ax.text(50, 135.5, "Scouting Strategy Optimization for Rugby Team using Genetic Algorithm",
        fontsize=12, ha='center', color=colors['text'], style='italic')

# ==================== LAYER 1: USER INTERFACE ====================
draw_layer_box(125, 133, colors['layer1'], "LAYER 1: USER INTERFACE (PRESENTATION)",
               "📁 templates/index.html")

# UI Components
draw_box(8, 126.5, 18, 5, "INPUT FORM", "Budget, Team Name", '#bbdefb')
draw_box(28, 126.5, 18, 5, "STRATEGY SELECT", "Scrum, Lineout...", '#bbdefb')
draw_box(48, 126.5, 18, 5, "GAME MODE", "7s / 10s / 15s", '#bbdefb')
draw_box(68, 126.5, 18, 5, "LOCKED PLAYERS", "Complete My Team", '#bbdefb')

# Submit button
draw_box(38, 125, 24, 2.5, "POST /api/optimize", "", '#1976d2')
ax.text(50, 125.7, "▼", fontsize=14, ha='center', color='white', fontweight='bold')

# ==================== LAYER 2: BACKEND SERVER ====================
draw_layer_box(113, 124, colors['layer2'], "LAYER 2: BACKEND SERVER (APPLICATION)",
               "📁 app.py (Flask)")

draw_box(15, 118, 30, 4, "FLASK ROUTES", "/, /api/optimize, /api/players", '#ffe0b2')
draw_box(55, 118, 30, 4, "PREPROCESSING MODULE", "load_data() Lines 185-253", '#ffcc80')

draw_arrow((50, 125), (50, 122.5))

# ==================== LAYER 3: DATA LAYER ====================
draw_layer_box(99, 112, colors['layer3'], "LAYER 3: DATA LAYER",
               "📁 Statistic on best rugby players 2023-2024.csv (133 Players)")

# Dataset table representation
ax.text(12, 108, "RAW DATA:", fontsize=9, fontweight='bold', color=colors['text'])
table_data = "Name | Position | Salary | Age | Height | Weight | Stats..."
ax.text(12, 106, table_data, fontsize=7, family='monospace', color=colors['text'])

# Preprocessing steps
preprocess_steps = [
    "1. Clean Salary → '620,000' → 620000",
    "2. Normalize Positions → 'Fly' → 'Flyhalf'", 
    "3. Calculate Experience → 2024 - start_career",
    "4. Compute Performance_Score",
    "5. Group Players by Position"
]
ax.text(55, 108, "📍 PREPROCESSING STEPS:", fontsize=9, fontweight='bold', color=colors['highlight'])
for i, step in enumerate(preprocess_steps):
    ax.text(55, 106 - (i * 1.5), step, fontsize=7, family='monospace', color=colors['text'])

draw_arrow((50, 117), (50, 112.5))

# ==================== LAYER 4: STRATEGY CONFIG ====================
draw_layer_box(88, 98, colors['layer4'], "LAYER 4: STRATEGY CONFIGURATION",
               "📁 strategies.py (Lines 1-377)")

draw_box(10, 90, 25, 6, "BASIC PLAY", "Scrum, Lineout\nRuck, Tackle", '#f8bbd9')
draw_box(38, 90, 25, 6, "TACTICAL PLAY", "Pick & Go, Crash Ball\nLoop Pass, Switch", '#f8bbd9')
draw_box(66, 90, 25, 6, "CONTINGENCY", "Kick Chase\nCounter Attack", '#f8bbd9')

draw_arrow((50, 99), (50, 96.5))

# ==================== LAYER 5: GA ENGINE ====================
draw_layer_box(28, 87, colors['layer5'], "LAYER 5: GENETIC ALGORITHM ENGINE",
               "📁 app.py (RugbyScoutGA Class Lines 148-800)")

# GA Process Steps
y_pos = 80
step_height = 8

# Step 1: Initialization
draw_process_box(5, y_pos, 43, step_height, "1", "INITIALIZATION",
                "create_random_team() - Lines 254-320",
                ["Generate POPULATION_SIZE (50-150) random teams",
                 "Respect team structure: {Prop:2, Hooker:1...}",
                 "Include locked players if specified"])

# Step 2: Fitness Evaluation
draw_process_box(52, y_pos, 43, step_height, "2", "FITNESS EVALUATION",
                "calculate_fitness() - Lines 322-395",
                ["IF Salary > Budget → FITNESS = 0 ❌",
                 "Performance_Score + Strategy_Bonus",
                 "ROI_Bonus for budget efficiency"])

y_pos -= 10

# Step 3: Selection
draw_process_box(5, y_pos, 43, step_height, "3", "SELECTION + ELITISM",
                "run() method + elite_size = 10",
                ["Sort population by fitness (DESC)",
                 "Select TOP 50% to survive",
                 "Keep TOP 10 elites unchanged"])

# Step 4: Crossover
draw_process_box(52, y_pos, 43, step_height, "4", "CROSSOVER",
                "crossover() - Lines 278-290",
                ["Single-Point Crossover at midpoint",
                 "Parent1[:7] + Parent2[7:] → Child1",
                 "Parent2[:7] + Parent1[7:] → Child2"])

y_pos -= 10

# Step 5: Mutation
draw_process_box(5, y_pos, 43, step_height, "5", "MUTATION",
                "_mutate() - Lines 502-560",
                ["IF random() < MUTATION_RATE",
                 "Replace 1 player with same position",
                 "Locked players CANNOT be mutated"])

# Step 6: Repair
draw_process_box(52, y_pos, 43, step_height, "6", "REPAIR MECHANISM",
                "fix_duplicates() - Lines 322-350",
                ["Remove duplicate players",
                 "Replace with valid alternatives",
                 "Ensure correct team size"])

y_pos -= 10

# Step 7: Termination
draw_process_box(25, y_pos, 50, step_height, "7", "TERMINATION CHECK",
                "for gen in range(GENERATIONS)",
                ["IF generation < GENERATIONS → Go to Step 2",
                 "ELSE → Return BEST TEAM found",
                 "Output: List of optimal player indices"])

# Arrows between GA steps
draw_arrow((47, 84), (52, 84), colors['highlight'])
draw_arrow((73, 80), (73, 78), colors['highlight'])
draw_arrow((73, 70), (48, 70), colors['highlight'])
draw_arrow((5, 64), (5, 62), colors['highlight'])
draw_arrow((48, 64), (48, 62), colors['highlight'])

# Loop back arrow
ax.annotate('', xy=(95, 75), xytext=(95, 55),
            arrowprops=dict(arrowstyle='->', color=colors['highlight'], lw=2,
                           connectionstyle="arc3,rad=0.3"))
ax.text(96, 65, "LOOP", fontsize=8, rotation=90, va='center', color=colors['highlight'])

draw_arrow((50, 44), (50, 42))

# ==================== LAYER 6: OUTPUT ====================
draw_layer_box(5, 27, colors['layer6'], "LAYER 6: OUTPUT GENERATION",
               "📁 app.py Lines 600-700, templates/index.html")

# Output components
draw_box(8, 15, 25, 10, "POST-PROCESSING", 
         "Starters vs Reserves\nValue Score calc\nMarket status", '#b2dfdb')
draw_box(38, 15, 25, 10, "JSON RESPONSE",
         "success: true\nstarters: [...]\nreserves: [...]", '#80cbc4')
draw_box(68, 15, 25, 10, "UI DISPLAY",
         "Team Table\nBudget Summary\nPlayer Cards", '#4db6ac')

# Final output box
draw_box(25, 7, 50, 6, "🏆 OPTIMIZED RUGBY TEAM OUTPUT", 
         "Starters + Reserves + Stats + Budget Analysis", '#00897b')
ax.patches[-1].set_edgecolor('#00897b')

# ==================== LEGEND ====================
ax.text(5, 3, "LEGEND:", fontsize=10, fontweight='bold', color=colors['text'])
legend_items = [
    ("📁", "File Location"),
    ("📍", "Code Reference (Lines)"),
    ("→", "Data Flow"),
    ("🔴", "GA Process Step"),
]
for i, (symbol, desc) in enumerate(legend_items):
    ax.text(18 + (i * 20), 3, f"{symbol} {desc}", fontsize=8, color=colors['text'])

# Code files summary
ax.text(5, 0.5, "KEY FILES: app.py | rugby_scouting_ga.py | strategies.py | index.html | CSV Dataset",
        fontsize=8, family='monospace', color=colors['code'])

plt.tight_layout()
plt.savefig('system_architecture_diagram.png', dpi=150, bbox_inches='tight',
            facecolor='#f8f9fa', edgecolor='none')
plt.savefig('system_architecture_diagram.pdf', dpi=150, bbox_inches='tight',
            facecolor='#f8f9fa', edgecolor='none')

print("✅ Diagram saved as:")
print("   - system_architecture_diagram.png")
print("   - system_architecture_diagram.pdf")
print(f"\n📁 Location: d:\\xampp\\htdocs\\fyp\\")

plt.show()
