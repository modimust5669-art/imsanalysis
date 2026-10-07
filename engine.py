import pandas as pd
import numpy as np
import json

def process_data():
    df = pd.read_csv('raw_data.csv')
    months = ['Jan 2026', 'Feb 2026', 'Mar 2026', 'Apr 2026', 'May 2026', 'Jun 2026', 'Jul 2026', 'Aug 2026']
    
    val_cols = [f'LC Value\n{m}' for m in months]
    unit_cols = [f'Units\n{m}' for m in months]
    share_cols = [f'Units Market Share\n{m}' for m in months]
    
    def clean_num(s):
        if pd.isna(s): return 0.0
        s = str(s).replace(',', '').replace('%', '').strip()
        return float(s) if s else 0.0

    # Clean columns
    for m in months:
        df[f'val_{m}'] = df[f'LC Value\n{m}'].apply(clean_num)
        df[f'unit_{m}'] = df[f'Units\n{m}'].apply(clean_num)
        df[f'raw_share_{m}'] = df[f'Units Market Share\n{m}'].apply(clean_num)

    # Distinguish duplicate MSM
    msm_indices = df[df['Corporation \\ Product'] == 'MSM'].index
    if len(msm_indices) == 2:
        df.loc[msm_indices[0], 'Product_Clean'] = 'MSM (Line 1 - Low Price)'
        df.loc[msm_indices[1], 'Product_Clean'] = 'MSM (Line 2 - High Price)'
    
    for idx in df.index:
        if idx not in msm_indices:
            df.loc[idx, 'Product_Clean'] = df.loc[idx, 'Corporation \\ Product'].strip()

    # Identify Corporation rollups vs Product lines
    # ALBOMED* and SEMICAL* are exact 100% duplicate rollups
    df['Is_Corp_Rollup'] = False
    df.loc[df['Product_Clean'].isin(['ALBOMED*', 'SEMICAL*']), 'Is_Corp_Rollup'] = True
    
    # We can also flag other asterisk rows as Corporation / Sub-brand
    df['Has_Asterisk'] = df['Product_Clean'].str.contains(r'\*')

    # Save processed dataframe summary
    print(f"Total Rows: {len(df)}")
    print(f"Corp Rollups flagged: {df['Is_Corp_Rollup'].sum()}")
    print(f"Pure Products: {(~df['Is_Corp_Rollup']).sum()}")
    
    # Calculate Market Totals for each month (using pure products for commercial accuracy)
    market_totals = {}
    pure_df = df[~df['Is_Corp_Rollup']].copy()
    
    for i, m in enumerate(months):
        tot_v = pure_df[f'val_{m}'].sum()
        tot_u = pure_df[f'unit_{m}'].sum()
        market_totals[m] = {
            'month': m,
            'month_idx': i,
            'total_value': tot_v,
            'total_units': tot_u,
            'avg_price': tot_v / tot_u if tot_u > 0 else 0
        }
        
    # MoM market growth
    for i, m in enumerate(months):
        if i == 0:
            market_totals[m]['val_growth_mom'] = None
            market_totals[m]['unit_growth_mom'] = None
        else:
            prev_m = months[i-1]
            prev_v = market_totals[prev_m]['total_value']
            prev_u = market_totals[prev_m]['total_units']
            market_totals[m]['val_growth_mom'] = ((market_totals[m]['total_value'] - prev_v) / prev_v * 100) if prev_v > 0 else None
            market_totals[m]['unit_growth_mom'] = ((market_totals[m]['total_units'] - prev_u) / prev_u * 100) if prev_u > 0 else None

    print("\n--- Market Monthly Performance (Pure Product Market) ---")
    for m in months:
        mt = market_totals[m]
        vg = f"{mt['val_growth_mom']:+.1f}%" if mt['val_growth_mom'] is not None else "N/A"
        ug = f"{mt['unit_growth_mom']:+.1f}%" if mt['unit_growth_mom'] is not None else "N/A"
        print(f"{m:8} | Value: {mt['total_value']:13,.0f} ({vg:>6}) | Units: {mt['total_units']:9,.0f} ({ug:>6}) | Avg Price: {mt['avg_price']:6.1f} LC")

    return df, months, market_totals

if __name__ == '__main__':
    process_data()
