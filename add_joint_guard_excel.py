import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import json

def add_joint_guard_tab(wb, data):
    months = data['months']
    market_monthly = data['market_monthly']
    products = data['products']

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
    gold_accent = "D97706"
    gold_light = "FEF3C7"

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
    font_gold = Font(name="Segoe UI", size=10, bold=True, color=gold_accent)

    fill_navy = PatternFill(start_color=navy_dark, end_color=navy_dark, fill_type="solid")
    fill_header = PatternFill(start_color=navy_header, end_color=navy_header, fill_type="solid")
    fill_sub = PatternFill(start_color=navy_sub, end_color=navy_sub, fill_type="solid")
    fill_accent = PatternFill(start_color=blue_accent, end_color=blue_accent, fill_type="solid")
    fill_light = PatternFill(start_color=blue_light, end_color=blue_light, fill_type="solid")
    fill_zebra = PatternFill(start_color=gray_bg, end_color=gray_bg, fill_type="solid")
    fill_gold = PatternFill(start_color=gold_light, end_color=gold_light, fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color=border_gray),
        right=Side(style='thin', color=border_gray),
        top=Side(style='thin', color=border_gray),
        bottom=Side(style='thin', color=border_gray)
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

    # Create sheet at index 0
    ws0 = wb.create_sheet(title="00_Joint_Guard_Focus", index=0)
    ws0.views.sheetView[0].showGridLines = True

    # Title Banner
    ws0.merge_cells("A1:L2")
    ws0["A1"] = "JOINT GUARD FRANCHISE — COMMERCIAL INTELLIGENCE & BRAND AUDIT"
    ws0["A1"].font = font_title
    ws0["A1"].fill = fill_navy
    ws0["A1"].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    ws0.merge_cells("A3:L3")
    ws0["A3"] = "Dedicated Franchise Deep-Dive: Joint Guard, Joint Guard Plus, and Joint Guard Ultra | Jan 2026 - Aug 2026 (YTD)"
    ws0["A3"].font = Font(name="Segoe UI", size=10, italic=True, color="64748B")
    ws0["A3"].alignment = Alignment(horizontal='left', vertical='center')

    # Extract products
    jg_ultra = next(p for p in products if p['name'] == 'JOINT GUARD UL.')
    jg_base = next(p for p in products if p['name'] == 'JOINT GUARD')
    jg_plus = next(p for p in products if p['name'] == 'JOINT GUARD PLUS')

    mkt_ytd_v = market_monthly[-1]['ytd_value']
    mkt_ytd_u = market_monthly[-1]['ytd_units']

    f_ytd_v = jg_ultra['total_value'] + jg_base['total_value'] + jg_plus['total_value']
    f_ytd_u = jg_ultra['total_units'] + jg_base['total_units'] + jg_plus['total_units']
    f_v_share = f_ytd_v / mkt_ytd_v
    f_u_share = f_ytd_u / mkt_ytd_u
    f_avg_price = f_ytd_v / f_ytd_u if f_ytd_u > 0 else 0

    # KPI 1: Franchise YTD Value
    ws0.merge_cells("B5:C5")
    ws0["B5"] = "FRANCHISE YTD VALUE"
    ws0["B5"].font = font_kpi_label
    ws0["B5"].alignment = align_center
    ws0.merge_cells("B6:C6")
    ws0["B6"] = f_ytd_v
    ws0["B6"].number_format = '#,##0 "LC"'
    ws0["B6"].font = font_kpi_num
    ws0["B6"].alignment = align_center
    ws0.merge_cells("B7:C7")
    ws0["B7"] = f"{f_v_share*100:.2f}% Market Value Share"
    ws0["B7"].font = Font(name="Segoe UI", size=8.5, bold=True, color="2563EB")
    ws0["B7"].alignment = align_center

    # KPI 2: Franchise YTD Units
    ws0.merge_cells("D5:E5")
    ws0["D5"] = "FRANCHISE YTD VOLUME"
    ws0["D5"].font = font_kpi_label
    ws0["D5"].alignment = align_center
    ws0.merge_cells("D6:E6")
    ws0["D6"] = f_ytd_u
    ws0["D6"].number_format = '#,##0 "Units"'
    ws0["D6"].font = font_kpi_num
    ws0["D6"].alignment = align_center
    ws0.merge_cells("D7:E7")
    ws0["D7"] = f"{f_u_share*100:.2f}% Market Volume Share"
    ws0["D7"].font = Font(name="Segoe UI", size=8.5, bold=True, color="2563EB")
    ws0["D7"].alignment = align_center

    # KPI 3: Blended Realized Price
    ws0.merge_cells("F5:G5")
    ws0["F5"] = "BLENDED REALIZED PRICE"
    ws0["F5"].font = font_kpi_label
    ws0["F5"].alignment = align_center
    ws0.merge_cells("F6:G6")
    ws0["F6"] = f_avg_price
    ws0["F6"].number_format = '#,##0.0 "LC"'
    ws0["F6"].font = font_kpi_num
    ws0["F6"].alignment = align_center
    ws0.merge_cells("F7:G7")
    ws0["F7"] = f"+31.7% vs Market Avg (329.7 LC)"
    ws0["F7"].font = Font(name="Segoe UI", size=8.5, bold=True, color="059669")
    ws0["F7"].alignment = align_center

    # KPI 4: Market Rank
    ws0.merge_cells("H5:I5")
    ws0["H5"] = "MARKET UMBRELLA RANK"
    ws0["H5"].font = font_kpi_label
    ws0["H5"].alignment = align_center
    ws0.merge_cells("H6:I6")
    ws0["H6"] = "#4 BRAND FAMILY"
    ws0["H6"].font = font_kpi_num
    ws0["H6"].alignment = align_center
    ws0.merge_cells("H7:I7")
    ws0["H7"] = "Behind Genuphil, Sulfax, Meralgo"
    ws0["H7"].font = Font(name="Segoe UI", size=8.5, color="64748B")
    ws0["H7"].alignment = align_center

    # KPI 5: Hero Product
    ws0.merge_cells("J5:K5")
    ws0["J5"] = "FLAGSHIP PRODUCT"
    ws0["J5"].font = font_kpi_label
    ws0["J5"].alignment = align_center
    ws0.merge_cells("J6:K6")
    ws0["J6"] = "JOINT GUARD ULTRA"
    ws0["J6"].font = Font(name="Segoe UI", size=14, bold=True, color="1E293B")
    ws0["J6"].alignment = align_center
    ws0.merge_cells("J7:K7")
    ws0["J7"] = "105.3M LC (70.3% of Portfolio)"
    ws0["J7"].font = Font(name="Segoe UI", size=8.5, bold=True, color="D97706")
    ws0["J7"].alignment = align_center

    for c_range in ["B5:C7", "D5:E7", "F5:G7", "H5:I7", "J5:K7"]:
        cols = c_range.split(":")
        col_start, row_start = cols[0][0], int(cols[0][1:])
        col_end, row_end = cols[1][0], int(cols[1][1:])
        # apply light fill
        for r in range(row_start, row_end+1):
            for c_char in [col_start, col_end]:
                c_idx = ord(c_char) - ord('A') + 1
                cell = ws0.cell(row=r, column=c_idx)
                cell.border = thin_border
                cell.fill = fill_light

    # Callout Banner
    ws0.merge_cells("B9:K10")
    ws0["B9"] = ("COMMERCIAL SUMMARY & STRATEGIC HIGHLIGHTS:\n"
                 "The Joint Guard Franchise represents our core corporate pillar in the Chondroprotective market, delivering 149.92M LC across 345,378 units YTD (6.05% market value share). "
                 "The franchise operates a clear 3-tier price architecture: Joint Guard Base (200 LC economy anchor), Joint Guard Plus (400 LC mid-tier), and Joint Guard Ultra (650 LC ultra-premium hero). "
                 "Ultra drives 70.3% of total revenue and ranks #9 in the entire market. Management priority: Smooth severe month-to-month wholesaler order volatility (sawtooth pattern) and scale Plus to bridge the mid-tier gap.")
    ws0["B9"].font = Font(name="Segoe UI", size=9, bold=False, color="1E293B")
    ws0["B9"].fill = fill_gold
    ws0["B9"].alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
    for r in [9, 10]:
        for c in range(2, 12):
            ws0.cell(row=r, column=c).border = thin_border
            ws0.cell(row=r, column=c).fill = fill_gold

    # -------------------------------------------------------------------------
    # Section 1: Portfolio SKU Architecture & Contribution
    # -------------------------------------------------------------------------
    ws0.cell(row=12, column=2, value="1. PORTFOLIO SKU ARCHITECTURE & YTD CONTRIBUTION (JAN - AUG 2026)").font = font_section
    
    sku_headers = ["SKU Name", "Commercial Tier", "YTD Value (LC)", "Value Share %", "Franchise Value Mix %", 
                   "YTD Units", "Unit Share %", "Franchise Volume Mix %", "Realized Price (LC)", 
                   "Market Rank (Val)", "Market Rank (Units)", "Strategic Role"]
    
    for c_idx, h in enumerate(sku_headers, start=2):
        cell = ws0.cell(row=13, column=c_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    skus_data = [
        ("Joint Guard Ultra", "Ultra-Premium Tier", jg_ultra['total_value'], jg_ultra['total_value']/mkt_ytd_v, jg_ultra['total_value']/f_ytd_v,
         jg_ultra['total_units'], jg_ultra['total_units']/mkt_ytd_u, jg_ultra['total_units']/f_ytd_u, jg_ultra['avg_price'],
         "#9 in Market", "#12 in Market", "Core Revenue Engine & Premium Hero"),
        ("Joint Guard (Base)", "Economy Tier", jg_base['total_value'], jg_base['total_value']/mkt_ytd_v, jg_base['total_value']/f_ytd_v,
         jg_base['total_units'], jg_base['total_units']/mkt_ytd_u, jg_base['total_units']/f_ytd_u, jg_base['avg_price'],
         "#22 in Market", "#13 in Market", "Volume Anchor & Mass Brand Recognition"),
        ("Joint Guard Plus", "Mid-Premium Tier", jg_plus['total_value'], jg_plus['total_value']/mkt_ytd_v, jg_plus['total_value']/f_ytd_v,
         jg_plus['total_units'], jg_plus['total_units']/mkt_ytd_u, jg_plus['total_units']/f_ytd_u, jg_plus['avg_price'],
         "#27 in Market", "#36 in Market", "Mid-Tier Bridge & Expansion Potential"),
        ("TOTAL JOINT GUARD FRANCHISE", "Full Portfolio Umbrella", f_ytd_v, f_v_share, 1.00,
         f_ytd_u, f_u_share, 1.00, f_avg_price,
         "#4 Brand Family", "#4 Brand Family", "Flagship Commercial Portfolio")
    ]

    for idx, row in enumerate(skus_data):
        r = 14 + idx
        is_total = (idx == len(skus_data)-1)
        curr_font = font_td_bold if is_total else font_td
        curr_fill = fill_accent if is_total else (fill_zebra if idx % 2 == 1 else PatternFill(fill_type=None))
        
        ws0.cell(row=r, column=2, value=row[0]).alignment = align_left
        ws0.cell(row=r, column=3, value=row[1]).alignment = align_center
        
        c_val = ws0.cell(row=r, column=4, value=row[2])
        c_val.number_format = '#,##0 "LC"'
        c_val.alignment = align_right
        
        c_vsh = ws0.cell(row=r, column=5, value=row[3])
        c_vsh.number_format = '0.00%'
        c_vsh.alignment = align_center
        
        c_vmix = ws0.cell(row=r, column=6, value=row[4])
        c_vmix.number_format = '0.0%'
        c_vmix.alignment = align_center
        
        c_u = ws0.cell(row=r, column=7, value=row[5])
        c_u.number_format = '#,##0'
        c_u.alignment = align_right
        
        c_ush = ws0.cell(row=r, column=8, value=row[6])
        c_ush.number_format = '0.00%'
        c_ush.alignment = align_center
        
        c_umix = ws0.cell(row=r, column=9, value=row[7])
        c_umix.number_format = '0.0%'
        c_umix.alignment = align_center
        
        c_pr = ws0.cell(row=r, column=10, value=row[8])
        c_pr.number_format = '#,##0.0'
        c_pr.alignment = align_right
        
        ws0.cell(row=r, column=11, value=row[9]).alignment = align_center
        ws0.cell(row=r, column=12, value=row[10]).alignment = align_center
        ws0.cell(row=r, column=13, value=row[11]).alignment = align_left

        for c in range(2, 14):
            cell = ws0.cell(row=r, column=c)
            cell.border = thin_border
            if is_total:
                cell.fill = fill_sub
                cell.font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
            elif idx % 2 == 1:
                cell.fill = fill_zebra

    # -------------------------------------------------------------------------
    # Section 2: Month-by-Month Value Progression & MoM Dynamics
    # -------------------------------------------------------------------------
    ws0.cell(row=20, column=2, value="2. MONTHLY VALUE PROGRESSION & MOM GROWTH DYNAMICS (JAN - AUG 2026)").font = font_section

    m_headers = ["Month", "Total Market (LC)", "Market MoM", "JG Ultra (LC)", "Ultra MoM", "JG Base (LC)", "Base MoM", 
                 "JG Plus (LC)", "Plus MoM", "Total Franchise (LC)", "Franchise MoM", "Franchise Share %"]
    for c_idx, h in enumerate(m_headers, start=2):
        cell = ws0.cell(row=21, column=c_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    prev_f_val = None
    for i, m in enumerate(months):
        r = 22 + i
        mkt_v = market_monthly[i]['value']
        mkt_mom = market_monthly[i]['val_growth_mom']
        
        u_v = jg_ultra['monthly'][i]['value']
        u_mom = jg_ultra['monthly'][i]['val_mom']
        
        b_v = jg_base['monthly'][i]['value']
        b_mom = jg_base['monthly'][i]['val_mom']
        
        p_v = jg_plus['monthly'][i]['value']
        p_mom = jg_plus['monthly'][i]['val_mom']
        
        f_v = u_v + b_v + p_v
        f_mom = ((f_v - prev_f_val) / prev_f_val * 100) if prev_f_val is not None else None
        prev_f_val = f_v
        f_sh = f_v / mkt_v if mkt_v > 0 else 0

        ws0.cell(row=r, column=2, value=m).alignment = align_center
        
        c = ws0.cell(row=r, column=3, value=mkt_v)
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws0.cell(row=r, column=4, value=(mkt_mom/100.0) if mkt_mom is not None else "N/A")
        if mkt_mom is not None:
            c.number_format = '+0.0%;-0.0%;0.0%'
            c.font = font_pos if mkt_mom >= 0 else font_neg
        c.alignment = align_center
        
        c = ws0.cell(row=r, column=5, value=u_v)
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws0.cell(row=r, column=6, value=(u_mom/100.0) if u_mom is not None else "N/A")
        if u_mom is not None:
            c.number_format = '+0.0%;-0.0%;0.0%'
            c.font = font_pos if u_mom >= 0 else font_neg
        c.alignment = align_center

        c = ws0.cell(row=r, column=7, value=b_v)
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws0.cell(row=r, column=8, value=(b_mom/100.0) if b_mom is not None else "N/A")
        if b_mom is not None:
            c.number_format = '+0.0%;-0.0%;0.0%'
            c.font = font_pos if b_mom >= 0 else font_neg
        c.alignment = align_center

        c = ws0.cell(row=r, column=9, value=p_v)
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws0.cell(row=r, column=10, value=(p_mom/100.0) if p_mom is not None else "N/A")
        if p_mom is not None:
            c.number_format = '+0.0%;-0.0%;0.0%'
            c.font = font_pos if p_mom >= 0 else font_neg
        c.alignment = align_center

        c = ws0.cell(row=r, column=11, value=f_v)
        c.number_format = '#,##0'
        c.alignment = align_right
        c.font = font_td_bold
        
        c = ws0.cell(row=r, column=12, value=(f_mom/100.0) if f_mom is not None else "N/A")
        if f_mom is not None:
            c.number_format = '+0.0%;-0.0%;0.0%'
            c.font = font_pos if f_mom >= 0 else font_neg
        c.alignment = align_center

        c = ws0.cell(row=r, column=13, value=f_sh)
        c.number_format = '0.00%'
        c.alignment = align_center
        c.font = font_td_bold

        for col_idx in range(2, 14):
            cell = ws0.cell(row=r, column=col_idx)
            cell.border = thin_border
            if i % 2 == 1:
                cell.fill = fill_zebra

    # -------------------------------------------------------------------------
    # Section 3: Monthly Unit Sales & Realized Price Architecture
    # -------------------------------------------------------------------------
    ws0.cell(row=32, column=2, value="3. MONTHLY VOLUME & PRICING ARCHITECTURE (JAN - AUG 2026)").font = font_section

    u_headers = ["Month", "Market Units", "JG Ultra Units", "Ultra Price (LC)", "JG Base Units", "Base Price (LC)", 
                 "JG Plus Units", "Plus Price (LC)", "Total Franchise Units", "Franchise Blended Price", "Franchise Unit Share %"]
    for c_idx, h in enumerate(u_headers, start=2):
        cell = ws0.cell(row=33, column=c_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    for i, m in enumerate(months):
        r = 34 + i
        mkt_u = market_monthly[i]['units']
        
        u_u = jg_ultra['monthly'][i]['units']
        u_p = jg_ultra['monthly'][i]['avg_price']
        
        b_u = jg_base['monthly'][i]['units']
        b_p = jg_base['monthly'][i]['avg_price']
        
        p_u = jg_plus['monthly'][i]['units']
        p_p = jg_plus['monthly'][i]['avg_price']
        
        f_u = u_u + b_u + p_u
        f_v = jg_ultra['monthly'][i]['value'] + jg_base['monthly'][i]['value'] + jg_plus['monthly'][i]['value']
        f_bp = f_v / f_u if f_u > 0 else 0
        f_ush = f_u / mkt_u if mkt_u > 0 else 0

        ws0.cell(row=r, column=2, value=m).alignment = align_center
        
        c = ws0.cell(row=r, column=3, value=mkt_u)
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws0.cell(row=r, column=4, value=u_u)
        c.number_format = '#,##0'
        c.alignment = align_right

        c = ws0.cell(row=r, column=5, value=u_p)
        c.number_format = '#,##0.0'
        c.alignment = align_right
        if i >= 3: # price hike to 650
            c.font = font_gold

        c = ws0.cell(row=r, column=6, value=b_u)
        c.number_format = '#,##0'
        c.alignment = align_right

        c = ws0.cell(row=r, column=7, value=b_p)
        c.number_format = '#,##0.0'
        c.alignment = align_right

        c = ws0.cell(row=r, column=8, value=p_u)
        c.number_format = '#,##0'
        c.alignment = align_right

        c = ws0.cell(row=r, column=9, value=p_p)
        c.number_format = '#,##0.0'
        c.alignment = align_right

        c = ws0.cell(row=r, column=10, value=f_u)
        c.number_format = '#,##0'
        c.alignment = align_right
        c.font = font_td_bold

        c = ws0.cell(row=r, column=11, value=f_bp)
        c.number_format = '#,##0.0'
        c.alignment = align_right
        c.font = font_td_bold

        c = ws0.cell(row=r, column=12, value=f_ush)
        c.number_format = '0.00%'
        c.alignment = align_center
        c.font = font_td_bold

        for col_idx in range(2, 13):
            cell = ws0.cell(row=r, column=col_idx)
            cell.border = thin_border
            if i % 2 == 1:
                cell.fill = fill_zebra

    # -------------------------------------------------------------------------
    # Section 4: Head-to-Head Competitive Benchmarking
    # -------------------------------------------------------------------------
    ws0.cell(row=44, column=2, value="4. HEAD-TO-HEAD COMPETITIVE BENCHMARKING").font = font_section

    bench_headers = ["Brand / Competitor", "Manufacturer / Segment", "YTD Value (LC)", "Value Share %", 
                     "YTD Units", "Avg Price (LC)", "Aug MoM Value %", "Head-to-Head Comparison vs Joint Guard"]
    for c_idx, h in enumerate(bench_headers, start=2):
        cell = ws0.cell(row=45, column=c_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    benchmarks = [
        ("⭐ JOINT GUARD ULTRA", "Our Hero Brand / Ultra-Premium", jg_ultra['total_value'], jg_ultra['total_value']/mkt_ytd_v, jg_ultra['total_units'], jg_ultra['avg_price'], -0.227, "Benchmark Leader in Ultra-Premium Segment (Rank #9)"),
        ("MOVENTOR ADVANCE", "Eva Pharma / Premium Line", 100016830, 100016830/mkt_ytd_v, 188711, 530.0, 0.148, "JG Ultra BEATS Moventor Advance (+5.3M LC lead, +104 LC higher price)"),
        ("PIASCLEDINE", "Expanscience / ASU Premium", 130435162, 130435162/mkt_ytd_v, 257777, 506.0, 0.094, "Direct target: Piascledine holds #7 with higher unit volume"),
        ("GENUPHIL ADVANCE", "Eva Pharma / Premium Glucosamine", 175203360, 175203360/mkt_ytd_v, 369302, 474.4, 0.102, "Key benchmark: Genuphil Advance captures 7.07% market share"),
        ("⭐ JOINT GUARD (BASE)", "Our Economy Anchor / Mass Tier", jg_base['total_value'], jg_base['total_value']/mkt_ytd_v, jg_base['total_units'], jg_base['avg_price'], 0.937, "Mass volume pillar (Rank #13 in Units, 135.8k units sold)"),
        ("JOINT PLUS", "Direct Rival / Glucosamine Combo", 64888290, 64888290/mkt_ytd_v, 179880, 360.7, 0.031, "Joint Plus priced 80% higher than JG Base (361 LC vs 200 LC)"),
        ("⭐ JOINT GUARD PLUS", "Our Mid-Tier Bridge", jg_plus['total_value'], jg_plus['total_value']/mkt_ytd_v, jg_plus['total_units'], jg_plus['avg_price'], -0.416, "Priced at 400 LC to bridge the gap between 200 LC and 650 LC"),
        ("MERALGO", "Ortho Competitor / High-End", 149457415, 149457415/mkt_ytd_v, 302602, 493.9, 0.027, "High-volume competitor in 490 LC range with 6.03% share")
    ]

    for idx, row in enumerate(benchmarks):
        r = 46 + idx
        is_our = "⭐" in row[0]
        
        c1 = ws0.cell(row=r, column=2, value=row[0])
        c1.alignment = align_left
        c1.font = font_td_bold if is_our else font_td
        
        ws0.cell(row=r, column=3, value=row[1]).alignment = align_left
        
        c = ws0.cell(row=r, column=4, value=row[2])
        c.number_format = '#,##0'
        c.alignment = align_right
        c.font = font_td_bold if is_our else font_td
        
        c = ws0.cell(row=r, column=5, value=row[3])
        c.number_format = '0.00%'
        c.alignment = align_center
        
        c = ws0.cell(row=r, column=6, value=row[7-1]) # units
        c.number_format = '#,##0'
        c.alignment = align_right
        
        c = ws0.cell(row=r, column=7, value=row[5]) # price
        c.number_format = '#,##0.0'
        c.alignment = align_right
        
        c = ws0.cell(row=r, column=8, value=row[6]) # mom
        c.number_format = '+0.0%;-0.0%;0.0%'
        c.alignment = align_center
        c.font = font_pos if row[6] >= 0 else font_neg
        
        ws0.cell(row=r, column=9, value=row[7]).alignment = align_left

        for col_idx in range(2, 10):
            cell = ws0.cell(row=r, column=col_idx)
            cell.border = thin_border
            if is_our:
                cell.fill = fill_light
            elif idx % 2 == 1:
                cell.fill = fill_zebra

    # -------------------------------------------------------------------------
    # Section 5: Strategic Action Plan for Commercial Management
    # -------------------------------------------------------------------------
    ws0.cell(row=56, column=2, value="5. STRATEGIC COMMERCIAL ACTION PLAN FOR BRAND MANAGERS & SALES LEADERSHIP").font = font_section

    action_headers = ["Strategic Pillar", "Diagnostic Finding", "Root Cause & Commercial Risk", "Actionable Recommendation", "Target Commercial KPI"]
    for c_idx, h in enumerate(action_headers, start=2):
        cell = ws0.cell(row=57, column=c_idx, value=h)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = header_border

    actions = [
        ("1. Wholesaler Order Smoothing", 
         "Extreme monthly volatility: Ultra swung +88% (May) to -52% (Jun); Base swung +653% (Jun) to -81% (Jul).",
         "Wholesaler batch quota-loading, distributor discount threshold hoarding, and periodic factory delivery lag.",
         "Implement rolling quarterly supply agreements with key distributors; institute pharmacy sell-out incentives rather than wholesale sell-in bonuses.",
         "Reduce MoM sales variance to < 20% and avoid artificial destocking slumps."),
        ("2. Margin & Pricing Power", 
         "Ultra successfully increased price from 600 LC to 650 LC in April (+8.3%) with zero share attrition (peaked at 22.1M in May).",
         "Doctor brand loyalty and patient compliance remain inelastic in the ultra-premium segment.",
         "Protect the 650 LC price point; defend clinical differentiation against Moventor Advance (530 LC); do not offer dilutive wholesale discounts.",
         "Maintain realized price >= 645 LC and preserve 70%+ gross margin profile."),
        ("3. Repositioning Joint Guard Plus", 
         "Plus currently represents only 11.6% of franchise value (17.4M LC) and experienced high volatility (1.2M - 4.3M LC).",
         "Under-detailed in clinics; doctor perception blurred between Base and Ultra; lacks clear patient profile.",
         "Position Plus (400 LC) specifically for active lifestyle / mild-to-moderate knee OA patients who cannot afford 650 LC Ultra.",
         "Double Plus sales contribution to 20% of franchise revenue (target: 35M LC annualized)."),
        ("4. Synergistic Detailing Packaging", 
         "Base sales exploded in June (45.5k units) when reps focused on volume, showing strong field pull-through.",
         "Reps alternate detailing effort between SKUs depending on monthly commercial bonuses rather than co-detailing.",
         "Structure medical rep incentive plans around 'Total Joint Guard Franchise' target rather than single-product quotas.",
         "Elevate total franchise market share from 6.05% to 7.50% (Surpass #3 Meralgo).")
    ]

    for idx, (pil, diag, root, rec, kpi) in enumerate(actions):
        r = 58 + idx
        ws0.cell(row=r, column=2, value=pil).alignment = align_left
        ws0.cell(row=r, column=2).font = font_td_bold
        
        ws0.cell(row=r, column=3, value=diag).alignment = align_left
        ws0.cell(row=r, column=4, value=root).alignment = align_left
        ws0.cell(row=r, column=5, value=rec).alignment = align_left
        ws0.cell(row=r, column=6, value=kpi).alignment = align_left
        
        for col_idx in range(2, 7):
            cell = ws0.cell(row=r, column=col_idx)
            cell.border = thin_border
            if idx % 2 == 1:
                cell.fill = fill_zebra

    # Column widths
    ws0.column_dimensions['A'].width = 4
    ws0.column_dimensions['B'].width = 28
    ws0.column_dimensions['C'].width = 24
    ws0.column_dimensions['D'].width = 22
    ws0.column_dimensions['E'].width = 20
    ws0.column_dimensions['F'].width = 22
    ws0.column_dimensions['G'].width = 22
    ws0.column_dimensions['H'].width = 22
    ws0.column_dimensions['I'].width = 24
    ws0.column_dimensions['J'].width = 24
    ws0.column_dimensions['K'].width = 24
    ws0.column_dimensions['L'].width = 22
    ws0.column_dimensions['M'].width = 30
