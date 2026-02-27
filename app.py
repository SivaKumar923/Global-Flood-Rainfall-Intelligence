import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Flood Intelligence", layout="wide")

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
Real-time hydrometeorological monitoring & flood risk intelligence
</p>
""", unsafe_allow_html=True)

st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")

API_KEY = "44e8c7f686dd477975e1eb85f8637d92"

# ---------- CITY SEARCH ----------
cities = ["Anantapur","Mumbai","London","Tokyo","New York","Sydney","Jakarta","Dubai","Paris","Singapore"]
city_name = st.selectbox("🔍 Search City", cities, index=0)

# ---------- GET COORDINATES ----------
geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
geo = requests.get(geo_url).json()

lat = geo[0]["lat"]
lon = geo[0]["lon"]
location = geo[0]["name"]

# ---------- FORECAST DATA ----------
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

# ---------- AI RISK SCORE ----------
risk_score = min(100, sum(rain_values) * 1.8)

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

c1,c2,c3,c4 = st.columns(4)

cards = [
    ("City", location),
    ("Past Rain", f"{rain_past} mm"),
    ("Next Rain", f"{rain_next} mm"),
    ("Flood Severity Index", f"{risk_score:.0f}/100"),
]

for col,(title,value) in zip([c1,c2,c3,c4], cards):
    col.markdown(f"""
    <div class="metric">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.write(f"🌤 Current Condition: **{weather}**")
st.write(f"Rainfall Intensity: **{intensity}**")

if risk == "HIGH":
    st.error("🚨 FLOOD ALERT: Immediate attention required")
elif risk == "MODERATE":
    st.warning("Waterlogging possible in low areas.")
else:
    st.success("Conditions safe.")

# ---------- RAINFALL TREND ----------
st.markdown('<div class="section">Rainfall Trend (Next 24 Hours)</div>', unsafe_allow_html=True)

df = pd.DataFrame({"Time": times, "Rainfall": rain_values})
st.line_chart(df.set_index("Time"))

# ---------- CITY MAP ----------
st.markdown('<div class="section">Flood Vulnerability & Risk Zones</div>', unsafe_allow_html=True)

city_map = folium.Map(location=[lat, lon], zoom_start=11)

folium.Circle([lat,lon], radius=3000, color=color, fill=True, fill_color=color, fill_opacity=0.25).add_to(city_map)

folium.Marker([lat,lon], popup=f"{location} - Risk: {risk}",
              icon=folium.Icon(color=color)).add_to(city_map)

# Heatmap overlay
HeatMap([[lat, lon, rain_next]]).add_to(city_map)

# Satellite precipitation layer
folium.TileLayer(
    tiles=f'https://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}',
    attr='OpenWeatherMap',
    name='Precipitation',
    overlay=True,
    control=True
).add_to(city_map)

folium.LayerControl().add_to(city_map)

st_folium(city_map, width=1200, height=450)

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

highest_city=None
highest_rain=0
city_rain_data={}

for city,(clat,clon) in global_cities.items():
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

# ---------- WORLD MAP ----------
st.markdown('<div class="section">Global Rainfall Risk Map</div>', unsafe_allow_html=True)

world_map=folium.Map(location=[20,0],zoom_start=2)

for city,(clat,clon) in global_cities.items():
    rain_val=city_rain_data[city]

    if rain_val>=25:
        c="red"
    elif rain_val>5:
        c="orange"
    else:
        c="green"

    folium.Marker([clat,clon], tooltip=city,
                  popup=f"{city}: {rain_val} mm",
                  icon=folium.Icon(color=c)).add_to(world_map)

st_folium(world_map, width=1200, height=500)

if highest_city:
    st.error(f"Highest rainfall risk: {highest_city} ({highest_rain} mm)")

# ---------- LEGEND ----------
st.markdown("### Risk Legend")
st.write("🟢 Low Risk")
st.write("🟠 Moderate Risk")
st.write("🔴 High Risk")

# ---------- SAFETY ----------
st.markdown('<div class="section">Safety Precautions</div>', unsafe_allow_html=True)

tips=[
"Avoid low-lying roads and underpasses.",
"Do not drive through floodwater.",
"Stay updated with weather alerts.",
"Keep emergency supplies ready.",
"Move valuables to higher levels if rain continues."
]

for t in tips:
    st.write("✔",t)

st.caption("Smart flood monitoring & disaster preparedness system")