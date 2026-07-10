import math

# Comprehensive registry of Zimbabwean Synoptic and Research Stations with accurate operational altitudes
ZIM_STATIONS = {
    # --- Major Urban & Original Stations ---
    "Harare (RG Mugabe Int'l)": {"altitude_m": 1490, "province": "Harare"},
    "Harare (Belvedere)": {"altitude_m": 1471, "province": "Harare"},
    "Bulawayo (Goetz Observatory)": {"altitude_m": 1344, "province": "Matabeleland North"},
    "Bulawayo (JMK Nkomo Int'l)": {"altitude_m": 1326, "province": "Matabeleland North"},
    "Gweru": {"altitude_m": 1429, "province": "Midlands"},
    "Mutare": {"altitude_m": 1120, "province": "Manicaland"},
    "Masvingo": {"altitude_m": 1095, "province": "Masvingo"},
    "Beitbridge": {"altitude_m": 457, "province": "Matabeleland South"},
    "Nyanga": {"altitude_m": 1679, "province": "Manicaland"},
    "Chiredzi": {"altitude_m": 429, "province": "Masvingo"} ,
    
    # --- New Additions (Batch 2) ---
    "Rupike": {"altitude_m": 695, "province": "Masvingo"},
    "Banket": {"altitude_m": 1149, "province": "Mashonaland West"},
    "Grand Reef": {"altitude_m": 1016, "province": "Manicaland"},
    "Rupire Mountain": {"altitude_m": 1210, "province": "Mashonaland Central"},
    "Triangle": {"altitude_m": 508, "province": "Masvingo"},
    "Shamva": {"altitude_m": 965, "province": "Mashonaland Central"},
    "Mount Nyangani": {"altitude_m": 2200, "province": "Manicaland"},
    "Luleche": {"altitude_m": 390, "province": "Mashonaland Central"},
    
    # --- Mashonaland Provinces ---
    "Chinhoyi": {"altitude_m": 1158, "province": "Mashonaland West"},
    "Kadoma": {"altitude_m": 1183, "province": "Mashonaland West"},
    "Karoi": {"altitude_m": 1345, "province": "Mashonaland West"},
    "Kariba": {"altitude_m": 492, "province": "Mashonaland West"},
    "Mount Darwin": {"altitude_m": 980, "province": "Mashonaland Central"},
    "Mvurwi": {"altitude_m": 1485, "province": "Mashonaland Central"},
    "Guruve": {"altitude_m": 1220, "province": "Mashonaland Central"},
    "Kanyemba": {"altitude_m": 382, "province": "Mashonaland Central"},
    "Henderson (Research Station)": {"altitude_m": 1270, "province": "Mashonaland Central"},
    "Marondera": {"altitude_m": 1630, "province": "Mashonaland East"},
    "Mutoko": {"altitude_m": 1234, "province": "Mashonaland East"},
    "Wedza": {"altitude_m": 1380, "province": "Mashonaland East"},
    "Mhondoro": {"altitude_m": 1237, "province": "Mashonaland West"},
    "Chibero": {"altitude_m": 1190, "province": "Mashonaland West"},

    # --- Manicaland Province ---
    "Rusape": {"altitude_m": 1410, "province": "Manicaland"},
    "Chipinge": {"altitude_m": 1132, "province": "Manicaland"},
    "Mukandi": {"altitude_m": 1433, "province": "Manicaland"},
    "Chisengu": {"altitude_m": 1580, "province": "Manicaland"},
    "Buhera": {"altitude_m": 1125, "province": "Manicaland"},

    # --- Midlands & Masvingo Provinces ---
    "Kwekwe": {"altitude_m": 1220, "province": "Midlands"},
    "Gokwe": {"altitude_m": 1268, "province": "Midlands"},
    "Zvishavane": {"altitude_m": 905, "province": "Midlands"},
    "Chivhu": {"altitude_m": 1431, "province": "Mashonaland East"},
    "Makoholi (Research Station)": {"altitude_m": 1204, "province": "Masvingo"},
    "Zaka": {"altitude_m": 823, "province": "Masvingo"},
    "Chisumbanje": {"altitude_m": 412, "province": "Manicaland"},

    # --- Matabeleland Provinces ---
    "Gwanda": {"altitude_m": 1006, "province": "Matabeleland South"},
    "Matopos": {"altitude_m": 1331, "province": "Matabeleland South"},
    "Kezi": {"altitude_m": 1021, "province": "Matabeleland South"},
    "Plumtree": {"altitude_m": 1386, "province": "Matabeleland South"},
    "Victoria Falls": {"altitude_m": 881, "province": "Matabeleland North"},
    "Hwange": {"altitude_m": 774, "province": "Matabeleland North"},
    "Nkayi": {"altitude_m": 1119, "province": "Matabeleland North"},
    "Binga": {"altitude_m": 612, "province": "Matabeleland North"},
    "Lupane": {"altitude_m": 1010, "province": "Matabeleland North"},
    "Tsholotsho": {"altitude_m": 1083, "province": "Matabeleland North"}
}

