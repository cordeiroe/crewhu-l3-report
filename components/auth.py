import os
import streamlit as st


def check_auth():
    expected = os.getenv("ACCESS_TOKEN", "")
    if not expected:
        return
    token = st.query_params.get("token", "")
    if token != expected:
        st.set_page_config(page_title="Access Denied", page_icon="🔒")
        st.error("🔒 Access denied. Use the link you received to open this report.")
        st.stop()
