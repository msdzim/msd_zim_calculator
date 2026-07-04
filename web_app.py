import streamlit as st
import datetime
from psychro_core import ZIM_STATIONS, calculate_humidity_and_dewpoint

# Configure the web page layout setup
st.set_page_config(page_title="MSD Zim Calculator", page_icon="🌦️", layout="centered")

# --- STRICT SHORTHAND ENGINE ---
def strict_shorthand_corrector(val):
    """
    If a decimal point is explicitly typed (e.g., '5.0'), it keeps it.
    Otherwise, it strictly treats the last digit as a decimal place.
    """
    try:
        val_str = str(val).strip()
        if not val_str:
            return None
        if '.' in val_str:
            return float(val_str)
            
        is_negative = val_str.startswith('-')
        if is_negative:
            val_str = val_str.lstrip('-')
            
        if len(val_str) == 1:
            val_str = '0' + val_str
            
        corrected_str = val_str[:-1] + '.' + val_str[-1]
        final_num = float(corrected_str)
        return -final_num if is_negative else final_num
    except (ValueError, TypeError):
        return None

# Visual Web Headers
st.title("🌦️ MSD Psychrometric Calculator")
st.write("Live lookup for Relative Humidity (RH) & Dew Point Parameters.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    selected_station = st.selectbox("Select Weather Station:", list(ZIM_STATIONS.keys()))
    station_meta = ZIM_STATIONS[selected_station]
    altitude = station_meta.get("altitude", station_meta.get("Altitude", 1400))
    st.caption(f"📍 Base Altitude: {altitude} meters")

with col2:
    obs_time = st.time_input("Observation Time (Local):", datetime.time(14, 0))
    dry_input = st.text_input("Dry Bulb Temp (°C or shorthand):", value="25.0")

wet_input = st.text_input("Wet Bulb Temp (°C or shorthand):", value="18.0")

# --- CALCULATION LOGIC WORKFLOW ---
if st.button("Calculate Parameters"):
    try:
        t_dry = float(strict_shorthand_corrector(dry_input))
        t_wet = float(strict_shorthand_corrector(wet_input))
        
        # Unpack the values returned from psychro_core
        # (Using a fallback wrapper to safely handle either 2 or 3 returned values seamlessly)
        calc_result = calculate_humidity_and_dewpoint(t_dry, t_wet, altitude)
        rh = calc_result[0]
        dew_point = calc_result[1]
        
        st.divider()

        # Main metrics display
        st.subheader("📊 Output Parameters")
        res_col1, res_col2 = st.columns(2)
        
        display_rh = f"{rh:.1f}%" if isinstance(rh, (int, float)) else str(rh)
        display_dp = f"{dew_point:.1f} °C" if isinstance(dew_point, (int, float)) else f"{dew_point} °C"
        
        res_col1.metric("Relative Humidity", display_rh)
        res_col2.metric("Dew Point", display_dp)
        
    except Exception as e:
        st.error(f"Error parsing inputs. Please verify entries format. Details: {e}")
