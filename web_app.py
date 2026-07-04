import streamlit as st
from psychro_core import ZIM_STATIONS, calculate_humidity_and_dewpoint

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

def get_temperature_description(t_dry, altitude_m):
    """
    Strictly maps the temperature to the official matrix columns from 
    file 5e1bd456-368a-4af6-85ca-9e49d31227dd based on nearest station altitude.
    """
    # Group the station into its closest table reference column
    if altitude_m >= 1375:
        # --- 1500m Column Thresholds ---
        if t_dry >= 33.0:
            return "Very Hot 🔴"
        elif t_dry >= 29.0:
            return "Hot 🟠"
        elif t_dry >= 25.0:
            return "Warm 🟡"
        elif t_dry >= 21.0:
            return "Mild 🟢"
        elif t_dry >= 17.0:
            return "Cool 🔵"  # Ensures 17°C in Harare (1490m) matches here perfectly
        else:
            return "Cold ❄️"
            
    elif altitude_m >= 1125:
        # --- 1250m Column Thresholds ---
        if t_dry >= 35.0:
            return "Very Hot 🔴"
        elif t_dry >= 31.0:
            return "Hot 🟠"
        elif t_dry >= 27.0:
            return "Warm 🟡"
        elif t_dry >= 23.0:
            return "Mild 🟢"
        elif t_dry >= 19.0:
            return "Cool 🔵"
        else:
            return "Cold ❄️"
            
    else:
        # --- 1000m Column Thresholds (And Low-veld Stations) ---
        if t_dry >= 37.0:
            return "Very Hot 🔴"
        elif t_dry >= 33.0:
            return "Hot 🟠"
        elif t_dry >= 29.0:
            return "Warm 🟡"
        elif t_dry >= 25.0:
            return "Mild 🟢"
        elif t_dry >= 21.0:
            return "Cool 🔵"
        else:
            return "Cold ❄️"

# Configure the web page layout setup
st.set_page_config(page_title="MSD Zim Calculator", page_icon="🌦️", layout="centered")

# Visual Web Headers
st.title("🌦️ MSD Psychrometric Calculator")
st.write("Live lookup for Relative Humidity (RH) & Dew Point Parameters.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    # Dropdown choice selection field
    selected_station = st.selectbox(
        "Select Weather Station:",
        options=sorted(list(ZIM_STATIONS.keys()))
    )
    
    altitude = ZIM_STATIONS[selected_station]["altitude_m"]
    province = ZIM_STATIONS[selected_station]["province"]
    st.caption(f"📍 Province: {province} | Base Altitude: {altitude} meters")

with col2:
    # Text entry inputs
    db_input = st.text_input("Dry Bulb Temp (°C or shorthand):", placeholder="e.g., 24.9 or 249")
    wb_input = st.text_input("Wet Bulb Temp (°C or shorthand):", placeholder="e.g., 21.3 or 213")

st.divider()

# Calculation execution block trigger
if st.button("Calculate Atmospheric Values", type="primary", use_container_width=True):
    if db_input and wb_input:
        try:
            db_val = strict_shorthand_corrector(db_input)
            wb_val = strict_shorthand_corrector(wb_input)
            
            if db_val is None or wb_val is None:
                st.error("⚠️ Invalid entry. Please check the entered values.")
                st.stop()

            results = calculate_humidity_and_dewpoint(db_val, wb_val, altitude)

            st.success("Calculations Complete")

            # Determine the condition using our fixed, strict-column logic
            temp_condition = get_temperature_description(db_val, altitude)

            # Displays your metrics alongside the new classification line
            st.markdown(f"### 🌡️ Temperature Condition: **{temp_condition}**")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("Station Pressure", f"{results['station_pressure_hPa']} hPa")
            res_col2.metric("Relative Humidity (RH)", f"{results['relative_humidity_pct']} %")
            res_col3.metric("Dewpoint Temperature", f"{results['dewpoint_c']} °C")

        except ValueError as e:
            if "Wet bulb" in str(e):
                st.error(f"Meteorological Rule Error: {str(e)}")
            else:
                st.error("Input Error: Please enter valid numeric temperatures.")
    else:
        st.warning("Please enter both Dry Bulb and Wet Bulb values before calculating.")
