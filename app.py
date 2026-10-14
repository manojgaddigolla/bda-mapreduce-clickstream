import streamlit as st
import pandas as pd
import os
import subprocess
import altair as alt
from datetime import datetime

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="MapReduce Clickstream Analysis",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Metric card styling */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
    border: 1px solid rgba(99, 120, 255, 0.25);
    border-radius: 14px;
    padding: 1rem 1.25rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
[data-testid="metric-container"] label {
    font-size: 0.78rem !important;
    color: #8892b0 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #e2e8f0 !important;
}

/* Header gradient */
.hero-header {
    background: linear-gradient(135deg, #1a1f35 0%, #0d1526 100%);
    border: 1px solid rgba(99,120,255,0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
}
.hero-header h1 { color: #e2e8f0; font-weight: 700; margin: 0 0 0.5rem 0; font-size: 1.8rem; }
.hero-header p  { color: #8892b0; margin: 0; font-size: 0.95rem; }
.badge {
    display: inline-block;
    background: rgba(99,120,255,0.15);
    border: 1px solid rgba(99,120,255,0.4);
    color: #7c8fff;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    margin-right: 0.4rem;
    letter-spacing: 0.04em;
}

/* Section card */
.section-card {
    background: linear-gradient(135deg, #1e2130 0%, #1a1d2e 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Tab styling */
[data-baseweb="tab-list"] {
    background: #12151f;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
[data-baseweb="tab"] {
    border-radius: 9px !important;
    color: #8892b0 !important;
    font-weight: 500;
}
[aria-selected="true"] {
    background: linear-gradient(135deg, #3b4cca, #5a4fcf) !important;
    color: #fff !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d1118;
    border-right: 1px solid rgba(255,255,255,0.06);
}
.sidebar-stat {
    background: rgba(99,120,255,0.08);
    border: 1px solid rgba(99,120,255,0.2);
    border-radius: 10px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
}
.sidebar-stat span { color: #7c8fff; font-weight: 600; float: right; }

/* Success / error status chips */
.chip-ok    { background:#0d3321; border:1px solid #2ecc71; color:#2ecc71; border-radius:20px; padding:2px 10px; font-size:0.75rem; }
.chip-warn  { background:#322b0d; border:1px solid #f39c12; color:#f39c12; border-radius:20px; padding:2px 10px; font-size:0.75rem; }
.chip-err   { background:#33100d; border:1px solid #e74c3c; color:#e74c3c; border-radius:20px; padding:2px 10px; font-size:0.75rem; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────

OUTPUT_DIR = "output"
DATA_FILE  = "clickstream.csv"

# ── Data Loading (100% Dynamic — reads from MapReduce output files) ───────────

@st.cache_data
def load_mapreduce_outputs():
    """Reads all three MapReduce output files and returns DataFrames."""
    pages_f  = os.path.join(OUTPUT_DIR, "output_pages.txt")
    status_f = os.path.join(OUTPUT_DIR, "output_status.txt")
    users_f  = os.path.join(OUTPUT_DIR, "output_users.txt")

    if not all(os.path.exists(f) for f in [pages_f, status_f, users_f]):
        return None, None, None

    df_pages  = pd.read_csv(pages_f,  sep="\t", names=["URL", "Visits"], comment="#")
    df_status = pd.read_csv(status_f, sep="\t", names=["Status_Code", "Count"], dtype={"Status_Code": str}, comment="#")
    df_users  = pd.read_csv(users_f,  sep="\t", names=["User_ID", "Requests"], comment="#")

    df_pages  = df_pages.sort_values("Visits",   ascending=False).reset_index(drop=True)
    df_users  = df_users.sort_values("Requests", ascending=False).reset_index(drop=True)

    return df_pages, df_status, df_users

def get_log_record_count():
    if not os.path.exists(DATA_FILE):
        return 0
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return max(0, sum(1 for _ in f) - 1)  # subtract header

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🗂️ MapReduce Pipeline")
    st.caption("Big Data Analytics Lab Project")
    st.divider()

    if st.button("▶  Run MapReduce Pipeline", use_container_width=True, type="primary"):
        with st.spinner("Executing Map → Shuffle/Sort → Reduce …"):
            result = subprocess.run(["python", "run_analysis.py"],
                                    capture_output=True, text=True)
        if result.returncode == 0:
            st.cache_data.clear()
            st.success("Pipeline completed!")
            st.rerun()
        else:
            st.error("Pipeline failed. Check terminal.")

    st.divider()
    st.markdown("#### Dataset Stats")

    rec_count = get_log_record_count()
    st.markdown(f"""
    <div class="sidebar-stat">Records processed <span>{rec_count:,}</span></div>
    <div class="sidebar-stat">MapReduce Jobs <span>3</span></div>
    <div class="sidebar-stat">Unique URLs <span>9</span></div>
    <div class="sidebar-stat">Unique Users <span>50</span></div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Paradigm")
    st.markdown("""
    - **Pattern:** Hadoop Streaming  
    - **Phases:** Map → Shuffle/Sort → Reduce  
    - **Input:** `clickstream.csv`  
    - **Output:** `output/*.txt`
    """)
    st.caption(f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}")

# ── Load Data ─────────────────────────────────────────────────────────────────

df_pages, df_status, df_users = load_mapreduce_outputs()

if df_pages is None:
    st.warning("⚠️ No MapReduce output found. Run the pipeline first.")
    if st.button("▶ Run Pipeline Now", type="primary"):
        subprocess.run(["python", "run_analysis.py"], check=True)
        st.cache_data.clear()
        st.rerun()
    st.stop()

# ── Compute KPIs dynamically from output files ────────────────────────────────

total_requests = int(df_status["Count"].sum())
total_200      = int(df_status.loc[df_status["Status_Code"] == "200", "Count"].sum())
total_404      = int(df_status.loc[df_status["Status_Code"] == "404", "Count"].sum())
total_500      = int(df_status.loc[df_status["Status_Code"] == "500", "Count"].sum())
total_errors   = total_404 + total_500
success_rate   = (total_200 / total_requests * 100) if total_requests else 0
error_rate     = (total_errors / total_requests * 100) if total_requests else 0
top_page       = df_pages.iloc[0]["URL"]
top_user       = df_users.iloc[0]["User_ID"]
most_visited_count = int(df_pages.iloc[0]["Visits"])

# ── Hero Header ───────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="hero-header">
  <h1>🗂️ Batch MapReduce Clickstream Log Analysis</h1>
  <p>End-to-end Big Data batch processing pipeline using the MapReduce paradigm on web server clickstream logs.</p>
  <br/>
  <span class="badge">MapReduce</span>
  <span class="badge">Hadoop Streaming</span>
  <span class="badge">Batch Processing</span>
  <span class="badge">Python</span>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📦 Total Log Events",   f"{total_requests:,}")
c2.metric("🏆 Top Page",           top_page, f"{most_visited_count:,} hits")
c3.metric("✅ Success Rate",        f"{success_rate:.1f}%")
c4.metric("🚨 Error Rate",         f"{error_rate:.1f}%")
c5.metric("👤 Most Active User",   top_user)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs([
    "📊  Analytics Dashboard",
    "📑  Raw MapReduce Output",
    "🏗️  Architecture Diagram"
])

# ═══════════════════════════════════════════════════════════
# Tab 1 — Analytics Dashboard
# ═══════════════════════════════════════════════════════════

with tab1:
    # ── Row 1: Page chart + Status donut ──
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("#### 📄 Job 1 — Page Visit Distribution")
        chart_pages = (
            alt.Chart(df_pages)
            .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
            .encode(
                x=alt.X("Visits:Q", title="Total Page Views",
                         axis=alt.Axis(labelColor="#8892b0", titleColor="#8892b0", gridColor="#1e2130")),
                y=alt.Y("URL:N", sort="-x", title=None,
                         axis=alt.Axis(labelColor="#e2e8f0")),
                color=alt.Color("Visits:Q", scale=alt.Scale(scheme="blues"), legend=None),
                tooltip=[
                    alt.Tooltip("URL:N", title="Page"),
                    alt.Tooltip("Visits:Q", title="Visits", format=",")
                ]
            )
            .properties(height=320, background="transparent")
            .configure_view(strokeWidth=0)
        )
        st.altair_chart(chart_pages, use_container_width=True)

    with col_r:
        st.markdown("#### 🌐 Job 2 — HTTP Status Distribution")
        status_labels = {
            "200": "200 OK",
            "301": "301 Redirect",
            "404": "404 Not Found",
            "500": "500 Server Error"
        }
        df_status_display = df_status.copy()
        df_status_display["Label"] = df_status_display["Status_Code"].map(
            lambda x: status_labels.get(x, f"HTTP {x}")
        )
        chart_status = (
            alt.Chart(df_status_display)
            .mark_arc(innerRadius=65, outerRadius=120, stroke="#0f1117", strokeWidth=2)
            .encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color(
                    "Label:N",
                    scale=alt.Scale(
                        domain=["200 OK", "301 Redirect", "404 Not Found", "500 Server Error"],
                        range=["#2ecc71", "#f39c12", "#e67e22", "#e74c3c"]
                    ),
                    legend=alt.Legend(
                        orient="bottom", columns=2,
                        labelColor="#e2e8f0", titleColor="#8892b0",
                        labelFontSize=11
                    )
                ),
                tooltip=[
                    alt.Tooltip("Label:N", title="Status"),
                    alt.Tooltip("Count:Q", title="Count", format=",")
                ]
            )
            .properties(height=320, background="transparent")
            .configure_view(strokeWidth=0)
        )
        st.altair_chart(chart_status, use_container_width=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Row 2: User chart + quick stats table ──
    col_u, col_t = st.columns([3, 2])

    with col_u:
        st.markdown("#### 👥 Job 3 — Top 10 Most Active Users")
        top10 = df_users.head(10).copy()
        chart_users = (
            alt.Chart(top10)
            .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
            .encode(
                x=alt.X("Requests:Q", title="Total Requests",
                         axis=alt.Axis(labelColor="#8892b0", titleColor="#8892b0", gridColor="#1e2130")),
                y=alt.Y("User_ID:N", sort="-x", title=None,
                         axis=alt.Axis(labelColor="#e2e8f0")),
                color=alt.Color("Requests:Q",
                                scale=alt.Scale(scheme="purples"), legend=None),
                tooltip=[
                    alt.Tooltip("User_ID:N", title="User"),
                    alt.Tooltip("Requests:Q", title="Requests", format=",")
                ]
            )
            .properties(height=300, background="transparent")
            .configure_view(strokeWidth=0)
        )
        st.altair_chart(chart_users, use_container_width=True)

    with col_t:
        st.markdown("#### 📋 HTTP Status Summary")
        for _, row in df_status_display.iterrows():
            pct = row["Count"] / total_requests * 100
            chip = "chip-ok" if row["Status_Code"] == "200" else \
                   "chip-warn" if row["Status_Code"] == "301" else "chip-err"
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        background:#1e2130; border-radius:10px; padding:0.65rem 1rem; margin-bottom:0.5rem;">
              <span class="{chip}">{row['Label']}</span>
              <span style="color:#e2e8f0; font-weight:600;">{row['Count']:,}</span>
              <span style="color:#8892b0; font-size:0.85rem;">{pct:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("#### 📈 Full URL Table")
        df_pages_show = df_pages.copy()
        df_pages_show.index = df_pages_show.index + 1
        st.dataframe(
            df_pages_show[["URL", "Visits"]],
            use_container_width=True,
            height=230
        )

# ═══════════════════════════════════════════════════════════
# Tab 2 — Raw MapReduce Output
# ═══════════════════════════════════════════════════════════

with tab2:
    st.markdown("""
    Each Reducer writes tab-delimited (`Key\\tValue`) records to a plain text file —
    the standard **Hadoop Streaming output format**. These files are read directly
    by the dashboard; nothing is hardcoded.
    """)

    oc1, oc2, oc3 = st.columns(3)

    with oc1:
        st.markdown("##### 📄 `output_pages.txt`")
        st.caption("URL → Visit Count (Job 1 Reducer output)")
        with open(os.path.join(OUTPUT_DIR, "output_pages.txt"), "r") as f:
            st.code(f.read().strip(), language="text")

    with oc2:
        st.markdown("##### 📄 `output_status.txt`")
        st.caption("HTTP Status Code → Count (Job 2 Reducer output)")
        with open(os.path.join(OUTPUT_DIR, "output_status.txt"), "r") as f:
            st.code(f.read().strip(), language="text")

    with oc3:
        st.markdown("##### 📄 `output_users.txt`  *(Top 15)*")
        st.caption("User ID → Request Count (Job 3 Reducer output)")
        top15 = df_users.head(15).apply(
            lambda r: f"{r['User_ID']}\t{r['Requests']}", axis=1
        ).str.cat(sep="\n")
        st.code(top15, language="text")

    st.markdown("<br/>", unsafe_allow_html=True)
    st.info("💡 All values above are read live from the output files. "
            "Click **Run MapReduce Pipeline** in the sidebar and refresh to see updated results.", icon="ℹ️")

# ═══════════════════════════════════════════════════════════
# Tab 3 — Architecture Diagram
# ═══════════════════════════════════════════════════════════

with tab3:
    st.markdown("#### MapReduce Pipeline Architecture")
    st.caption("End-to-end data flow from raw clickstream logs to analytics output.")

    arch_img = "architecture.png"
    if os.path.exists(arch_img):
        st.image(arch_img, use_container_width=True)
    else:
        st.warning("Architecture image not found. Ensure `architecture.png` is in the project folder.")

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("""
    | Phase | Description |
    |---|---|
    | **Input Splits** | Raw `clickstream.csv` is logically partitioned across processing workers |
    | **Map Phase** | Each mapper reads one record and emits a `(Key, 1)` intermediate pair |
    | **Shuffle & Sort** | Framework groups identical keys from all mappers and sorts them |
    | **Reduce Phase** | Reducer receives sorted keys and aggregates counts into final results |
    | **Output** | Tab-separated key-value files written to the `output/` directory |
    | **Visualization** | Streamlit dashboard reads output files dynamically for display |
    """)
