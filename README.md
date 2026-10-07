# Chondroprotective Market — Commercial Intelligence & Sales Dashboard

> **Pharmaceutical Commercial Analytics, BI Dashboard & Executive Decision-Support System**  
> **Audit Period:** January 2026 – August 2026 (YTD)  
> **Coverage:** 228 Validated Products | 8 Monthly Periods | Value Sales (LC) & Unit Volume

---

## 📊 Project Overview

This repository contains a comprehensive commercial analytics and business intelligence solution for the **Chondroprotective Market** based strictly on audited monthly sales data.

The project delivers:
1. **Interactive Single-Page Web Dashboard (`index.html`)**: Fully self-contained BI dashboard built with Chart.js, featuring dynamic Value/Units slicers, period filters, 10 analytical charts, BCG Growth-Share matrix, growth contribution waterfalls, and live monthly data ingestion.
2. **Automated Multi-Tab Excel Workbook (`Chondroprotective_Market_Dashboard_2026.xlsx`)**: Institutional-grade 8-tab workbook with KPI cards, monthly trends, product performance, market shares, contribution waterfalls, detailed normalized models, and raw data input zones.
3. **Automated Python Analytical Engine**: Scripts for ETL, data hygiene, reconciliation, and automated dashboard generation.

---

## 📈 Market Snapshot (Jan – Aug 2026 YTD)

* **YTD Market Value**: **2,624,447,830 LC** (~2.62 Billion LC across pure products)
* **YTD Market Units**: **7,365,851 Units**
* **Latest Month (August 2026)**: **359,906,555 LC** (+7.6% MoM) | **1,014,141 Units** (+0.4% MoM)
* **Market Value Leader**: **GENUPHIL** (307.47M LC | 11.7% value share)
* **Market Volume Leader**: **SULFAX** (1,290,497 Units | 17.5% volume share)
* **Dominant Franchise**: **EVA Pharma Genuphil Family** (Genuphil, Advance, Woman = 613.10M LC | 23.4% of market revenue)

---

## 🚀 Live Dashboard Features (`index.html`)

* **Value vs. Units Slicer**: Instant recalculation across all 10 charts, tables, rankings, and KPIs.
* **Period & Cutoff Filtering**: Full 8-month YTD or isolated monthly views (Jan through Aug).
* **10 Interactive Visualizations**:
  1. *Dual-Axis Monthly Market Progression & MoM Growth %*
  2. *Top 10 Brand Value/Unit Rankings*
  3. *Monthly Value/Unit Trends*
  4. *Cumulative YTD Progression Run-Rate*
  5. *Weighted Average Realized Unit Price (LC)*
  6. *Multi-Brand Comparative Sales Trendlines*
  7. *Market Share Distribution Donut (Top 7 + Others)*
  8. *Market Share Gainers & Losers (percentage points pp)*
  9. *Monthly Market Share Evolution Over Time*
  10. *August vs July Growth Contribution Waterfall*
* **Strategic BCG Matrix**: Classifies brands into *Stars*, *Cash Cows*, *Question Marks*, and *Dogs*.
* **Detailed Analytical Table**: Multi-column sorting, instant search, pagination, and one-click CSV export.
* **Live Monthly Ingestion**: Paste or upload newly released monthly CSV exports to recalculate the entire dashboard in real time.

---

## 📁 Repository Structure

```
├── index.html                                  # Standalone interactive executive web dashboard
├── Chondroprotective_Market_Dashboard_2026.xlsx # Institutional 8-tab automated Excel workbook
├── raw_data.csv                                # Raw monthly sales dataset (single source of truth)
├── dashboard_data.json                         # Precomputed structured analytics dataset
├── engine.py                                   # Python calculation & validation engine
├── build_dashboard_data.py                     # JSON dataset builder
├── build_excel.py                              # Openpyxl Excel workbook generator
├── generate_html_dashboard.py                  # HTML/JS dashboard compiler
├── .gitignore                                  # Git ignore rules
└── README.md                                   # Project documentation
```

---

## 🌐 Enabling GitHub Pages (Public Online Hosting)

To host the interactive dashboard online via GitHub Pages:
1. Go to this repository's **Settings** tab on GitHub.
2. Under the left sidebar, click **Pages**.
3. Under **Build and deployment → Branch**:
   * Select `main` branch
   * Select folder `/ (root)`
4. Click **Save**.
5. Your dashboard will be live at:  
   `https://modimust5669-art.github.io/imsanalysis/`

---

## 📄 License & Attribution

Pharmaceutical Market Analytics & Commercial Decision-Support System. Built for Commercial Managers, Brand Managers, and Senior Leadership.
