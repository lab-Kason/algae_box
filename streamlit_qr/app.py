"""
Streamlit Web App for Algae Box Monitoring
Replaces Flutter APK - accessible via QR code scan
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuration
BACKEND_URL = "https://labkason.pythonanywhere.com"

st.set_page_config(
    page_title="Algae Box Monitor",
    page_icon="🌿",
    layout="wide"
)

# Get tank_id from URL query parameter
query_params = st.query_params
tank_id = query_params.get("tank", "1")

# Custom CSS for better mobile display
st.markdown("""
<style>
    .big-font { font-size: 2rem !important; font-weight: bold; }
    .status-ok { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-danger { color: #dc3545; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def fetch_tank_info(tank_id):
    """Fetch tank details from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/tanks/{tank_id}", timeout=10)
        if response.status_code == 200:
            return response.json().get('tank')
    except Exception as e:
        st.error(f"Error fetching tank info: {e}")
    return None


def fetch_current_sensors(tank_id):
    """Fetch latest sensor readings"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/sensors/current/{tank_id}", timeout=10)
        if response.status_code == 200:
            return response.json().get('reading')
    except Exception as e:
        st.error(f"Error fetching sensors: {e}")
    return None


def fetch_sensor_history(tank_id, hours=24):
    """Fetch sensor history for charts"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/sensors/history/{tank_id}?hours={hours}", timeout=10)
        if response.status_code == 200:
            return response.json().get('readings', [])
    except Exception as e:
        st.error(f"Error fetching history: {e}")
    return []


def fetch_recommendations(tank_id):
    """Fetch recommendations for tank"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/recommendations/{tank_id}", timeout=10)
        if response.status_code == 200:
            return response.json().get('recommendations', [])
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
    return []


def fetch_species():
    """Fetch all algae species"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/species", timeout=10)
        if response.status_code == 200:
            return response.json().get('species', [])
    except Exception as e:
        st.error(f"Error fetching species: {e}")
    return []


def get_status_color(is_safe):
    """Return color based on safety status"""
    return "status-ok" if is_safe else "status-danger"


def main():
    # Header
    st.title("🌿 Algae Box Monitor")
    
    # Fetch tank info
    tank = fetch_tank_info(tank_id)
    
    if tank:
        st.markdown(f"### Tank: **{tank['name']}** ({tank['algae_type']})")
        st.caption(f"Volume: {tank['volume_liters']}L | Status: {tank['status']}")
    else:
        st.warning(f"Tank {tank_id} not found. Create a tank first.")
        
        # Tank creation form
        with st.expander("➕ Create New Tank"):
            with st.form("create_tank"):
                name = st.text_input("Tank Name")
                species_list = fetch_species()
                species_names = [s['name'] for s in species_list] if species_list else ["Spirulina", "Chlorella"]
                algae_type = st.selectbox("Algae Type", species_names)
                volume = st.number_input("Volume (Liters)", min_value=1.0, value=20.0)
                notes = st.text_area("Notes (optional)")
                
                if st.form_submit_button("Create Tank"):
                    try:
                        response = requests.post(f"{BACKEND_URL}/api/tanks", json={
                            "name": name,
                            "algae_type": algae_type,
                            "volume_liters": volume,
                            "notes": notes
                        }, timeout=10)
                        if response.status_code == 201:
                            st.success("Tank created! Refresh the page.")
                            st.rerun()
                        else:
                            st.error(f"Failed to create tank: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        return
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (10s)", value=True)
    
    # Fetch current sensor data
    sensors = fetch_current_sensors(tank_id)
    
    if sensors:
        st.markdown("---")
        st.subheader("📊 Current Readings")
        
        # Display metrics in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ph_status = "✅" if sensors.get('ph_safe', True) else "⚠️"
            st.metric(
                label=f"pH {ph_status}",
                value=f"{sensors['ph']:.2f}",
                delta=None
            )
        
        with col2:
            temp_status = "✅" if sensors.get('temperature_safe', True) else "⚠️"
            st.metric(
                label=f"Temperature {temp_status}",
                value=f"{sensors['temperature_c']:.1f}°C",
                delta=None
            )
        
        with col3:
            harvest_status = "🌾 Ready!" if sensors.get('harvest_ready', False) else "🌱 Growing"
            st.metric(
                label=f"Turbidity {harvest_status}",
                value=f"{sensors['turbidity_ntu']:.0f} NTU",
                delta=None
            )
        
        st.caption(f"Last updated: {sensors['timestamp']}")
        
    else:
        st.info("📡 Waiting for sensor data... Make sure the ESP32 is connected and sending data.")
    
    # Recommendations
    st.markdown("---")
    st.subheader("💡 Recommendations")
    
    recommendations = fetch_recommendations(tank_id)
    if recommendations:
        for rec in recommendations:
            priority = rec.get('priority', 'info')
            icon = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"
            st.markdown(f"{icon} **{rec.get('title', 'Tip')}**: {rec.get('message', '')}")
    else:
        st.success("✅ All parameters are within optimal range!")
    
    # Sensor History Chart
    st.markdown("---")
    st.subheader("📈 Sensor History (24h)")
    
    history = fetch_sensor_history(tank_id, hours=24)
    if history and len(history) > 1:
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        tab1, tab2, tab3 = st.tabs(["pH", "Temperature", "Turbidity"])
        
        with tab1:
            st.line_chart(df.set_index('timestamp')['ph'])
        
        with tab2:
            st.line_chart(df.set_index('timestamp')['temperature_c'])
        
        with tab3:
            st.line_chart(df.set_index('timestamp')['turbidity_ntu'])
    else:
        st.info("Not enough data for charts yet. Keep the sensors running!")
    
    # Actions
    st.markdown("---")
    st.subheader("⚙️ Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🌾 Start Harvest Collection"):
            try:
                response = requests.post(f"{BACKEND_URL}/api/collection/start/{tank_id}", timeout=10)
                if response.status_code == 200:
                    st.success("Harvest collection started!")
                else:
                    st.error(f"Failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("🔄 Force Refresh"):
            st.rerun()
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(10)
        st.rerun()


if __name__ == "__main__":
    main()
