"""
sk_analytics.py
Analytics helper functions for the Suzuki-Kasami Streamlit app.
"""

import pandas as pd


def summary_stats(sim):
    return {
        "Total Requests": sim.total_requests,
        "Token Transfers": sim.total_token_transfers,
        "Critical-Section Entries": sim.total_cs_entries,
        "Messages Sent": sim.total_messages,
    }


def requests_by_process_df(sim):
    data = sim.requests_by_process()
    df = pd.DataFrame(list(data.items()), columns=["Process", "Requests"])
    return df.set_index("Process")


def rn_matrix_df(sim):
    """RN[i][j]: what process i (row) knows about process j's requests (column)."""
    names = [f"P{i}" for i in range(sim.n)]
    return pd.DataFrame(sim.RN, index=[f"RN of {n}" for n in names], columns=names)


def logs_df(sim):
    if not sim.logs:
        return pd.DataFrame(columns=["time", "event", "process", "detail"])
    return pd.DataFrame(sim.logs)


def event_counts_df(sim):
    df = logs_df(sim)
    if df.empty:
        return pd.DataFrame()
    counts = df["event"].value_counts()
    return counts.to_frame(name="Count")
