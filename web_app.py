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
    if altitude_m >= 1375:
        if t_dry >= 33.0: return "Very Hot 🔴"
        elif t_dry >= 29.0: return "Hot 🟠"
        elif t_dry >= 25.0: return "Warm 🟡"
        elif t_dry >= 21.0: return "Mild 🟢"
        elif t_dry >= 17.0: return "Cool 🔵"
        else: return "Cold ❄️"
    elif altitude_m >= 1125:
        if t_dry >= 35.0: return "Very Hot 🔴"
        elif t_dry >= 31.0: return "Hot 🟠"
        elif t_dry >= 27.0: return "Warm 🟡"
        elif t_dry >= 23.0: return "Mild 🟢"
        elif t_dry >= 19.0: return "Cool 🔵"
        else: return "Cold ❄️"
    else:
        if t_dry >= 37.0: return "Very Hot 🔴"
        elif t_dry >= 33.0: return "Hot 🟠"
        elif t_dry >= 29.0: return "Warm 🟡"
        elif t_dry >= 25.0: return "Mild 🟢"
        elif t_dry >= 21.0: return "Cool 🔵"
        else: return "Cold ❄️"

# Configure the web page layout setup
st.set_page_config(page_title="MSD Zim Calculator", page_icon="🌦️", layout="centered")

# --- PROFESSIONAL CENTERED HEADER BLOCK ---
try:
    official_logo = "https://weadapt.org/wp-content/uploads/2023/05/msd_logo.jpg"
    img_col1, img_col2, img_col3 = st.columns([1, 1.2, 1])
    with img_col2:
        st.image(official_logo, use_container_width=True)
except:
    pass

# Title streamlined to remove the redundant "MSD" text
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>Psychrometric Calculator</h1>", unsafe_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Live lookup for Relative Humidity (RH) & Dew Point Parameters.</p>", unsafe_html=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    selected_station = st.selectbox(
        "Select Weather Station:",
        options=sorted(list(ZIM_STATIONS.keys()))
    )
    altitude = ZIM_STATIONS[selected_station]["altitude_m"]
    province = ZIM_STATIONS[selected_station]["province"]
    st.caption(f"📍 Province: {province} | Base Altitude: {altitude} meters")

with col2:
    db_input = st.text_input("Dry Bulb Temp (°C or shorthand):", placeholder="e.g., 24.9 or 249")
    wb_input = st.text_input("Wet Bulb Temp (°C or shorthand):", placeholder="e.g., 21.3 or 213")

st.divider()

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

            temp_condition = get_temperature_description(db_val, altitude)
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
