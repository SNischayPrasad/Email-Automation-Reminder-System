"""
Optional Streamlit dashboard - view reminder reports in the browser.

    pip install streamlit
    streamlit run dashboard.py
"""

import pandas as pd
import streamlit as st

from src import config
from src.data_loader import load_reminders

st.set_page_config(page_title="Email Reminder Dashboard", layout="wide")
st.title("Email Automation & Reminder Dashboard")

history_file = config.OUTPUTS_DIR / "report_history.csv"
if not history_file.exists():
    st.warning("No reports yet. Run `python main.py --all` first.")
    st.stop()

df = pd.read_csv(history_file).fillna("")

total = len(df)
sent = df["status"].isin(["SENT", "DRY_RUN"]).sum()
failed = (df["status"] == "FAILED").sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total processed", total)
c2.metric("Sent / Dry-run", int(sent))
c3.metric("Failed", int(failed))
c4.metric("Success rate", f"{(sent / total * 100) if total else 0:.1f}%")

left, right = st.columns(2)
left.subheader("Emails by status")
left.bar_chart(df["status"].value_counts())
right.subheader("Emails by template")
right.bar_chart(df["template"].value_counts())

st.subheader("Failed emails")
st.dataframe(df[df["status"] == "FAILED"][["reminder_id", "name", "email", "template", "error"]], use_container_width=True)

st.subheader("Upcoming reminder schedule")
st.dataframe(load_reminders().sort_values("send_at"), use_container_width=True)

st.subheader("Full history")
st.dataframe(df, use_container_width=True)
