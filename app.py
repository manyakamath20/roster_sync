import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from datetime import datetime
import time

from algorithms.topo_sort import ServiceScheduler
from algorithms.scheduler import run_scheduler
from algorithms.aging import run_scheduler_with_aging

# ─────────────────────────────────────────────
#  Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RosterSync",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  Global CSS  — dark industrial / terminal aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

/* ── Root Palette ── */
:root {
    --bg:        #f0f4f8;
    --surface:   #ffffff;
    --border:    #cbd5e1;
    --accent:    #0ea5e9;
    --accent2:   #7c3aed;
    --warn:      #d97706;
    --danger:    #dc2626;
    --success:   #059669;
    --text:      #0f172a;
    --muted:     #64748b;
    --mono:      'Space Mono', monospace;
    --sans:      'Syne', sans-serif;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #1e293b !important;
    border-right: 1px solid #334155 !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Sidebar logo area */
.sidebar-logo {
    font-family: var(--sans);
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--accent) !important;
    padding: 1rem 0 0.25rem;
    line-height: 1;
}
.sidebar-sub {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* Nav items */
[data-testid="stSelectbox"] > div > div {
    background: var(--border) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
}
[data-testid="stSelectbox"] label {
    font-family: var(--mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* ── Page Header ── */
.page-header {
    display: flex;
    align-items: flex-end;
    gap: 1rem;
    margin-bottom: 0.25rem;
}
.page-title {
    font-family: var(--sans);
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
}
.page-badge {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 4px;
    padding: 2px 8px;
    margin-bottom: 6px;
    opacity: 0.85;
}
.page-divider {
    height: 1px;
    background: linear-gradient(to right, var(--accent), transparent);
    margin: 0.6rem 0 1.8rem;
    border: none;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.card-title {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
}

/* ── Stat chips ── */
.stat-row { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.2rem; }
.stat-chip {
    background: var(--border);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.stat-value {
    font-family: var(--mono);
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.stat-label {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--muted);
}

/* ── Boot order pills ── */
.boot-flow {
    font-family: var(--mono);
    font-size: 0.8rem;
    color: #0c4a6e;
    background: #e0f2fe;
    border: 1px solid var(--accent);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    overflow-x: auto;
    white-space: nowrap;
    letter-spacing: 0.5px;
    margin: 0.5rem 0 1rem;
}

/* ── Alert boxes ── */
.alert {
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: var(--mono);
    font-size: 0.82rem;
    margin: 0.75rem 0;
    border-left: 4px solid;
}
.alert-success { background: #d1fae5; border-color: var(--success); color: #064e3b; }
.alert-warn    { background: #fef3c7; border-color: var(--warn);    color: #78350f; }
.alert-danger  { background: #fee2e2; border-color: var(--danger);  color: #7f1d1d; }
.alert-info    { background: #e0f2fe; border-color: var(--accent);  color: #0c4a6e; }

/* ── Data editor / table ── */
/* Canvas-based grid (Glide Data Grid) is styled via config.toml theme — see .streamlit/config.toml */
[data-testid="stDataEditor"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}


/* ── Text area / input ── */
textarea, [data-baseweb="textarea"] textarea {
    background: #f8fafc !important;
    color: #0f172a !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
[data-baseweb="input"] input {
    background: #f8fafc !important;
    color: #0f172a !important;
    border: 1px solid var(--border) !important;
    font-family: var(--mono) !important;
}

/* ── Buttons ── */
[data-testid="baseButton-primary"],
[data-testid="baseButton-secondary"] {
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
[data-testid="baseButton-primary"] {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
}
[data-testid="baseButton-secondary"] {
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
}
button[kind="primary"]:hover  { opacity: 0.85 !important; }
button[kind="secondary"]:hover { background: rgba(14,165,233,0.08) !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border) !important;
    gap: 0.25rem;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 0.5rem 1rem !important;
    border: none !important;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: rgba(14,165,233,0.08) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: var(--mono) !important;
    font-size: 0.6rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--mono) !important;
    color: var(--accent) !important;
    font-size: 1.6rem !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 1px !important;
    color: var(--text) !important;
}

/* ── Info / warning banners ── */
[data-testid="stInfo"]    { background: #e0f2fe !important; border-color: var(--accent)  !important; }
[data-testid="stSuccess"] { background: #d1fae5 !important; border-color: var(--success) !important; }
[data-testid="stWarning"] { background: #fef3c7 !important; border-color: var(--warn)    !important; }
[data-testid="stError"]   { background: #fee2e2 !important; border-color: var(--danger)  !important; }

/* ── Slider ── */
[data-testid="stSlider"] [role="slider"] {
    background: var(--accent) !important;
}
[data-testid="stSlider"] > div > div > div > div {
    background: var(--accent) !important;
}

/* ── Checkboxes & selectboxes ── */
[data-baseweb="checkbox"] { accent-color: var(--accent); }

/* ── Log output lines ── */
.log-line {
    font-family: var(--mono);
    font-size: 0.75rem;
    padding: 3px 6px;
    border-radius: 3px;
    margin: 1px 0;
}
.log-run  { color: #0369a1; background: #e0f2fe; }
.log-done { color: #065f46; background: #d1fae5; }
.log-idle { color: var(--muted); }

/* ── Service pill ── */
.svc-pill {
    display: inline-block;
    background: #e0f2fe;
    border: 1px solid var(--accent);
    color: #0c4a6e;
    font-family: var(--mono);
    font-size: 0.7rem;
    border-radius: 20px;
    padding: 3px 10px;
    margin: 3px 2px;
}
.svc-pill.failed {
    background: #fee2e2;
    border-color: var(--danger);
    color: #7f1d1d;
    text-decoration: line-through;
}

/* ── Info sidebar card ── */
.info-card {
    background: #f1f5f9;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    font-family: var(--mono);
    font-size: 0.72rem;
    color: #334155;
    line-height: 1.7;
}
.info-card b { color: #0ea5e9; }

/* ── Matplotlib light style override ── */
/* Applied per-chart in code */
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Matplotlib light theme helper
# ─────────────────────────────────────────────
def apply_dark_style(ax, fig):
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")
    ax.tick_params(colors="#475569", labelsize=8)
    ax.xaxis.label.set_color("#475569")
    ax.yaxis.label.set_color("#475569")
    ax.title.set_color("#0f172a")
    for spine in ax.spines.values():
        spine.set_edgecolor("#cbd5e1")

ACCENT_COLORS = ["#0ea5e9", "#7c3aed", "#10b981", "#f59e0b", "#ef4444", "#ec4899"]

# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🌐 RosterSync</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Network Scheduling OS</div>', unsafe_allow_html=True)

    menu = st.selectbox(
        "MODULE",
        [
            "🔧  Service Boot Sequencer",
            "⚡  Bandwidth Job Scheduler",
            "🕐  Aging Demo",
            "🚨  Critical Service Flag",
            "⏰  Time-of-Day Scheduling",
        ],
        label_visibility="visible",
    )

    st.markdown("---")
    now = datetime.now()
    st.markdown(
        f'<div class="info-card">'
        f'<b>System Time</b><br>{now.strftime("%H:%M:%S")}<br>'
        f'<b>Date</b><br>{now.strftime("%Y-%m-%d")}<br>'
        f'<b>Status</b><br><span style="color:#10b981">● ONLINE</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def page_header(icon, title, badge):
    st.markdown(
        f'<div class="page-header">'
        f'<div class="page-title">{icon} {title}</div>'
        f'<div class="page-badge">{badge}</div>'
        f'</div>'
        f'<hr class="page-divider">',
        unsafe_allow_html=True,
    )

def alert(kind, text):
    st.markdown(f'<div class="alert alert-{kind}">{text}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  MODULE 1 — Service Boot Sequencer
# ═══════════════════════════════════════════════════════════════
if menu == "🔧  Service Boot Sequencer":
    page_header("🔧", "Service Boot Sequencer", "Topological Sort · DFS · O(V+E)")

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown('<div class="card-title">Service Dependency Map</div>', unsafe_allow_html=True)
        st.caption("Format: `ServiceA ServiceB`  →  A depends on B")

        dep_default = (
            "DNS Proxy\nProxy Firewall\nFirewall Monitoring\nMonitoring Database\n"
            "Database Authentication\nAuthentication WebServer\nWebServer LoadBalancer\n"
            "LoadBalancer Analytics\nAnalytics Backup\nBackup Storage\n"
            "Storage Notification\nNotification Logging\nLogging Reporting\n"
            "Reporting Dashboard\nDashboard AlertSystem\nAlertSystem EmailService\n"
            "EmailService SMTPGateway"
        )
        dependency_input = st.text_area("", value=dep_default, height=310, label_visibility="collapsed")

        run_btn = st.button("🚀  Generate Boot Order", use_container_width=True, type="primary")

    with col_right:
        st.markdown(
            '<div class="info-card">'
            '<b>Algorithm</b><br>Topological Sort via DFS<br><br>'
            '<b>Complexity</b><br>Time: O(V + E)<br>Space: O(V)<br><br>'
            '<b>Features</b><br>'
            '→ Cycle detection<br>'
            '→ Dependency ordering<br>'
            '→ Graph visualisation<br>'
            '→ Correct startup sequence'
            '</div>',
            unsafe_allow_html=True,
        )

        lines_raw = [l for l in dependency_input.strip().split("\n") if l.strip()]
        all_svc = set()
        for l in lines_raw:
            parts = l.split()
            if len(parts) == 2:
                all_svc.update(parts)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Services", len(all_svc))
        c2.metric("Edges", len(lines_raw))

    if run_btn:
        scheduler = ServiceScheduler()
        lines_raw = [l for l in dependency_input.strip().split("\n") if l.strip()]
        for line in lines_raw:
            parts = line.strip().split()
            if len(parts) == 2:
                scheduler.add_dependency(parts[0], parts[1])

        order = scheduler.topological_sort()

        if order:
            alert("success", f"✅ Valid boot order resolved — {len(order)} services scheduled")

            # Boot flow scrollable
            flow_str = " → ".join(order)
            st.markdown(f'<div class="boot-flow">{flow_str}</div>', unsafe_allow_html=True)

            # Service pills in numbered grid
            st.markdown("#### Boot Sequence")
            pills_html = ""
            for i, svc in enumerate(order):
                pills_html += f'<span class="svc-pill">{i+1}. {svc}</span>'
            st.markdown(pills_html, unsafe_allow_html=True)

            # Graph
            st.markdown("#### Dependency Graph")
            G = nx.DiGraph()
            for line in lines_raw:
                parts = line.strip().split()
                if len(parts) == 2:
                    G.add_edge(parts[0], parts[1])

            fig, ax = plt.subplots(figsize=(14, 7))
            apply_dark_style(ax, fig)
            pos = nx.spring_layout(G, k=2.2, iterations=60, seed=42)
            nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#94a3b8",
                                   arrows=True, arrowstyle="-|>", arrowsize=18,
                                   width=1.5, connectionstyle="arc3,rad=0.08")
            nx.draw_networkx_nodes(G, pos, ax=ax, node_color="#e0f2fe",
                                   node_size=2800, linewidths=1.5,
                                   edgecolors="#0ea5e9")
            nx.draw_networkx_labels(G, pos, ax=ax, font_color="#0c4a6e",
                                    font_family="monospace", font_size=7.5)
            ax.axis("off")
            st.pyplot(fig)
            plt.close()

        else:
            alert("danger", "❌ Circular Dependency Detected — unable to schedule boot order")
            if hasattr(scheduler, "cycle") and scheduler.cycle:
                st.markdown(
                    f'<div class="boot-flow" style="border-color:#ef4444;color:#fca5a5">'
                    f'{" → ".join(scheduler.cycle)}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

# ═══════════════════════════════════════════════════════════════
#  MODULE 2 — Bandwidth Job Scheduler
# ═══════════════════════════════════════════════════════════════
elif menu == "⚡  Bandwidth Job Scheduler":
    page_header("⚡", "Bandwidth Job Scheduler", "Preemptive Priority · Context Switch Log")

    jobs_default = [
        {"name": "Backup",          "arrival": 0, "burst": 8, "priority": 5},
        {"name": "Video Stream",    "arrival": 1, "burst": 4, "priority": 1},
        {"name": "OS Update",       "arrival": 2, "burst": 5, "priority": 2},
        {"name": "File Sync",       "arrival": 3, "burst": 3, "priority": 4},
        {"name": "Email Sync",      "arrival": 4, "burst": 2, "priority": 3},
        {"name": "Database Backup", "arrival": 5, "burst": 6, "priority": 6},
    ]

    st.markdown('<div class="card-title">Job Configuration · Lower priority number = Higher priority</div>', unsafe_allow_html=True)
    df = pd.DataFrame(jobs_default)
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    if st.button("▶  Run Scheduler", use_container_width=True, type="primary"):
        jobs = edited_df.to_dict("records")
        log, waiting_times = run_scheduler(jobs)

        st.session_state["sched_log"]  = log
        st.session_state["sched_wait"] = waiting_times

    if "sched_log" in st.session_state:
        log           = st.session_state["sched_log"]
        waiting_times = st.session_state["sched_wait"]
        avg_wait      = sum(waiting_times.values()) / len(waiting_times)
        max_wait      = max(waiting_times.values())
        ctx_switches  = len([l for l in log if "Running" in l])
        throughput    = len(jobs_default) / sum(j["burst"] for j in jobs_default)

        # KPI row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg Wait",         f"{avg_wait:.2f} u")
        c2.metric("Max Wait",         f"{max_wait} u")
        c3.metric("Context Switches", ctx_switches)
        c4.metric("Throughput",       f"{throughput:.3f} j/u")

        tab1, tab2, tab3 = st.tabs(["Context Switch Log", "Waiting Times", "Analysis"])

        with tab1:
            with st.expander("Execution Log", expanded=True):
                for item in log[:60]:
                    if "Running" in item:
                        st.markdown(f'<div class="log-line log-run">▶ {item}</div>', unsafe_allow_html=True)
                    elif "completed" in item:
                        st.markdown(f'<div class="log-line log-done">✓ {item}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="log-line log-idle">· {item}</div>', unsafe_allow_html=True)

        with tab2:
            wdf = (
                pd.DataFrame([{"Job": k, "Waiting Time": v} for k, v in waiting_times.items()])
                .sort_values("Waiting Time", ascending=False)
            )
            st.dataframe(wdf, use_container_width=True, hide_index=True)

            fig, ax = plt.subplots(figsize=(10, 4))
            apply_dark_style(ax, fig)
            bars = ax.bar(wdf["Job"], wdf["Waiting Time"],
                          color=ACCENT_COLORS[:len(wdf)], zorder=3, width=0.5)
            ax.set_ylabel("Waiting Time", fontsize=8)
            ax.set_title("Job Waiting Times", fontsize=10, pad=12)
            ax.yaxis.grid(True, linestyle="--", alpha=0.3, color="#1e2d40")
            ax.set_axisbelow(True)
            plt.xticks(rotation=30, ha="right", fontsize=7)
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.1,
                        str(int(h)), ha="center", va="bottom",
                        fontsize=7, color="#e2e8f0", fontfamily="monospace")
            st.pyplot(fig)
            plt.close()

        with tab3:
            starvation = "⚠ HIGH" if max_wait > 15 else "✅ LOW"
            alert("info",
                  f"Context Switches: {ctx_switches} &nbsp;|&nbsp; "
                  f"Starvation Risk: {starvation} &nbsp;|&nbsp; "
                  f"Throughput: {throughput:.3f} jobs/unit")

# ═══════════════════════════════════════════════════════════════
#  MODULE 3 — Aging Demo
# ═══════════════════════════════════════════════════════════════
elif menu == "🕐  Aging Demo":
    page_header("🕐", "Starvation Prevention — Priority Aging", "Aging · Fairness · Anti-Starvation")

    jobs_default = [
        {"name": "Backup",           "arrival": 2, "burst": 5, "priority": 1},
        {"name": "Emergency Alert",  "arrival": 6, "burst": 5, "priority": 1},
        {"name": "Streaming",        "arrival": 8, "burst": 6, "priority": 3},
        {"name": "Low Priority Job", "arrival": 1, "burst": 2, "priority": 4},
    ]

    st.markdown('<div class="card-title">Job Configuration</div>', unsafe_allow_html=True)
    df = pd.DataFrame(jobs_default)
    edited_df = st.data_editor(df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("❌  Run WITHOUT Aging", use_container_width=True):
            log_no, wait_no = run_scheduler(edited_df.to_dict("records"))
            st.session_state["no_aging_wait"] = wait_no
            alert("warn", "Completed — no aging applied")
    with c2:
        if st.button("✅  Run WITH Aging", use_container_width=True, type="primary"):
            log_yes, wait_yes = run_scheduler_with_aging(edited_df.to_dict("records"))
            st.session_state["with_aging_wait"] = wait_yes
            alert("success", "Completed — aging active")

    if "no_aging_wait" in st.session_state and "with_aging_wait" in st.session_state:
        st.markdown("---")
        st.markdown("#### Comparison Results")

        comp = []
        for job, wo in st.session_state["no_aging_wait"].items():
            w = st.session_state["with_aging_wait"].get(job, 0)
            comp.append({"Job": job, "Without Aging": wo, "With Aging": w, "Saved": wo - w})
        cdf = pd.DataFrame(comp)
        st.dataframe(cdf, use_container_width=True, hide_index=True)

        fig, ax = plt.subplots(figsize=(10, 5))
        apply_dark_style(ax, fig)
        x     = range(len(cdf))
        width = 0.35
        ax.bar([i - width / 2 for i in x], cdf["Without Aging"], width,
               label="Without Aging", color="#ef4444", alpha=0.9, zorder=3)
        ax.bar([i + width / 2 for i in x], cdf["With Aging"], width,
               label="With Aging",    color="#10b981", alpha=0.9, zorder=3)
        ax.set_xticks(x)
        ax.set_xticklabels(cdf["Job"], fontsize=8)
        ax.set_ylabel("Waiting Time", fontsize=8)
        ax.set_title("Aging Impact on Waiting Times", fontsize=10, pad=12)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3, color="#1e2d40")
        ax.set_axisbelow(True)
        ax.legend(fontsize=8, facecolor="#111827", edgecolor="#1e2d40", labelcolor="#e2e8f0")
        st.pyplot(fig)
        plt.close()

        saved = cdf["Saved"].sum()
        if saved > 0:
            alert("success", f"✅ Total improvement: {saved} time units saved across all jobs")
        elif saved == 0:
            alert("info", "No change in total waiting time — scheduling order unchanged")
        else:
            alert("warn", f"Aging increased total waiting by {abs(saved)} units — review priorities")

# ═══════════════════════════════════════════════════════════════
#  MODULE 4 — Critical Service Flag
# ═══════════════════════════════════════════════════════════════
elif menu == "🚨  Critical Service Flag":
    page_header("🚨", "Critical Service Failure Handler", "Bonus · Cascade Detection")

    col_l, col_r = st.columns([2, 2], gap="large")

    with col_l:
        st.markdown('<div class="card-title">Dependency Graph</div>', unsafe_allow_html=True)
        deps_default = (
            "DNS Proxy\nProxy Firewall\nFirewall Monitoring\n"
            "Monitoring Database\nDatabase WebServer\nWebServer LoadBalancer"
        )
        dep_input = st.text_area("", value=deps_default, height=190, label_visibility="collapsed")

        all_svcs = []
        for line in dep_input.strip().split("\n"):
            parts = line.strip().split()
            if len(parts) == 2:
                all_svcs.extend(parts)
        all_svcs = list(dict.fromkeys(all_svcs))  # dedupe preserving order

        critical_service = st.selectbox("🔴 Critical Service", all_svcs if all_svcs else ["DNS"])
        simulate_failure = st.checkbox("⚠️  Simulate Failure")
        run_critical = st.button("🚀  Run with Failure Check", use_container_width=True, type="primary")

    with col_r:
        st.markdown(
            '<div class="info-card">'
            '<b>Feature</b><br>Critical service cascade detection<br><br>'
            '<b>Behaviour</b><br>'
            '→ Boot runs in topological order<br>'
            '→ On failure: downstream services skipped<br>'
            '→ Upstream services remain running<br>'
            '→ Full cascade audit trail'
            '</div>',
            unsafe_allow_html=True,
        )

    if run_critical:
        scheduler = ServiceScheduler()
        lines_raw = [l for l in dep_input.strip().split("\n") if l.strip()]
        for line in lines_raw:
            parts = line.strip().split()
            if len(parts) == 2:
                scheduler.add_dependency(parts[0], parts[1])

        order = scheduler.topological_sort()

        if not order:
            alert("danger", "❌ Circular dependency detected — cannot determine boot order")
        elif not simulate_failure:
            # No failure simulated — just show normal boot order
            alert("success", "✅ No failure simulated — showing normal boot sequence")
            pills = "".join(f'<span class="svc-pill">{i+1}. {s}</span>' for i, s in enumerate(order))
            st.markdown(pills, unsafe_allow_html=True)
        elif critical_service not in order:
            alert("warn", f"⚠️ '{critical_service}' not found in resolved boot order — check dependencies")
            st.markdown("**Resolved order:**")
            pills = "".join(f'<span class="svc-pill">{i+1}. {s}</span>' for i, s in enumerate(order))
            st.markdown(pills, unsafe_allow_html=True)
        else:
            # Failure simulation
            idx     = order.index(critical_service)
            started = order[:idx]
            skipped = order[idx + 1:]

            alert("danger", f"🚨 CRITICAL FAILURE — '{critical_service}' could not start")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**✅ Started (before failure)**")
                if started:
                    pills = "".join(f'<span class="svc-pill">{s}</span>' for s in started)
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.markdown("<em style='color:#64748b'>No services started before failure</em>", unsafe_allow_html=True)

            with col_b:
                st.markdown("**⛔ Skipped (cascade)**")
                if skipped:
                    pills_skip = "".join(f'<span class="svc-pill failed">{s}</span>' for s in skipped)
                    st.markdown(pills_skip, unsafe_allow_html=True)
                else:
                    st.markdown("<em style='color:#64748b'>No downstream services</em>", unsafe_allow_html=True)

            st.markdown("**💀 Failed Service**")
            st.markdown(f'<span class="svc-pill failed">💀 {critical_service}</span>', unsafe_allow_html=True)

            if skipped:
                alert("warn", f"⛔ {len(skipped)} downstream service(s) were not started due to cascade failure")

# ═══════════════════════════════════════════════════════════════
#  MODULE 5 — Time-of-Day Scheduling
# ═══════════════════════════════════════════════════════════════
elif menu == "⏰  Time-of-Day Scheduling":
    page_header("⏰", "Time-of-Day Scheduling Policy", "Bonus · Dynamic Priority Shift")

    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        current_hour = st.slider("Current Hour (0–23)", 0, 23, 14, format="%d:00")
        is_peak      = 9 <= current_hour <= 18

        if is_peak:
            alert("info", f"🌞  PEAK HOURS ({current_hour}:00) — Critical jobs elevated, maintenance deprioritised")
        else:
            alert("info", f"🌙  OFF-PEAK ({current_hour}:00) — Maintenance elevated, critical jobs deprioritised")

    with col_r:
        # 24-h arc indicator
        progress = current_hour / 23
        colour   = "#f59e0b" if is_peak else "#7c3aed"
        st.markdown(
            f'<div style="background:#f1f5f9;border:1px solid #cbd5e1;border-radius:10px;padding:1rem;">'
            f'<div style="font-family:monospace;font-size:0.65rem;color:#64748b;letter-spacing:2px;'
            f'text-transform:uppercase;margin-bottom:0.5rem;">Time Indicator</div>'
            f'<div style="background:#e2e8f0;border-radius:4px;height:6px;width:100%;">'
            f'<div style="background:{colour};height:6px;border-radius:4px;width:{progress*100:.1f}%"></div>'
            f'</div>'
            f'<div style="font-family:monospace;font-size:1.4rem;color:{colour};margin-top:0.5rem;font-weight:700;">'
            f'{current_hour:02d}:00</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    jobs_data = [
        {"name": "Video Conference", "base_priority": 1, "type": "critical"},
        {"name": "Email Sync",       "base_priority": 3, "type": "normal"},
        {"name": "Database Backup",  "base_priority": 5, "type": "maintenance"},
        {"name": "System Update",    "base_priority": 4, "type": "maintenance"},
        {"name": "Web Traffic",      "base_priority": 2, "type": "critical"},
    ]

    for job in jobs_data:
        t = job["type"]
        if is_peak:
            job["adjusted_priority"] = (
                job["base_priority"] if t == "critical"
                else job["base_priority"] + 3 if t == "maintenance"
                else job["base_priority"] + 1
            )
        else:
            job["adjusted_priority"] = (
                max(1, job["base_priority"] - 2) if t == "maintenance"
                else job["base_priority"] + 2   if t == "critical"
                else job["base_priority"]
            )

    st.markdown("#### Priority Adjustments")
    comp_df = pd.DataFrame([
        {
            "Job":               j["name"],
            "Type":              j["type"],
            "Base Priority":     j["base_priority"],
            "Adjusted Priority": j["adjusted_priority"],
            "Δ":                 j["adjusted_priority"] - j["base_priority"],
        }
        for j in jobs_data
    ])
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    if st.button("🔄  Run Time-Aware Scheduler", use_container_width=True, type="primary"):
        sched_jobs = [
            {"name": j["name"], "arrival": i * 2, "burst": 4, "priority": j["adjusted_priority"]}
            for i, j in enumerate(jobs_data)
        ]
        log, waiting_times = run_scheduler(sched_jobs)

        st.markdown("#### Execution Log")
        with st.expander("View Schedule", expanded=True):
            for item in log[:30]:
                if "Running" in item:
                    st.markdown(f'<div class="log-line log-run">▶ {item}</div>', unsafe_allow_html=True)
                elif "completed" in item:
                    st.markdown(f'<div class="log-line log-done">✓ {item}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="log-line log-idle">· {item}</div>', unsafe_allow_html=True)

        st.markdown("#### Waiting Times")
        wt_df = pd.DataFrame([{"Job": k, "Wait": v} for k, v in waiting_times.items()])
        st.dataframe(wt_df, use_container_width=True, hide_index=True)

        avg_w = sum(waiting_times.values()) / len(waiting_times)
        mode  = "Peak — critical traffic elevated" if is_peak else "Off-peak — maintenance elevated"
        alert("info", f"📊 {mode} · Avg wait: {avg_w:.1f} units")