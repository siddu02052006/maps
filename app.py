import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import math
import pydeck as pdk
import pandas as pd
import uuid
import time
import requests

# 🔥 CLICKABLE MAP SUPPORT
import folium
from streamlit_folium import st_folium

# 🔥 AUTO REFRESH
from streamlit_autorefresh import st_autorefresh

# 🔥 Firebase
import firebase_admin
from firebase_admin import credentials, db

# =====================================================
# ⭐ MAPBOX INTEGRATION
# =====================================================
pdk.settings.mapbox_api_key = st.secrets["MAPBOX_API_KEY"]

st.set_page_config(layout="wide", page_title="Precision Location System")

# =====================================================
# 🔁 LIVE AUTO REFRESH
# =====================================================
refresh_count = st_autorefresh(interval=10000, key="live_tracking_refresh")

# =====================================================
# FIREBASE INIT
# =====================================================
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://precision-location-hackathon-default-rtdb.firebaseio.com/"
    })

# =====================================================
# DEFAULT TARGET
# =====================================================
TARGET_LAT = 17.3850
TARGET_LON = 78.4867

st.title("🚀 Precision Location Identification System")
st.caption("🔥Real time Tracking Dashboard")

# =====================================================
# SESSION STATE
# =====================================================
if "history" not in st.session_state:
    st.session_state.history = []

if "uid" not in st.session_state:
    st.session_state.uid = str(uuid.uuid4())[:8]

if "prev_lat" not in st.session_state:
    st.session_state.prev_lat = None
if "prev_lon" not in st.session_state:
    st.session_state.prev_lon = None

if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = TARGET_LAT
if "selected_lon" not in st.session_state:
    st.session_state.selected_lon = TARGET_LON

# =====================================================
# 👑 ADMIN SYSTEM
# =====================================================
admin_ref = db.reference("admin").get()
if not admin_ref:
    db.reference("admin").set(st.session_state.uid)
admin_uid = db.reference("admin").get()
IS_ADMIN = admin_uid == st.session_state.uid

# =====================================================
# LOAD TARGET FROM FIREBASE
# =====================================================
target_ref = db.reference("target")
target_data = target_ref.get()

if target_data and "lat" in target_data and "lon" in target_data:
    TARGET_LAT = target_data["lat"]
    TARGET_LON = target_data["lon"]

# =====================================================
# DISTANCE CALCULATION
# =====================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# =====================================================
# 🧭 MAPBOX DIRECTIONS ROUTE FUNCTION (ADMIN ONLY)
# =====================================================
@st.cache_data(ttl=20)
def get_admin_route(start_lat, start_lon, end_lat, end_lon):

    MAPBOX_KEY = st.secrets["MAPBOX_API_KEY"]

    url = (
        f"https://api.mapbox.com/directions/v5/mapbox/walking/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
        f"?geometries=geojson&access_token={MAPBOX_KEY}"
    )

    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data["routes"][0]["geometry"]["coordinates"]
    except Exception as e:
        print("Mapbox Route Error:", e)

    return []

# =====================================================
# GET LIVE GPS
# =====================================================
coords = streamlit_js_eval(
    js_expressions="""
        new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    resolve({
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude,
                        accuracy: pos.coords.accuracy
                    });
                },
                (err) => reject(err.message)
            );
        })
    """,
    key="geo"
)

col1, col2 = st.columns([1,2])

# =====================================================
# LEFT PANEL
# =====================================================
with col1:

    st.subheader("📡 Live Verification Status")

    # =====================================================
    # 👑 ADMIN MAP PICKER
    # =====================================================
    if IS_ADMIN:

        st.markdown("### 👑 Pick Target On Map")

        pick_map = folium.Map(
            location=[TARGET_LAT, TARGET_LON],
            zoom_start=18,
            control_scale=True
        )

        folium.Marker(
            [TARGET_LAT, TARGET_LON],
            tooltip="Current Target",
            icon=folium.Icon(color="red")
        ).add_to(pick_map)

        map_data = st_folium(pick_map, height=250)

        if map_data and map_data.get("last_clicked"):
            st.session_state.selected_lat = map_data["last_clicked"]["lat"]
            st.session_state.selected_lon = map_data["last_clicked"]["lng"]

        st.write("📍 Selected Lat:", round(st.session_state.selected_lat,6))
        st.write("📍 Selected Lon:", round(st.session_state.selected_lon,6))

        if st.button("🎯 Set Target"):
            target_ref.set({
                "lat": st.session_state.selected_lat,
                "lon": st.session_state.selected_lon
            })
            TARGET_LAT = st.session_state.selected_lat
            TARGET_LON = st.session_state.selected_lon
            st.toast("🎯 Target updated from map selection")

    # =====================================================
    # USER GPS
    # =====================================================
    if coords:

        user_lat = coords["lat"]
        user_lon = coords["lon"]
        accuracy = coords["accuracy"]

        if st.session_state.prev_lat is not None:
            user_lat = (user_lat + st.session_state.prev_lat) / 2
            user_lon = (user_lon + st.session_state.prev_lon) / 2

        st.session_state.prev_lat = user_lat
        st.session_state.prev_lon = user_lon

        st.session_state.history.append([user_lat, user_lon])
        st.session_state.history = st.session_state.history[-40:]

        user_ref = db.reference(f"users/{st.session_state.uid}")
        user_ref.update({
            "lat": float(user_lat),
            "lon": float(user_lon),
            "ts": time.time()
        })

        distance = haversine(user_lat,user_lon,TARGET_LAT,TARGET_LON)

        st.metric("User ID", st.session_state.uid)
        st.metric("GPS Accuracy (m)", f"{accuracy:.2f}")
        st.metric("Distance From Target (m)", f"{distance:.2f}")

        if distance <= max(accuracy,12):
            st.success("✅ LOCATION VERIFIED")
            color = [0,255,140]
        else:
            st.error("❌ LOCATION MISMATCH")
            color = [255,80,80]

    else:
        user_lat, user_lon, accuracy, color = TARGET_LAT, TARGET_LON, 10, [150,150,150]

