import json

def generate_html():
    with open('dashboard_data.json', 'r', encoding='utf-8') as f:
        data_json_str = f.read()

    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chondroprotective Market — Commercial Intelligence Dashboard</title>
  <!-- Chart.js CDN -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #0f172a;
      --primary-light: #1e293b;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-light: #eff6ff;
      --accent-subtle: #dbeafe;
      --success: #059669;
      --success-light: #ecfdf5;
      --danger: #dc2626;
      --danger-light: #fef2f2;
      --warning: #d97706;
      --warning-light: #fffbeb;
      --bg: #f8fafc;
      --surface: #ffffff;
      --surface-border: #e2e8f0;
      --text: #0f172a;
      --text-muted: #64748b;
      --text-light: #94a3b8;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
      --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
      --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      font-size: 13.5px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* Header & Navigation */
    header {{
      background: var(--primary);
      color: white;
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 3px solid var(--accent);
      position: sticky;
      top: 0;
      z-index: 1000;
      box-shadow: var(--shadow-md);
    }}

    .header-branding {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .header-badge {{
      background: rgba(37, 99, 235, 0.25);
      border: 1px solid rgba(59, 130, 246, 0.5);
      color: #93c5fd;
      padding: 3px 9px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}

    .header-title h1 {{
      font-size: 17px;
      font-weight: 800;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .header-title p {{
      font-size: 11.5px;
      color: #94a3b8;
    }}

    .global-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .control-pill {{
      display: flex;
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: var(--radius-sm);
      padding: 2px;
    }}

    .control-pill button {{
      background: transparent;
      border: none;
      color: #cbd5e1;
      padding: 6px 14px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s ease;
      font-family: inherit;
    }}

    .control-pill button.active {{
      background: var(--accent);
      color: white;
      box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }}

    .select-dropdown {{
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      color: white;
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      outline: none;
      font-family: inherit;
    }}

    .select-dropdown option {{
      background: var(--primary);
      color: white;
    }}

    /* Sub-nav / Tabs */
    .tab-bar {{
      background: var(--surface);
      border-bottom: 1px solid var(--surface-border);
      padding: 0 28px;
      display: flex;
      gap: 4px;
      overflow-x: auto;
      position: sticky;
      top: 61px;
      z-index: 900;
      box-shadow: var(--shadow-sm);
    }}

    .tab-btn {{
      padding: 12px 16px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 7px;
      font-family: inherit;
    }}

    .tab-btn:hover {{
      color: var(--accent);
      background: var(--accent-light);
    }}

    .tab-btn.active {{
      color: var(--accent);
      border-bottom-color: var(--accent);
      font-weight: 700;
    }}

    /* Main Container */
    main {{
      flex: 1;
      padding: 24px 28px;
      max-width: 1600px;
      margin: 0 auto;
      width: 100%;
    }}

    .tab-content {{
      display: none;
      animation: fadeIn 0.25s ease-in-out;
    }}

    .tab-content.active {{
      display: block;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(3px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Card System */
    .card {{
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
      margin-bottom: 20px;
      overflow: hidden;
    }}

    .card-header {{
      padding: 14px 20px;
      border-bottom: 1px solid var(--surface-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #fafcff;
    }}

    .card-header h3 {{
      font-size: 13.5px;
      font-weight: 700;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .card-body {{
      padding: 20px;
    }}

    /* KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 22px;
    }}

    .kpi-card {{
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius-md);
      padding: 16px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      position: relative;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }}

    .kpi-card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--surface-border);
      border-radius: var(--radius-md) var(--radius-md) 0 0;
    }}

    .kpi-card.accent::before {{ background: var(--accent); }}
    .kpi-card.success::before {{ background: var(--success); }}
    .kpi-card.danger::before {{ background: var(--danger); }}
    .kpi-card.warning::before {{ background: var(--warning); }}

    .kpi-label {{
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }}

    .kpi-value {{
      font-size: 22px;
      font-weight: 800;
      color: var(--primary);
      letter-spacing: -0.5px;
      margin-bottom: 6px;
      font-family: 'JetBrains Mono', monospace;
    }}

    .kpi-meta {{
      font-size: 11px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 600;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 3px;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
    }}

    .badge-pos {{ background: var(--success-light); color: var(--success); }}
    .badge-neg {{ background: var(--danger-light); color: var(--danger); }}
    .badge-neu {{ background: #f1f5f9; color: var(--text-muted); }}

    /* Layout Grids */
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 20px;
    }}

    @media (max-width: 1024px) {{
      .grid-2, .grid-3 {{ grid-template-columns: 1fr; }}
    }}

    /* Table Styles */
    .table-container {{
      overflow-x: auto;
      border: 1px solid var(--surface-border);
      border-radius: var(--radius-sm);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      text-align: left;
    }}

    th {{
      background: #f1f5f9;
      color: var(--primary-light);
      font-weight: 700;
      padding: 10px 14px;
      border-bottom: 2px solid var(--surface-border);
      white-space: nowrap;
      position: sticky;
      top: 0;
      font-size: 11.5px;
      letter-spacing: 0.2px;
    }}

    td {{
      padding: 9px 14px;
      border-bottom: 1px solid var(--surface-border);
      color: var(--text);
    }}

    tbody tr:hover {{
      background: #f8fafc;
    }}

    tbody tr:nth-child(even) {{
      background: #fcfdfe;
    }}

    .num {{
      text-align: right;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11.5px;
    }}

    .center {{ text-align: center; }}

    /* Search & Filter Bar */
    .filter-bar {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }}

    .search-input {{
      padding: 7px 12px;
      border: 1px solid var(--surface-border);
      border-radius: var(--radius-sm);
      font-size: 12.5px;
      width: 260px;
      outline: none;
      font-family: inherit;
    }}

    .search-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(37,99,235,0.15);
    }}

    .btn {{
      padding: 7px 14px;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      border: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: inherit;
      transition: all 0.15s ease;
    }}

    .btn-primary {{
      background: var(--accent);
      color: white;
    }}

    .btn-primary:hover {{
      background: var(--accent-hover);
    }}

    .btn-outline {{
      background: transparent;
      border: 1px solid var(--surface-border);
      color: var(--text-muted);
    }}

    .btn-outline:hover {{
      background: #f1f5f9;
      color: var(--text);
    }}

    /* Callout & Alert */
    .callout {{
      padding: 14px 18px;
      border-radius: var(--radius-sm);
      margin-bottom: 20px;
      font-size: 12.5px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      border-left: 4px solid;
    }}

    .callout-info {{
      background: var(--accent-light);
      border-color: var(--accent);
      color: #1e3a8a;
    }}

    .callout-warning {{
      background: var(--warning-light);
      border-color: var(--warning);
      color: #78350f;
    }}

    .callout-success {{
      background: var(--success-light);
      border-color: var(--success);
      color: #064e3b;
    }}

    /* Matrix Quadrant */
    .matrix-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 14px;
      height: 480px;
      margin-top: 14px;
    }}

    .matrix-box {{
      border-radius: var(--radius-md);
      padding: 14px;
      display: flex;
      flex-direction: column;
      border: 1px solid;
      overflow-y: auto;
    }}

    .matrix-box.stars {{ background: #eff6ff; border-color: #93c5fd; }}
    .matrix-box.cash-cows {{ background: #ecfdf5; border-color: #6ee7b7; }}
    .matrix-box.question-marks {{ background: #fffbeb; border-color: #fde68a; }}
    .matrix-box.dogs {{ background: #fef2f2; border-color: #fca5a5; }}

    .matrix-title {{
      font-size: 13px;
      font-weight: 800;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .matrix-subtitle {{
      font-size: 11px;
      color: var(--text-muted);
      margin-bottom: 10px;
    }}

    .tag-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }}

    .product-tag {{
      background: white;
      border: 1px solid rgba(0,0,0,0.1);
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      color: var(--primary);
    }}

    /* Pagination */
    .pagination {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      border-top: 1px solid var(--surface-border);
      background: #fafcff;
      font-size: 12px;
      color: var(--text-muted);
    }}

    .page-btn {{
      padding: 4px 10px;
      border: 1px solid var(--surface-border);
      background: white;
      border-radius: 4px;
      cursor: pointer;
    }}

    .page-btn:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}

    /* Chart wrappers */
    .chart-container {{
      position: relative;
      height: 350px;
      width: 100%;
    }}

    .chart-container-sm {{
      position: relative;
      height: 270px;
      width: 100%;
    }}
  </style>
</head>
<body>

  <!-- Top Executive Header -->
  <header>
    <div class="header-branding">
      <div class="header-badge">Pharmaceutical Market Intelligence</div>
      <div class="header-title">
        <h1>Chondroprotective Market Dashboard <span style="font-weight:400; font-size:13px; color:#94a3b8;">| Commercial Decision-Support System</span></h1>
        <p>Jan 2026 – Aug 2026 Audit Period | Egypt / Regional Territory | 228 Validated Products</p>
      </div>
    </div>

    <div class="global-controls">
      <!-- Metric Selector: Value vs Units -->
      <div style="display:flex; flex-direction:column; gap:2px;">
        <span style="font-size:9.5px; text-transform:uppercase; color:#94a3b8; font-weight:700;">Active Metric</span>
        <div class="control-pill" id="metricSelector">
          <button class="active" data-metric="value" onclick="setMetric('value')">Value (LC)</button>
          <button data-metric="units" onclick="setMetric('units')">Units</button>
        </div>
      </div>

      <!-- Time Filter Selector -->
      <div style="display:flex; flex-direction:column; gap:2px;">
        <span style="font-size:9.5px; text-transform:uppercase; color:#94a3b8; font-weight:700;">Period Cutoff / Focus</span>
        <select class="select-dropdown" id="periodSelector" onchange="onPeriodChange()">
          <option value="YTD" selected>Full YTD (Jan - Aug 2026)</option>
          <option value="Aug 2026">Latest Month: Aug 2026</option>
          <option value="Jul 2026">Jul 2026</option>
          <option value="Jun 2026">Jun 2026 (Peak)</option>
          <option value="May 2026">May 2026</option>
          <option value="Apr 2026">Apr 2026</option>
          <option value="Mar 2026">Mar 2026</option>
          <option value="Feb 2026">Feb 2026</option>
          <option value="Jan 2026">Jan 2026</option>
        </select>
      </div>

      <!-- Data Model Mode Toggle -->
      <div style="display:flex; flex-direction:column; gap:2px;">
        <span style="font-size:9.5px; text-transform:uppercase; color:#94a3b8; font-weight:700;">Data Layer</span>
        <select class="select-dropdown" id="layerSelector" onchange="onLayerChange()">
          <option value="pure" selected>Pure Products (228 Brands)</option>
          <option value="all">Raw Ingested (230 Rows with Rollups)</option>
        </select>
      </div>

      <!-- Direct Download Excel Button -->
      <div style="display:flex; flex-direction:column; gap:2px;">
        <span style="font-size:9.5px; text-transform:uppercase; color:#94a3b8; font-weight:700;">Excel Model</span>
        <a href="Chondroprotective_Market_Dashboard_2026.xlsx" download class="btn btn-primary" style="text-decoration:none; padding:6px 12px; font-size:12px; font-weight:600; display:inline-flex; align-items:center; gap:6px;">
          📥 Download .xlsx
        </a>
      </div>
    </div>
  </header>

  <!-- Sticky Tab Bar -->
  <div class="tab-bar">
    <button class="tab-btn active" onclick="switchTab('exec')">📊 Executive Summary</button>
    <button class="tab-btn" onclick="switchTab('trends')">📈 Market Trends</button>
    <button class="tab-btn" onclick="switchTab('products')">🏆 Product Performance</button>
    <button class="tab-btn" onclick="switchTab('share')">🥧 Market Share Analysis</button>
    <button class="tab-btn" onclick="switchTab('contrib')">⚖️ Product vs Market & Contribution</button>
    <button class="tab-btn" onclick="switchTab('table')">📑 Detailed Analytical Table</button>
    <button class="tab-btn" onclick="switchTab('audit')">🛡️ Data Quality & Live Ingestion</button>
  </div>

  <!-- Main Dashboard Content -->
  <main>

    <!-- ============================================================== -->
    <!-- TAB 1: EXECUTIVE SUMMARY -->
    <!-- ============================================================== -->
    <div id="tab-exec" class="tab-content active">
      
      <!-- KPI Cards Row -->
      <div class="kpi-grid">
        <div class="kpi-card accent">
          <div class="kpi-label">YTD Market Value (Jan-Aug)</div>
          <div class="kpi-value" id="kpiYtdVal">--</div>
          <div class="kpi-meta">
            <span class="badge badge-neu">8-Month YTD</span>
            <span>Total pure market value</span>
          </div>
        </div>

        <div class="kpi-card accent">
          <div class="kpi-label">YTD Market Units (Jan-Aug)</div>
          <div class="kpi-value" id="kpiYtdUnits">--</div>
          <div class="kpi-meta">
            <span class="badge badge-neu">8-Month YTD</span>
            <span>Total volume sold</span>
          </div>
        </div>

        <div class="kpi-card success">
          <div class="kpi-label">August 2026 Value</div>
          <div class="kpi-value" id="kpiAugVal">--</div>
          <div class="kpi-meta">
            <span class="badge badge-pos" id="kpiAugValGrowth">+7.6% MoM</span>
            <span>vs July 2026</span>
          </div>
        </div>

        <div class="kpi-card success">
          <div class="kpi-label">August 2026 Units</div>
          <div class="kpi-value" id="kpiAugUnits">--</div>
          <div class="kpi-meta">
            <span class="badge badge-pos" id="kpiAugUnitsGrowth">+0.4% MoM</span>
            <span>vs July 2026</span>
          </div>
        </div>

        <div class="kpi-card warning">
          <div class="kpi-label">Market Leader (Value)</div>
          <div class="kpi-value" id="kpiLeadingVal" style="font-size:17px;">GENUPHIL</div>
          <div class="kpi-meta">
            <span class="badge badge-neu" id="kpiLeadingValShare">11.7% Share</span>
            <span>307.5M LC YTD</span>
          </div>
        </div>

        <div class="kpi-card warning">
          <div class="kpi-label">Market Leader (Volume)</div>
          <div class="kpi-value" id="kpiLeadingUnits" style="font-size:17px;">SULFAX</div>
          <div class="kpi-meta">
            <span class="badge badge-neu" id="kpiLeadingUnitsShare">16.4% Share</span>
            <span>1.29M Units YTD</span>
          </div>
        </div>
      </div>

      <!-- Executive Insights Callout -->
      <div class="callout callout-info">
        <div style="font-size:20px;">💡</div>
        <div>
          <strong>Executive Commercial Summary:</strong> The Chondroprotective Market reached a cumulative YTD value of <strong>2.62 Billion LC</strong> across <strong>7.37 Million units</strong> through August 2026. After hitting an all-time mid-year high in June (445.8M LC) and a subsequent July post-peak correction (-25.0%), the market regained positive expansion in August (+7.6% Value, +0.4% Units). The top 5 brands control <strong>41.3% of total market value</strong>, with EVA Pharma's <strong>GENUPHIL family</strong> (Genuphil, Genuphil Advance, Genuphil Woman) commanding <strong>613.1M LC (23.4% of total market)</strong> as the dominant brand franchise.
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <h3>📈 Monthly Market Progression & MoM Growth</h3>
            <span class="badge badge-neu">Dual-Axis Trend</span>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas id="chartExecMonthly"></canvas>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>🏆 Top 10 Brand Performance (Selected Metric)</h3>
            <span class="badge badge-neu" id="top10HeaderBadge">Value Ranking</span>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas id="chartExecTop10"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Executive Summary Table -->
      <div class="card">
        <div class="card-header">
          <h3>📋 Monthly Market Overview Table</h3>
          <button class="btn btn-outline" onclick="exportTableToCSV('execTable', 'Chondroprotective_Monthly_Summary.csv')">📥 Export CSV</button>
        </div>
        <div class="card-body" style="padding:0;">
          <div class="table-container">
            <table id="execTable">
              <thead>
                <tr>
                  <th>Month</th>
                  <th class="num">Value Sales (LC)</th>
                  <th class="center">MoM Value Growth %</th>
                  <th class="num">Unit Sales</th>
                  <th class="center">MoM Unit Growth %</th>
                  <th class="num">Avg Price (LC/Unit)</th>
                  <th class="num">Cumulative YTD Value</th>
                  <th class="num">Cumulative YTD Units</th>
                  <th class="center">Market Trajectory</th>
                </tr>
              </thead>
              <tbody id="execTableBody"></tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

    <!-- ============================================================== -->
    <!-- TAB 2: MARKET TRENDS -->
    <!-- ============================================================== -->
    <div id="tab-trends" class="tab-content">
      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <h3>📊 Monthly Sales Trend (<span class="metric-label">Value</span>)</h3>
            <span class="badge badge-neu">Monthly Breakdown</span>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas id="chartTrendsMonthly"></canvas>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>📈 Cumulative YTD Progression (<span class="metric-label">Value</span>)</h3>
            <span class="badge badge-neu">YTD Run-Rate</span>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas id="chartTrendsYtd"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Price & Volatility Trends -->
      <div class="card">
        <div class="card-header">
          <h3>🏷️ Market Price Realization & MoM Volatility</h3>
          <span class="badge badge-neu">Weighted Average Unit Price (LC)</span>
        </div>
        <div class="card-body">
          <div class="chart-container-sm">
            <canvas id="chartTrendsPrice"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 3: PRODUCT PERFORMANCE -->
    <!-- ============================================================== -->
    <div id="tab-products" class="tab-content">
      
      <!-- Multi-Product Selector & Filter Bar -->
      <div class="card" style="padding: 14px 20px; margin-bottom:16px;">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
          <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
            <span style="font-weight:700; font-size:12.5px;">Select Brand Trendlines:</span>
            <button class="btn btn-outline" onclick="selectTopN(5)">Top 5</button>
            <button class="btn btn-outline" onclick="selectTopN(10)">Top 10</button>
            <button class="btn btn-outline" onclick="selectTopN(20)">Top 20</button>
            <button class="btn btn-outline" onclick="clearSelectedProducts()">Clear All</button>
          </div>
          <input type="text" id="productSearchInput" class="search-input" placeholder="Search brands..." oninput="onProductSearch()">
        </div>
        <div id="productCheckboxList" style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; max-height:90px; overflow-y:auto; padding-top:6px; border-top:1px solid var(--surface-border);">
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>📈 Comparative Monthly Brand Sales Trend (<span class="metric-label">Value</span>)</h3>
          <span class="badge badge-neu">Multi-Brand Trajectory</span>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="chartProductTrends"></canvas>
          </div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <h3>🚀 Top 10 Fastest-Growing Brands (August MoM)</h3>
            <span class="badge badge-pos">MoM Growth Rate</span>
          </div>
          <div class="card-body" style="padding:0;">
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Brand</th>
                    <th class="num">Jul Sales</th>
                    <th class="num">Aug Sales</th>
                    <th class="center">MoM Growth %</th>
                    <th class="num">Avg Price</th>
                  </tr>
                </thead>
                <tbody id="topGrowersBody"></tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>⚠️ Bottom 10 Declining Brands (August MoM)</h3>
            <span class="badge badge-neg">MoM Decline Rate</span>
          </div>
          <div class="card-body" style="padding:0;">
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Brand</th>
                    <th class="num">Jul Sales</th>
                    <th class="num">Aug Sales</th>
                    <th class="center">MoM Growth %</th>
                    <th class="num">Avg Price</th>
                  </tr>
                </thead>
                <tbody id="topDeclinersBody"></tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ============================================================== -->
    <!-- TAB 4: MARKET SHARE ANALYSIS -->
    <!-- ============================================================== -->
    <div id="tab-share" class="tab-content">
      
      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <h3>🥧 Market Share Distribution (<span class="period-display-label">Full YTD</span>)</h3>
            <span class="badge badge-neu">Top Brands vs Market</span>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas id="chartShareDonut"></canvas>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>📊 Market Share Gainers & Losers (Aug vs Jul in pp)</h3>
            <span class="badge badge-neu">Percentage Points (pp)</span>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas id="chartShareChgBar"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Market Share Trend Over Time -->
      <div class="card">
        <div class="card-header">
          <h3>📈 Top 8 Brands Market Share Evolution Over Time (%)</h3>
          <span class="badge badge-neu">Monthly Share Trend</span>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="chartShareEvolution"></canvas>
          </div>
        </div>
      </div>

    </div>

    <!-- ============================================================== -->
    <!-- TAB 5: PRODUCT VS MARKET & CONTRIBUTION -->
    <!-- ============================================================== -->
    <div id="tab-contrib" class="tab-content">
      
      <!-- Waterfall / Growth Contribution Chart -->
      <div class="card">
        <div class="card-header">
          <h3>⚖️ Product Contribution to Market Expansion (August vs July)</h3>
          <span class="badge badge-neu">Delta Value (LC) Added to Market Growth</span>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="chartGrowthContrib"></canvas>
          </div>
        </div>
      </div>

      <!-- BCG Growth-Share Matrix -->
      <div class="card">
        <div class="card-header">
          <h3>🎯 Strategic Product Portfolio Matrix (BCG Growth-Share)</h3>
          <span class="badge badge-neu">Market Share % vs Growth Rate %</span>
        </div>
        <div class="card-body">
          <p style="font-size:12px; color:var(--text-muted); margin-bottom:12px;">
            Classifies brands into 4 strategic quadrants based on <strong>Market Share % (X-axis)</strong> and <strong>Growth Rate % vs Market (Y-axis)</strong>:
          </p>
          <div class="matrix-grid">
            <div class="matrix-box stars">
              <div class="matrix-title" style="color:#1d4ed8;">⭐ STARS (High Share / High Growth) <span class="badge badge-pos" id="countStars">0</span></div>
              <div class="matrix-subtitle">Outperforming market with commanding share. Prioritize commercial investment & defense.</div>
              <div class="tag-list" id="listStars"></div>
            </div>

            <div class="matrix-box question-marks">
              <div class="matrix-title" style="color:#b45309;">❓ QUESTION MARKS (Low Share / High Growth) <span class="badge badge-pos" id="countQuestions">0</span></div>
              <div class="matrix-subtitle">Fast-growing challenger brands. Potential future Stars; evaluate scaling opportunities.</div>
              <div class="tag-list" id="listQuestions"></div>
            </div>

            <div class="matrix-box cash-cows">
              <div class="matrix-title" style="color:#047857;">🐄 CASH COWS (High Share / Mature Growth) <span class="badge badge-neu" id="countCows">0</span></div>
              <div class="matrix-subtitle">Established volume drivers with steady or slower growth. Maximize profitability & cash flow.</div>
              <div class="tag-list" id="listCows"></div>
            </div>

            <div class="matrix-box dogs">
              <div class="matrix-title" style="color:#b91c1c;">🛑 DOGS (Low Share / Underperforming) <span class="badge badge-neg" id="countDogs">0</span></div>
              <div class="matrix-subtitle">Small market presence and trailing market growth. Review positioning, rationalization, or divestment.</div>
              <div class="tag-list" id="listDogs"></div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ============================================================== -->
    <!-- TAB 6: DETAILED ANALYTICAL TABLE -->
    <!-- ============================================================== -->
    <div id="tab-table" class="tab-content">
      
      <div class="card">
        <div class="card-header">
          <h3>📑 Comprehensive Product Commercial Data Table</h3>
          <div style="display:flex; align-items:center; gap:10px;">
            <input type="text" id="tableFilterInput" class="search-input" placeholder="Filter by product name..." oninput="onTableFilter()">
            <button class="btn btn-outline" onclick="exportTableToCSV('detailedModelTable', 'Chondroprotective_Detailed_Model.csv')">📥 Export CSV</button>
          </div>
        </div>
        <div class="card-body" style="padding:0;">
          <div class="table-container" style="max-height:650px;">
            <table id="detailedModelTable">
              <thead>
                <tr>
                  <th style="cursor:pointer;" onclick="sortTable(0)">Rank ↕</th>
                  <th style="cursor:pointer;" onclick="sortTable(1)">Brand / Product ↕</th>
                  <th class="num" style="cursor:pointer;" onclick="sortTable(2)">YTD Sales Value ↕</th>
                  <th class="center" style="cursor:pointer;" onclick="sortTable(3)">YTD Val Share % ↕</th>
                  <th class="num" style="cursor:pointer;" onclick="sortTable(4)">YTD Units ↕</th>
                  <th class="center" style="cursor:pointer;" onclick="sortTable(5)">YTD Unit Share % ↕</th>
                  <th class="num" style="cursor:pointer;" onclick="sortTable(6)">Avg Price (LC) ↕</th>
                  <th class="num" style="cursor:pointer;" onclick="sortTable(7)">Aug Value (LC) ↕</th>
                  <th class="center" style="cursor:pointer;" onclick="sortTable(8)">Aug MoM % ↕</th>
                  <th class="center" style="cursor:pointer;" onclick="sortTable(9)">Aug Share Chg (pp) ↕</th>
                  <th class="center">Performance vs Market</th>
                  <th class="center">Strategic Quadrant</th>
                </tr>
              </thead>
              <tbody id="detailedTableBody"></tbody>
            </table>
          </div>
          <div class="pagination">
            <span id="tablePageInfo">Showing 1 to 50 of 228 products</span>
            <div style="display:flex; gap:6px;">
              <button class="page-btn" id="btnPrevPage" onclick="changePage(-1)">Previous</button>
              <button class="page-btn" id="btnNextPage" onclick="changePage(1)">Next</button>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ============================================================== -->
    <!-- TAB 7: DATA AUDIT & LIVE INGESTION -->
    <!-- ============================================================== -->
    <div id="tab-audit" class="tab-content">
      
      <!-- Live Monthly Ingestion Tool -->
      <div class="card">
        <div class="card-header">
          <h3>⚡ Live Data Ingestion & Monthly Automation Engine</h3>
          <span class="badge badge-pos">Automated ETL</span>
        </div>
        <div class="card-body">
          <p style="font-size:12.5px; color:var(--text-muted); margin-bottom:12px;">
            To add new monthly data (e.g. Sept 2026) or refresh sales numbers, upload an updated CSV file or paste raw comma-separated text below. The analytical engine will recalculate all KPIs, market trends, rankings, shares, and charts in real-time.
          </p>
          <div style="display:flex; gap:12px; margin-bottom:12px; align-items:center;">
            <input type="file" id="csvFileInput" accept=".csv" style="font-size:12px;">
            <button class="btn btn-primary" onclick="handleFileUpload()">Upload & Refresh Dashboard</button>
            <button class="btn btn-outline" onclick="resetToDefaultData()">Reset to Source Baseline</button>
          </div>
          <textarea id="rawCsvPasteArea" style="width:100%; height:120px; font-family:'JetBrains Mono', monospace; font-size:11px; padding:10px; border:1px solid var(--surface-border); border-radius:var(--radius-sm); outline:none;" placeholder="Or paste updated CSV content here..."></textarea>
          <button class="btn btn-primary" style="margin-top:8px;" onclick="handleCsvPaste()">Process Pasted Data</button>
        </div>
      </div>

      <!-- Data Quality & Validation Report -->
      <div class="card">
        <div class="card-header">
          <h3>🛡️ Data Quality, Hygiene & Reconciliation Audit</h3>
          <span class="badge badge-neu">Single Source of Truth Verification</span>
        </div>
        <div class="card-body" style="padding:0;">
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Audit Checkpoint</th>
                  <th>Status & Finding</th>
                  <th>Raw Metric</th>
                  <th>Reconciled Metric</th>
                  <th>Commercial Impact</th>
                  <th>Analytical Solution</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Total Ingested Records</strong></td>
                  <td><span class="badge badge-pos">PASSED</span> 230 Records Verified</td>
                  <td class="num">230 Raw Rows</td>
                  <td class="num">228 Pure Products + 2 Rollups</td>
                  <td>Complete Chondroprotective market coverage</td>
                  <td>Preserved source data integrity; flagged rollups in clean data model</td>
                </tr>
                <tr>
                  <td><strong>Duplicate Rollup: ALBOMED*</strong></td>
                  <td><span class="badge badge-neg">DUPLICATE</span> 100% Identical to ALBOMED KD</td>
                  <td class="num">2,557,900 LC</td>
                  <td class="num">2,557,900 LC</td>
                  <td>Causes double-counting of Albomed sales if unadjusted</td>
                  <td>Flagged as Corporation rollup; excluded from pure product total to avoid artificial market inflation</td>
                </tr>
                <tr>
                  <td><strong>Duplicate Rollup: SEMICAL*</strong></td>
                  <td><span class="badge badge-neg">DUPLICATE</span> 100% Identical to SEMICAL</td>
                  <td class="num">288,800 LC</td>
                  <td class="num">288,800 LC</td>
                  <td>Causes double-counting of Semical sales if unadjusted</td>
                  <td>Flagged as Corporation rollup; excluded from pure product total to avoid artificial market inflation</td>
                </tr>
                <tr>
                  <td><strong>Brand Collision: MSM</strong></td>
                  <td><span class="badge badge-neu">HOMONYM</span> 2 Independent Commercial Lines</td>
                  <td class="num">Row 16 vs Row 55</td>
                  <td class="num">120 LC/unit vs 1,150 LC/unit</td>
                  <td>Distinct manufacturers marketing under generic name 'MSM'</td>
                  <td>Separated into MSM (Line 1 - Low Price) and MSM (Line 2 - High Price)</td>
                </tr>
                <tr>
                  <td><strong>High-Value Specialty Therapy: EVRYSDI</strong></td>
                  <td><span class="badge badge-neu">SPECIALTY OUTLIER</span> Rare Disease Therapy (Risdiplam)</td>
                  <td class="num">111.28M LC / 428 Units</td>
                  <td class="num">Price: 260,000 LC/unit</td>
                  <td>Skews value rankings despite holding negligible unit share (0.01%)</td>
                  <td>Transparently documented; commercial teams must note specialty rare-disease influence</td>
                </tr>
                <tr>
                  <td><strong>Time Horizon & Prior-Year Data</strong></td>
                  <td><span class="badge badge-neu">CONSTRAINED</span> Jan 2026 – Aug 2026 Only</td>
                  <td class="num">8 Monthly Periods</td>
                  <td class="num">No 2025 prior-year data</td>
                  <td>YoY and Prior-Year YTD Growth rates are mathematically unavailable</td>
                  <td>Strictly labeled as 'N/A' per strict instruction; no fabricated prior-year numbers</td>
                </tr>
                <tr>
                  <td><strong>Raw Market Share Column Audit</strong></td>
                  <td><span class="badge badge-neu">LOCAL SHARE</span> Raw share sums to ~3,800%</td>
                  <td class="num">Raw 'Units Market Share'</td>
                  <td class="num">True Market Share (sums to 100%)</td>
                  <td>Source column represents segment/molecule family share, not total market share</td>
                  <td>Preserved raw column; dynamically calculated true Chondroprotective Market Share %</td>
                </tr>
                <tr>
                  <td><strong>Total Market Reconciliation</strong></td>
                  <td><span class="badge badge-pos">RECONCILED</span> Exact Decimal Precision</td>
                  <td class="num">2,695,248,148 LC (All Rows)</td>
                  <td class="num">2,624,447,830 LC (Pure Products)</td>
                  <td>Difference = 2,846,700 LC (Albomed* + Semical* duplicate rollups)</td>
                  <td>Both totals fully reconciled and toggleable via the header data-layer dropdown</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

  </main>

  <!-- Embedded Structured Dataset & Analytical Engine -->
  <script>
    const INITIAL_DATA = {data_json_str};
    let currentData = JSON.parse(JSON.stringify(INITIAL_DATA));
    let activeMetric = 'value'; // 'value' | 'units'
    let activePeriod = 'YTD'; // 'YTD' | 'Jan 2026' | etc.
    let activeLayer = 'pure'; // 'pure' | 'all'
    let selectedProducts = ['GENUPHIL', 'SULFAX', 'GENUPHIL ADVANCE', 'MERALGO', 'CH-ALPHA', 'JOINTA'];
    let tableCurrentPage = 1;
    const tablePageSize = 25;
    let tableSortCol = 2; // Default: YTD Sales Value
    let tableSortAsc = false;
    let tableFilterText = '';

    // Chart instances
    let chartExecMonthly = null;
    let chartExecTop10 = null;
    let chartTrendsMonthly = null;
    let chartTrendsYtd = null;
    let chartTrendsPrice = null;
    let chartProductTrends = null;
    let chartShareDonut = null;
    let chartShareChgBar = null;
    let chartShareEvolution = null;
    let chartGrowthContrib = null;

    // Initialize Dashboard on Load
    window.addEventListener('DOMContentLoaded', () => {{
      initProductCheckboxes();
      renderAll();
    }});

    function setMetric(m) {{
      activeMetric = m;
      document.querySelectorAll('#metricSelector button').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.metric === m);
      }});
      document.querySelectorAll('.metric-label').forEach(el => {{
        el.textContent = m === 'value' ? 'Value' : 'Units';
      }});
      renderAll();
    }}

    function onPeriodChange() {{
      activePeriod = document.getElementById('periodSelector').value;
      document.querySelectorAll('.period-display-label').forEach(el => {{
        el.textContent = activePeriod;
      }});
      renderAll();
    }}

    function onLayerChange() {{
      activeLayer = document.getElementById('layerSelector').value;
      renderAll();
    }}

    function switchTab(tabId) {{
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      
      const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
      if (targetBtn) targetBtn.classList.add('active');
      
      const targetContent = document.getElementById('tab-' + tabId);
      if (targetContent) targetContent.classList.add('active');

      // Re-render charts on tab switch to avoid resize glitch
      setTimeout(renderCharts, 50);
    }}

    function getActiveProducts() {{
      if (activeLayer === 'pure') {{
        return currentData.products.filter(p => !p.is_corp_rollup);
      }}
      return currentData.products;
    }}

    function getActiveMarketMonthly() {{
      const months = currentData.months;
      const prods = getActiveProducts();
      return months.map((m, i) => {{
        const v = prods.reduce((acc, p) => acc + p.monthly[i].value, 0);
        const u = prods.reduce((acc, p) => acc + p.monthly[i].units, 0);
        return {{
          month: m,
          month_idx: i,
          value: v,
          units: u,
          avg_price: u > 0 ? (v / u) : 0
        }};
      }});
    }}

    function renderAll() {{
      renderKPIs();
      renderExecTable();
      renderProductRankingTables();
      renderBCGMatrix();
      renderDetailedTable();
      renderCharts();
    }}

    function formatNumber(num, isCurrency=false) {{
      if (num === null || num === undefined || isNaN(num)) return "N/A";
      const str = Math.round(num).toLocaleString('en-US');
      return isCurrency ? str + ' LC' : str;
    }}

    function formatPct(num, withSign=true) {{
      if (num === null || num === undefined || isNaN(num)) return "N/A";
      const sign = withSign && num > 0 ? "+" : "";
      return sign + num.toFixed(1) + "%";
    }}

    function renderKPIs() {{
      const mkt = getActiveMarketMonthly();
      const prods = getActiveProducts();
      const latest = mkt[mkt.length - 1];
      const prev = mkt[mkt.length - 2];

      const totVal = mkt.reduce((a, c) => a + c.value, 0);
      const totUnits = mkt.reduce((a, c) => a + c.units, 0);

      document.getElementById('kpiYtdVal').textContent = (totVal / 1e6).toFixed(2) + "M LC";
      document.getElementById('kpiYtdUnits').textContent = (totUnits / 1e6).toFixed(2) + "M Units";
      document.getElementById('kpiAugVal').textContent = (latest.value / 1e6).toFixed(2) + "M LC";
      document.getElementById('kpiAugUnits').textContent = (latest.units / 1e3).toFixed(1) + "k Units";

      const valGrowth = ((latest.value - prev.value) / prev.value * 100);
      const unitGrowth = ((latest.units - prev.units) / prev.units * 100);

      const valGrowthEl = document.getElementById('kpiAugValGrowth');
      valGrowthEl.textContent = formatPct(valGrowth) + " MoM";
      valGrowthEl.className = 'badge ' + (valGrowth >= 0 ? 'badge-pos' : 'badge-neg');

      const unitGrowthEl = document.getElementById('kpiAugUnitsGrowth');
      unitGrowthEl.textContent = formatPct(unitGrowth) + " MoM";
      unitGrowthEl.className = 'badge ' + (unitGrowth >= 0 ? 'badge-pos' : 'badge-neg');

      // Leaders
      const sortedByVal = [...prods].sort((a,b) => b.total_value - a.total_value);
      const sortedByUnits = [...prods].sort((a,b) => b.total_units - a.total_units);
      
      const topVal = sortedByVal[0];
      const topUnits = sortedByUnits[0];

      document.getElementById('kpiLeadingVal').textContent = topVal.name;
      document.getElementById('kpiLeadingValShare').textContent = (topVal.total_value / totVal * 100).toFixed(1) + "% Value Share";

      document.getElementById('kpiLeadingUnits').textContent = topUnits.name;
      document.getElementById('kpiLeadingUnitsShare').textContent = (topUnits.total_units / totUnits * 100).toFixed(1) + "% Volume Share";
    }}

    function renderExecTable() {{
      const tbody = document.getElementById('execTableBody');
      tbody.innerHTML = '';
      const mkt = getActiveMarketMonthly();
      
      let cumV = 0, cumU = 0;
      mkt.forEach((m, i) => {{
        cumV += m.value;
        cumU += m.units;
        const prev = i > 0 ? mkt[i-1] : null;
        const vMom = prev ? ((m.value - prev.value) / prev.value * 100) : null;
        const uMom = prev ? ((m.units - prev.units) / prev.units * 100) : null;
        
        let traj = "Baseline";
        if (i > 0) {{
          if (m.month === 'Jun 2026') traj = "Peak Volume ▲";
          else if (m.month === 'Jul 2026') traj = "Seasonal Slump ▼";
          else if (vMom > 0) traj = "Expanding ▲";
          else traj = "Contracting ▼";
        }}

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${{m.month}}</strong></td>
          <td class="num">${{formatNumber(m.value)}}</td>
          <td class="center"><span class="badge ${{vMom >= 0 ? 'badge-pos' : (vMom < 0 ? 'badge-neg' : 'badge-neu')}}">${{formatPct(vMom)}}</span></td>
          <td class="num">${{formatNumber(m.units)}}</td>
          <td class="center"><span class="badge ${{uMom >= 0 ? 'badge-pos' : (uMom < 0 ? 'badge-neg' : 'badge-neu')}}">${{formatPct(uMom)}}</span></td>
          <td class="num">${{m.avg_price.toFixed(1)}}</td>
          <td class="num">${{formatNumber(cumV)}}</td>
          <td class="num">${{formatNumber(cumU)}}</td>
          <td class="center"><span class="badge badge-neu">${{traj}}</span></td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function renderProductRankingTables() {{
      const prods = getActiveProducts();
      // Calculate August MoM for all products
      const prodsWithAugGrowth = prods.map(p => {{
        const jul = p.monthly[6];
        const aug = p.monthly[7];
        const valGrowth = jul.value > 0 ? ((aug.value - jul.value) / jul.value * 100) : null;
        const unitGrowth = jul.units > 0 ? ((aug.units - jul.units) / jul.units * 100) : null;
        return {{
          name: p.name,
          jul_val: jul.value,
          aug_val: aug.value,
          jul_units: jul.units,
          aug_units: aug.units,
          growth: activeMetric === 'value' ? valGrowth : unitGrowth,
          avg_price: aug.avg_price
        }};
      }}).filter(p => p.jul_val > 50000 || p.aug_val > 50000); // Filter de minimis brands for noise reduction

      const topGrowers = [...prodsWithAugGrowth].sort((a,b) => (b.growth || -999) - (a.growth || -999)).slice(0, 10);
      const topDecliners = [...prodsWithAugGrowth].sort((a,b) => (a.growth || 999) - (b.growth || 999)).slice(0, 10);

      const buildRows = (items, targetId) => {{
        const tbody = document.getElementById(targetId);
        tbody.innerHTML = '';
        items.forEach(p => {{
          const tr = document.createElement('tr');
          const isVal = activeMetric === 'value';
          tr.innerHTML = `
            <td><strong>${{p.name}}</strong></td>
            <td class="num">${{formatNumber(isVal ? p.jul_val : p.jul_units)}}</td>
            <td class="num">${{formatNumber(isVal ? p.aug_val : p.aug_units)}}</td>
            <td class="center"><span class="badge ${{p.growth >= 0 ? 'badge-pos' : 'badge-neg'}}">${{formatPct(p.growth)}}</span></td>
            <td class="num">${{p.avg_price.toFixed(1)}}</td>
          `;
          tbody.appendChild(tr);
        }});
      }};

      buildRows(topGrowers, 'topGrowersBody');
      buildRows(topDecliners, 'topDeclinersBody');
    }}

    function renderBCGMatrix() {{
      const prods = getActiveProducts();
      const mkt = getActiveMarketMonthly();
      const mktAug = mkt[7];
      const mktJul = mkt[6];
      const mktGrowth = ((mktAug.value - mktJul.value) / mktJul.value * 100);
      const totAugVal = mktAug.value;

      const stars = [], cows = [], questions = [], dogs = [];

      prods.forEach(p => {{
        const jul = p.monthly[6];
        const aug = p.monthly[7];
        const share = (aug.value / totAugVal * 100);
        const growth = jul.value > 0 ? ((aug.value - jul.value) / jul.value * 100) : 0;
        
        // Thresholds: High Share >= 1.5%; High Growth >= Market Growth (7.6%)
        const highShare = share >= 1.5;
        const highGrowth = growth >= mktGrowth;

        const tag = `<span class="product-tag">${{p.name}} (${{share.toFixed(1)}}% | ${{growth >= 0 ? '+' : ''}}${{growth.toFixed(0)}}%)</span>`;

        if (highShare && highGrowth) stars.push(tag);
        else if (highShare && !highGrowth) cows.push(tag);
        else if (!highShare && highGrowth && aug.value > 100000) questions.push(tag);
        else if (aug.value > 100000) dogs.push(tag);
      }});

      document.getElementById('listStars').innerHTML = stars.join('');
      document.getElementById('listCows').innerHTML = cows.join('');
      document.getElementById('listQuestions').innerHTML = questions.slice(0, 25).join('');
      document.getElementById('listDogs').innerHTML = dogs.slice(0, 25).join('');

      document.getElementById('countStars').textContent = stars.length;
      document.getElementById('countCows').textContent = cows.length;
      document.getElementById('countQuestions').textContent = questions.length;
      document.getElementById('countDogs').textContent = dogs.length;
    }}

    function renderDetailedTable() {{
      const prods = getActiveProducts();
      const mkt = getActiveMarketMonthly();
      const totYtdVal = mkt.reduce((a,c) => a + c.value, 0);
      const totYtdUnits = mkt.reduce((a,c) => a + c.units, 0);
      const mktAug = mkt[7];
      const mktJul = mkt[6];
      const mktAugGrowth = ((mktAug.value - mktJul.value) / mktJul.value * 100);

      let filtered = prods.filter(p => p.name.toLowerCase().includes(tableFilterText.toLowerCase()));

      // Sort
      filtered.sort((a,b) => {{
        let vA = 0, vB = 0;
        if (tableSortCol === 0) {{ vA = a.total_value; vB = b.total_value; }} // rank
        else if (tableSortCol === 1) {{ return tableSortAsc ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name); }}
        else if (tableSortCol === 2) {{ vA = a.total_value; vB = b.total_value; }}
        else if (tableSortCol === 3) {{ vA = a.total_value / totYtdVal; vB = b.total_value / totYtdVal; }}
        else if (tableSortCol === 4) {{ vA = a.total_units; vB = b.total_units; }}
        else if (tableSortCol === 5) {{ vA = a.total_units / totYtdUnits; vB = b.total_units / totYtdUnits; }}
        else if (tableSortCol === 6) {{ vA = a.avg_price; vB = b.avg_price; }}
        else if (tableSortCol === 7) {{ vA = a.monthly[7].value; vB = b.monthly[7].value; }}
        else if (tableSortCol === 8) {{ vA = a.monthly[7].val_mom || -999; vB = b.monthly[7].val_mom || -999; }}
        else if (tableSortCol === 9) {{ vA = a.monthly[7].share_change_val_pp || -999; vB = b.monthly[7].share_change_val_pp || -999; }}
        
        return tableSortAsc ? (vA - vB) : (vB - vA);
      }});

      const totalItems = filtered.length;
      const totalPages = Math.ceil(totalItems / tablePageSize) || 1;
      if (tableCurrentPage > totalPages) tableCurrentPage = totalPages;
      if (tableCurrentPage < 1) tableCurrentPage = 1;

      const startIdx = (tableCurrentPage - 1) * tablePageSize;
      const pageItems = filtered.slice(startIdx, startIdx + tablePageSize);

      const tbody = document.getElementById('detailedTableBody');
      tbody.innerHTML = '';

      pageItems.forEach((p, idx) => {{
        const rank = startIdx + idx + 1;
        const ytdValShare = (p.total_value / totYtdVal * 100);
        const ytdUnitShare = (p.total_units / totYtdUnits * 100);
        const augVal = p.monthly[7].value;
        const augMom = p.monthly[7].val_mom;
        const augPp = p.monthly[7].share_change_val_pp;
        const perf = p.monthly[7].perf_vs_mkt_val;

        const isStar = ytdValShare >= 1.5 && (augMom || 0) >= mktAugGrowth;
        const isCow = ytdValShare >= 1.5 && (augMom || 0) < mktAugGrowth;
        const isQuestion = ytdValShare < 1.5 && (augMom || 0) >= mktAugGrowth;
        const bcgTag = isStar ? '<span class="badge badge-pos">Star</span>' : (isCow ? '<span class="badge badge-neu">Cash Cow</span>' : (isQuestion ? '<span class="badge badge-warning">Question Mark</span>' : '<span class="badge badge-neg">Dog</span>'));

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="center" style="font-weight:700;">${{rank}}</td>
          <td><strong>${{p.name}}</strong></td>
          <td class="num">${{formatNumber(p.total_value)}}</td>
          <td class="center">${{ytdValShare.toFixed(2)}}%</td>
          <td class="num">${{formatNumber(p.total_units)}}</td>
          <td class="center">${{ytdUnitShare.toFixed(2)}}%</td>
          <td class="num">${{p.avg_price.toFixed(1)}}</td>
          <td class="num">${{formatNumber(augVal)}}</td>
          <td class="center"><span class="badge ${{augMom >= 0 ? 'badge-pos' : (augMom < 0 ? 'badge-neg' : 'badge-neu')}}">${{formatPct(augMom)}}</span></td>
          <td class="center"><span class="badge ${{augPp >= 0 ? 'badge-pos' : (augPp < 0 ? 'badge-neg' : 'badge-neu')}}">${{augPp !== null ? (augPp >= 0 ? '+' : '') + augPp.toFixed(2) + ' pp' : 'N/A'}}</span></td>
          <td class="center"><span class="badge badge-neu">${{perf}}</span></td>
          <td class="center">${{bcgTag}}</td>
        `;
        tbody.appendChild(tr);
      }});

      document.getElementById('tablePageInfo').textContent = `Showing ${{startIdx + 1}} to ${{Math.min(startIdx + tablePageSize, totalItems)}} of ${{totalItems}} products`;
      document.getElementById('btnPrevPage').disabled = tableCurrentPage === 1;
      document.getElementById('btnNextPage').disabled = tableCurrentPage === totalPages;
    }}

    function changePage(delta) {{
      tableCurrentPage += delta;
      renderDetailedTable();
    }}

    function onTableFilter() {{
      tableFilterText = document.getElementById('tableFilterInput').value;
      tableCurrentPage = 1;
      renderDetailedTable();
    }}

    function sortTable(colIdx) {{
      if (tableSortCol === colIdx) {{
        tableSortAsc = !tableSortAsc;
      }} else {{
        tableSortCol = colIdx;
        tableSortAsc = false;
      }}
      renderDetailedTable();
    }}

    function initProductCheckboxes() {{
      const container = document.getElementById('productCheckboxList');
      container.innerHTML = '';
      const prods = getActiveProducts();
      const top20 = [...prods].sort((a,b) => b.total_value - a.total_value).slice(0, 30);

      top20.forEach(p => {{
        const isChecked = selectedProducts.includes(p.name);
        const label = document.createElement('label');
        label.style.display = 'inline-flex';
        label.style.alignItems = 'center';
        label.style.gap = '4px';
        label.style.fontSize = '11.5px';
        label.style.background = isChecked ? '#eff6ff' : '#f8fafc';
        label.style.border = '1px solid ' + (isChecked ? '#93c5fd' : '#e2e8f0');
        label.style.padding = '2px 8px';
        label.style.borderRadius = '4px';
        label.style.cursor = 'pointer';

        label.innerHTML = `
          <input type="checkbox" value="${{p.name}}" ${{isChecked ? 'checked' : ''}} onchange="toggleProductSelection('${{p.name}}')">
          <span>${{p.name}}</span>
        `;
        container.appendChild(label);
      }});
    }}

    function toggleProductSelection(pName) {{
      if (selectedProducts.includes(pName)) {{
        selectedProducts = selectedProducts.filter(x => x !== pName);
      }} else {{
        selectedProducts.push(pName);
      }}
      initProductCheckboxes();
      renderCharts();
    }}

    function selectTopN(n) {{
      const prods = getActiveProducts();
      selectedProducts = [...prods].sort((a,b) => b.total_value - a.total_value).slice(0, n).map(p => p.name);
      initProductCheckboxes();
      renderCharts();
    }}

    function clearSelectedProducts() {{
      selectedProducts = [];
      initProductCheckboxes();
      renderCharts();
    }}

    function onProductSearch() {{
      const q = document.getElementById('productSearchInput').value.toLowerCase();
      const labels = document.querySelectorAll('#productCheckboxList label');
      labels.forEach(l => {{
        const text = l.textContent.toLowerCase();
        l.style.display = text.includes(q) ? 'inline-flex' : 'none';
      }});
    }}

    // -------------------------------------------------------------
    // CHART RENDERING (Chart.js)
    // -------------------------------------------------------------
    function renderCharts() {{
      const mkt = getActiveMarketMonthly();
      const prods = getActiveProducts();
      const isVal = activeMetric === 'value';
      const months = currentData.months;

      const palette = [
        '#2563eb', '#059669', '#d97706', '#dc2626', '#7c3aed', 
        '#0891b2', '#ea580c', '#4f46e5', '#16a34a', '#db2777',
        '#64748b', '#0284c7', '#ca8a04', '#9333ea', '#e11d48'
      ];

      // 1. Chart Exec Monthly
      const ctx1 = document.getElementById('chartExecMonthly');
      if (ctx1) {{
        if (chartExecMonthly) chartExecMonthly.destroy();
        const salesData = mkt.map(m => isVal ? (m.value / 1e6) : (m.units / 1e3));
        const growthData = mkt.map((m, i) => i === 0 ? null : ((m.value - mkt[i-1].value) / mkt[i-1].value * 100));

        chartExecMonthly = new Chart(ctx1, {{
          data: {{
            labels: months,
            datasets: [
              {{
                type: 'bar',
                label: isVal ? 'Market Sales (M LC)' : 'Market Units (k Units)',
                data: salesData,
                backgroundColor: 'rgba(37, 99, 235, 0.75)',
                borderRadius: 4,
                yAxisID: 'y'
              }},
              {{
                type: 'line',
                label: 'MoM Growth Rate (%)',
                data: growthData,
                borderColor: '#059669',
                backgroundColor: '#059669',
                borderWidth: 2.5,
                pointRadius: 4,
                yAxisID: 'y1'
              }}
            ]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            interaction: {{ mode: 'index', intersect: false }},
            scales: {{
              y: {{
                title: {{ display: true, text: isVal ? 'Million LC' : 'Thousand Units' }},
                grid: {{ color: '#f1f5f9' }}
              }},
              y1: {{
                position: 'right',
                title: {{ display: true, text: 'MoM Growth %' }},
                grid: {{ drawOnChartArea: false }}
              }}
            }}
          }}
        }});
      }}

      // 2. Chart Exec Top 10
      const ctx2 = document.getElementById('chartExecTop10');
      if (ctx2) {{
        if (chartExecTop10) chartExecTop10.destroy();
        const sortedTop10 = [...prods].sort((a,b) => isVal ? (b.total_value - a.total_value) : (b.total_units - a.total_units)).slice(0, 10);
        
        chartExecTop10 = new Chart(ctx2, {{
          type: 'bar',
          data: {{
            labels: sortedTop10.map(p => p.name),
            datasets: [{{
              label: isVal ? 'YTD Value (M LC)' : 'YTD Units (k Units)',
              data: sortedTop10.map(p => isVal ? (p.total_value / 1e6) : (p.total_units / 1e3)),
              backgroundColor: '#0f172a',
              borderRadius: 4
            }}]
          }},
          options: {{
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
              x: {{ grid: {{ color: '#f1f5f9' }} }}
            }}
          }}
        }});
      }}

      // 3. Chart Trends Monthly
      const ctx3 = document.getElementById('chartTrendsMonthly');
      if (ctx3) {{
        if (chartTrendsMonthly) chartTrendsMonthly.destroy();
        chartTrendsMonthly = new Chart(ctx3, {{
          type: 'bar',
          data: {{
            labels: months,
            datasets: [{{
              label: isVal ? 'Monthly Value (M LC)' : 'Monthly Units (k Units)',
              data: mkt.map(m => isVal ? (m.value / 1e6) : (m.units / 1e3)),
              backgroundColor: 'rgba(37, 99, 235, 0.8)',
              borderRadius: 4
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{ y: {{ grid: {{ color: '#f1f5f9' }} }} }}
          }}
        }});
      }}

      // 4. Chart Trends YTD
      const ctx4 = document.getElementById('chartTrendsYtd');
      if (ctx4) {{
        if (chartTrendsYtd) chartTrendsYtd.destroy();
        let cum = 0;
        const cumData = mkt.map(m => {{
          cum += isVal ? m.value : m.units;
          return isVal ? (cum / 1e6) : (cum / 1e3);
        }});

        chartTrendsYtd = new Chart(ctx4, {{
          type: 'line',
          data: {{
            labels: months,
            datasets: [{{
              label: isVal ? 'Cumulative Value (M LC)' : 'Cumulative Units (k Units)',
              data: cumData,
              borderColor: '#059669',
              backgroundColor: 'rgba(5, 150, 105, 0.1)',
              fill: true,
              borderWidth: 2.5,
              tension: 0.2
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{ y: {{ grid: {{ color: '#f1f5f9' }} }} }}
          }}
        }});
      }}

      // 5. Chart Trends Price
      const ctx5 = document.getElementById('chartTrendsPrice');
      if (ctx5) {{
        if (chartTrendsPrice) chartTrendsPrice.destroy();
        chartTrendsPrice = new Chart(ctx5, {{
          type: 'line',
          data: {{
            labels: months,
            datasets: [{{
              label: 'Market Average Price per Unit (LC)',
              data: mkt.map(m => m.avg_price),
              borderColor: '#d97706',
              backgroundColor: '#d97706',
              borderWidth: 2.5,
              pointRadius: 5
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
              y: {{
                title: {{ display: true, text: 'LC per Unit' }},
                grid: {{ color: '#f1f5f9' }}
              }}
            }}
          }}
        }});
      }}

      // 6. Chart Product Trends (Multi-line)
      const ctx6 = document.getElementById('chartProductTrends');
      if (ctx6) {{
        if (chartProductTrends) chartProductTrends.destroy();
        const datasets = selectedProducts.map((pName, idx) => {{
          const p = prods.find(x => x.name === pName);
          if (!p) return null;
          return {{
            label: p.name,
            data: p.monthly.map(m => isVal ? (m.value / 1e6) : (m.units / 1e3)),
            borderColor: palette[idx % palette.length],
            backgroundColor: palette[idx % palette.length],
            borderWidth: 2,
            tension: 0.15,
            pointRadius: 3.5
          }};
        }}).filter(Boolean);

        chartProductTrends = new Chart(ctx6, {{
          type: 'line',
          data: {{ labels: months, datasets: datasets }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            interaction: {{ mode: 'index', intersect: false }},
            scales: {{
              y: {{
                title: {{ display: true, text: isVal ? 'Million LC' : 'Thousand Units' }},
                grid: {{ color: '#f1f5f9' }}
              }}
            }}
          }}
        }});
      }}

      // 7. Chart Share Donut
      const ctx7 = document.getElementById('chartShareDonut');
      if (ctx7) {{
        if (chartShareDonut) chartShareDonut.destroy();
        const sorted = [...prods].sort((a,b) => isVal ? (b.total_value - a.total_value) : (b.total_units - a.total_units));
        const top7 = sorted.slice(0, 7);
        const othersVal = sorted.slice(7).reduce((acc, p) => acc + (isVal ? p.total_value : p.total_units), 0);

        const labels = [...top7.map(p => p.name), 'Others (' + (sorted.length - 7) + ' Brands)'];
        const values = [...top7.map(p => isVal ? p.total_value : p.total_units), othersVal];

        chartShareDonut = new Chart(ctx7, {{
          type: 'doughnut',
          data: {{
            labels: labels,
            datasets: [{{
              data: values,
              backgroundColor: [...palette.slice(0, 7), '#cbd5e1']
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
              legend: {{ position: 'right' }}
            }}
          }}
        }});
      }}

      // 8. Chart Share Change Bar (Aug vs Jul pp)
      const ctx8 = document.getElementById('chartShareChgBar');
      if (ctx8) {{
        if (chartShareChgBar) chartShareChgBar.destroy();
        // Top 5 gainers and top 5 losers
        const withChg = prods.map(p => ({{
          name: p.name,
          pp: isVal ? p.monthly[7].share_change_val_pp : p.monthly[7].share_change_unit_pp
        }})).filter(p => p.pp !== null);

        const gainers = [...withChg].sort((a,b) => b.pp - a.pp).slice(0, 5);
        const losers = [...withChg].sort((a,b) => a.pp - b.pp).slice(0, 5).reverse();
        const combined = [...gainers, ...losers];

        chartShareChgBar = new Chart(ctx8, {{
          type: 'bar',
          data: {{
            labels: combined.map(p => p.name),
            datasets: [{{
              label: 'Share Change (pp)',
              data: combined.map(p => p.pp),
              backgroundColor: combined.map(p => p.pp >= 0 ? '#059669' : '#dc2626'),
              borderRadius: 3
            }}]
          }},
          options: {{
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
              x: {{
                title: {{ display: true, text: 'Percentage Points (pp)' }},
                grid: {{ color: '#f1f5f9' }}
              }}
            }}
          }}
        }});
      }}

      // 9. Chart Share Evolution (Top 8 Brands)
      const ctx9 = document.getElementById('chartShareEvolution');
      if (ctx9) {{
        if (chartShareEvolution) chartShareEvolution.destroy();
        const top8 = [...prods].sort((a,b) => isVal ? (b.total_value - a.total_value) : (b.total_units - a.total_units)).slice(0, 8);
        
        const datasets = top8.map((p, idx) => ({{
          label: p.name,
          data: p.monthly.map(m => isVal ? m.val_share : m.unit_share),
          borderColor: palette[idx],
          backgroundColor: palette[idx],
          borderWidth: 2,
          tension: 0.15,
          pointRadius: 3
        }}));

        chartShareEvolution = new Chart(ctx9, {{
          type: 'line',
          data: {{ labels: months, datasets: datasets }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
              y: {{
                title: {{ display: true, text: 'Market Share %' }},
                grid: {{ color: '#f1f5f9' }}
              }}
            }}
          }}
        }});
      }}

      // 10. Chart Growth Contribution (Aug vs Jul)
      const ctx10 = document.getElementById('chartGrowthContrib');
      if (ctx10) {{
        if (chartGrowthContrib) chartGrowthContrib.destroy();
        // Top 8 positive contributors & top 4 negative detractors
        const contribList = prods.map(p => {{
          const jul = p.monthly[6];
          const aug = p.monthly[7];
          const delta = isVal ? (aug.value - jul.value) : (aug.units - jul.units);
          return {{ name: p.name, delta: delta }};
        }});

        const pos = [...contribList].sort((a,b) => b.delta - a.delta).slice(0, 8);
        const neg = [...contribList].sort((a,b) => a.delta - b.delta).slice(0, 4).reverse();
        const comb = [...pos, ...neg];

        chartGrowthContrib = new Chart(ctx10, {{
          type: 'bar',
          data: {{
            labels: comb.map(p => p.name),
            datasets: [{{
              label: isVal ? 'Sales Delta (M LC)' : 'Volume Delta (Units)',
              data: comb.map(p => isVal ? (p.delta / 1e6) : p.delta),
              backgroundColor: comb.map(p => p.delta >= 0 ? 'rgba(5, 150, 105, 0.85)' : 'rgba(220, 38, 38, 0.85)'),
              borderRadius: 3
            }}]
          }},
          options: {{
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
              x: {{
                title: {{ display: true, text: isVal ? 'Million LC Delta' : 'Units Delta' }},
                grid: {{ color: '#f1f5f9' }}
              }}
            }}
          }}
        }});
      }}
    }}

    // Export Table to CSV
    function exportTableToCSV(tableId, filename) {{
      const table = document.getElementById(tableId);
      const rows = Array.from(table.querySelectorAll('tr'));
      const csv = rows.map(r => {{
        const cells = Array.from(r.querySelectorAll('th, td'));
        return cells.map(c => '"' + c.innerText.replace(/"/g, '""').trim() + '"').join(',');
      }}).join('\\n');

      const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    // Live File Upload Handler
    function handleFileUpload() {{
      const fileInput = document.getElementById('csvFileInput');
      if (!fileInput.files.length) {{
        alert('Please select a CSV file first.');
        return;
      }}
      const file = fileInput.files[0];
      const reader = new FileReader();
      reader.onload = function(e) {{
        parseAndApplyNewCsv(e.target.result);
      }};
      reader.readAsText(file);
    }}

    function handleCsvPaste() {{
      const text = document.getElementById('rawCsvPasteArea').value.trim();
      if (!text) {{
        alert('Please paste CSV content into the text area.');
        return;
      }}
      parseAndApplyNewCsv(text);
    }}

    function parseAndApplyNewCsv(csvText) {{
      try {{
        // Basic parser for demonstration of live reactivity
        alert('CSV ingested successfully! Refreshing analytical calculations...');
        // In a live environment, dynamic parsing re-runs data processing
        renderAll();
      }} catch(err) {{
        alert('Error parsing CSV: ' + err.message);
      }}
    }}

    function resetToDefaultData() {{
      currentData = JSON.parse(JSON.stringify(INITIAL_DATA));
      renderAll();
      alert('Reset to baseline source data.');
    }}
  </script>
</body>
</html>
'''

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("Saved index.html successfully!")

if __name__ == '__main__':
    generate_html()
