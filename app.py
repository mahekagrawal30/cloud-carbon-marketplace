from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.calculator import aggregate, calculate_emissions, summary_metrics
from modules.database import get_transactions, initialize_database, record_transaction
from modules.recommendations import generate_recommendations
from modules.reports import build_certificate, build_sustainability_report

ROOT = Path(__file__).parent
DATA, DB_PATH = ROOT / "data", ROOT / "database" / "marketplace.db"
JADE, DEEP_JADE, CRUISE, PALE_CRUISE, TEXT, MUTED, AMBER = "#00A86B", "#046C4E", "#B5E3D8", "#EFFBF7", "#17342C", "#5B6F69", "#E5A93E"
COLORS = [JADE, DEEP_JADE, "#58BFA0", "#7FD1BC", AMBER, "#5E9F8B"]

st.set_page_config(page_title="Cloud Carbon Marketplace", page_icon="🌿", layout="wide")


def inject_styles() -> None:
    st.markdown(f"""<style>
    :root {{ --jade:{JADE}; --deep:{DEEP_JADE}; --cruise:{CRUISE}; --pale:{PALE_CRUISE}; --ink:{TEXT}; --muted:{MUTED}; --amber:{AMBER}; }}
    .stApp {{background:var(--pale);color:var(--ink)}} [data-testid="stHeader"] {{background:rgba(239,251,247,.9)}}
    .block-container {{max-width:1320px;padding-top:2rem;padding-bottom:3rem}} h1,h2,h3 {{color:var(--ink)!important;letter-spacing:-.03em}} h1{{font-weight:800!important}}
    .top-brand{{display:flex;align-items:center;justify-content:space-between;background:#fff;border:1px solid #D5EDE5;border-radius:16px;padding:.85rem 1.15rem;margin-bottom:.65rem;box-shadow:0 6px 18px rgba(4,108,78,.05)}} .brand-kicker{{color:var(--deep);font-size:.68rem;letter-spacing:.12em;font-weight:800;text-transform:uppercase}} .brand-title{{color:var(--ink);font-size:1.12rem;font-weight:800;line-height:1.2}} .brand-subtitle{{color:var(--muted);font-size:.82rem;font-weight:650}}
    [data-testid="stRadio"]{{background:#fff;border:1px solid #D5EDE5;border-radius:13px;padding:.32rem .55rem;margin-bottom:1.3rem;box-shadow:0 6px 18px rgba(4,108,78,.05)}} [data-testid="stRadio"] [role="radiogroup"]{{gap:.3rem;justify-content:space-between}} [data-testid="stRadio"] label{{border-radius:9px;padding:.42rem .6rem;margin:0!important}} [data-testid="stRadio"] label:has(input:checked){{background:#DDF5EC;font-weight:800}} [data-testid="stRadio"] label:has(input:checked) p{{color:var(--deep)!important}}
    .hero{{background:linear-gradient(115deg,#fff,#E3F8F0);border:1px solid #C7E9DE;border-radius:22px;padding:2.2rem;box-shadow:0 14px 35px rgba(4,108,78,.08);margin-bottom:1.35rem}} .eyebrow,.section-label{{color:var(--deep);font-size:.77rem;letter-spacing:.12em;font-weight:800;text-transform:uppercase}} .hero-title{{font-size:clamp(2rem,3.3vw,3.15rem);font-weight:800;line-height:1.04;letter-spacing:-.055em;margin:.55rem 0 .75rem}} .hero-copy,.section-copy,.card-copy{{color:var(--muted);line-height:1.6}}
    .workflow{{display:flex;flex-wrap:wrap;gap:.55rem;align-items:center;margin-top:1.55rem;font-weight:750;color:var(--deep)}} .step{{background:#fff;border:1px solid #C7E9DE;border-radius:999px;padding:.42rem .75rem}} .arrow{{color:var(--jade)}}
    .notice{{background:#fff;border-left:4px solid var(--jade);border-radius:12px;padding:.95rem 1.1rem;color:var(--muted);box-shadow:0 6px 18px rgba(4,108,78,.06);margin:.85rem 0 1.5rem}} .notice strong{{color:var(--deep)}} .section-copy{{margin-bottom:1rem}}
    .kpi{{background:#fff;border:1px solid #D5EDE5;border-top:4px solid var(--jade);border-radius:16px;padding:1rem 1.1rem;min-height:126px;box-shadow:0 8px 20px rgba(4,108,78,.06)}} .kpi-label,.detail-label{{color:var(--muted);font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;margin-top:.3rem}} .kpi-value{{color:var(--ink);font-size:1.36rem;font-weight:800;letter-spacing:-.035em;margin-top:.18rem;word-break:break-word}}
    .chart-shell{{background:#fff;border:1px solid #D5EDE5;border-radius:16px;padding:.4rem .7rem .15rem;box-shadow:0 8px 20px rgba(4,108,78,.06);margin-bottom:1rem}} .rec-card,.project-card{{background:#fff;border:1px solid #D5EDE5;border-radius:16px;padding:1.15rem 1.2rem;box-shadow:0 7px 18px rgba(4,108,78,.055);margin:.65rem 0}} .rec-card{{border-left:5px solid var(--jade)}} .project-card{{min-height:215px}} .selected{{border:2px solid var(--jade);background:#F6FFFB;box-shadow:0 10px 24px rgba(0,168,107,.12)}} .card-title{{color:var(--ink);font-weight:800;font-size:1.05rem;line-height:1.3}}
    .badge{{display:inline-block;border-radius:999px;padding:.23rem .58rem;font-size:.72rem;font-weight:800;margin:.45rem .25rem .2rem 0}} .high{{background:#D8F4E9;color:var(--deep)}} .medium{{background:#FFF3D6;color:#986700}} .success{{background:var(--jade);color:#fff}} .neutral{{background:#E7F6F0;color:var(--deep)}}
    .detail-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.55rem;margin-top:.75rem}} .detail{{background:#F7FCFA;border-radius:10px;padding:.6rem .7rem}} .detail-value{{font-size:.87rem;color:var(--ink);margin-top:.18rem;font-weight:700}}
    .offset-panel{{background:linear-gradient(115deg,#046C4E,#07845F);border-radius:18px;padding:1.35rem 1.45rem;color:#fff;box-shadow:0 12px 26px rgba(4,108,78,.17);margin:.6rem 0 1.1rem}} .offset-panel *{{color:#fff}} .offset-label{{opacity:.8;font-size:.8rem;font-weight:700}} .offset-value{{font-size:2rem;font-weight:800;margin:.15rem 0}} .report-panel{{background:linear-gradient(115deg,#fff,#E3F8F0);border:1px solid #C7E9DE;border-radius:18px;padding:1.45rem;box-shadow:0 8px 22px rgba(4,108,78,.06);margin-bottom:1rem}}
    div.stButton>button,div.stDownloadButton>button{{background:var(--jade);color:#fff;border:0;border-radius:9px;font-weight:750;padding:.55rem 1rem}} div.stButton>button:hover,div.stDownloadButton>button:hover{{background:var(--deep);color:#fff;transform:translateY(-1px);box-shadow:0 5px 13px rgba(4,108,78,.22)}}
    [data-testid="stDataFrame"],[data-testid="stFileUploader"]{{background:#fff;border-radius:12px}} @media(max-width:760px){{.hero{{padding:1.4rem}}.detail-grid{{grid-template-columns:1fr}}.kpi{{min-height:auto;margin-bottom:.65rem}}}}
    </style>""", unsafe_allow_html=True)