# =====================================================
# FETCH USERS
# =====================================================
users_ref = db.reference("users")
all_users = users_ref.get()

real_users = []
labels = []

if all_users:
    now = time.time()

    for uid, data in all_users.items():

        if "lat" not in data or "lon" not in data:
            continue

        online = (now - data.get("ts",0)) < 20
        opacity = 255 if online else 80

        real_users.append({
            "name": uid,
            "lat": float(data["lat"]),
            "lon": float(data["lon"]),
            "color":[255,0,255,opacity]
        })

        labels.append({
            "name": uid,
            "lat": float(data["lat"]),
            "lon": float(data["lon"])
        })

real_users_df = pd.DataFrame(real_users)
labels_df = pd.DataFrame(labels)

# =====================================================
# RIGHT PANEL — CYBER MAP
# =====================================================
with col2:

    st.subheader("🗺 Destination Tracker")

    history_df = pd.DataFrame(
        st.session_state.history,
        columns=["lat","lon"]
    )

    MAP_STYLE = "mapbox://styles/mapbox/dark-v11"

    # 👑 ADMIN ROUTE
    admin_route_path = []
    if IS_ADMIN and coords:
        admin_route_path = get_admin_route(
            user_lat,
            user_lon,
            TARGET_LAT,
            TARGET_LON
        )

    pulse_size = (refresh_count % 20) * 3 + accuracy

    radar_layer = pdk.Layer(
        "ScatterplotLayer",
        pd.DataFrame([{"lat":user_lat,"lon":user_lon}]),
        get_position='[lon, lat]',
        get_fill_color=[0,255,255,50],
        get_radius=pulse_size,
    )

    target_glow = pdk.Layer(
        "ScatterplotLayer",
        pd.DataFrame([{"lat":TARGET_LAT,"lon":TARGET_LON}]),
        get_position='[lon, lat]',
        get_fill_color=[255,0,0,30],
        get_radius=20,
    )

    target_icon_df = pd.DataFrame([{
        "lat": TARGET_LAT,
        "lon": TARGET_LON,
        "icon_data": {
            "url": "https://cdn-icons-png.flaticon.com/512/684/684908.png",
            "width":128,
            "height":128,
            "anchorY":128
        }
    }])

    target_icon_layer = pdk.Layer(
        "IconLayer",
        data=target_icon_df,
        get_icon="icon_data",
        get_position='[lon, lat]',
        get_size=8,
        size_scale=10,
    )

    admin_route_layer = pdk.Layer(
    "PathLayer",
    data=[{"path": admin_route_path}] if admin_route_path else [],
    get_path="path",
    get_color=[0,255,255,200],
    get_width=3,          # ⭐ control thickness directly
    width_min_pixels=1,   # ⭐ allow thin rendering
    width_scale=1,
)


    trail_layer = pdk.Layer(
        "PathLayer",
        data=[{
            "path":[[row["lon"],row["lat"]] for _,row in history_df.iterrows()]
        }],
        get_path="path",
        get_color=[255,140,0],
        width_scale=20,
        width_min_pixels=3,
    )

    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        real_users_df,
        get_position='[lon, lat]',
        radiusPixels=20,
        intensity=0.4,
        threshold=0.6
    )

    real_users_layer = pdk.Layer(
        "ScatterplotLayer",
        real_users_df,
        get_position='[lon, lat]',
        get_fill_color="color",
        get_radius=6,
    )

    text_layer = pdk.Layer(
        "TextLayer",
        labels_df,
        get_position='[lon, lat]',
        get_text="name",
        get_size=16,
        get_color=[255,255,0],
        get_alignment_baseline="'bottom'",
    )

    view_state = pdk.ViewState(
        latitude=user_lat,
        longitude=user_lon,
        zoom=18,
        pitch=0,
        bearing=0
    )

    deck = pdk.Deck(
        map_style=MAP_STYLE,
        layers=[
            radar_layer,
            target_glow,
            target_icon_layer,
            admin_route_layer,
            trail_layer,
            heatmap_layer,
            real_users_layer,
            text_layer
        ],
        initial_view_state=view_state
    )

    st.pydeck_chart(deck)

st.caption("🧠 Real time tracking — Intelligence System")
