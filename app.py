import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Urban Flood Intelligence - India", layout="wide")

# ---------- UI ----------
st.markdown("""
<style>
body {background-color: #0e1117;}
.metric {
    background: #161b22;
    padding: 18px;
    border-radius: 12px;
    text-align:center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.metric-title {color:#9ca3af;font-size:13px;}
.metric-value {color:white;font-size:26px;font-weight:600;}
.section {font-size:22px;font-weight:600;margin-top:20px;}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<h1 style='text-align:center;
background: linear-gradient(90deg,#60a5fa,#22d3ee);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;'>
🇮🇳 Smart Urban Flood Intelligence System
</h1>
<p style='text-align:center;color:gray;'>
Monsoon rainfall monitoring & urban flood risk intelligence for Indian cities
</p>
""", unsafe_allow_html=True)

st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")

API_KEY = "44e8c7f686dd477975e1eb85f8637d92"

# ---------- MAJOR INDIAN CITIES ----------
cities = {
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Mumbai": (19.0760, 72.8777),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Delhi": (28.6139, 77.2090),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Vijayawada": (16.5062, 80.6480),
    "Visakhapatnam": (17.6868, 83.2185),
    "Patna": (25.5941, 85.1376),
    "Guwahati": (26.1445, 91.7362)
}

city_name = st.selectbox("Select Indian City", list(cities.keys()))
lat, lon = cities[city_name]

# ---------- WEATHER DATA ----------
forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
forecast = requests.get(forecast_url).json()

rain_values = []
times = []

for entry in forecast["list"][:8]:
    rain = entry.get("rain", {}).get("3h", 0)
    rain_values.append(rain)
    times.append(entry["dt_txt"][11:16])

rain_next = rain_values[0]
rain_past = rain_values[1]

weather = forecast["list"][0]["weather"][0]["main"]

# ---------- RAIN INTENSITY ----------
if rain_next < 2:
    intensity = "Light Rain"
elif rain_next < 10:
    intensity = "Moderate Rain"
else:
    intensity = "Heavy Rain"

# ---------- URBAN FLOOD RISK INDEX ----------
risk_score = min(100, sum(rain_values) * 2)

if risk_score < 20:
    risk = "LOW"
    color = "green"
elif risk_score < 50:
    risk = "MODERATE"
    color = "orange"
else:
    risk = "HIGH"
    color = "red"

# ---------- DRAINAGE OVERLOAD WARNING ----------
drainage_warning = rain_next > 20

# ---------- DASHBOARD ----------
st.markdown('<div class="section">Urban Flood Dashboard</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

cards = [
    ("City", city_name),
    ("Past Rain", f"{rain_past} mm"),
    ("Next Rain", f"{rain_next} mm"),
    ("Urban Flood Risk Index", f"{risk_score:.0f}/100"),
]

for col,(title,value) in zip([c1,c2,c3,c4], cards):
    col.markdown(f"""
    <div class="metric">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.write(f"🌤 Weather: **{weather}**")
st.write(f"Rainfall Intensity: **{intensity}**")

# ---------- ALERTS ----------
if risk == "HIGH":
    st.error("🚨 HIGH URBAN FLOOD RISK")
elif risk == "MODERATE":
    st.warning("⚠ Waterlogging possible in low-lying areas")
else:
    st.success("Conditions normal")

if drainage_warning:
    st.error("⚠ Drainage Overload Warning: Heavy rainfall may overwhelm stormwater drains")

# ---------- TREND ----------
st.markdown('<div class="section">Rainfall Trend (Next 24 Hours)</div>', unsafe_allow_html=True)
df = pd.DataFrame({"Time": times, "Rainfall": rain_values})
st.line_chart(df.set_index("Time"))

# ---------- CITY MAP ----------
st.markdown('<div class="section">Flood Vulnerability Map</div>', unsafe_allow_html=True)

city_map = folium.Map(location=[lat, lon], zoom_start=11)

folium.Circle([lat, lon], radius=3000, color=color,
              fill=True, fill_color=color, fill_opacity=0.25).add_to(city_map)

folium.Marker([lat, lon],
              popup=f"{city_name} Risk: {risk}",
              icon=folium.Icon(color=color)).add_to(city_map)

# Simulated flood-prone hotspots
hotspots = [
    [lat+0.02, lon+0.02],
    [lat-0.015, lon+0.01],
    [lat+0.01, lon-0.02]
]

for h in hotspots:
    folium.CircleMarker(h, radius=6, color="blue", fill=True).add_to(city_map)

HeatMap([[lat, lon, rain_next]]).add_to(city_map)

st_folium(city_map, width=1200, height=450)

# ---------- NATIONAL MONITOR ----------
st.markdown('<div class="section">Indian Cities Rainfall Monitor</div>', unsafe_allow_html=True)

highest_city=None
highest_rain=0
city_rain_data={}

for city,(clat,clon) in cities.items():
    url=f"https://api.openweathermap.org/data/2.5/forecast?lat={clat}&lon={clon}&appid={API_KEY}&units=metric"
    data=requests.get(url).json()
    rain_val=data["list"][0].get("rain",{}).get("3h",0)
    city_rain_data[city]=rain_val

    if rain_val>highest_rain:
        highest_rain=rain_val
        highest_city=city

    if rain_val>=25:
        st.error(f"{city}: EXTREME RAIN")
    elif rain_val>5:
        st.warning(f"{city}: Heavy Rain")
    else:
        st.success(f"{city}: Normal")

if highest_city:
    st.error(f"⚠ Highest rainfall risk in India: {highest_city} ({highest_rain} mm)")

# ---------- MONSOON PREPAREDNESS ----------
st.markdown('<div class="section">Monsoon Preparedness & Safety</div>', unsafe_allow_html=True)

tips=[
"Avoid underpasses and low-lying roads during heavy rain.",
"Plan alternate travel routes during monsoon alerts.",
"Do not drive through waterlogged streets.",
"Keep emergency contacts and supplies ready.",
"Monitor local municipal flood alerts."
]

for t in tips:
    st.write("✔",t)

st.caption("Designed for Indian monsoon flood preparedness & smart city resilience")