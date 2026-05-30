import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import io
import random

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ColdSentinel · Breach Intelligence",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=Inter:wght@300;400;500&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #e8e8e8;
}
.stApp {
    background: #080c10;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,180,255,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 90% 80%, rgba(255,60,60,0.06) 0%, transparent 50%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0b1118 !important;
    border-right: 1px solid rgba(0,180,255,0.12);
}
[data-testid="stSidebar"] * { color: #c8d8e8 !important; }

/* ── Headings ── */
h1,h2,h3 { font-family: 'Syne', sans-serif !important; }

/* ── Cards ── */
.sentinel-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(0,180,255,0.15);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    backdrop-filter: blur(8px);
}
.breach-card {
    background: rgba(255,60,60,0.06);
    border: 1px solid rgba(255,60,60,0.3);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.ok-card {
    background: rgba(0,220,120,0.05);
    border: 1px solid rgba(0,220,120,0.25);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
}

/* ── Metric tiles ── */
.metric-tile {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(0,180,255,0.12);
    border-radius: 10px;
    padding: 18px 16px;
    text-align: center;
}
.metric-value {
    font-family: 'DM Mono', monospace;
    font-size: 2rem;
    font-weight: 500;
    line-height: 1;
    margin-bottom: 4px;
}
.metric-label {
    font-size: 0.72rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #6a8a9a;
}
.metric-danger  { color: #ff4444; }
.metric-warning { color: #ffaa00; }
.metric-ok      { color: #00dc78; }
.metric-info    { color: #00b4ff; }

/* ── Severity badges ── */
.badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: .06em;
    text-transform: uppercase;
    padding: 2px 10px;
    border-radius: 4px;
}
.badge-critical { background: rgba(255,40,40,0.2);  color: #ff6060; border: 1px solid rgba(255,40,40,0.4); }
.badge-high     { background: rgba(255,140,0,0.2);  color: #ffaa40; border: 1px solid rgba(255,140,0,0.4); }
.badge-medium   { background: rgba(255,210,0,0.2);  color: #ffd040; border: 1px solid rgba(255,210,0,0.4); }
.badge-ok       { background: rgba(0,220,120,0.15); color: #00dc78; border: 1px solid rgba(0,220,120,0.3); }

/* ── Logo / header ── */
.sentinel-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -.02em;
}
.sentinel-logo span { color: #00b4ff; }

/* ── Section divider ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: #00b4ff;
    opacity: 0.7;
    margin-bottom: 10px;
}

/* ── Timeline row ── */
.timeline-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 0.85rem;
}
.timeline-time {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #4a6a7a;
    min-width: 140px;
}

/* ── Report box ── */
.report-box {
    background: #0a0f14;
    border: 1px solid rgba(0,180,255,0.2);
    border-radius: 10px;
    padding: 24px 28px;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.8;
    color: #b8d0e0;
    white-space: pre-wrap;
    max-height: 420px;
    overflow-y: auto;
}

/* ── Button overrides ── */
.stButton>button {
    background: linear-gradient(135deg, #0062aa, #0088dd) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: .03em !important;
    padding: 0.5rem 1.4rem !important;
    transition: opacity .2s !important;
}
.stButton>button:hover { opacity: .85 !important; }

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    border: 1.5px dashed rgba(0,180,255,0.3) !important;
    border-radius: 10px !important;
    background: rgba(0,180,255,0.03) !important;
}

/* ── Tab strip ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(0,180,255,0.15) !important;
    gap: 4px;
}
[data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #5a7a8a !important;
    background: transparent !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 8px 18px !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: #00b4ff !important;
    border-bottom: 2px solid #00b4ff !important;
    background: rgba(0,180,255,0.06) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,180,255,0.3); border-radius: 4px; }

/* ── Plotly bg fix ── */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  HELPERS / MOCK PIPELINE
# ═══════════════════════════════════════════════════════════════

PHARMA_LIMITS = {"min_temp": 2.0,  "max_temp": 8.0,  "label": "Pharma (2–8 °C)"}
FOOD_LIMITS   = {"min_temp": -2.0, "max_temp": 5.0,  "label": "Food (-2–5 °C)"}

SEVERITY_MAP = {
    "critical": ("🔴", "badge-critical", "#ff4444"),
    "high":     ("🟠", "badge-high",     "#ffaa00"),
    "medium":   ("🟡", "badge-medium",   "#ffd040"),
    "ok":       ("🟢", "badge-ok",       "#00dc78"),
}

def classify_severity(delta: float) -> str:
    if delta >= 5:   return "critical"
    if delta >= 3:   return "high"
    if delta > 0:    return "medium"
    return "ok"

def detect_excursions(df: pd.DataFrame, limits: dict) -> list[dict]:
    excursions = []
    in_breach = False
    start_idx = None
    for i, row in df.iterrows():
        temp = row["temperature_celsius"]
        breach = temp < limits["min_temp"] or temp > limits["max_temp"]
        if breach and not in_breach:
            in_breach = True
            start_idx = i
        elif not breach and in_breach:
            in_breach = False
            end_idx = i - 1
            sub = df.loc[start_idx:end_idx]
            max_t = sub["temperature_celsius"].max()
            min_t = sub["temperature_celsius"].min()
            delta = max(abs(max_t - limits["max_temp"]), abs(min_t - limits["min_temp"]))
            duration_min = len(sub) * 5
            excursions.append({
                "start": sub.iloc[0]["timestamp"],
                "end":   sub.iloc[-1]["timestamp"],
                "duration_min": duration_min,
                "max_temp": round(max_t, 2),
                "min_temp": round(min_t, 2),
                "delta":    round(delta, 2),
                "severity": classify_severity(delta),
                "sensor_id": sub.iloc[0].get("sensor_id", "SENS-001"),
            })
    return excursions

def generate_sample_data(scenario: str, n: int = 200) -> pd.DataFrame:
    import numpy as np
    np.random.seed(42)
    times = pd.date_range("2024-06-01 08:00", periods=n, freq="5min")
    if scenario == "Pharmaceutical":
        base, noise = 5.0, 0.4
        breach_zones = [(60, 80, 11.5), (140, 155, -1.2)]
    else:
        base, noise = 2.0, 0.5
        breach_zones = [(50, 70, 8.0), (130, 148, -4.5)]
    temps = np.random.normal(base, noise, n)
    for s, e, spike in breach_zones:
        temps[s:e] = np.random.normal(spike, 0.3, e - s)
    df = pd.DataFrame({
        "timestamp":          times,
        "temperature_celsius": np.round(temps, 2),
        "humidity_percent":   np.round(np.random.normal(55, 5, n), 1),
        "sensor_id":          [f"SENS-{random.choice(['A01','B02','C03'])}" for _ in range(n)],
        "location":           [random.choice(["Mumbai WH", "Delhi Hub", "Pune ColdStore"]) for _ in range(n)],
        "batch_number":       [f"BT-{random.randint(1000,9999)}" for _ in range(n)],
    })
    return df

def build_temp_chart(df: pd.DataFrame, limits: dict, excursions: list) -> go.Figure:
    fig = go.Figure()
    fig.add_hrect(y0=limits["min_temp"], y1=limits["max_temp"],
                  fillcolor="rgba(0,220,120,0.06)", line_width=0, annotation_text="Safe zone",
                  annotation_font_color="#00dc78", annotation_font_size=11)
    fig.add_hline(y=limits["max_temp"], line_dash="dot", line_color="rgba(0,220,120,0.4)", line_width=1)
    fig.add_hline(y=limits["min_temp"], line_dash="dot", line_color="rgba(0,220,120,0.4)", line_width=1)
    for ex in excursions:
        fig.add_vrect(x0=ex["start"], x1=ex["end"],
                      fillcolor=SEVERITY_MAP[ex["severity"]][2],
                      opacity=0.10, line_width=0)
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["temperature_celsius"],
        mode="lines", name="Temperature",
        line=dict(color="#00b4ff", width=1.6),
        hovertemplate="<b>%{y:.1f}°C</b><br>%{x}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
        xaxis=dict(showgrid=False, color="#4a6a7a", tickfont_size=11),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#4a6a7a", tickfont_size=11, title="°C"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8ab0c0"),
        font=dict(family="DM Mono, monospace"),
        hovermode="x unified",
    )
    return fig

def build_humidity_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["humidity_percent"],
        mode="lines", fill="tozeroy",
        line=dict(color="#9b6dff", width=1.4),
        fillcolor="rgba(155,109,255,0.07)",
        hovertemplate="<b>%{y:.1f}%</b><br>%{x}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=180,
        xaxis=dict(showgrid=False, color="#4a6a7a", tickfont_size=11),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#4a6a7a", tickfont_size=11, title="%"),
        font=dict(family="DM Mono, monospace"),
    )
    return fig

def build_severity_pie(excursions: list) -> go.Figure:
    if not excursions:
        return None
    counts = {}
    for ex in excursions:
        counts[ex["severity"]] = counts.get(ex["severity"], 0) + 1
    labels = list(counts.keys())
    values = list(counts.values())
    colors = [SEVERITY_MAP[l][2] for l in labels]
    fig = go.Figure(go.Pie(
        labels=[l.upper() for l in labels], values=values,
        marker_colors=colors, hole=0.65,
        textfont_size=11, textfont_family="DM Mono, monospace",
        hovertemplate="<b>%{label}</b>: %{value} breach(es)<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0), height=200,
        legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8ab0c0", font_size=11),
        showlegend=True,
    )
    return fig

def render_fda_report(df: pd.DataFrame, excursions: list, limits: dict, scenario: str) -> str:
    total_readings = len(df)
    breach_count   = len(excursions)
    total_breach_min = sum(e["duration_min"] for e in excursions)
    worst = max(excursions, key=lambda x: x["delta"]) if excursions else None
    report_date = datetime.now().strftime("%B %d, %Y")
    lines = [
        "═" * 64,
        "  COLD CHAIN DEVIATION REPORT",
        f"  FDA 21 CFR Part 211 / WHO GDP Compliant",
        "═" * 64,
        "",
        f"  Report Date     : {report_date}",
        f"  Report ID       : CCR-{datetime.now().strftime('%Y%m%d-%H%M')}",
        f"  Scenario        : {scenario} Cold Chain",
        f"  Temperature Std : {limits['label']}",
        "",
        "─" * 64,
        "  SECTION 1 — MONITORING SUMMARY",
        "─" * 64,
        f"  Total Readings     : {total_readings}",
        f"  Monitoring Period  : {df['timestamp'].min().strftime('%Y-%m-%d %H:%M')} – {df['timestamp'].max().strftime('%Y-%m-%d %H:%M')}",
        f"  Sensors Active     : {df['sensor_id'].nunique()}",
        f"  Locations Covered  : {df['location'].nunique()}",
        f"  Avg Temperature    : {df['temperature_celsius'].mean():.2f} °C",
        f"  Min Temperature    : {df['temperature_celsius'].min():.2f} °C",
        f"  Max Temperature    : {df['temperature_celsius'].max():.2f} °C",
        "",
        "─" * 64,
        "  SECTION 2 — EXCURSION EVENTS",
        "─" * 64,
        f"  Total Breaches     : {breach_count}",
        f"  Total Breach Time  : {total_breach_min} minutes",
    ]
    if worst:
        lines += [
            f"  Worst Deviation    : {worst['delta']:.2f} °C above/below limit",
            f"  Worst Severity     : {worst['severity'].upper()}",
        ]
    lines += [""]
    for i, ex in enumerate(excursions, 1):
        lines += [
            f"  BREACH #{i}",
            f"    Start         : {ex['start']}",
            f"    End           : {ex['end']}",
            f"    Duration      : {ex['duration_min']} minutes",
            f"    Peak Temp     : {ex['max_temp']} °C",
            f"    Min Temp      : {ex['min_temp']} °C",
            f"    Deviation     : {ex['delta']} °C",
            f"    Severity      : {ex['severity'].upper()}",
            f"    Sensor        : {ex['sensor_id']}",
            "",
        ]
    lines += [
        "─" * 64,
        "  SECTION 3 — REGULATORY COMPLIANCE",
        "─" * 64,
        "  FDA 21 CFR 211.68  : Temperature monitoring logged continuously.",
        "  WHO GDP Chapter 7  : Cold chain records maintained per guidelines.",
        "  ICH Q1A(R2)        : Stability excursion documentation completed.",
        "",
        "─" * 64,
        "  SECTION 4 — RECOMMENDED ACTIONS",
        "─" * 64,
    ]
    if breach_count == 0:
        lines += ["  ✓ No excursions detected. Shipment compliant.", ""]
    else:
        lines += [
            "  1. Quarantine affected batches pending stability review.",
            "  2. Notify QA team and batch release officer immediately.",
            "  3. Initiate CAPA (Corrective and Preventive Action) procedure.",
            "  4. Contact product manufacturer for stability assessment.",
            "  5. Document all findings in the site Quality Management System.",
            "",
        ]
    lines += [
        "─" * 64,
        "  Prepared by  : ColdSentinel GenAI System v1.0",
        f"  Timestamp    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "  Disclaimer   : This report is AI-generated. Human QA review required.",
        "═" * 64,
    ]
    return "\n".join(lines)

def render_insurance_claim(df: pd.DataFrame, excursions: list, scenario: str) -> str:
    total_breach_min = sum(e["duration_min"] for e in excursions)
    estimated_loss   = len(excursions) * 45000
    report_date = datetime.now().strftime("%B %d, %Y")
    lines = [
        "═" * 64,
        "  INSURANCE CLAIM LETTER",
        "  Cold Chain Temperature Excursion — Evidence Annexure",
        "═" * 64,
        "",
        f"  Date           : {report_date}",
        f"  Claim Ref No.  : CLM-{datetime.now().strftime('%Y%m%d%H%M')}",
        f"  Policy Type    : Pharmaceutical / Food Cold Chain Cargo",
        "",
        "  TO:",
        "  The Underwriter / Claims Manager",
        "  [Insurance Company Name]",
        "  [Address]",
        "",
        "  SUBJECT: Insurance Claim — Cold Chain Temperature Excursion",
        "           Estimated Loss: ₹{:,}".format(estimated_loss),
        "",
        "─" * 64,
        "  SECTION A — INCIDENT DETAILS",
        "─" * 64,
        f"  Incident Type  : Temperature Excursion During Cold Chain Transit",
        f"  Scenario       : {scenario}",
        f"  No. of Breaches: {len(excursions)}",
        f"  Total Duration : {total_breach_min} minutes of non-compliant exposure",
        f"  Date Range     : {df['timestamp'].min().strftime('%Y-%m-%d')} – {df['timestamp'].max().strftime('%Y-%m-%d')}",
        "",
        "─" * 64,
        "  SECTION B — BREACH EVIDENCE",
        "─" * 64,
    ]
    for i, ex in enumerate(excursions, 1):
        lines += [
            f"  Incident {i}:",
            f"    Time Window   : {ex['start']} → {ex['end']}",
            f"    Exposure Time : {ex['duration_min']} min",
            f"    Peak Deviation: {ex['delta']} °C beyond safe limit",
            f"    Severity Class: {ex['severity'].upper()}",
            f"    Sensor ID     : {ex['sensor_id']}",
            "",
        ]
    lines += [
        "─" * 64,
        "  SECTION C — FINANCIAL IMPACT",
        "─" * 64,
        f"  Affected Batches      : {df['batch_number'].nunique()} unique batch numbers",
        f"  Estimated Product Loss: ₹{estimated_loss:,}",
        "  Basis of Estimate     : Industry standard spoilage rates per breach event.",
        "",
        "─" * 64,
        "  SECTION D — SUPPORTING DOCUMENTS (ANNEXED)",
        "─" * 64,
        "  Annex 1 : FDA/WHO Compliant Cold Chain Deviation Report (CCR)",
        "  Annex 2 : Temperature sensor log CSV (raw data)",
        "  Annex 3 : Plotly temperature excursion chart (PNG export)",
        "  Annex 4 : Batch traceability records",
        "",
        "─" * 64,
        "  DECLARATION",
        "─" * 64,
        "  We hereby certify that the information provided is accurate and",
        "  supported by continuous IoT sensor records. We request prompt",
        "  processing of this claim as per policy terms.",
        "",
        "  Authorized Signatory : _______________________",
        "  Designation          : Quality Assurance Manager",
        f"  Date                 : {report_date}",
        "",
        "  Generated by ColdSentinel GenAI System · AI-assisted · QA review required.",
        "═" * 64,
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='padding:8px 0 20px'>
      <div class='sentinel-logo'>❄ Cold<span>Sentinel</span></div>
      <div style='font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;
                  color:#4a7a8a;margin-top:4px;font-family:DM Mono,monospace'>
        Breach Intelligence v1.0
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='section-label'>Configuration</div>", unsafe_allow_html=True)

    scenario = st.selectbox("🧪 Cold Chain Type", ["Pharmaceutical", "Food"])
    limits   = PHARMA_LIMITS if scenario == "Pharmaceutical" else FOOD_LIMITS

    st.markdown(f"""
    <div class='sentinel-card' style='margin-top:8px;padding:14px 16px'>
      <div style='font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;
                  color:#4a7a8a;margin-bottom:8px;font-family:DM Mono,monospace'>
        Safe Range
      </div>
      <div style='font-family:DM Mono,monospace;font-size:1.1rem;color:#00dc78'>
        {limits['min_temp']} °C → {limits['max_temp']} °C
      </div>
      <div style='font-size:.75rem;color:#5a8a9a;margin-top:4px'>{limits['label']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-label' style='margin-top:16px'>Data Source</div>", unsafe_allow_html=True)
    data_source = st.radio("", ["Use Sample Data", "Upload CSV"], label_visibility="collapsed")

    uploaded_file = None
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload sensor log CSV", type=["csv", "json"],
                                         label_visibility="collapsed")
        st.markdown("""
        <div style='font-size:.72rem;color:#4a6a7a;margin-top:6px;font-family:DM Mono,monospace'>
          Required columns:<br>
          timestamp, temperature_celsius,<br>
          sensor_id, location, batch_number
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    run_analysis = st.button("⚡  Run Analysis", use_container_width=True)

    st.markdown("""
    <div style='margin-top:32px;font-size:.7rem;color:#2a4a5a;
                font-family:DM Mono,monospace;line-height:1.8'>
      FDA 21 CFR Part 211<br>
      WHO GDP Guidelines<br>
      ICH Q1A(R2) Compliant
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ═══════════════════════════════════════════════════════════════

# ── Header ──
st.markdown("""
<div style='padding:8px 0 24px'>
  <div style='font-family:Syne,sans-serif;font-size:2rem;font-weight:800;
              color:#fff;letter-spacing:-.02em'>
    Cold Chain Breach Alert
    <span style='color:#00b4ff'>&</span> Insurance Claim Assistant
  </div>
  <div style='font-size:.85rem;color:#4a7a8a;margin-top:4px;font-family:DM Mono,monospace'>
    GenAI · IoT Sensor Ingestion · FDA/WHO Compliance · Automated Claim Drafting
  </div>
</div>
""", unsafe_allow_html=True)

# ── Load data ──
df = None
excursions = []

if run_analysis or "df" in st.session_state:
    if run_analysis:
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".json"):
                    raw = json.load(uploaded_file)
                    df  = pd.DataFrame(raw)
                else:
                    df = pd.read_csv(uploaded_file)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.sort_values("timestamp").reset_index(drop=True)
            except Exception as e:
                st.error(f"❌ File parse error: {e}")
                df = None
        else:
            df = generate_sample_data(scenario)

        if df is not None:
            excursions = detect_excursions(df, limits)
            st.session_state["df"]          = df
            st.session_state["excursions"]  = excursions
            st.session_state["scenario"]    = scenario
            st.session_state["limits"]      = limits
    else:
        df         = st.session_state.get("df")
        excursions = st.session_state.get("excursions", [])
        scenario   = st.session_state.get("scenario", scenario)
        limits     = st.session_state.get("limits", limits)

# ── Placeholder when not yet run ──
if df is None:
    st.markdown("""
    <div style='text-align:center;padding:80px 20px'>
      <div style='font-size:3.5rem;margin-bottom:16px'>🧊</div>
      <div style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:700;
                  color:#fff;margin-bottom:8px'>
        Ready to Analyze
      </div>
      <div style='font-size:.9rem;color:#4a7a8a;max-width:400px;margin:0 auto'>
        Select a cold chain type, choose your data source, and click
        <strong style='color:#00b4ff'>Run Analysis</strong> to begin.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════
#  METRIC TILES
# ═══════════════════════════════════════════════════════════════

total_breach_min = sum(e["duration_min"] for e in excursions)
critical_count   = sum(1 for e in excursions if e["severity"] == "critical")
worst_delta      = max((e["delta"] for e in excursions), default=0)

c1, c2, c3, c4, c5 = st.columns(5)
tiles = [
    (c1, str(len(df)),         "Sensor Readings",    "metric-info"),
    (c2, str(len(excursions)), "Breach Events",      "metric-danger" if excursions else "metric-ok"),
    (c3, str(critical_count),  "Critical Breaches",  "metric-danger" if critical_count else "metric-ok"),
    (c4, f"{total_breach_min}m","Total Breach Time", "metric-warning" if total_breach_min else "metric-ok"),
    (c5, f"{worst_delta:.1f}°","Worst Deviation",    "metric-danger" if worst_delta >= 5 else "metric-warning" if worst_delta > 0 else "metric-ok"),
]
for col, val, label, cls in tiles:
    with col:
        st.markdown(f"""
        <div class='metric-tile'>
          <div class='metric-value {cls}'>{val}</div>
          <div class='metric-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "📈  Live Monitor",
    "🚨  Breach Events",
    "📋  FDA / WHO Report",
    "📄  Insurance Claim",
])

# ─── TAB 1 — Live Monitor ────────────────────────────────────
with tab1:
    st.markdown("<div class='section-label'>Temperature Timeline</div>", unsafe_allow_html=True)
    st.plotly_chart(build_temp_chart(df, limits, excursions), use_container_width=True)

    col_h, col_p = st.columns([2, 1])
    with col_h:
        st.markdown("<div class='section-label' style='margin-top:8px'>Humidity %</div>", unsafe_allow_html=True)
        st.plotly_chart(build_humidity_chart(df), use_container_width=True)
    with col_p:
        st.markdown("<div class='section-label' style='margin-top:8px'>Breach Severity Mix</div>", unsafe_allow_html=True)
        pie = build_severity_pie(excursions)
        if pie:
            st.plotly_chart(pie, use_container_width=True)
        else:
            st.markdown("""
            <div class='ok-card' style='text-align:center;margin-top:20px'>
              <div style='font-size:1.8rem'>✅</div>
              <div style='font-size:.9rem;color:#00dc78;font-family:DM Mono,monospace'>
                No breaches detected
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-label' style='margin-top:12px'>Raw Sensor Log</div>", unsafe_allow_html=True)
    show_n = st.slider("Rows to preview", 10, min(200, len(df)), 30, key="raw_rows")
    st.dataframe(
        df.head(show_n).style.background_gradient(subset=["temperature_celsius"], cmap="RdYlGn_r"),
        use_container_width=True, height=280,
    )

    csv_bytes = df.to_csv(index=False).encode()
    st.download_button("⬇ Download CSV", csv_bytes, "sensor_log.csv", "text/csv",
                       use_container_width=True)

# ─── TAB 2 — Breach Events ───────────────────────────────────
with tab2:
    if not excursions:
        st.markdown("""
        <div class='ok-card' style='text-align:center;padding:40px'>
          <div style='font-size:2.5rem'>✅</div>
          <div style='font-size:1.1rem;color:#00dc78;font-family:Syne,sans-serif;font-weight:700;margin-top:8px'>
            All Clear — No Excursions Detected
          </div>
          <div style='font-size:.85rem;color:#4a8a6a;margin-top:6px'>
            Temperature maintained within safe limits throughout the shipment.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='section-label'>{len(excursions)} Excursion Event(s) Found</div>",
                    unsafe_allow_html=True)
        for i, ex in enumerate(excursions, 1):
            icon, badge_cls, color = SEVERITY_MAP[ex["severity"]]
            st.markdown(f"""
            <div class='breach-card'>
              <div style='display:flex;align-items:center;gap:12px;margin-bottom:10px'>
                <span style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#fff'>
                  Breach #{i}
                </span>
                <span class='badge {badge_cls}'>{ex['severity'].upper()}</span>
              </div>
              <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:12px;
                          font-family:DM Mono,monospace;font-size:.8rem;color:#8ab0c0'>
                <div><div style='color:#4a6a7a;font-size:.68rem;letter-spacing:.06em;
                                 text-transform:uppercase;margin-bottom:2px'>Start</div>
                     {ex['start']}</div>
                <div><div style='color:#4a6a7a;font-size:.68rem;letter-spacing:.06em;
                                 text-transform:uppercase;margin-bottom:2px'>End</div>
                     {ex['end']}</div>
                <div><div style='color:#4a6a7a;font-size:.68rem;letter-spacing:.06em;
                                 text-transform:uppercase;margin-bottom:2px'>Duration</div>
                     {ex['duration_min']} min</div>
                <div><div style='color:#4a6a7a;font-size:.68rem;letter-spacing:.06em;
                                 text-transform:uppercase;margin-bottom:2px'>Peak Temp</div>
                     <span style='color:{color}'>{ex['max_temp']} °C</span></div>
                <div><div style='color:#4a6a7a;font-size:.68rem;letter-spacing:.06em;
                                 text-transform:uppercase;margin-bottom:2px'>Deviation</div>
                     <span style='color:{color}'>+{ex['delta']} °C</span></div>
                <div><div style='color:#4a6a7a;font-size:.68rem;letter-spacing:.06em;
                                 text-transform:uppercase;margin-bottom:2px'>Sensor</div>
                     {ex['sensor_id']}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ─── TAB 3 — FDA / WHO Report ────────────────────────────────
with tab3:
    fda_report = render_fda_report(df, excursions, limits, scenario)
    st.markdown("<div class='section-label'>FDA / WHO Compliant Deviation Report</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='report-box'>{fda_report}</div>", unsafe_allow_html=True)
    st.download_button("⬇ Download Report (.txt)", fda_report.encode(),
                       f"FDA_WHO_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                       "text/plain", use_container_width=True)

# ─── TAB 4 — Insurance Claim ─────────────────────────────────
with tab4:
    ins_claim = render_insurance_claim(df, excursions, scenario)
    st.markdown("<div class='section-label'>Insurance Claim Letter with Evidence Annexure</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='report-box'>{ins_claim}</div>", unsafe_allow_html=True)

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button("⬇ Download Claim (.txt)", ins_claim.encode(),
                           f"Insurance_Claim_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                           "text/plain", use_container_width=True)
    with col_dl2:
        combined = fda_report + "\n\n" + "=" * 64 + "\n\n" + ins_claim
        st.download_button("⬇ Download Full Package", combined.encode(),
                           f"ColdSentinel_Full_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                           "text/plain", use_container_width=True)