@st.cache_data
def load_factors(): return pd.read_csv(DATA / "emission_factors.csv")


@st.cache_data
def load_projects(): return pd.read_csv(DATA / "carbon_projects.csv")


def set_data(usage: pd.DataFrame):
    st.session_state["usage"] = usage
    st.session_state["calculated"] = calculate_emissions(usage, load_factors())
    st.session_state["recommendations"] = generate_recommendations(st.session_state["calculated"])


def setup():
    initialize_database(DB_PATH)
    if "calculated" not in st.session_state: set_data(pd.read_csv(DATA / "sample_cloud_usage.csv"))
    if "implemented" not in st.session_state: st.session_state["implemented"] = set()


def section(label: str, title: str, copy: str = ""):
    st.markdown(f'<div class="section-label">{escape(label)}</div><h2>{escape(title)}</h2>', unsafe_allow_html=True)
    if copy: st.markdown(f'<div class="section-copy">{escape(copy)}</div>', unsafe_allow_html=True)


def metrics(summary):
    cards = [("◌", "Estimated emissions", f"{summary['total_tonnes']:.3f} tCO2e"), ("$", "Estimated cloud cost", f"${summary['total_cost']:,.2f}"), ("▣", "Top service", summary["top_service"]), ("⌖", "Top region", summary["top_region"])]
    for column, (icon, label, value) in zip(st.columns(4), cards):
        column.markdown(f'<div class="kpi"><div>{icon}</div><div class="kpi-label">{escape(label)}</div><div class="kpi-value">{escape(str(value))}</div></div>', unsafe_allow_html=True)


