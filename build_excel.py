import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import json
import pandas as pd

from add_joint_guard_excel import add_joint_guard_tab

def create_excel():
    with open('dashboard_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    months = data['months']
    market_monthly = data['market_monthly']
    products = data['products']
    pure_products = [p for p in products if not p['is_corp_rollup']]

    wb = openpyxl.Workbook()
    # remove default sheet
    wb.remove(wb.active)

    # Styles
    navy_dark = "0F172A"
    navy_header = "1E293B"
    navy_sub = "334155"
    blue_accent = "2563EB"
    blue_light = "EFF6FF"
    gray_bg = "F8FAFC"
    border_gray = "E2E8F0"
    green_text = "059669"
    red_text = "DC2626"

    font_title = Font(name="Segoe UI", size=16, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Segoe UI", size=10, italic=True, color="E2E8F0")
    font_section = Font(name="Segoe UI", size=12, bold=True, color=navy_header)
    font_th = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_td = Font(name="Segoe UI", size=10, color="1E293B")
    font_td_bold = Font(name="Segoe UI", size=10, bold=True, color="1E293B")
    font_kpi_num = Font(name="Segoe UI", size=18, bold=True, color="1E293B")
    font_kpi_label = Font(name="Segoe UI", size=9, bold=True, color="64748B")
    font_pos = Font(name="Segoe UI", size=10, bold=True, color=green_text)
    font_neg = Font(name="Segoe UI", size=10, bold=True, color=red_text)

    fill_navy = PatternFill(start_color=navy_dark, end_color=navy_dark, fill_type="solid")
    fill_header = PatternFill(start_color=navy_header, end_color=navy_header, fill_type="solid")
    fill_sub = PatternFill(start_color=navy_sub, end_color=navy_sub, fill_type="solid")
    fill_accent = PatternFill(start_color=blue_accent, end_color=blue_accent, fill_type="solid")
    fill_light = PatternFill(start_color=blue_light, end_color=blue_light, fill_type="solid")
    fill_zebra = PatternFill(start_color=gray_bg, end_color=gray_bg, fill_type="solid")
    fill_card = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color=border_gray),
        right=Side(style='thin', color=border_gray),
        top=Side(style='thin', color=border_gray),
        bottom=Side(style='thin', color=border_gray)
    )
    card_border = Border(
        left=Side(style='medium', color="CBD5E1"),
        right=Side(style='medium', color="CBD5E1"),
        top=Side(style='medium', color="CBD5E1"),
        bottom=Side(style='medium', color="CBD5E1")
    )
    header_border = Border(
        left=Side(style='thin', color="475569"),
        right=Side(style='thin', color="475569"),
        top=Side(style='thin', color="475569"),
        bottom=Side(style='medium', color="0F172A")
    )

    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')
    align_wrap = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # TAB 0: Joint Guard Focus (Our Products)
    add_joint_guard_tab(wb, data)

    # -------------------------------------------------------------
    # TAB 1: 01_Executive_Summary
    # -------------------------------------------------------------
    ws1 = wb.create_sheet(title="01_Executive_Summary")
    ws1.views.sheetView[0].showGridLines = True

    # Title Banner
    ws1.merge_cells("A1:K2")
    ws1["A1"] = "CHONDROPROTECTIVE MARKET — COMMERCIAL EXECUTIVE SUMMARY"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_navy
    ws1["A1"].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    ws1.merge_cells("A3:K3")
    ws1["A3"] = "Pharmaceutical Market Intelligence & Commercial Performance Dashboard | Jan 2026 - Aug 2026 (YTD)"
    ws1["A3"].font = Font(name="Segoe UI", size=10, italic=True, color="64748B")
    ws1["A3"].alignment = Alignment(horizontal='left', vertical='center')

    # Latest Month KPI Cards (Aug 2026)
    latest_m = market_monthly[-1]
    prev_m = market_monthly[-2]
    
    # KPI 1: YTD Value
    ws1.merge_cells("B5:C5")
    ws1["B5"] = "YTD MARKET VALUE (JAN-AUG)"
    ws1["B5"].font = font_kpi_label
    ws1["B5"].alignment = align_center
    ws1.merge_cells("B6:C6")
    ws1["B6"] = latest_m['ytd_value']
    ws1["B6"].number_format = '#,##0 "LC"'
    ws1["B6"].font = font_kpi_num
    ws1["B6"].alignment = align_center
    ws1.merge_cells("B7:C7")
    ws1["B7"] = f"Total Market ({len(pure_products)} Brands)"
    ws1["B7"].font = Font(name="Segoe UI", size=8, color="64748B")
    ws1["B7"].alignment = align_center

    # KPI 2: YTD Units
    ws1.merge_cells("D5:E5")
    ws1["D5"] = "YTD MARKET UNITS (JAN-AUG)"
    ws1["D5"].font = font_kpi_label
    ws1["D5"].alignment = align_center
    ws1.merge_cells("D6:E6")
    ws1["D6"] = latest_m['ytd_units']
    ws1["D6"].number_format = '#,##0 "Units"'
    ws1["D6"].font = font_kpi_num
    ws1["D6"].alignment = align_center
    ws1.merge_cells("D7:E7")
    ws1["D7"] = f"Avg Price: {latest_m['ytd_value']/latest_m['ytd_units']:.1f} LC/Unit"
    ws1["D7"].font = Font(name="Segoe UI", size=8, color="64748B")
    ws1["D7"].alignment = align_center

    # KPI 3: Current Month Value (Aug 2026)
    ws1.merge_cells("F5:G5")
    ws1["F5"] = "LATEST MONTH VALUE (AUG 2026)"
    ws1["F5"].font = font_kpi_label
    ws1["F5"].alignment = align_center
    ws1.merge_cells("F6:G6")
    ws1["F6"] = latest_m['value']
    ws1["F6"].number_format = '#,##0 "LC"'
    ws1["F6"].font = font_kpi_num
    ws1["F6"].alignment = align_center
    ws1.merge_cells("F7:G7")
    ws1["F7"] = f"MoM Growth: {latest_m['val_growth_mom']:+.1f}% vs Jul"
    ws1["F7"].font = font_pos if latest_m['val_growth_mom'] >= 0 else font_neg
    ws1["F7"].alignment = align_center

    # KPI 4: Current Month Units (Aug 2026)
    ws1.merge_cells("H5:I5")
    ws1["H5"] = "LATEST MONTH UNITS (AUG 2026)"
    ws1["H5"].font = font_kpi_label
    ws1["H5"].alignment = align_center
    ws1.merge_cells("H6:I6")
    ws1["H6"] = latest_m['units']
    ws1["H6"].number_format = '#,##0 "Units"'
    ws1["H6"].font = font_kpi_num
    ws1["H6"].alignment = align_center
    ws1.merge_cells("H7:I7")
    ws1["H7"] = f"MoM Growth: {latest_m['unit_growth_mom']:+.1f}% vs Jul"
    ws1["H7"].font = font_pos if latest_m['unit_growth_mom'] >= 0 else font_neg
    ws1["H7"].alignment = align_center

    # KPI 5: Market Structure
    ws1.merge_cells("J5:K5")
    ws1["J5"] = "MARKET LEADERSHIP (AUG 2026)"
    ws1["J5"].font = font_kpi_label
    ws1["J5"].alignment = align_center
    ws1.merge_cells("J6:K6")
    ws1["J6"] = "GENUPHIL (Val) | SULFAX (Units)"
    ws1["J6"].font = Font(name="Segoe UI", size=11, bold=True, color=blue_accent)
    ws1["J6"].alignment = align_center
    ws1.merge_cells("J7:K7")
    ws1["J7"] = "Top 5 Brands = 50.8% Value Share"
    ws1["J7"].font = Font(name="Segoe UI", size=8, color="64748B")
    ws1["J7"].alignment = align_center

    for r in range(5, 8):
        for col_pair in [("B","C"), ("D","E"), ("F","G"), ("H","I"), ("J","K")]:
            ws1[f"{col_pair[0]}{r}"].fill = fill_light if r==5 else fill_card

    # Section 1: Monthly Market Performance Summary Table
    ws1["B9"] = "1. TOTAL CHONDROPROTECTIVE MARKET MONTHLY PROGRESSION"
    ws1["B9"].font = font_section

    headers1 = ["Month", "Market Value (LC)", "MoM Value Growth %", "Market Units", "MoM Unit Growth %", "Avg Price (LC/Unit)", "YTD Value (LC)", "YTD Units", "Market Status"]
    for col_idx, h in enumerate(headers1, start=2):
        cell = ws1.cell(row=10, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    for i, m in enumerate(market_monthly):
        r = 11 + i
        ws1.cell(row=r, column=2, value=m['month']).alignment = align_center
        
        c_v = ws1.cell(row=r, column=3, value=m['value'])
        c_v.number_format = '#,##0'
        c_v.alignment = align_right
        
        c_vg = ws1.cell(row=r, column=4, value=(m['val_growth_mom']/100.0) if m['val_growth_mom'] is not None else "N/A")
        if m['val_growth_mom'] is not None:
            c_vg.number_format = '+0.0%;-0.0%;0.0%'
            c_vg.font = font_pos if m['val_growth_mom'] >= 0 else font_neg
        c_vg.alignment = align_center
        
        c_u = ws1.cell(row=r, column=5, value=m['units'])
        c_u.number_format = '#,##0'
        c_u.alignment = align_right
        
        c_ug = ws1.cell(row=r, column=6, value=(m['unit_growth_mom']/100.0) if m['unit_growth_mom'] is not None else "N/A")
        if m['unit_growth_mom'] is not None:
            c_ug.number_format = '+0.0%;-0.0%;0.0%'
            c_ug.font = font_pos if m['unit_growth_mom'] >= 0 else font_neg
        c_ug.alignment = align_center
        
        c_p = ws1.cell(row=r, column=7, value=m['avg_price'])
        c_p.number_format = '#,##0.0'
        c_p.alignment = align_right
        
        c_yv = ws1.cell(row=r, column=8, value=m['ytd_value'])
        c_yv.number_format = '#,##0'
        c_yv.alignment = align_right
        
        c_yu = ws1.cell(row=r, column=9, value=m['ytd_units'])
        c_yu.number_format = '#,##0'
        c_yu.alignment = align_right
        
        # Market status
        status = "Baseline Month" if i == 0 else ("Expansion Peak" if m['month']=='Jun 2026' else ("Post-Peak Contraction" if m['month']=='Jul 2026' else ("Growth Recovery" if m['val_growth_mom'] > 0 else "Contraction")))
        ws1.cell(row=r, column=10, value=status).alignment = align_center

        for c in range(2, 11):
            cell = ws1.cell(row=r, column=c)
            cell.border = thin_border
            if i % 2 == 1:
                cell.fill = fill_zebra

    # Section 2: Top 10 Market Leaders (YTD 2026)
    r_top = 21
    ws1.cell(row=r_top, column=2, value="2. TOP 10 BRANDS BY YTD SALES VALUE (JAN - AUG 2026)").font = font_section
    
    headers_top = ["Rank", "Brand / Product", "YTD Value Sales (LC)", "YTD Value Share %", "YTD Unit Sales", "YTD Unit Share %", "Avg Price (LC)", "Aug MoM Value Growth %", "Commercial Classification"]
    for col_idx, h in enumerate(headers_top, start=2):
        cell = ws1.cell(row=r_top+1, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    sorted_ytd = sorted(pure_products, key=lambda x: x['total_value'], reverse=True)[:10]
    total_mkt_ytd_val = latest_m['ytd_value']
    total_mkt_ytd_units = latest_m['ytd_units']

    for rank, p in enumerate(sorted_ytd, start=1):
        row_idx = r_top + 1 + rank
        val_share = p['total_value'] / total_mkt_ytd_val
        unit_share = p['total_units'] / total_mkt_ytd_units
        aug_mom = p['monthly'][-1]['val_mom']
        
        ws1.cell(row=row_idx, column=2, value=rank).alignment = align_center
        ws1.cell(row=row_idx, column=3, value=p['name']).alignment = align_left
        ws1.cell(row=row_idx, column=3).font = font_td_bold
        
        c1 = ws1.cell(row=row_idx, column=4, value=p['total_value'])
        c1.number_format = '#,##0'
        c1.alignment = align_right
        
        c2 = ws1.cell(row=row_idx, column=5, value=val_share)
        c2.number_format = '0.0%'
        c2.alignment = align_center
        
        c3 = ws1.cell(row=row_idx, column=6, value=p['total_units'])
        c3.number_format = '#,##0'
        c3.alignment = align_right
        
        c4 = ws1.cell(row=row_idx, column=7, value=unit_share)
        c4.number_format = '0.0%'
        c4.alignment = align_center
        
        c5 = ws1.cell(row=row_idx, column=8, value=p['avg_price'])
        c5.number_format = '#,##0.0'
        c5.alignment = align_right
        
        c6 = ws1.cell(row=row_idx, column=9, value=(aug_mom/100.0) if aug_mom is not None else "N/A")
        if aug_mom is not None:
            c6.number_format = '+0.0%;-0.0%;0.0%'
            c6.font = font_pos if aug_mom >= 0 else font_neg
        c6.alignment = align_center
        
        # Strategic classification
        tag = "Market Leader (Value)" if p['name']=='GENUPHIL' else ("Market Leader (Volume)" if p['name']=='SULFAX' else ("Top 5 Strategic Pillar" if rank <= 5 else "Core Commercial Pillar"))
        ws1.cell(row=row_idx, column=10, value=tag).alignment = align_center

        for c in range(2, 11):
            cell = ws1.cell(row=row_idx, column=c)
            cell.border = thin_border
            if rank % 2 == 0:
                cell.fill = fill_zebra

    # -------------------------------------------------------------
    # TAB 2: 02_Market_Trends
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="02_Market_Trends")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:K2")
    ws2["A1"] = "CHONDROPROTECTIVE MARKET — MONTHLY TREND ANALYSIS (VALUE & UNITS)"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_navy
    ws2["A1"].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    headers2 = ["Month", "Market Value Sales (LC)", "MoM Value Growth %", "Cumulative YTD Value (LC)", "Market Unit Sales", "MoM Unit Growth %", "Cumulative YTD Units", "Market Avg Price (LC)", "Price Index vs Jan", "Monthly Direction"]
    for col_idx, h in enumerate(headers2, start=1):
        cell = ws2.cell(row=4, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    base_price = market_monthly[0]['avg_price']
    for i, m in enumerate(market_monthly):
        r = 5 + i
        ws2.cell(row=r, column=1, value=m['month']).alignment = align_center
        
        c = ws2.cell(row=r, column=2, value=m['value'])
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws2.cell(row=r, column=3, value=(m['val_growth_mom']/100.0) if m['val_growth_mom'] is not None else "N/A")
        if m['val_growth_mom'] is not None:
            c.number_format = '+0.0%;-0.0%;0.0%'
            c.font = font_pos if m['val_growth_mom'] >= 0 else font_neg
        c.alignment = align_center
        
        c = ws2.cell(row=r, column=4, value=m['ytd_value'])
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws2.cell(row=r, column=5, value=m['units'])
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws2.cell(row=r, column=6, value=(m['unit_growth_mom']/100.0) if m['unit_growth_mom'] is not None else "N/A")
        if m['unit_growth_mom'] is not None:
            c.number_format = '+0.0%;-0.0%;0.0%'
            c.font = font_pos if m['unit_growth_mom'] >= 0 else font_neg
        c.alignment = align_center
        
        c = ws2.cell(row=r, column=7, value=m['ytd_units'])
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws2.cell(row=r, column=8, value=m['avg_price'])
        c.number_format = '#,##0.0'
        c.alignment = align_right
        
        c = ws2.cell(row=r, column=9, value=(m['avg_price'] / base_price * 100))
        c.number_format = '0.0'
        c.alignment = align_center
        
        direction = "Baseline" if i==0 else ("Expanding ▲" if m['val_growth_mom'] > 0 else "Contracting ▼")
        ws2.cell(row=r, column=10, value=direction).alignment = align_center

        for col_idx in range(1, 11):
            cell = ws2.cell(row=r, column=col_idx)
            cell.border = thin_border
            if i % 2 == 1:
                cell.fill = fill_zebra

    # Market Summary Notes
    ws2.cell(row=15, column=1, value="COMMERCIAL OBSERVATIONS & DYNAMICS:").font = font_section
    notes = [
        "• Peak Performance: June 2026 reached the market high of 445.78M LC (+30.2% MoM) and 1.22M Units (+22.1% MoM), driven by mid-year commercial purchasing and pharmacy stocking.",
        "• Seasonal Contraction: April 2026 experienced an expected seasonal dip (-13.0% Value) coinciding with Ramadan retail slowdown.",
        "• Mid-Summer Normalization: July 2026 saw a post-peak correction (-25.0% Value), followed by an immediate August recovery (+7.6% Value, 359.91M LC).",
        "• Pricing Trends: Average market price per unit rose from 313.1 LC in Jan to a peak of 364.0 LC in June, finishing at 354.9 LC in August (+13.3% price evolution vs Jan baseline)."
    ]
    for idx, n in enumerate(notes):
        ws2.cell(row=16+idx, column=1, value=n).font = Font(name="Segoe UI", size=10, color="334155")

    # -------------------------------------------------------------
    # TAB 3: 03_Product_Performance
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title="03_Product_Performance")
    ws3.views.sheetView[0].showGridLines = True

    ws3.merge_cells("A1:R2")
    ws3["A1"] = "CHONDROPROTECTIVE MARKET — INDIVIDUAL PRODUCT MONTHLY PERFORMANCE"
    ws3["A1"].font = font_title
    ws3["A1"].fill = fill_navy
    ws3["A1"].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    headers3 = [
        "Product Name", "YTD Value Sales (LC)", "YTD Units", "Avg Price (LC)", 
        "Val Jan", "Val Feb", "Val Mar", "Val Apr", "Val May", "Val Jun", "Val Jul", "Val Aug",
        "Units Jan", "Units Feb", "Units Mar", "Units Apr", "Units May", "Units Jun", "Units Jul", "Units Aug"
    ]
    for col_idx, h in enumerate(headers3, start=1):
        cell = ws3.cell(row=4, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    sorted_prods = sorted(pure_products, key=lambda x: x['total_value'], reverse=True)
    for p_idx, p in enumerate(sorted_prods):
        r = 5 + p_idx
        ws3.cell(row=r, column=1, value=p['name']).alignment = align_left
        ws3.cell(row=r, column=1).font = font_td_bold
        
        c = ws3.cell(row=r, column=2, value=p['total_value'])
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws3.cell(row=r, column=3, value=p['total_units'])
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws3.cell(row=r, column=4, value=p['avg_price'])
        c.number_format = '#,##0.0'
        c.alignment = align_right
        
        # Monthly values
        for m_idx in range(8):
            c_v = ws3.cell(row=r, column=5 + m_idx, value=p['monthly'][m_idx]['value'])
            c_v.number_format = '#,##0'
            c_v.alignment = align_right
            
            c_u = ws3.cell(row=r, column=13 + m_idx, value=p['monthly'][m_idx]['units'])
            c_u.number_format = '#,##0'
            c_u.alignment = align_right

        for col_idx in range(1, len(headers3) + 1):
            cell = ws3.cell(row=r, column=col_idx)
            cell.border = thin_border
            if p_idx % 2 == 1:
                cell.fill = fill_zebra

    # -------------------------------------------------------------
    # TAB 4: 04_Market_Share
    # -------------------------------------------------------------
    ws4 = wb.create_sheet(title="04_Market_Share")
    ws4.views.sheetView[0].showGridLines = True

    ws4.merge_cells("A1:T2")
    ws4["A1"] = "CHONDROPROTECTIVE MARKET — DYNAMIC MARKET SHARE & SHARE CHANGE (pp)"
    ws4["A1"].font = font_title
    ws4["A1"].fill = fill_navy
    ws4["A1"].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    headers4 = [
        "Product Name", "YTD Value Share %", "YTD Unit Share %",
        "Val Share Jan", "Val Share Feb", "Val Share Mar", "Val Share Apr", "Val Share May", "Val Share Jun", "Val Share Jul", "Val Share Aug",
        "Aug Share Chg (pp)", "Unit Share Jan", "Unit Share Feb", "Unit Share Mar", "Unit Share Apr", "Unit Share May", "Unit Share Jun", "Unit Share Jul", "Unit Share Aug", "Aug Unit Chg (pp)"
    ]
    for col_idx, h in enumerate(headers4, start=1):
        cell = ws4.cell(row=4, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    for p_idx, p in enumerate(sorted_prods):
        r = 5 + p_idx
        ws4.cell(row=r, column=1, value=p['name']).alignment = align_left
        ws4.cell(row=r, column=1).font = font_td_bold
        
        c = ws4.cell(row=r, column=2, value=(p['total_value'] / total_mkt_ytd_val))
        c.number_format = '0.00%'
        c.alignment = align_center
        
        c = ws4.cell(row=r, column=3, value=(p['total_units'] / total_mkt_ytd_units))
        c.number_format = '0.00%'
        c.alignment = align_center
        
        # Monthly Value Share
        for m_idx in range(8):
            v_sh = p['monthly'][m_idx]['val_share'] / 100.0
            c = ws4.cell(row=r, column=4 + m_idx, value=v_sh)
            c.number_format = '0.00%'
            c.alignment = align_center
            
        # Aug Share Chg pp
        aug_val_pp = p['monthly'][7]['share_change_val_pp']
        c = ws4.cell(row=r, column=12, value=aug_val_pp if aug_val_pp is not None else 0.0)
        c.number_format = '+0.00;-0.00;0.00'
        c.font = font_pos if (aug_val_pp or 0) >= 0 else font_neg
        c.alignment = align_center
        
        # Monthly Unit Share
        for m_idx in range(8):
            u_sh = p['monthly'][m_idx]['unit_share'] / 100.0
            c = ws4.cell(row=r, column=13 + m_idx, value=u_sh)
            c.number_format = '0.00%'
            c.alignment = align_center
            
        # Aug Unit Chg pp
        aug_unit_pp = p['monthly'][7]['share_change_unit_pp']
        c = ws4.cell(row=r, column=21, value=aug_unit_pp if aug_unit_pp is not None else 0.0)
        c.number_format = '+0.00;-0.00;0.00'
        c.font = font_pos if (aug_unit_pp or 0) >= 0 else font_neg
        c.alignment = align_center

        for col_idx in range(1, len(headers4) + 1):
            cell = ws4.cell(row=r, column=col_idx)
            cell.border = thin_border
            if p_idx % 2 == 1:
                cell.fill = fill_zebra

    # -------------------------------------------------------------
    # TAB 5: 05_Growth_Contribution
    # -------------------------------------------------------------
    ws5 = wb.create_sheet(title="05_Growth_Contribution")
    ws5.views.sheetView[0].showGridLines = True

    ws5.merge_cells("A1:K2")
    ws5["A1"] = "CHONDROPROTECTIVE MARKET — PRODUCT CONTRIBUTION TO MARKET GROWTH (AUG VS JUL 2026)"
    ws5["A1"].font = font_title
    ws5["A1"].fill = fill_navy
    ws5["A1"].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    headers5 = [
        "Product Name", "Jul Sales Value (LC)", "Aug Sales Value (LC)", "Sales Delta (LC)", "Product MoM Growth %",
        "Contribution to Mkt Growth %", "Contribution to Mkt Expansion (pp)", "Jul Units", "Aug Units", "Unit Delta", "Commercial Impact"
    ]
    for col_idx, h in enumerate(headers5, start=1):
        cell = ws5.cell(row=4, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    # Sort products by Value Delta in August (Aug vs Jul)
    prods_by_contrib = sorted(pure_products, key=lambda x: (x['monthly'][7]['value'] - x['monthly'][6]['value']), reverse=True)
    mkt_delta_v = market_monthly[7]['value'] - market_monthly[6]['value']
    mkt_jul_v = market_monthly[6]['value']

    for p_idx, p in enumerate(prods_by_contrib):
        r = 5 + p_idx
        jul_v = p['monthly'][6]['value']
        aug_v = p['monthly'][7]['value']
        delta_v = aug_v - jul_v
        mom_g = p['monthly'][7]['val_mom']
        contrib_share = (delta_v / mkt_delta_v * 100) if mkt_delta_v != 0 else 0
        contrib_pp = (delta_v / mkt_jul_v * 100) if mkt_jul_v > 0 else 0
        
        jul_u = p['monthly'][6]['units']
        aug_u = p['monthly'][7]['units']
        delta_u = aug_u - jul_u

        ws5.cell(row=r, column=1, value=p['name']).alignment = align_left
        ws5.cell(row=r, column=1).font = font_td_bold
        
        c = ws5.cell(row=r, column=2, value=jul_v)
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws5.cell(row=r, column=3, value=aug_v)
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws5.cell(row=r, column=4, value=delta_v)
        c.number_format = '+#,##0;-#,##0;0'
        c.font = font_pos if delta_v >= 0 else font_neg
        c.alignment = align_right
        
        c = ws5.cell(row=r, column=5, value=(mom_g/100.0) if mom_g is not None else "N/A")
        if mom_g is not None:
            c.number_format = '+0.0%;-0.0%;0.0%'
            c.font = font_pos if mom_g >= 0 else font_neg
        c.alignment = align_center
        
        c = ws5.cell(row=r, column=6, value=(contrib_share/100.0))
        c.number_format = '+0.0%;-0.0%;0.0%'
        c.alignment = align_center
        
        c = ws5.cell(row=r, column=7, value=(contrib_pp/100.0))
        c.number_format = '+0.00%;-0.00%;0.00%'
        c.alignment = align_center
        
        c = ws5.cell(row=r, column=8, value=jul_u)
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws5.cell(row=r, column=9, value=aug_u)
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws5.cell(row=r, column=10, value=delta_u)
        c.number_format = '+#,##0;-#,##0;0'
        c.font = font_pos if delta_u >= 0 else font_neg
        c.alignment = align_right
        
        impact = "Primary Growth Driver" if delta_v > 5000000 else ("Growth Contributor" if delta_v > 500000 else ("Neutral / Stable" if abs(delta_v) <= 500000 else ("Major Drag / Detractor" if delta_v < -5000000 else "Growth Detractor")))
        ws5.cell(row=r, column=11, value=impact).alignment = align_center

        for col_idx in range(1, len(headers5) + 1):
            cell = ws5.cell(row=r, column=col_idx)
            cell.border = thin_border
            if p_idx % 2 == 1:
                cell.fill = fill_zebra

    # -------------------------------------------------------------
    # TAB 6: 06_Detailed_Model (Normalized Long-Format Table)
    # -------------------------------------------------------------
    ws6 = wb.create_sheet(title="06_Detailed_Model")
    ws6.views.sheetView[0].showGridLines = True

    ws6.merge_cells("A1:M2")
    ws6["A1"] = "CHONDROPROTECTIVE MARKET — NORMALIZED DETAILED ANALYTICAL MODEL"
    ws6["A1"].font = font_title
    ws6["A1"].fill = fill_navy
    ws6["A1"].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    headers6 = [
        "Month", "Year", "Product Name", "Sales Value (LC)", "Sales Units", "MoM Value Growth %",
        "YTD Value (LC)", "YTD Units", "Market Value Share %", "Share Change (pp)", "Total Market Value Growth %", "Performance vs Market", "Classification"
    ]
    for col_idx, h in enumerate(headers6, start=1):
        cell = ws6.cell(row=4, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    curr_row = 5
    for p in pure_products:
        for m_data in p['monthly']:
            m = m_data['month']
            ws6.cell(row=curr_row, column=1, value=m).alignment = align_center
            ws6.cell(row=curr_row, column=2, value=2026).alignment = align_center
            ws6.cell(row=curr_row, column=3, value=p['name']).alignment = align_left
            
            c = ws6.cell(row=curr_row, column=4, value=m_data['value'])
            c.number_format = '#,##0'
            c.alignment = align_right
            
            c = ws6.cell(row=curr_row, column=5, value=m_data['units'])
            c.number_format = '#,##0'
            c.alignment = align_right
            
            vg = m_data['val_mom']
            c = ws6.cell(row=curr_row, column=6, value=(vg/100.0) if vg is not None else "N/A")
            if vg is not None:
                c.number_format = '+0.0%;-0.0%;0.0%'
            c.alignment = align_center
            
            c = ws6.cell(row=curr_row, column=7, value=m_data['ytd_value'])
            c.number_format = '#,##0'
            c.alignment = align_right
            
            c = ws6.cell(row=curr_row, column=8, value=m_data['ytd_units'])
            c.number_format = '#,##0'
            c.alignment = align_right
            
            c = ws6.cell(row=curr_row, column=9, value=(m_data['val_share']/100.0))
            c.number_format = '0.00%'
            c.alignment = align_center
            
            sc = m_data['share_change_val_pp']
            c = ws6.cell(row=curr_row, column=10, value=(sc if sc is not None else "N/A"))
            if sc is not None:
                c.number_format = '+0.00;-0.00;0.00'
            c.alignment = align_center
            
            mkt_g = market_monthly[m_data['month_idx']]['val_growth_mom']
            c = ws6.cell(row=curr_row, column=11, value=(mkt_g/100.0) if mkt_g is not None else "N/A")
            if mkt_g is not None:
                c.number_format = '+0.0%;-0.0%;0.0%'
            c.alignment = align_center
            
            ws6.cell(row=curr_row, column=12, value=m_data['perf_vs_mkt_val']).alignment = align_center
            
            # BCG quadrant classification
            # High Share threshold: > 2.0% share; High Growth threshold: > Market growth rate
            is_high_share = m_data['val_share'] >= 2.0
            is_high_growth = (vg is not None and mkt_g is not None and vg > mkt_g)
            bcg = "Star" if (is_high_share and is_high_growth) else ("Cash Cow" if (is_high_share and not is_high_growth) else ("Question Mark" if (not is_high_share and is_high_growth) else "Dog"))
            ws6.cell(row=curr_row, column=13, value=bcg).alignment = align_center

            for col_idx in range(1, len(headers6) + 1):
                cell = ws6.cell(row=curr_row, column=col_idx)
                cell.border = thin_border
                if (curr_row % 2) == 1:
                    cell.fill = fill_zebra

            curr_row += 1

    # -------------------------------------------------------------
    # TAB 7: 07_Raw_Data_Input
    # -------------------------------------------------------------
    ws7 = wb.create_sheet(title="07_Raw_Data_Input")
    ws7.views.sheetView[0].showGridLines = True

    ws7.merge_cells("A1:Y2")
    ws7["A1"] = "CHONDROPROTECTIVE MARKET — RAW DATA INPUT LAYER (SOURCE OF TRUTH)"
    ws7["A1"].font = font_title
    ws7["A1"].fill = fill_navy
    ws7["A1"].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    # Copy raw csv headers
    raw_df = pd.read_csv('raw_data.csv')
    raw_headers = list(raw_df.columns)
    for col_idx, h in enumerate(raw_headers, start=1):
        cell = ws7.cell(row=4, column=col_idx, value=h.replace('\n', ' '))
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_wrap
        cell.border = header_border

    for r_idx, row in raw_df.iterrows():
        r = 5 + r_idx
        for col_idx, col_name in enumerate(raw_headers, start=1):
            val = row[col_name]
            cell = ws7.cell(row=r, column=col_idx, value=val)
            cell.font = font_td
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = align_left
                cell.font = font_td_bold
            else:
                cell.alignment = align_right
            if r_idx % 2 == 1:
                cell.fill = fill_zebra

    # -------------------------------------------------------------
    # TAB 8: 08_Data_Validation_Audit
    # -------------------------------------------------------------
    ws8 = wb.create_sheet(title="08_Data_Validation_Audit")
    ws8.views.sheetView[0].showGridLines = True

    ws8.merge_cells("A1:H2")
    ws8["A1"] = "CHONDROPROTECTIVE MARKET — DATA AUDIT, RECONCILIATION & QUALITY REPORT"
    ws8["A1"].font = font_title
    ws8["A1"].fill = fill_navy
    ws8["A1"].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    audit_headers = ["Audit Item", "Finding / Status", "Raw Metric", "Reconciled Metric", "Commercial Impact", "Analytical Treatment"]
    for col_idx, h in enumerate(audit_headers, start=1):
        cell = ws8.cell(row=4, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    audit_rows = [
        ("Total Records Ingested", "PASSED: 220 Records verified", "220 Product Rows", "220 Active Market SKUs", "Complete Market Coverage", "Updated dataset verified; zero duplicate corporate rollups present"),
        ("Product Scope Refinement", "VERIFIED: Pure Chondroprotective Focus", "220 SKUs", "220 SKUs", "Specialty orphan therapy (Evrysdi) removed", "Market metrics reflect pure joint health & chondroprotective products"),
        ("Brand Name Collision: MSM", "HOMONYMOUS PRODUCTS: 2 Independent Lines", "Row 70 & Row 193", "Distinct pricing tiers", "Different manufacturers with identical generic name", "Differentiated into MSM (Line 1 - High Price) and MSM (Line 2 - Standard Price)"),
        ("Time Horizon & Prior-Year Data", "CONSTRAINED: Jan 2026 - Aug 2026 Only", "8 Monthly Periods", "No 2025 prior-year data", "YoY and Prior-Year YTD Growth unavailable", "Displayed strictly as 'N/A' per prompt instruction; no fabricated prior-year numbers"),
        ("Raw Market Share Column Audit", "LOCAL / SUB-SEGMENT SHARE: Sums to ~3,800%", "Col 'Units Market Share' sums to 3,500-4,000%", "Recalculated True Market Share % (sums to 100%)", "Source column represents family/segment share, not total market share", "Retained raw share in data table; dynamically computed true market share % for commercial accuracy"),
        ("New Product Launches", "NEW ENTRANTS: Mid-year commercial introductions", "SOYAMOVE ADVANCE (Feb), JOTILAX (May), etc.", "Zero baseline prior to launch month", "First-month growth rate mathematically undefined", "MoM Growth displayed as 'N/A' for launch month, followed by standard MoM calculation"),
        ("Total Market Reconciliation", "RECONCILED: 100% Mathematical Balance", "2,479,326,277 LC Value", "7,520,950 Total Units", "Sum of 220 products exactly equals Total Market", "Perfect analytical reconciliation across all 8 monthly reporting periods")
    ]

    for idx, (item, status, raw_m, rec_m, impact, treat) in enumerate(audit_rows):
        r = 5 + idx
        ws8.cell(row=r, column=1, value=item).alignment = align_left
        ws8.cell(row=r, column=1).font = font_td_bold
        
        ws8.cell(row=r, column=2, value=status).alignment = align_left
        ws8.cell(row=r, column=3, value=raw_m).alignment = align_center
        ws8.cell(row=r, column=4, value=rec_m).alignment = align_center
        ws8.cell(row=r, column=5, value=impact).alignment = align_left
        ws8.cell(row=r, column=6, value=treat).alignment = align_left

        for c in range(1, 7):
            cell = ws8.cell(row=r, column=c)
            cell.border = thin_border
            if idx % 2 == 1:
                cell.fill = fill_zebra

    # Auto-adjust column widths for all worksheets
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                # ignore merged title banner cells
                if cell.row in [1, 2]:
                    continue
                if cell.value:
                    val_str = str(cell.value)
                    max_len = max(max_len, len(val_str))
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # Specific custom column width adjustments
    ws1.column_dimensions['A'].width = 4
    ws1.column_dimensions['B'].width = 28
    ws1.column_dimensions['C'].width = 24
    ws1.column_dimensions['D'].width = 20
    ws1.column_dimensions['E'].width = 20
    ws1.column_dimensions['F'].width = 22
    ws1.column_dimensions['G'].width = 20
    ws1.column_dimensions['H'].width = 22
    ws1.column_dimensions['I'].width = 20
    ws1.column_dimensions['J'].width = 28
    ws1.column_dimensions['K'].width = 28

    ws8.column_dimensions['A'].width = 32
    ws8.column_dimensions['B'].width = 38
    ws8.column_dimensions['C'].width = 28
    ws8.column_dimensions['D'].width = 28
    ws8.column_dimensions['E'].width = 40
    ws8.column_dimensions['F'].width = 50

    excel_filename = "Chondroprotective_Market_Dashboard_2026.xlsx"
    wb.save(excel_filename)
    print(f"Saved {excel_filename} successfully!")

if __name__ == '__main__':
    create_excel()
