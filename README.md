# India Startup Funding Pulse

**Day 07 of the 21-Day Build Challenge**

🔗 **Live:** [indian-startup-pulse.streamlit.app](https://indian-startup-pulse.streamlit.app)

---

## What It Does

India saw one of the most dramatic startup funding cycles in the world between 2015 and 2021 — edtech exploded, fintech matured, and unicorns multiplied. But most of that data lives in scattered CSVs and news articles.

This app merges 4,200+ real funding deals across 7 years and turns them into a navigable intelligence layer. Not another bar chart dashboard — an actual ecosystem decoder.

---

## Features

**Big Picture**
- Deal volume and funding amount year-on-year (2015–2019, 2021)
- Sector heat timeline — heatmap showing where money moved across years
- Funding stage mix by year — tracks ecosystem maturity from seed-heavy to late-stage

**Sectors**
- Pick any sector and see its full arc: deal trend, stage distribution, top funded startups, average ticket size by year

**Cities**
- Geo bubble map of India showing funding concentration by city
- City vs city head-to-head comparison — sector breakdown, deal count, total funding
- Top cities deal volume over time

**Investors**
- Top investors by deal count and by total funding deployed
- Investor deep-dive — sector preference, stage preference, average ticket size
- Co-investment pairs — which VCs always show up together

---

## Stack

| Tool | Use |
|------|-----|
| Python | Core logic |
| Streamlit | UI and deployment |
| Plotly | All charts and geo map |
| Pandas | Data merging, normalization, analysis |

---

## Data Sources

- **SRK Dataset** (`sudalairajkumar/indian-startup-funding`) — 3,044 real deals, 2015–2019, via Kaggle
- **2021 Dataset** (`India-startup-funding-2021-full`) — 1,209 deals, full year 2021, via Kaggle

**Note on data quality:** 2020 is excluded — the SRK dataset only captures January 2020 (7 entries), which creates a misleading gap. Amounts above $5B are capped as data entry errors.

---

## How to Run Locally

```bash
git clone https://github.com/yourusername/india-startup-funding-pulse
cd india-startup-funding-pulse

pip install -r requirements.txt

# Place datasets in data/
# data/startup_funding_srk.csv
# data/startup_funding_2021.csv

streamlit run app.py
```

---

## What I Learned

- Real-world datasets are messy in predictable ways — Indian number formatting (`20,00,00,000`), city name variants (Bangalore/Bengaluru, Gurgaon/Gurugram), and industry labels that are actually sub-verticals all need explicit normalization before anything useful can be built
- A single bad row (Alteria Capital with a `$150,000,000,000` entry) can completely distort a chart — outlier detection before plotting is non-negotiable
- Merging datasets across years requires checking schema compatibility column by column, not just assuming field names match intent
- Planning the full feature set before writing code (learned on Day 6) made this the smoothest build of the week