def chart_shell(fig):
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", font={"color": TEXT, "family": "Arial"}, margin={"l":18,"r":18,"t":58,"b":18}, title={"font":{"size":17,"color":TEXT}}, legend={"title":"","orientation":"h","y":-.18})
    fig.update_xaxes(gridcolor="#EDF4F1"); fig.update_yaxes(gridcolor="#EDF4F1")
    st.markdown('<div class="chart-shell">', unsafe_allow_html=True); st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False}); st.markdown('</div>', unsafe_allow_html=True)


def home():
    st.markdown('''<div class="hero"><div class="eyebrow">Sustainability analytics</div><div class="hero-title">Cloud carbon decisions,<br/>made actionable.</div><div class="hero-copy">Translate multi-cloud usage into clear emissions insights, practical reduction opportunities, and a transparent carbon-offset workflow.</div><div class="workflow"><span class="step">Upload</span><span class="arrow">→</span><span class="step">Measure</span><span class="arrow">→</span><span class="step">Reduce</span><span class="arrow">→</span><span class="step">Offset</span><span class="arrow">→</span><span class="step">Report</span></div></div>''', unsafe_allow_html=True)
    section("At a glance", "Your carbon footprint snapshot", "A quick overview of the currently loaded cloud-usage dataset."); metrics(summary_metrics(st.session_state["calculated"]))
    section("Method", "Transparent by design", "A simple, explainable calculation makes every result easy to understand.")
    st.latex(r"\text{Estimated emissions (kg CO2e)} = \text{Energy (kWh)} \times \text{Regional carbon intensity (kg CO2e/kWh)}")


def upload_data():
    section("Dataset", "Upload cloud usage data", "Bring your own CSV or explore the dashboard with the bundled AWS, Azure, and GCP sample records.")
    c1,c2=st.columns([1,2]); c1.download_button("Download sample CSV", (DATA/"sample_cloud_usage.csv").read_bytes(), "sample_cloud_usage.csv", "text/csv"); c2.markdown('<div class="notice"><strong>Required columns:</strong> month, provider, service, region, usage_hours, energy_kwh, cost_usd</div>', unsafe_allow_html=True)
    uploaded=st.file_uploader("Choose a cloud-usage CSV",type="csv")
    if uploaded:
        try:
            usage=pd.read_csv(uploaded); calculate_emissions(usage,load_factors()); set_data(usage); st.success("Usage data accepted. The dashboard and recommendations have been updated."); st.dataframe(usage,use_container_width=True,hide_index=True)
        except Exception as error: st.error(f"Could not use this CSV: {error}")
    if st.button("Restore bundled sample data"): set_data(pd.read_csv(DATA/"sample_cloud_usage.csv")); st.success("Sample data restored.")


