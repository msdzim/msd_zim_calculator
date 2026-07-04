import streamlit as st
from psychro_core import ZIM_STATIONS, calculate_humidity_and_dewpoint

st.set_page_config(page_title="MSD Zim Calculator", page_icon="🌦️", layout="centered")

def strict_shorthand_corrector(val):
    try:
        val_str = str(val).strip()
        if not val_str: return None
        if '.' in val_str: return float(val_str)
        is_negative = val_str.startswith('-')
        if is_negative: val_str = val_str.lstrip('-')
        if len(val_str) == 1: val_str = '0' + val_str
        corrected_str = val_str[:-1] + '.' + val_str[-1]
        final_num = float(corrected_str)
        return -final_num if is_negative else final_num
    except:
        return None

# Simple Title
st.title("🌦️ MSD Psychrometric Calculator")
st.write("Live lookup for Relative Humidity (RH) & Dew Point Parameters.")
st.divider()

# Extended metadata dictionary tracking provinces
STATION_PROVINCES = {
    "Banket": "Mashonaland West",
    "Beitbridge": "Matabeleland South",
    "Binga": "Matabeleland North",
    "Buffalo Range": "Masvingo",
    "Buhera": "Manicaland",
    "Bulawayo (Goetz Obsy)": "Bulawayo",
    "Bulawayo (JNM Airport)": "Bulawayo",
    "Chibero": "Mashonaland West",
    "Chinhoyi": "Mashonaland West",
    "Chipinge": "Manicaland",
    "Chisengu": "Manicaland",
    "Chisumbanje": "Manicaland",
    "Chivhu": "Mashonaland East",
    "Gokwe": "Midlands",
    "Grand Reef Airport": "Manicaland",
    "Guruve": "Mashonaland Central",
    "Gweru": "Midlands",
    "Harare (Belvedere)": "Harare",
    "Harare (RG Mugabe Int'l)": "Harare",
    "Henderson": "Mashonaland Central",
    "Hwange National Park": "Matabeleland North",
    "Kadoma": "Mashonaland West",
    "Kanyemba": "Mashonaland Central",
    "Kariba": "Mashonaland West",
    "Karoi": "Mashonaland West",
    "Kezi": "Matabeleland South",
    "Kwekwe": "Midlands",
    "Lupane": "Matabeleland North",
    "Makoholi": "Masvingo",
    "Marondera": "Mashonaland East",
    "Masvingo": "Masvingo",
    "Matopos": "Matabeleland South",
    "Mhondoro": "Mashonaland West",
    "Mount Darwin": "Mashonaland Central",
    "Mukandi": "Manicaland",
    "Mutare": "Manicaland",
    "Mvurwi": "Mashonaland Central",
    "Nkayi": "Matabeleland North",
    "Nyanga": "Manicaland",
    "Plumtree": "Matabeleland South",
    "Rupike": "Masvingo",
    "Rusape": "Manicaland",
    "Tsholotsho": "Matabeleland North",
    "Victoria Falls": "Matabeleland North",
    "Wedza": "Mashonaland East",
    "West Nicholson (Gwanda)": "Matabeleland South",
    "Zaka": "Masvingo",
    "Zvishavane": "Midlands"
}

# Safely inject missing stations dynamically with accurate baseline parameters
if "Banket" not in ZIM_STATIONS:
    ZIM_STATIONS["Banket"] = {"altitude": 1145}
if "Zvishavane" not in ZIM_STATIONS:
    ZIM_STATIONS["Zvishavane"] = {"altitude": 918}

# Alphabetically sort the stations pulled from psychro_core
sorted_station_names = sorted(list(ZIM_STATIONS.keys()))

# Format drop-down options to visually display the Province alongside the name
station_options = {name: f"{name} ({STATION_PROVINCES.get(name, 'Unknown Province')})" for name in sorted_station_names}

selected_name = st.selectbox(
    "Select Weather Station:", 
    options=sorted_station_names, 
    format_func=lambda x: station_options[x]
)

station_meta = ZIM_STATIONS[selected_name]
altitude = station_meta.get("altitude", station_meta.get("Altitude", 1400))
province_label = STATION_PROVINCES.get(selected_name, "Unknown")

# Display metadata line directly underneath selection box
st.markdown(f"📍 **Province:** {province_label} | **Base Altitude:** {altitude} meters")

# Main Input fields stacked vertically
dry_input = st.text_input("Dry Bulb Temp (°C or shorthand):")
wet_input = st.text_input("Wet Bulb Temp (°C or shorthand):")

# Button matches the text in image 49709.jpg
if st.button("Calculate Atmospheric Values"):
    try:
        t_dry = float(strict_shorthand_corrector(dry_input))
        t_wet = float(strict_shorthand_corrector(wet_input))
        
        calc_result = calculate_humidity_and_dewpoint(t_dry, t_wet, altitude)
        
        # Extract fields directly from the dictionary returned by psychro_core
        if isinstance(calc_result, dict):
            pressure = calc_result.get("station_pressure", "N/A")
            rh = calc_result.get("rh", calc_result.get("relative_humidity", "N/A"))
            dew_point = calc_result.get("dewpoint", calc_result.get("dew_point", "N/A"))
        else:
            # Fallback if it returns a tuple
            pressure = "N/A"
            rh = calc_result[0] if len(calc_result) > 0 else "N/A"
            dew_point = calc_result[1] if len(calc_result) > 1 else "N/A"
        
        # Green success banner matching image 49709.jpg
        st.success("Calculations Complete")
        
        # Format strings for clean metric display
        display_pres = f"{pressure:.1f} hPa" if isinstance(pressure, (int, float)) else f"{pressure}"
        display_rh = f"{rh:.1f} %" if isinstance(rh, (int, float)) else f"{rh}"
        display_dp = f"{dew_point:.1f} °C" if isinstance(dew_point, (int, float)) else f"{dew_point}"
        
        # Single column layout metric blocks matching the look in the picture
        st.metric("Station Pressure", display_pres)
        st.metric("Relative Humidity (RH)", display_rh)
        st.metric("Dewpoint Temperature", display_dp)
        
    except Exception as e:
        st.error(f"Error parsing inputs. Please verify entries format. Details: {e}")
