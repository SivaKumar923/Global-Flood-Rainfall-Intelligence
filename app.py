import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import pandas as pd

st.set_page_config(layout="wide")

# ---------- MODERN UI ----------
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
Global Flood & Rainfall Intelligence
</h1>
<p style='text-align:center;color:gray;'>
AI-driven rainfall monitoring and flood risk prediction
</p>
""", unsafe_allow_html=True)

API_KEY = "44e8c7f686dd477975e1eb85f8637d92"

# ---------- AUTOCOMPLETE CITY SEARCH ----------
popular_cities = [
    "Anantapur","Mumbai","Chennai","Hyderabad","Delhi",
    "Tokyo","New York","London","Sydney","Jakarta",
    "Lima","Bangkok","Singapore","Dubai","Paris"
]

city_name = st.selectbox("🔍 Search City", popular_cities, index=0)

# ---------- GET CITY COORDINATES ----------
geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
geo_response = requests.get(geo_url).json()

lat = geo_response[0]["lat"]
lon = geo_response[0]["lon"]
location = geo_response[0]["name"]

# ---------- FORECAST DATA ----------
forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
forecast = requests.get(forecast_url).json()

rain_values = []
times = []

for entry in forecast["list"][:8]:   # next 24 hours (3-hr blocks)
    rain = entry.get("rain", {}).get("3h", 0)
    rain_values.append(rain)
    times.append(entry["dt_txt"][11:16])

rain_next = rain_values[0]
rain_past = rain_values[1]

# ---------- AI FLOOD RISK SCORING ----------
risk_score = min(100, (sum(rain_values) * 1.8))

if risk_score < 20:
    risk = "LOW"
    color = "green"
elif risk_score < 50:
    risk = "MODERATE"
    color = "orange"
else:
    risk = "HIGH"
    color = "red"

# ---------- DASHBOARD ----------
st.markdown('<div class="section">City Rainfall Dashboard</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

cards = [
    ("City", location),
    ("Past Rain", f"{rain_past} mm"),
    ("Next Rain", f"{rain_next} mm"),
    ("AI Risk Score", f"{risk_score:.0f}/100"),
]

for col, (title, value) in zip([c1,c2,c3,c4], cards):
    col.markdown(f"""
    <div class="metric">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- ALERT ----------
if risk == "LOW":
    st.success("Conditions safe.")
elif risk == "MODERATE":
    st.warning("Waterlogging possible in low areas.")
else:
    st.error("HIGH FLOOD RISK — Avoid low-lying roads.")

# ---------- RAINFALL TREND CHART ----------
st.markdown('<div class="section">Rainfall Trend (Next 24 Hours)</div>', unsafe_allow_html=True)

df = pd.DataFrame({
    "Time": times,
    "Rainfall (mm)": rain_values
})

st.line_chart(df.set_index("Time"))

# ---------- CITY MAP ----------
st.markdown('<div class="section">City Risk Map</div>', unsafe_allow_html=True)

city_map = folium.Map(location=[lat, lon], zoom_start=11)

folium.Circle(
    [lat, lon],
    radius=3000,
    color=color,
    fill=True,
    fill_color=color,
    fill_opacity=0.25,
).add_to(city_map)

folium.Marker(
    [lat, lon],
    popup=f"{location}<br>Risk: {risk}",
    tooltip=location,
    icon=folium.Icon(color=color),
).add_to(city_map)

folium_static(city_map, width=1200, height=450)

# ---------- GLOBAL MONITOR ----------
st.markdown('<div class="section">Global Heavy Rain Monitor</div>', unsafe_allow_html=True)

global_cities = {
    "Mumbai": (19.0760,72.8777),
    "Jakarta": (-6.2088,106.8456),
    "Tokyo": (35.6762,139.6503),
    "New York": (40.7128,-74.0060),
    "Sydney": (-33.8688,151.2093),
    "London": (51.5074,-0.1278),
}

highest_city = None
highest_rain = 0
city_rain_data = {}

for city,(clat,clon) in global_cities.items():
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={clat}&lon={clon}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()
    rain_val = data["list"][0].get("rain", {}).get("3h", 0)
    city_rain_data[city] = rain_val

    if rain_val > highest_rain:
        highest_rain = rain_val
        highest_city = city

    if rain_val >= 25:
        st.error(f"🌧 {city}: {rain_val} mm — EXTREME")
    elif rain_val > 5:
        st.warning(f"{city}: {rain_val} mm — Heavy")
    else:
        st.success(f"{city}: Normal")

# ---------- WORLD MAP ----------
st.markdown('<div class="section">Global Rainfall Risk Map</div>', unsafe_allow_html=True)

world_map = folium.Map(location=[20,0], zoom_start=2)

for city,(clat,clon) in global_cities.items():
    rain_val = city_rain_data[city]

    if rain_val >= 25:
        marker_color = "red"
        status = "Extreme"
    elif rain_val > 5:
        marker_color = "orange"
        status = "Heavy"
    else:
        marker_color = "green"
        status = "Normal"

    folium.Marker(
        [clat,clon],
        popup=f"{city}<br>{rain_val} mm<br>{status}",
        tooltip=city,
        icon=folium.Icon(color=marker_color),
    ).add_to(world_map)

folium_static(world_map, width=1200, height=500)

if highest_city:
    st.error(f"🌧 Highest rainfall risk: {highest_city} ({highest_rain} mm)")

# ---------- SAFETY PRECAUTIONS ----------
st.markdown('<div class="section">Safety Precautions</div>', unsafe_allow_html=True)

precautions = [
    "Avoid low-lying roads and underpasses.",
    "Stay updated with local weather alerts.",
    "Do not attempt to walk or drive through floodwaters.",
    "Keep emergency contacts and essentials ready.",
    "Move valuables to higher levels if heavy rain continues."
]

for p in precautions:
    st.write("✔", p)

st.caption("AI-powered flood risk intelligence prototype")