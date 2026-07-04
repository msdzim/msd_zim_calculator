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

# --- MSD SEASON & REMINDERS ENGINE ---
def get_msd_climate_status():
    today = datetime.date.today()
    this_year = today.year
    reminders = []
    
    # 1. Permanent Season Tracker (Every Day)
    # Winter: 1 May to 30 September
    # Summer: 1 October to 30 April
    winter_start = datetime.date(this_year, 5, 1)
    winter_end = datetime.date(this_year, 9, 30)
    
    if winter_start <= today <= winter_end:
        current_season = "❄️ **Current Season:** MSD Winter Period (1 May - 30 Sep)"
    else:
        current_season = "☀️ **Current Season:** MSD Summer Period (1 Oct - 30 Apr)"
        
    # 2. Transition Reminders (Trigger 3 days before start)
    events = [
        {"name": "World Meteorological Day", "month": 3, "day": 23},
        {"name": "MSD March Equinox Window (1 Mar - 11 Apr)", "month": 3, "day": 1},
        {"name": "MSD September Equinox Window (3 Sep - 14 Oct)", "month": 9, "day": 3}
    ]
    
    for ev in events:
        event_date = datetime.date(this_year, ev["month"], ev["day"])
        delta = (event_date - today).days
        if 0 <= delta <= 3:
            reminders.append(f"⏰ **Upcoming Milestone:** {ev['name']} begins in {delta} days!")
            
    return current_season, reminders

# Visual Web Headers
st.title("🌦️ MSD Psychrometric Calculator")
st.write("Live lookup for Relative Humidity (RH) & Dew Point Parameters.")

# Fetch Climate Season and Reminders
season_status, active_reminders = get_msd_climate_status()

# Display permanent daily season marker
st.sidebar.markdown("### 📅 Station Climate Tracker")
st.sidebar.info(season_status)

# Display active notifications if found within the 3-day window
for reminder in active_reminders:
    st.warning(reminder)

st.divider()

col1, col2 = st.columns(2)

with col1:
    selected_station = st.selectbox("Select Weather Station:", list(ZIM_STATIONS.keys()))
    station_meta = ZIM_STATIONS[selected_station]
    
    # SAFE FIX: Checks both lowercase 'altitude' and uppercase 'Altitude' to prevent KeyError crashes
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
        
        # FIXED: Added the third variable slot '_' to successfully capture and hide the station pressure output
        rh, dew_point, _ = calculate_humidity_and_dewpoint(t_dry, t_wet, altitude)
        
        st.divider()
        
        # --- OFFICIAL TEMPERATURE CLASSIFICATION (From b7c9b6f1-ffa5-4679-91b8-1b06f65fdd9e) ---
        comfort = "Normal"
        # Determine the correct altitude column to map against
        if altitude < 1125:
            # 1000m Column
            if 37.0 <= t_dry <= 40.0: comfort = "Very hot 🔥"
            elif 33.0 <= t_dry <= 36.0: comfort = "Hot ☀️"
            elif 29.0 <= t_dry <= 32.0: comfort = "Warm 🌤️"
            elif 25.0 <= t_dry <= 28.0: comfort = "Mild 🍃"
            elif 21.0 <= t_dry <= 24.0: comfort = "Cool 🧥"
            elif 13.0 <= t_dry <= 16.0: comfort = "Cold 🥶"
        elif altitude < 1375:
            # 1250m Column
            if 35.0 <= t_dry <= 38.0: comfort = "Very hot 🔥"
            elif 31.0 <= t_dry <= 34.0: comfort = "Hot ☀️"
            elif 27.0 <= t_dry <= 30.0: comfort = "Warm 🌤️"
            elif 23.0 <= t_dry <= 26.0: comfort = "Mild 🍃"
            elif 19.0 <= t_dry <= 22.0: comfort = "Cool 🧥"
            elif 11.0 <= t_dry <= 14.0: comfort = "Cold 🥶"
        else:
            # 1500m Column
            if 33.0 <= t_dry <= 36.0: comfort = "Very hot 🔥"
            elif 29.0 <= t_dry <= 32.0: comfort = "Hot ☀️"
            elif 25.0 <= t_dry <= 28.0: comfort = "Warm 🌤️"
            elif 21.0 <= t_dry <= 24.0: comfort = "Mild 🍃"
            elif 17.0 <= t_dry <= 20.0: comfort = "Cool 🧥"
            elif 9.0 <= t_dry <= 12.0: comfort = "Cold 🥶"

        # --- GROUND FROST RISK ESTIMATION (From b7c9b6f1-ffa5-4679-91b8-1b06f65fdd9e) ---
        # Ground temperature drops below screen temperature on radiating nights. 
        estimated_ground_temp = t_dry - 4.0 
        
        if estimated_ground_temp <= 2.0:
            st.subheader("❄️ Ground Frost Assessment")
            if estimated_ground_temp < -4.0:
                st.error("🚨 Severe Ground Frost Expected (Lower than -4°C at ground level)")
            elif -4.0 <= estimated_ground_temp <= -3.0:
                st.error("⚠️ Moderate to Severe Ground Frost Expected (-3°C to -4°C at ground level)")
            elif -3.0 <= estimated_ground_temp <= -2.0:
                st.warning("⚠️ Moderate Ground Frost Expected (-2°C to -3°C at ground level)")
            elif -2.0 <= estimated_ground_temp <= 1.0:
                st.warning("❄️ Slight to Moderate Ground Frost Expected (-1°C to 2°C at ground level)")
            elif -1.0 <= estimated_ground_temp <= 0.0:
                st.info("❄️ Slight Ground Frost Expected (0°C to -1°C at ground level)")

        # --- CONVECTIVE CUMULUS CLOUD BASE (8 AM to 3 PM Window) ---
        start_time = datetime.time(8, 0)
        end_time = datetime.time(15, 0)
        
        if start_time <= obs_time <= end_time:
            st.subheader("☁️ Convective Cloud Assessment (Cumulus Only)")
            if t_dry > dew_point:
                # Espy's Equation for solar convection cloud bases
                cb_height = (t_dry - dew_point) * 122
                st.success(f"Estimated Cumulus Base Height: **{int(cb_height)} meters** above station ground level.")
            else:
                st.caption("Air is saturated at surface; cloud base cannot be estimated via dry convection.")

        # Main metrics display
        st.subheader("📊 Output Parameters")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Relative Humidity", f"{rh:.1f}%")
        res_col2.metric("Dew Point", f"{dew_point:.1f} °C")
        res_col3.metric("Thermal State", comfort)
        
    except Exception as e:
        st.error(f"Error parsing inputs. Please verify entries format. Details: {e}")
