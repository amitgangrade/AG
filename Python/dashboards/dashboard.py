import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="System Monitor Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for a "Grafana-like" dark theme aesthetic
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .metric-card {
        background-color: #1f2937;
        border: 1px solid #374151;
        padding: 20px;
        border-radius: 8px;
        color: white;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #60a5fa;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to generate fake time-series data
def get_time_series_data(hours=24):
    dates = [datetime.now() - timedelta(minutes=i) for i in range(hours * 60)]
    dates.reverse()
    
    df = pd.DataFrame({
        'timestamp': dates,
        'cpu_usage': np.random.normal(50, 15, len(dates)).clip(0, 100),
        'memory_usage': np.random.normal(60, 10, len(dates)).clip(0, 100),
        'network_in': np.random.poisson(100, len(dates)),
        'network_out': np.random.poisson(80, len(dates))
    })
    return df

# Sidebar Controls
st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("---")
view_mode = st.sidebar.selectbox("View Mode", ["Live Overview", "Historical Analysis", "System Health"])
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 10)
time_range = st.sidebar.selectbox("Time Range", ["Last 1 Hour", "Last 6 Hours", "Last 24 Hours"])

st.sidebar.markdown("### 🛠 Simulation Settings")
if st.sidebar.button("🚨 Simulate Critical Alert"):
    st.sidebar.error("CRITICAL: CPU Temp exceeded 90°C provided by 'Server-01'")

# Main Content
st.title("📊 System Telemetry & Monitoring")
st.markdown("Real-time observability dashboard for production clusters.")

if view_mode == "Live Overview":
    # Top Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    # Generate random current metrics
    cpu = np.random.randint(20, 90)
    mem = np.random.randint(40, 80)
    req_sec = np.random.randint(1000, 5000)
    errors = np.random.randint(0, 50)

    delta_cpu = np.random.randint(-5, 5)
    delta_mem = np.random.randint(-2, 2)

    with col1:
        st.metric("CPU Usage", f"{cpu}%", f"{delta_cpu}%")
    with col2:
        st.metric("Memory Usage", f"{mem}%", f"{delta_mem}%")
    with col3:
        st.metric("Requests/Sec", f"{req_sec}", "+120")
    with col4:
        st.metric("Error Rate", f"{errors}", "-2", delta_color="inverse")

    # Interactive Plots
    st.markdown("### 📈 Real-time Traffic Analysis")
    
    # Fake Data
    df = get_time_series_data(hours=1 if time_range == "Last 1 Hour" else 6 if time_range == "Last 6 Hours" else 24)
    
    # Area Chart for Network Traffic
    fig_network = go.Figure()
    fig_network.add_trace(go.Scatter(x=df['timestamp'], y=df['network_in'], mode='lines', fill='tozeroy', name='Ingress', line=dict(color='#82ca9d')))
    fig_network.add_trace(go.Scatter(x=df['timestamp'], y=df['network_out'], mode='lines', fill='tozeroy', name='Egress', line=dict(color='#8884d8')))
    
    fig_network.update_layout(
        title="Network Traffic (Mbps)",
        xaxis_title="Time",
        yaxis_title="Mbps",
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_network, use_container_width=True)

    # Split row for Heatmap and Pie chart
    row2_col1, row2_col2 = st.columns([2, 1])

    with row2_col1:
        st.markdown("### 🌡️ Hourly Load Heatmap")
        heatmap_data = np.random.rand(24, 7)
        fig_map = px.imshow(heatmap_data, 
                            labels=dict(x="Day of Week", y="Hour of Day", color="Load"),
                            x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                            y=[f"{i}:00" for i in range(24)],
                            color_continuous_scale="Viridis",
                            template="plotly_dark")
        fig_map.update_layout(height=400)
        st.plotly_chart(fig_map, use_container_width=True)

    with row2_col2:
        st.markdown("### 📦 Service Distribution")
        services = ['Auth Service', 'Payment API', 'Frontend', 'Worker Node', 'DB-Main']
        usage = [15, 30, 25, 20, 10]
        fig_pie = px.pie(values=usage, names=services, hole=0.4, template="plotly_dark", title="Resource Allocation")
        fig_pie.update_layout(height=400, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

elif view_mode == "Historical Analysis":
    st.subheader("Data Explorer")
    df = get_time_series_data(24)
    st.markdown("Filter and inspect raw telemetry logs.")
    
    # Data Table with highlighting
    st.dataframe(
        df.style.highlight_max(axis=0, color="#b91c1c"),
        use_container_width=True,
        height=600
    )

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Report CSV", csv, "system_report.csv", "text/csv")

elif view_mode == "System Health":
    st.subheader("Node Health Status")
    
    nodes = [f"worker-node-{i}" for i in range(1, 9)]
    status = np.random.choice(["Operational", "Degraded", "Maintenance"], size=8, p=[0.7, 0.2, 0.1])
    
    cols = st.columns(4)
    for i, (node, stat) in enumerate(zip(nodes, status)):
        color = "green" if stat == "Operational" else "orange" if stat == "Degraded" else "red"
        with cols[i % 4]:
            st.markdown(f"""
            <div style="border:1px solid #444; padding:10px; border-radius:5px; margin-bottom:10px; text-align:center;">
                <h4>{node}</h4>
                <p style="color:{color}; font-weight:bold;">{stat}</p>
            </div>
            """, unsafe_allow_html=True)
            
st.markdown("---")
st.caption("Generated by Python & Streamlit | Dashboard Demo")