def dashboard():
    section("Analytics", "Carbon dashboard", "Estimated emissions based on uploaded or bundled sample data."); data=st.session_state["calculated"]; metrics(summary_metrics(data))
    service,region,provider=aggregate(data,"service"),aggregate(data,"region"),aggregate(data,"provider"); monthly=data.groupby("month",as_index=False)["emissions_kg_co2e"].sum().sort_values("month")
    c1,c2=st.columns(2)
    with c1: chart_shell(px.bar(service,x="service",y="emissions_kg_co2e",color="service",color_discrete_sequence=COLORS,title="Estimated emissions by service",labels={"emissions_kg_co2e":"kg CO2e"}).update_traces(hovertemplate="%{x}<br><b>%{y:.2f} kg CO2e</b><extra></extra>"))
    with c2: chart_shell(px.pie(region,names="region",values="emissions_kg_co2e",color_discrete_sequence=COLORS,hole=.52,title="Estimated emissions by region").update_traces(textinfo="percent",hovertemplate="%{label}<br><b>%{value:.2f} kg CO2e</b><extra></extra>"))
    c3,c4=st.columns(2)
    with c3: chart_shell(px.bar(provider,x="provider",y="emissions_kg_co2e",color="provider",color_discrete_sequence=COLORS,title="Estimated emissions by provider",labels={"emissions_kg_co2e":"kg CO2e"}).update_traces(hovertemplate="%{x}<br><b>%{y:.2f} kg CO2e</b><extra></extra>"))
    with c4: chart_shell(px.line(monthly,x="month",y="emissions_kg_co2e",markers=True,line_shape="spline",color_discrete_sequence=[JADE],title="Monthly estimated-emissions trend",labels={"emissions_kg_co2e":"kg CO2e"}).update_traces(line={"width":4},marker={"size":9},hovertemplate="%{x}<br><b>%{y:.2f} kg CO2e</b><extra></extra>"))
    with st.expander("View calculation records"): st.dataframe(data,use_container_width=True,hide_index=True)


def recommendations_page():
    section("Optimise", "Reduction recommendations", "Explainable, rule-based suggestions that make the path from measurement to reduction clear."); recs=st.session_state["recommendations"]
    if recs.empty: st.success("No recommendations were generated from the current data."); return
    total=recs["estimated_savings_kg"].sum(); st.markdown(f'<div class="offset-panel"><div class="offset-label">POTENTIAL ESTIMATED SAVINGS</div><div class="offset-value">{total:.2f} kg CO2e</div><div>Across all current recommendations before implementation status is considered.</div></div>',unsafe_allow_html=True)
    for index,rec in recs.iterrows():
        key=str(index); implemented=key in st.session_state["implemented"]; priority="high" if rec["priority"]=="High" else "medium"; status='<span class="badge success">Implemented</span>' if implemented else f'<span class="badge {priority}">{escape(str(rec["priority"]))} priority</span>'
        st.markdown(f'''<div class="rec-card"><div class="card-title">{escape(str(rec["title"]))}</div>{status}<span class="badge neutral">{escape(str(rec["category"]))}</span><div class="card-copy">{escape(str(rec["reason"]))}</div><div class="detail-grid"><div class="detail"><div class="detail-label">Estimated savings</div><div class="detail-value">{float(rec["estimated_savings_kg"]):.2f} kg CO2e</div></div><div class="detail"><div class="detail-label">Implementation effort</div><div class="detail-value">{escape(str(rec["effort"]))}</div></div><div class="detail"><div class="detail-label">Cost effect</div><div class="detail-value">{escape(str(rec["cost_effect"]))}</div></div></div></div>''',unsafe_allow_html=True)
        if not implemented and st.button("Mark as implemented",key=f"implement_{index}"): st.session_state["implemented"].add(key); st.rerun()


