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
    }


def requests_by_process_df(sim):
    data = sim.requests_by_process()
    df = pd.DataFrame(list(data.items()), columns=["Process", "Requests"])
    return df.set_index("Process")


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