import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ======================================================
# 1. DCF ENGINE  (Valuation Logic)
# ======================================================

def run_dcf(revenue_growth_y1_y5, terminal_growth, wacc, current_revenue, initial_fcf_margin):
    """
    Calculates Enterprise Value based on variable inputs.
    """
    # Forecast Period (5 Years)
    years = 5
    revenues = []
    fcfs = []
    
    # Year 1 Forecast
    rev = current_revenue * (1 + revenue_growth_y1_y5)
    revenues.append(rev)
    # Assume Margin expands slightly over time as they scale
    margin = initial_fcf_margin
    fcfs.append(rev * margin)
    
    # Years 2-5 Forecast
    for i in range(1, years):
        rev = revenues[-1] * (1 + (revenue_growth_y1_y5 * 0.9)) # Growth slows slightly each year
        revenues.append(rev)
        margin += 0.02 # Margin expansion (operating leverage)
        fcfs.append(rev * margin)
        
    # Terminal Value (Gordon Growth Model)
    # The value of the company forever after year 5
    terminal_value = (fcfs[-1] * (1 + terminal_growth)) / (wacc - terminal_growth)
    
    # Discounting Cash Flows to Present Value
    discount_factors = [(1 + wacc) ** i for i in range(1, years + 1)]
    pv_fcf = sum([fcf / df for fcf, df in zip(fcfs, discount_factors)])
    pv_terminal_value = terminal_value / ((1 + wacc) ** years)
    
    enterprise_value = pv_fcf + pv_terminal_value
    return enterprise_value

# ======================================================
# 2. BASE CASE INPUTS (Based on Research)
# ======================================================

# Financials (in £ Millions)
current_revenue_gbp = 1200  # FY25 Actual
initial_fcf_margin = 0.15   # Approx 15% Free Cash Flow Margin starting

# Base Assumptions
base_wacc = 0.105           # 10.5% (Tech/Bank Hybrid Risk)
base_growth = 0.30          # 30% Revenue Growth (CAGR)
base_terminal = 0.03        # 3% Long term growth

# ======================================================
# 3. SENSITIVITY ANALYSIS (Stress Testing)
# ======================================================

# We create ranges to test different outcomes
wacc_range = np.linspace(0.085, 0.125, 5) # 8.5% to 12.5%
growth_range = np.linspace(0.02, 0.04, 5) # 2% to 4% Terminal Growth

# Create the Data Table
sensitivity_data = np.zeros((len(wacc_range), len(growth_range)))

for r, w in enumerate(wacc_range):
    for c, g in enumerate(growth_range):
        ev = run_dcf(revenue_growth_y1_y5=base_growth, 
                     terminal_growth=g, 
                     wacc=w, 
                     current_revenue=current_revenue_gbp, 
                     initial_fcf_margin=initial_fcf_margin)
        sensitivity_data[r, c] = ev / 1000 # Convert to Billions

# Convert to DataFrame for plotting
df_sensitivity = pd.DataFrame(sensitivity_data, 
                              index=[f"{x:.1%}" for x in wacc_range], 
                              columns=[f"{x:.1%}" for x in growth_range])

# ======================================================
# 4. VISUALIZATION (Heatmap)
# ======================================================

plt.figure(figsize=(10, 8))
sns.set(style="white")

# Create Heatmap
ax = sns.heatmap(df_sensitivity, annot=True, fmt=".2f", cmap="RdYlGn", 
                 cbar_kws={'label': 'Enterprise Value (£bn)'}, linewidths=.5)

# Formatting
plt.title("Monzo Valuation Sensitivity Analysis (£ Billions)\nvariable: WACC vs. Terminal Growth Rate", fontsize=14, pad=20)
plt.ylabel("WACC (Discount Rate)", fontsize=12)
plt.xlabel("Terminal Growth Rate", fontsize=12)

# Highlight the Base Case area
plt.show()

# ======================================================
# 5. IMPLIED SHARE PRICE MODEL
# ======================================================

# 1. Calculate the raw valuation (result is in £ Millions, e.g., 9640.50)
base_case_val_mln = run_dcf(base_growth, base_terminal, base_wacc, current_revenue_gbp, initial_fcf_margin)

# 2. Define shares (also in Millions)
# Monzo has roughly 600m shares outstanding (hypothetically)
estimated_shares_mln = 600 

# 3. Simple division: Millions / Millions = GBP per share
share_price = base_case_val_mln / estimated_shares_mln

print(f"--- CALCULATOR OUTPUT ---")
print(f"Base Case Valuation: £{base_case_val_mln/1000:.2f} Billion")
print(f"Implied Share Price: £{share_price:.2f}")

# Sensitivity note (Ensure the index matches your heatmap labels)
wacc_check = "11.5%"
term_check = "3.0%"
if wacc_check in df_sensitivity.index and term_check in df_sensitivity.columns:
    val_drop = df_sensitivity.loc[wacc_check][term_check]
    print(f"Note: If WACC increases to {wacc_check}, Valuation drops to: £{val_drop:.2f}bn")