def marketplace():
    section("Offset", "Carbon-credit marketplace", "Match residual emissions with carbon-credit projects from the marketplace.")
    summary=summary_metrics(st.session_state["calculated"]); indexes=[int(i) for i in st.session_state["implemented"]]; savings=st.session_state["recommendations"].iloc[indexes]["estimated_savings_kg"].sum() if indexes else 0; residual=max(0,(summary["total_kg"]-savings)/1000)
    st.markdown(f'<div class="offset-panel"><div class="offset-label">ESTIMATED RESIDUAL EMISSIONS</div><div class="offset-value">{residual:.3f} tCO2e</div><div>Total estimated footprint minus savings from implemented recommendations.</div></div>',unsafe_allow_html=True)
    projects=load_projects(); selected_name=st.selectbox("Choose a sample project",projects["name"]); project=projects.loc[projects["name"]==selected_name].iloc[0].to_dict()
    for column,(_,item) in zip(st.columns(len(projects)),projects.iterrows()):
        css="project-card selected" if item["name"]==selected_name else "project-card"
        column.markdown(f'''<div class="{css}"><div class="card-title">{escape(str(item["name"]))}</div><span class="badge neutral">{escape(str(item["type"]))}</span><div class="card-copy">{escape(str(item["description"]))}</div><div class="detail"><div class="detail-label">Location & standard</div><div class="detail-value">{escape(str(item["country"]))} · {escape(str(item["standard"]))}</div></div><div class="detail" style="margin-top:.5rem"><div class="detail-label">Price & availability</div><div class="detail-value">${float(item["price_per_tonne"]):.2f}/t · {int(item["available_credits"])} credits</div></div></div>''',unsafe_allow_html=True)
    c1,c2=st.columns(2); credits=c1.number_input("Credits to offset (1 credit = 1 tCO2e)",min_value=.001,value=max(.001,round(residual,3)),step=.001); total=credits*float(project["price_per_tonne"]); c2.markdown(f'<div class="rec-card"><div class="detail-label">CHECKOUT TOTAL</div><div class="kpi-value">${total:,.2f}</div><div class="card-copy">{credits:.3f} credits at ${float(project["price_per_tonne"]):.2f} per tCO2e.</div></div>',unsafe_allow_html=True)
    if st.button("Complete offset"): st.session_state["latest_transaction"]=record_transaction(DB_PATH,project,credits); st.success(f"Offset recorded. Certificate ID: {st.session_state['latest_transaction']['certificate_id']}")
    if st.session_state.get("latest_transaction"):
        tx=st.session_state["latest_transaction"]; st.download_button("Download offset certificate",build_certificate(tx),f"{tx['certificate_id']}.pdf","application/pdf")
    transactions=get_transactions(DB_PATH)
    if transactions: section("Ledger","Transaction history"); st.dataframe(pd.DataFrame(transactions),use_container_width=True,hide_index=True)


def reports_page():
    section("Report", "Ready to present your findings", "Generate a shareable report with the footprint summary, recommendations, methodology, and transaction history.")
    st.markdown('<div class="report-panel"><div class="card-title">Sustainability report</div><div class="card-copy">Download a polished report with the current footprint summary, suggested reductions, offsets, assumptions, and methodology.</div></div>',unsafe_allow_html=True)
    report=build_sustainability_report(summary_metrics(st.session_state["calculated"]),st.session_state["recommendations"],get_transactions(DB_PATH)); st.download_button("Download sustainability report",report,"cloud_carbon_sustainability_report.pdf","application/pdf")


setup(); inject_styles()
st.markdown('<div class="top-brand"><div><div class="brand-kicker">Sustainability analytics</div><div class="brand-title">🌿 Cloud Carbon Marketplace</div></div><div class="brand-subtitle">Measure • Reduce • Offset</div></div>',unsafe_allow_html=True)
page=st.radio("Navigate",["Home","Upload Data","Carbon Dashboard","Recommendations","Carbon Credit Marketplace","Reports"],horizontal=True,label_visibility="collapsed")
{"Home":home,"Upload Data":upload_data,"Carbon Dashboard":dashboard,"Recommendations":recommendations_page,"Carbon Credit Marketplace":marketplace,"Reports":reports_page}[page]()
