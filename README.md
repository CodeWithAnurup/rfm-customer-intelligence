<div align="center">

# 📊 RFM Customer Intelligence Dashboard

**A production-grade customer segmentation and retention analytics platform built with Streamlit and Plotly.**

Transforms raw transactional data into actionable customer intelligence using RFM (Recency, Frequency, Monetary) analysis — complete with interactive visualizations and market-perspective insights.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](#-deployment)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](LICENSE)

</div>

---

## Overview

This dashboard segments **4,372 customers** across **38 markets** using quartile-based RFM scoring on **541,909 transactions**. It surfaces revenue concentration risks, churn early-warning signals, and segment-specific intervention strategies — the kind of analysis that typically sits behind a \$50K consulting engagement.

### What It Does

| Capability | Description |
|:--|:--|
| **RFM Scoring Engine** | Quartile-based R/F/M scoring (1–4 scale) with composite segmentation |
| **Value Tiering** | Automatic classification into High / Mid / Low value customer tiers |
| **Lifecycle Mapping** | Five lifecycle stages: VIP/Loyal → Potential Loyal → At Risk → Can't Lose → Lost |
| **Interactive Filters** | Real-time filtering by date range, country/market, and value segment |
| **Market Insights** | Six unique business-strategy perspectives — from CAC analysis to whale dependency |

---

## Tech Stack

| Component | Technology |
|:--|:--|
| Frontend & Framework | [Streamlit](https://streamlit.io) |
| Visualization | [Plotly](https://plotly.com/python/) (interactive, dark-themed) |
| Data Processing | [Pandas](https://pandas.pydata.org/) |
| Deployment | Streamlit Community Cloud / Any Python host |

---

## Dashboard Sections

### 1. Executive KPI Bar
Five real-time metrics: Total Customers, Lifetime Revenue, Average Order Value, Average Recency, and Churn Risk percentage — with conditional health indicators.

### 2. Customer Distribution by Value Tier
Bar chart showing High / Mid / Low value customer counts.
> **Insight lens:** Customer Acquisition Cost — quantifies the cost of losing high-value customers vs. investing in mid-value growth.

### 3. Customer Portfolio Treemap
Hierarchical breakdown: Value Tier → Lifecycle Stage.
> **Insight lens:** Revenue Concentration Risk — Pareto analysis showing portfolio dependency on top customer segments.

### 4. VIP Behavioral Box Plot
Recency, Frequency, and Monetary distribution spreads for the VIP/Loyal segment with outlier detection.
> **Insight lens:** Whale Customer Dependency — identifies accounts whose loss would materially impact revenue, with KAM recommendations.

### 5. RFM Correlation Heatmap
R/F/M score correlations within the Champions segment.
> **Insight lens:** Behavioral Predictability — assesses pricing power and subscription-model opportunity from spending patterns.

### 6. Customer Lifecycle Distribution
Counts across all five lifecycle stages (Lost → VIP/Loyal).
> **Insight lens:** Funnel Health Score — computes erosion ratio against industry benchmarks.

### 7. Segment DNA Fingerprint
Grouped bar chart of average R/F/M scores per lifecycle stage.
> **Insight lens:** Competitive Positioning — exact intervention playbook per segment with timing-specific win-back probabilities.

---

## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/CodeWithAnurup/rfm-customer-intelligence.git
cd rfm-customer-intelligence

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

---

## Project Structure

```
.
├── app.py                 # Main dashboard application (single-file, deploy-ready)
├── online_retail.csv      # UCI Online Retail dataset (541K transactions)
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Theme and server configuration
├── Notebook.ipynb         # Original exploratory analysis (reference only)
└── README.md
```

---

## Data

**Source:** [UCI Machine Learning Repository — Online Retail Dataset](https://archive.ics.uci.edu/ml/datasets/online+retail)

| Attribute | Detail |
|:--|:--|
| Records | 541,909 transactions |
| Period | December 2010 – December 2011 |
| Markets | 38 countries |
| Unique Customers | 4,372 (after cleaning) |
| Features | InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country |

---

## Methodology

```
Raw Transactions
    │
    ▼
┌─────────────────┐
│  Data Cleaning   │  Drop null CustomerIDs, parse dates, compute TotalAmount
└────────┬────────┘
         ▼
┌─────────────────┐
│  RFM Aggregation │  Group by CustomerID → Recency, Frequency, Monetary
└────────┬────────┘
         ▼
┌─────────────────┐
│  Quartile Scoring│  Each dimension scored 1–4 based on distribution quartiles
└────────┬────────┘
         ▼
┌─────────────────┐
│  Segmentation    │  Composite score (3–12) → Value Tier + Lifecycle Stage
└────────┬────────┘
         ▼
┌─────────────────┐
│  Visualization   │  Interactive Plotly charts with market-strategy insights
└─────────────────┘
```

**Reference date:** All Recency calculations are anchored to `max(InvoiceDate) + 1 day` — the analysis simulates being run the morning after the last transaction, not relative to today.

---

## Deployment

### Streamlit Community Cloud (Recommended)

1. Fork or push this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Deploy

### Docker (Self-hosted)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
<sub>Built with Streamlit · Plotly · Pandas</sub>
</div>
