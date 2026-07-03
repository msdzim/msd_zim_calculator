import streamlit as st
from psychro_core import ZIM_STATIONS, calculate_humidity_and_dewpoint

# Configure the web page layout setup
st.set_page_config(page_title="MSD Zim Psychrometric Calculator", page_icon="🌤️", layout="centered")

# Visual Web Headers
st.title("🇿🇼 MSD Zim Psychrometric Calculator")
st.markdown("### Altitude-Adjusted Psychrometric Calculations")
st.write("Official station parameters lookup designed for synoptic and research observers.")

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
            db_val = float(db_input)
            wb_val = float(wb_input)
            
            results = calculate_humidity_and_dewpoint(db_val, wb_val, altitude)
            
            st.success("### Calculations Complete")
            
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