import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap
import requests
import pandas as pd
from datetime import datetime
import base64

st.set_page_config(page_title="Urban Flood Intelligence India", layout="wide")

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
Monsoon flood risk intelligence & emergency response system
</p>
""", unsafe_allow_html=True)

st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")

API_KEY = "44e8c7f686dd477975e1eb85f8637d92"

# ---------- ALARM ----------
def play_alarm():
    sound_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
    st.markdown(f"""
        <audio autoplay>
        <source src="{sound_url}" type="audio/wav">
        </audio>
    """, unsafe_allow_html=True)

# ---------- INDIAN CITIES ----------
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

# ---------- WEATHER ----------
url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
forecast = requests.get(url).json()

rain_values=[]
times=[]

for entry in forecast["list"][:8]:
    rain = entry.get("rain", {}).get("3h", 0)
    rain_values.append(rain)
    times.append(entry["dt_txt"][11:16])

rain_next = rain_values[0]
rain_past = rain_values[1]

weather = forecast["list"][0]["weather"][0]["main"]

# ---------- INTENSITY ----------
if rain_next < 2:
    intensity="Light Rain"
elif rain_next < 10:
    intensity="Moderate Rain"
else:
    intensity="Heavy Rain"

# ---------- FLOOD RISK INDEX ----------
risk_score = min(100, sum(rain_values)*2)

if risk_score < 20:
    risk="LOW"
    color="green"
elif risk_score < 50:
    risk="MODERATE"
    color="orange"
else:
    risk="HIGH"
    color="red"

drainage_warning = rain_next > 20

# ---------- DASHBOARD ----------
st.markdown('<div class="section">Urban Flood Dashboard</div>', unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)

cards=[
("City",city_name),
("Past Rain",f"{rain_past} mm"),
("Next Rain",f"{rain_next} mm"),
("Flood Risk Index",f"{risk_score:.0f}/100")
]

for col,(t,v) in zip([c1,c2,c3,c4],cards):
    col.markdown(f"""
    <div class="metric">
    <div class="metric-title">{t}</div>
    <div class="metric-value">{v}</div>
    </div>
    """,unsafe_allow_html=True)

st.write(f"🌤 Weather: **{weather}**")
st.write(f"Rainfall Intensity: **{intensity}**")

# ---------- ALERT ----------
if risk=="HIGH":
    st.error("🚨 EXTREME URBAN FLOOD RISK")
    play_alarm()
elif risk=="MODERATE":
    st.warning("⚠ Waterlogging possible")
else:
    st.success("Conditions normal")

if drainage_warning:
    st.error("⚠ Drainage overload risk due to heavy rainfall")

# ---------- TREND ----------
st.markdown('<div class="section">Rainfall Trend (Next 24 Hours)</div>', unsafe_allow_html=True)
df=pd.DataFrame({"Time":times,"Rainfall":rain_values})
st.line_chart(df.set_index("Time"))

# ---------- EMERGENCY RESPONSE ----------
st.markdown('<div class="section">Emergency Response</div>', unsafe_allow_html=True)

if risk=="HIGH":
    st.warning("Move to elevated safe areas immediately")

    st.markdown("### ☎ Emergency Contacts")
    st.write("Disaster Management: **112**")
    st.write("Flood Helpline: **1070**")
    st.write("District Control Room: **1077**")

    safe_zones=[
        ("Government School High Ground", lat+0.03, lon+0.02),
        ("City Stadium Safe Zone", lat-0.025, lon+0.03),
        ("Collector Office Complex", lat+0.02, lon-0.025)
    ]

    st.markdown("### 🧭 Safe Elevated Areas")
    for name,_,_ in safe_zones:
        st.write("✔",name)

    st.markdown("### 🚦 Traffic Diversion")
    st.write("Use elevated flyovers and ring roads.")
    st.write("Avoid underpasses and low roads.")
    st.write("Follow police diversion routes.")
else:
    st.info("No evacuation required.")

# ---------- MAP ----------
st.markdown('<div class="section">Flood Risk & Safe Zone Map</div>', unsafe_allow_html=True)

m=folium.Map(location=[lat,lon],zoom_start=11)

folium.Circle([lat,lon],radius=3000,color=color,
fill=True,fill_color=color,fill_opacity=0.25).add_to(m)

# hotspots
for h in [[lat+0.02,lon+0.02],[lat-0.015,lon+0.01],[lat+0.01,lon-0.02]]:
    folium.CircleMarker(h,radius=6,color="blue",fill=True).add_to(m)

# safe zones markers
if risk=="HIGH":
    for name,slat,slon in safe_zones:
        folium.Marker([slat,slon],popup=name,
        icon=folium.Icon(color="green")).add_to(m)

HeatMap([[lat,lon,rain_next]]).add_to(m)

st_folium(m,width=1200,height=450)

# ---------- NATIONAL MONITOR ----------
st.markdown('<div class="section">Indian Cities Rainfall Monitor</div>', unsafe_allow_html=True)

highest_city=None
highest_rain=0

for city,(clat,clon) in cities.items():
    url=f"https://api.openweathermap.org/data/2.5/forecast?lat={clat}&lon={clon}&appid={API_KEY}&units=metric"
    data=requests.get(url).json()
    rain=data["list"][0].get("rain",{}).get("3h",0)

    if rain>highest_rain:
        highest_rain=rain
        highest_city=city

    if rain>=25:
        st.error(f"{city}: EXTREME RAIN")
    elif rain>5:
        st.warning(f"{city}: Heavy Rain")
    else:
        st.success(f"{city}: Normal")

if highest_city:
    st.error(f"⚠ Highest rainfall risk: {highest_city} ({highest_rain} mm)")

# ---------- SAFETY ----------
st.markdown('<div class="section">Monsoon Preparedness</div>', unsafe_allow_html=True)

tips=[
"Avoid low-lying roads during heavy rain.",
"Do not drive through floodwater.",
"Plan alternate routes.",
"Keep emergency supplies ready.",
"Follow municipal alerts."
]

for t in tips:
    st.write("✔",t)

st.caption("Designed for Indian urban flood preparedness & emergency response")