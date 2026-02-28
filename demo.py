import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap
import requests
from datetime import datetime

st.set_page_config(page_title="Flood Emergency Demo", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {background-color:#0e1117;}
.alert {
    padding:18px;
    border-radius:12px;
    text-align:center;
    font-weight:700;
    font-size:22px;
    animation: blink 1s infinite;
}
@keyframes blink {50% {opacity:0.3;}}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center;
background: linear-gradient(90deg,#60a5fa,#22d3ee);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;'>
Flood Emergency Response System
</h1>
<p style='text-align:center;color:gray;'>
Rainfall prediction • siren alerts • evacuation guidance • traffic risk
</p>
""", unsafe_allow_html=True)

st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")

API_KEY = "44e8c7f686dd477975e1eb85f8637d92"

# ---------------- DEMO CONTROL PANEL ----------------
st.sidebar.title("🧪 DEMO CONTROL PANEL")

mode = st.sidebar.radio(
    "Select Weather Scenario",
    ["Normal Conditions", "Moderate Rain", "Heavy Rain (Flood Risk)"]
)

demo_rain = {
    "Normal Conditions": 1,
    "Moderate Rain": 8,
    "Heavy Rain (Flood Risk)": 28
}

rain_next = demo_rain[mode]
rain_past = rain_next / 2

# ---------------- FLOOD RISK ENGINE ----------------
river_level = rain_next * 0.6
risk_score = min(100, rain_next * 3)

if risk_score < 20:
    risk="LOW"
    color="green"
elif risk_score < 50:
    risk="MODERATE"
    color="orange"
else:
    risk="HIGH"
    color="red"

# ---------------- DASHBOARD ----------------
st.subheader("Rainfall Prediction Dashboard")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Rain (Last 3 hrs)", f"{rain_past} mm")
c2.metric("Rain (Next 3 hrs)", f"{rain_next} mm")
c3.metric("River Rise", f"{river_level:.1f} m")
c4.metric("Flood Risk Index", f"{risk_score}/100")

# ---------------- EMERGENCY ALERT ----------------
emergency_trigger = rain_next >= 20

if emergency_trigger:

    st.markdown("""
    <div class="alert" style="background:red;color:white;">
    🚨 FLOOD WARNING 🚨
    </div>
    """, unsafe_allow_html=True)

    st.error("Heavy rainfall predicted in next 3 hours!")

    # 🔊 LOOPING SIREN (FIXED — NO ERROR)
    st.audio(
        "https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg",
        autoplay=True,
        loop=True
    )

    st.warning("⚠ Move immediately to safe elevated areas.")

elif risk=="MODERATE":
    st.warning("⚠ Waterlogging possible in low areas.")
else:
    st.success("Conditions safe.")

# ---------------- MAP ----------------
st.subheader("Risk Zones & Evacuation Guidance")

lat, lon = 14.6819, 77.6006  # Anantapur demo location

city_map = folium.Map(location=[lat, lon], zoom_start=13)

# risk zone circle
folium.Circle([lat,lon],3000,color=color,fill=True,fill_opacity=0.25).add_to(city_map)

# flood-prone zones
flood_zones=[(lat+0.02,lon+0.01),(lat-0.015,lon-0.02)]
for f in flood_zones:
    folium.Circle(f,1000,color="red",fill=True,fill_opacity=0.4,
                  popup="Flood-Prone Area").add_to(city_map)

# shelters
shelters=[(lat+0.03,lon),(lat-0.03,lon+0.02)]
for s in shelters:
    folium.Marker(s,
        icon=folium.Icon(color="green",icon="home"),
        popup="Relief Shelter").add_to(city_map)

# elevated safe zones
safe_areas=[(lat+0.05,lon-0.02)]
for sa in safe_areas:
    folium.Marker(sa,
        icon=folium.Icon(color="blue",icon="arrow-up"),
        popup="Elevated Safe Zone").add_to(city_map)

# TRAFFIC CONGESTION during heavy rain
if emergency_trigger:
    traffic=[(lat+0.01,lon+0.03),(lat-0.02,lon+0.01)]
    for t in traffic:
        folium.Marker(t,
            icon=folium.Icon(color="orange",icon="road"),
            popup="Heavy Traffic Congestion").add_to(city_map)

HeatMap([[lat,lon,rain_next]]).add_to(city_map)

st_folium(city_map,width=1200,height=500)

# ---------------- EVACUATION MESSAGE ----------------
st.subheader("Evacuation Guidance")

if emergency_trigger:
    st.error("Proceed to nearest shelters and avoid flooded roads.")
elif risk=="MODERATE":
    st.warning("Avoid low-lying streets and underpasses.")
else:
    st.success("No evacuation needed.")

# ---------------- EMERGENCY CONTACT ----------------
st.subheader("Emergency Contacts")
st.write("☎ Disaster Response: 112")
st.write("🚑 Ambulance: 108")
st.write("👮 Police: 100")
st.write("🔥 Fire: 101")

# ---------------- SAFETY ----------------
st.subheader("Safety Tips")

tips=[
"Avoid walking or driving through flood water.",
"Switch off electricity in flooded homes.",
"Keep emergency kit ready.",
"Follow evacuation instructions.",
"Stay away from drains and canals."
]

for t in tips:
    st.write("✔", t)

st.caption("Demo system for flood early warning & emergency response")