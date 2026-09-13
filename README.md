# Cloud Carbon Footprint Marketplace

A submission-ready Streamlit college-project MVP that turns simulated cloud usage into estimated emissions, reduction recommendations, a simulated carbon-credit marketplace, and PDF reports.

## Features

- CSV upload plus bundled AWS, Azure, and GCP sample data
- Transparent estimated emissions calculation by service, region, provider, and month
- Interactive Plotly dashboard
- Explainable rule-based recommendations
- Simulated carbon-credit transactions stored in SQLite
- Simulated offset certificate and sustainability-report PDF downloads

## Local setup

Use Python 3.11 or newer.

```powershell
cd cloud-carbon-marketplace
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit shows, normally `http://localhost:8501`.

## Tests

```powershell
python -m pytest tests
```

## Data format

Cloud-usage uploads require: `month`, `provider`, `service`, `region`, `usage_hours`, `energy_kwh`, and `cost_usd`.

## Deployment to Streamlit Community Cloud

1. Create a new GitHub repository and add this entire project folder.
2. Commit and push the code. Do not add credentials or `.streamlit/secrets.toml`.
3. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
4. Select **Create app**, choose your repository and `main` branch, and set the entry-point file to `app.py`.
5. Click **Deploy** and wait for the hosted URL.

The prototype uses a local SQLite file for simulated transactions. On hosted Streamlit deployments, storage may reset; this is acceptable for a demonstration. Use a hosted database only if persistent multi-user records become a future requirement.

## Academic disclaimer

All figures are estimates derived from simulated data and static emission factors. Carbon projects, purchases, and certificates are fictional demonstration artifacts; they are not verified emissions disclosures or real carbon-credit transactions.
