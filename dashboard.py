import streamlit as st
import json
import os
import time
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Nifty ORB Bot", layout="wide", initial_sidebar_state="collapsed")

# --- Custom CSS for Sleek Modern Look ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        color: #E6E6E6;
    }
    .metric-card {
        background-color: rgba(30, 33, 41, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #00E5FF;
        margin-top: 10px;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
    }
    .metric-label {
        font-size: 0.9rem;
        color: #AAAAAA;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    .status-active { color: #00E5FF; }
    .status-wait { color: #FFB300; }
    .status-pos { color: #FF5252; }
    h1 {
        text-align: center;
        margin-bottom: 5px;
    }
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 40px;
    }
</style>
""", unsafe_allow_html=True)

STATE_FILE = "state.json"

st.title("📈 Nifty ORB Trading Dashboard")
st.markdown('<p class="subtitle">Automated Opening Range Breakout Strategy for Nifty 50</p>', unsafe_allow_html=True)

ui_placeholder = st.empty()

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return None

def render_ui(state):
    with ui_placeholder.container():
        if state:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Live Nifty Price</div><div class="metric-value">{state.get("live_price", 0):.2f}</div></div>', unsafe_allow_html=True)
            with col2:
                high_val = state.get('session_high', -1)
                high_str = f"{high_val:.2f}" if high_val != -1 else "---"
                st.markdown(f'<div class="metric-card"><div class="metric-label">ORB High</div><div class="metric-value">{high_str}</div></div>', unsafe_allow_html=True)
            with col3:
                low_val = state.get('session_low', 999999)
                low_str = f"{low_val:.2f}" if low_val != 999999 else "---"
                st.markdown(f'<div class="metric-card"><div class="metric-label">ORB Low</div><div class="metric-value">{low_str}</div></div>', unsafe_allow_html=True)
            with col4:
                status = state.get('status', 'WAITING')
                color_class = "status-active" if status == "ACTION" else "status-pos" if status == "IN_POSITION" else "status-wait"
                st.markdown(f'<div class="metric-card"><div class="metric-label">Status</div><div class="metric-value {color_class}">{status}</div></div>', unsafe_allow_html=True)
            
            st.write("")
            st.subheader("Trade Log")
            trade = state.get('trade')
            if trade:
                df = pd.DataFrame([trade])
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                pnl = trade.get('pnl', 0.0)
                if trade.get('exit_time') is None:
                    if pnl > 0:
                        st.success(f"🟢 **Current Virtual PnL: +{pnl:.2f} points**")
                    else:
                        st.error(f"🔴 **Current Virtual PnL: {pnl:.2f} points**")
                else:
                    if pnl > 0:
                        st.success(f"🟢 **Final Trade PnL: +{pnl:.2f} points**")
                    else:
                        st.error(f"🔴 **Final Trade PnL: {pnl:.2f} points**")
            else:
                st.info("No trades taken today yet.")
        else:
            st.warning("Waiting for strategy engine to start...")

# Normal Live Monitoring Loop
while True:
    state = load_state()
    render_ui(state)
    time.sleep(1)