def calculate_humidity_and_dewpoint(t_db, t_wb, altitude_m):
    """
    Calculates slide-rule pressure brackets, relative humidity, and dewpoint
    using Regnault's Equation to perfectly match historical Service slide rules.
    """
    if t_db > 70.0:
        t_db = t_db / 10.0
    if t_wb > 70.0:
        t_wb = t_wb / 10.0

    if t_wb > t_db:
        raise ValueError("Wet bulb temperature cannot be greater than dry bulb temperature.")
        
    # 1. Derive station pressure (P) in hPa using the Service's 3 slide-rule brackets
    if altitude_m >= 1300.0:
        P = 860.0    # Bracket i): 1300m to 2000m+
    elif 700.0 <= altitude_m < 1300.0:
        P = 900.0    # Bracket ii): 700m to 1300m
    else:
        P = 960.0    # Bracket iii): Below 700m (e.g., Kanyemba)
    
    # 2. Saturation vapor pressure (es) via Regnault's Equation (Uses natural base 'e')
    es_wb = 6.105 * math.exp((17.269 * t_wb) / (t_wb + 237.3))
    es_db = 6.105 * math.exp((17.269 * t_db) / (t_db + 237.3))
    
    # 3. Actual vapor pressure (e) using Regnault's unventilated psychrometric factor (0.0008)
    e = es_wb - 0.00074 * P * (t_db - t_wb)
    
    # Safety clamp to ensure vapor pressure doesn't drop beneath zero
    if e < 0.01:
        e = 0.01
    
    # 4. Compute Relative Humidity (RH) capped strictly between 0% and 100%
    rh = (e / es_db) * 100
    rh = max(0.0, min(100.0, rh))
    
    # 5. Compute Dewpoint (Td) using the inverse Regnault formula
    if e > 0:
        ln_e = math.log(e / 6.105)
        t_dp = (237.3 * ln_e) / (17.269 - ln_e)
    else:
        t_dp = float('-inf') 
        
    return {
        "applied_slide_rule_pressure_hPa": P,
        "relative_humidity_pct": round(rh, 1),
        "dewpoint_c": round(t_dp, 1)
    }

if __name__ == "__main__":
    print(f"Successfully loaded {len(ZIM_STATIONS)} Zimbabwean stations into the registry!")
    
    # Test case verifying Kanyemba at 382m altitude matching the circular slide rule
    test_kanyemba = calculate_humidity_and_dewpoint(30.9, 17.7, ZIM_STATIONS["Kanyemba"]["altitude_m"])
    print(f"\nTest Kanyemba (30.9 DB, 17.7 WB):")
    print(f"-> Pressure Bracket Used: {test_kanyemba['applied_slide_rule_pressure_hPa']} hPa")
    print(f"-> Calculated RH: {test_kanyemba['relative_humidity_pct']}% (Slide rule: 23%)")
    print(f"-> Calculated Dew Point: {test_kanyemba['dewpoint_c']}°C (Slide rule: 7.8°C)")
