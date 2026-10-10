"""
app.py
------
Suzuki-Kasami Mutual Exclusion Algorithm — Visual Simulator
MCA Tiny Project (textured edition, textbook algorithm)

Run with:
    streamlit run app.py
"""

import streamlit as st
from simulator import SuzukiKasami, NUM_PROCESSES
import sk_analytics as an
from ring_view import build_ring_svg

st.set_page_config(page_title="Suzuki-Kasami Simulator", page_icon="🔑", layout="centered")

# ----------------------------------------------------------------------
# Global styling (cards, chips, header banner)
# ----------------------------------------------------------------------
st.markdown("""
<style>
/* ---------- Textured, lighter background (all inline, no config file) ---------- */
.stApp {
    background-color: #3d3591;
    background-image:
        radial-gradient(circle at 15% 8%,  rgba(255, 110, 199, 0.38), transparent 42%),
        radial-gradient(circle at 85% 0%,  rgba(34, 211, 238, 0.34), transparent 40%),
        radial-gradient(circle at 50% 100%, rgba(255, 209, 102, 0.16), transparent 45%),
        repeating-linear-gradient(45deg, rgba(255, 255, 255, 0.045) 0px, rgba(255, 255, 255, 0.045) 2px, transparent 2px, transparent 14px),
        radial-gradient(rgba(255, 255, 255, 0.10) 1px, transparent 1px);
    background-size: auto, auto, auto, auto, 24px 24px;
    background-attachment: fixed;
    color: #ffffff;
}
section[data-testid="stSidebar"] {
    background: #2c2672;
    border-right: 1px solid rgba(255, 255, 255, 0.25);
}
p, label, li, span, div[data-testid="stMarkdownContainer"] { color: #ffffff; }

/* All headings: bright, never black */
h1, h2, h3, h4 {
    color: #ffd166 !important;
    text-shadow: 0 0 12px rgba(255, 209, 102, 0.35);
}

.stButton button {
    background: linear-gradient(135deg, #ffd166 0%, #ff6ec7 100%);
    color: #1b1740 !important;
    font-weight: 800;
    border: none;
    border-radius: 10px;
}
.stButton button:hover { filter: brightness(1.1); }
.stButton button:disabled { opacity: 0.4; }

div[data-testid="stMetricValue"] { color: #22d3ee !important; }
div[data-testid="stMetricLabel"] p { color: #ffd166 !important; }
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 12px;
    padding: 8px 12px;
}

.sk-banner {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.30);
    border-radius: 16px;
    padding: 22px 26px;
    margin-bottom: 18px;
}
.sk-banner h1 {
    margin: 0; font-size: 2rem; font-weight: 800;
    background: linear-gradient(90deg, #ffd166 0%, #ff6ec7 50%, #22d3ee 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none;
    filter: drop-shadow(0 0 10px rgba(255, 110, 199, 0.45));
}
.sk-banner p  { margin: 6px 0 0 0; color: #e6e8ff; }

.sk-card {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 14px;
}
.sk-card h4 { margin-top: 0; color: #ffd166 !important; }

.chip {
    display:inline-block; padding: 3px 10px; border-radius: 999px;
    font-size: 0.78rem; font-weight: 700; letter-spacing: .02em;
}
.chip-request  { background: #2d3a63; color: #8fb1ff; }
.chip-transfer { background: #4a3a1f; color: #f5b544; }
.chip-enter    { background: #1f4a33; color: #39d98a; }
.chip-exit     { background: #4a1f2a; color: #ff6b81; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
if "sim" not in st.session_state:
    st.session_state.sim = SuzukiKasami()

sim: SuzukiKasami = st.session_state.sim

CHIP_CLASS = {
    "REQUEST": "chip-request",
    "TOKEN TRANSFER": "chip-transfer",
    "ENTER CS": "chip-enter",
    "EXIT CS": "chip-exit",
}

# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
st.sidebar.markdown("## 🔑 Suzuki-Kasami")
st.sidebar.caption("Distributed Mutual Exclusion — Visual Simulator")
page = st.sidebar.radio("Navigate", ["🏠 Home", "⚙️ Simulator", "📊 Analytics", "📋 Event Log"])
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Simulation", use_container_width=True):
    sim.reset()
    st.rerun()

# ----------------------------------------------------------------------
# 🏠 HOME
# ----------------------------------------------------------------------
if page == "🏠 Home":
    st.markdown("""
    <div class="sk-banner">
      <h1>🔑 Suzuki–Kasami Algorithm</h1>
      <p>A live, animated demo of token-based mutual exclusion in distributed systems</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
<div class="sk-card">
<h4>What's happening?</h4>
A single <b>TOKEN</b> circulates among processes. Only whoever holds it may
enter the <b>Critical Section (CS)</b> — even though there's no shared memory
or central coordinator. Every process keeps its own <b>RN array</b> (highest request number
heard from each process); the token carries <b>LN[j]</b> (last granted
request of j) and a <b>queue</b> of processes waiting their turn.
</div>

<div class="sk-card">
<h4>Why it matters</h4>
A request costs only <b>N messages</b> (N-1 REQUEST broadcasts + 1 TOKEN) and
nothing at all if the requester already holds the idle token. There is no
central coordinator — a classic, elegant solution from Distributed
Systems / OS coursework.
</div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Processes", NUM_PROCESSES)
    c2.metric("Token holder", f"P{sim.current_holder}")
    c3.metric("In Critical Section", "Yes" if sim.in_cs else "No")

    st.info("👉 Head to **⚙️ Simulator** to watch the token move live.")

# ----------------------------------------------------------------------
# ⚙️ SIMULATOR
# ----------------------------------------------------------------------
elif page == "⚙️ Simulator":
    st.markdown("## ⚙️ Live Simulator")

    status_color = "#39d98a" if sim.in_cs else "#f5b544"
    st.markdown(
        f'<div class="sk-card" style="border-color:{status_color}; text-align:center;">'
        f'<span style="color:{status_color}; font-size:1.05rem; font-weight:700;">'
        f'{sim.status_text()}</span></div>',
        unsafe_allow_html=True,
    )

    # ---- the animated ring ----
    st.markdown(build_ring_svg(sim), unsafe_allow_html=True)

    legend = """
    <div style="display:flex; gap:18px; justify-content:center; font-size:0.8rem; color:#e6e8ff; margin-bottom:10px;">
      <span>🟡 Holding token</span>
      <span>🟢 Inside Critical Section</span>
      <span>🟧 Waiting in queue</span>
      <span>⚪ Idle</span>
    </div>
    """
    st.markdown(legend, unsafe_allow_html=True)

    st.markdown("#### Request Critical Section")
    req_cols = st.columns(4)
    for i in range(NUM_PROCESSES):
        with req_cols[i]:
            if st.button(f"REQUEST P{i}", key=f"req_{i}", use_container_width=True):
                sim.request_cs(i)
                st.rerun()

    st.markdown("#### Token Movement")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("▶ NEXT STEP / SEND TOKEN", use_container_width=True):
            sim.next_step()
            st.rerun()
    with b2:
        if st.button("⏹ EXIT CS (holder finishes)", use_container_width=True,
                      disabled=not sim.in_cs):
            sim.exit_cs()
            st.rerun()

    s1, s2, s3 = st.columns(3)
    s1.metric("Token with", f"P{sim.current_holder}")
    s2.metric("Queue", ", ".join(f"P{p}" for p in sim.token_queue) or "—")
    s3.metric("Requests made", str([sim.RN[i][i] for i in range(NUM_PROCESSES)]))

    with st.expander("🔬 Algorithm state (RN matrix + token LN)"):
        st.caption("Row = a process's own RN array: RN[row][col] is what that process "
                   "knows about the column process's requests.")
        st.dataframe(an.rn_matrix_df(sim))
        st.markdown(f"**Token LN[]** (last granted request per process): `{sim.token_LN}`")
        st.markdown(f"**Token queue:** `{['P%d' % p for p in sim.token_queue]}`")

# ----------------------------------------------------------------------
# 📊 ANALYTICS
# ----------------------------------------------------------------------
elif page == "📊 Analytics":
    st.markdown("## 📊 Analytics")

    stats = an.summary_stats(sim)
    c1, c2 = st.columns(2)
    c1.metric("Total Requests", stats["Total Requests"])
    c2.metric("Token Transfers", stats["Token Transfers"])
    c3, c4 = st.columns(2)
    c3.metric("CS Entries", stats["Critical-Section Entries"])
    c4.metric("Messages Sent", stats["Messages Sent"])

    st.markdown("#### Requests by Process")
    st.bar_chart(an.requests_by_process_df(sim), color="#f5b544")

    st.markdown("#### Event Type Breakdown")
    ev_df = an.event_counts_df(sim)
    if not ev_df.empty:
        st.bar_chart(ev_df, color="#39d98a")
    else:
        st.caption("No events yet — make some requests in the Simulator tab!")

# ----------------------------------------------------------------------
# 📋 EVENT LOG
# ----------------------------------------------------------------------
elif page == "📋 Event Log":
    st.markdown("## 📋 Event Log")

    df = an.logs_df(sim)
    if df.empty:
        st.caption("No events logged yet. Head to the Simulator tab and click REQUEST.")
    else:
        for row in df.iloc[::-1].itertuples():
            chip = CHIP_CLASS.get(row.event, "chip-request")
            st.markdown(
                f'<div class="sk-card" style="padding:10px 16px; margin-bottom:8px; '
                f'display:flex; align-items:center; gap:12px;">'
                f'<span class="chip {chip}">{row.event}</span>'
                f'<b>{row.process}</b>'
                f'<span style="color:#d8dbff;">{row.detail}</span>'
                f'<span style="margin-left:auto; color:#cfd3ff; font-size:0.78rem;">{row.time}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.download_button(
            "⬇ Download log as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="events.csv",
            mime="text/csv",
        )
