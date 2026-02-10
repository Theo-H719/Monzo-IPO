import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. ASSUMPTIONS & INPUTS (FY26 Forecasts)
# ==========================================

# Financial Forecasts (in £ millions)
revenue_fy26_est = 1750
net_income_fy26_est = 214
free_cash_flow_fy26 = 250

# General Assumptions
risk_free_rate = 0.040  # UK 10Y Gilt approx
market_return = 0.095   # Equity Market Return
beta = 1.4              # Fintech Beta
tax_rate = 0.25

# WACC Calculation
cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
cost_of_debt = 0.065
debt_to_equity = 0.10
# Fixed WACC formula: (E/V * Re) + (D/V * Rd * (1-T))
wacc = (cost_of_equity * (1 - debt_to_equity)) + (cost_of_debt * (1 - tax_rate) * debt_to_equity)

# Comparable Multiples
mult_global_fintech = 8.5  
mult_us_neobank = 4.5      
mult_uk_challenger = 25.0  
mult_uk_trad = 8.0         

# ==========================================
# 2. DCF MODEL (Discounted Cash Flow)
# ==========================================

def calculate_dcf(growth_rate, terminal_growth, years=5):
    # Fixed: Initialized the list
    fcf_projections = []
    current_fcf = free_cash_flow_fy26
    
    for i in range(years):
        current_fcf = current_fcf * (1 + growth_rate)
        fcf_projections.append(current_fcf)
    
    # Terminal Value (Gordon Growth Method)
    terminal_value = fcf_projections[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    
    # Discount Factors
    discount_factors = [(1 + wacc) ** i for i in range(1, years + 1)]
    
    # Present Values
    pv_fcf = sum([fcf / df for fcf, df in zip(fcf_projections, discount_factors)])
    pv_terminal = terminal_value / ((1 + wacc) ** years)
    
    return pv_fcf + pv_terminal

# Scenarios
bear_dcf = calculate_dcf(growth_rate=0.15, terminal_growth=0.02)
base_dcf = calculate_dcf(growth_rate=0.30, terminal_growth=0.03)
bull_dcf = calculate_dcf(growth_rate=0.45, terminal_growth=0.04)

# ==========================================
# 3. COMPARABLE COMPANY ANALYSIS (COMPS)
# ==========================================

# Implied Valuations (Single points)
val_global_fintech = revenue_fy26_est * mult_global_fintech
val_us_neobank = revenue_fy26_est * mult_us_neobank
val_uk_challenger = net_income_fy26_est * mult_uk_challenger
val_uk_trad = net_income_fy26_est * mult_uk_trad

# ==========================================
# 4. VISUALIZATION (Football Field Chart)
# ==========================================

# Define ranges: [Label, Min, Max]
# For DCF, we use our calculated scenarios. For Comps, we apply a +/- 15% sensitivity.
valuation_ranges = [
    ['DCF Analysis', bear_dcf, bull_dcf],
    ['Global Fintech (EV/Rev)', val_global_fintech * 0.85, val_global_fintech * 1.15],
    ['US Neobank (EV/Rev)', val_us_neobank * 0.85, val_us_neobank * 1.15],
    ['UK Challenger (P/E)', val_uk_challenger * 0.85, val_uk_challenger * 1.15],
    ['UK Trad Bank (P/E)', val_uk_trad * 0.85, val_uk_trad * 1.15]
]

# Convert to DataFrame
df_val = pd.DataFrame(valuation_ranges, columns=['Methodology', 'Min_Val', 'Max_Val'])

# Plotting
plt.figure(figsize=(12, 7))
plt.title(f"Monzo Bank IPO Valuation Matrix (GBP Millions) - Feb 2026\nFY26E Revenue: £{revenue_fy26_est}m | FY26E Net Income: £{net_income_fy26_est}m", fontsize=14, fontweight='bold')

# Create horizontal bars
for i, row in df_val.iterrows():
    plt.plot([row['Min_Val'], row['Max_Val']], [i, i], color='#E94B35', linewidth=15, alpha=0.8) # Monzo "Hot Coral"
    plt.text(row['Max_Val'] + 200, i, f"£{row['Max_Val']/1000:.1f}bn", verticalalignment='center', color='black', fontsize=10)
    plt.text(row['Min_Val'] - 800, i, f"£{row['Min_Val']/1000:.1f}bn", verticalalignment='center', color='black', fontsize=10)

# Target IPO Range (Overlay)
plt.axvline(x=6500, color='grey', linestyle='--', label='IPO Target Floor (£6.5bn)')
plt.axvline(x=8500, color='black', linestyle='--', label='IPO Target Ceiling (£8.5bn)')

plt.yticks(range(len(df_val)), df_val['Methodology'], fontsize=11)
plt.xlabel('Implied Enterprise Value (£ Millions)', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.3)
plt.legend(loc='lower right')

plt.tight_layout()
plt.show()

# ==========================================
# 5. SUMMARY OUTPUT
# ==========================================

print("--- MONZO VALUATION SUMMARY (Feb 2026) ---")
print(f"Base Case DCF Valuation: £{base_dcf/1000:.2f} bn")
print(f"Implied Multiple (EV/Revenue FY26): {(base_dcf / revenue_fy26_est):.2f}x")
print("-" * 40)
print("Valuation Ranges by Methodology:")
for index, row in df_val.iterrows():
    print(f"{row['Methodology']}: £{row['Min_Val']/1000:.2f}bn - £{row['Max_Val']/1000:.2f}bn")
