import pandas as pd
import numpy as np
import json

def build_data():
    df = pd.read_csv('raw_data.csv')
    months = ['Jan 2026', 'Feb 2026', 'Mar 2026', 'Apr 2026', 'May 2026', 'Jun 2026', 'Jul 2026', 'Aug 2026']
    
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
        df.loc[msm_indices[0], 'Product_Clean'] = 'MSM (Line 1 - High Price)'
        df.loc[msm_indices[1], 'Product_Clean'] = 'MSM (Line 2 - Standard Price)'
    
    for idx in df.index:
        if idx not in msm_indices:
            df.loc[idx, 'Product_Clean'] = df.loc[idx, 'Corporation \\ Product'].strip()

    df['Is_Corp_Rollup'] = False
    df.loc[df['Product_Clean'].isin(['ALBOMED*', 'SEMICAL*']), 'Is_Corp_Rollup'] = True
    df['Has_Asterisk'] = df['Product_Clean'].str.contains(r'\*')

    # Calculate Market Totals for each month
    # We will provide both pure product market and all rows totals
    pure_df = df[~df['Is_Corp_Rollup']].copy()
    
    market_monthly = []
    cum_v = 0.0
    cum_u = 0.0
    
    for i, m in enumerate(months):
        tot_v = float(pure_df[f'val_{m}'].sum())
        tot_u = float(pure_df[f'unit_{m}'].sum())
        cum_v += tot_v
        cum_u += tot_u
        
        avg_price = tot_v / tot_u if tot_u > 0 else 0
        
        v_mom = None
        u_mom = None
        if i > 0:
            prev_v = market_monthly[i-1]['value']
            prev_u = market_monthly[i-1]['units']
            v_mom = ((tot_v - prev_v) / prev_v * 100) if prev_v > 0 else None
            u_mom = ((tot_u - prev_u) / prev_u * 100) if prev_u > 0 else None
            
        market_monthly.append({
            'month': m,
            'index': i,
            'value': tot_v,
            'units': tot_u,
            'ytd_value': cum_v,
            'ytd_units': cum_u,
            'avg_price': avg_price,
            'val_growth_mom': v_mom,
            'unit_growth_mom': u_mom
        })

    # Prepare Products Data
    products = []
    
    for _, row in df.iterrows():
        p_name = row['Product_Clean']
        is_rollup = bool(row['Is_Corp_Rollup'])
        has_ast = bool(row['Has_Asterisk'])
        
        m_data = []
        p_cum_v = 0.0
        p_cum_u = 0.0
        
        for i, m in enumerate(months):
            val = float(row[f'val_{m}'])
            units = float(row[f'unit_{m}'])
            raw_s = float(row[f'raw_share_{m}'])
            p_cum_v += val
            p_cum_u += units
            
            # Market Share % in Chondroprotective Market
            tot_mkt_v = market_monthly[i]['value']
            tot_mkt_u = market_monthly[i]['units']
            
            val_share = (val / tot_mkt_v * 100) if tot_mkt_v > 0 else 0.0
            unit_share = (units / tot_mkt_u * 100) if tot_mkt_u > 0 else 0.0
            
            # MoM growth
            val_mom = None
            unit_mom = None
            val_contrib_pct = None
            unit_contrib_pct = None
            val_contrib_mkt = None
            unit_contrib_mkt = None
            share_change_val_pp = None
            share_change_unit_pp = None
            
            if i > 0:
                prev_val = float(row[f'val_{months[i-1]}'])
                prev_units = float(row[f'unit_{months[i-1]}'])
                prev_tot_v = market_monthly[i-1]['value']
                prev_tot_u = market_monthly[i-1]['units']
                
                # Product growth
                if prev_val > 0:
                    val_mom = ((val - prev_val) / prev_val * 100)
                elif val > 0:
                    val_mom = None # New launch / baseline 0
                else:
                    val_mom = 0.0
                    
                if prev_units > 0:
                    unit_mom = ((units - prev_units) / prev_units * 100)
                elif units > 0:
                    unit_mom = None
                else:
                    unit_mom = 0.0
                
                # Market share change in percentage points
                prev_val_share = (prev_val / prev_tot_v * 100) if prev_tot_v > 0 else 0.0
                prev_unit_share = (prev_units / prev_tot_u * 100) if prev_tot_u > 0 else 0.0
                share_change_val_pp = val_share - prev_val_share
                share_change_unit_pp = unit_share - prev_unit_share
                
                # Product Contribution to Market Growth
                # Formula A: Delta Sales / Delta Market Sales * 100 (Share of market expansion/contraction)
                # Formula B: Delta Sales / Prior Market Sales * 100 (Percentage points added to market growth rate)
                delta_mkt_v = tot_mkt_v - prev_tot_v
                delta_mkt_u = tot_mkt_u - prev_tot_u
                delta_p_v = val - prev_val
                delta_p_u = units - prev_units
                
                val_contrib_pct = (delta_p_v / delta_mkt_v * 100) if delta_mkt_v != 0 else 0.0
                unit_contrib_pct = (delta_p_u / delta_mkt_u * 100) if delta_mkt_u != 0 else 0.0
                
                val_contrib_mkt = (delta_p_v / prev_tot_v * 100) if prev_tot_v > 0 else 0.0
                unit_contrib_mkt = (delta_p_u / prev_tot_u * 100) if prev_tot_u > 0 else 0.0
                
            # Product vs Market classification
            mkt_v_mom = market_monthly[i]['val_growth_mom']
            mkt_u_mom = market_monthly[i]['unit_growth_mom']
            
            perf_vs_mkt_val = "N/A"
            if val_mom is not None and mkt_v_mom is not None:
                if val_mom > mkt_v_mom and val_mom > 0:
                    perf_vs_mkt_val = "Outperforming Market"
                elif val_mom > 0 and val_mom <= mkt_v_mom:
                    perf_vs_mkt_val = "Growing Slower than Market"
                elif val_mom <= 0 and mkt_v_mom > 0:
                    perf_vs_mkt_val = "Declining while Market Grows"
                elif val_mom > 0 and mkt_v_mom <= 0:
                    perf_vs_mkt_val = "Growing while Market Declines"
                else:
                    perf_vs_mkt_val = "Declining with Market"
                    
            m_data.append({
                'month': m,
                'month_idx': i,
                'value': val,
                'units': units,
                'ytd_value': p_cum_v,
                'ytd_units': p_cum_u,
                'avg_price': (val / units) if units > 0 else 0.0,
                'val_share': val_share,
                'unit_share': unit_share,
                'raw_share': raw_s,
                'val_mom': val_mom,
                'unit_mom': unit_mom,
                'share_change_val_pp': share_change_val_pp,
                'share_change_unit_pp': share_change_unit_pp,
                'val_contrib_pct': val_contrib_pct,
                'unit_contrib_pct': unit_contrib_pct,
                'val_contrib_mkt': val_contrib_mkt,
                'unit_contrib_mkt': unit_contrib_mkt,
                'perf_vs_mkt_val': perf_vs_mkt_val
            })
            
        products.append({
            'name': p_name,
            'is_corp_rollup': is_rollup,
            'has_asterisk': has_ast,
            'total_value': p_cum_v,
            'total_units': p_cum_u,
            'avg_price': (p_cum_v / p_cum_u) if p_cum_u > 0 else 0.0,
            'monthly': m_data
        })

    dataset = {
        'months': months,
        'market_monthly': market_monthly,
        'products': products
    }
    
    with open('dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)
    print("Saved dashboard_data.json successfully!")

if __name__ == '__main__':
    build_data()
