# 🚀 Precision Location Identification System

A real-time geolocation tracking and navigation dashboard built with **Streamlit**, **Firebase**, **PyDeck**, and **Mapbox Directions API**.
The system allows multiple users to share live GPS positions, while an admin sets a target location and monitors movement on an interactive cyber-style map.

---

# 🧭 Features

## 📡 Live GPS Tracking

* Reads browser GPS using Geolocation API
* Smooths coordinates to reduce jitter
* Stores last 40 positions as movement trail
* Syncs live user positions via Firebase

## 👑 Admin Target Control

* First connected user becomes Admin
* Admin selects a target on mini map
* Target updates globally in real time

## 🗺️ Mapbox Navigation

* Real walking routes using Mapbox Directions API
* PathLayer renders navigation line
* Dark cyber map style using Mapbox tiles

## ✅ Location Verification

* Uses Haversine distance calculation
* Compares GPS accuracy radius
* Shows VERIFIED or MISMATCH status

## 🌐 Multi-User Visualization

* Radar pulse around active user
* Heatmap of all users
* Live labels and status opacity
* Neon route + trail effects

---

# 🧱 Tech Stack

Frontend:

* Streamlit
* PyDeck (WebGL map rendering)
* Folium (admin map picker)

Backend:

* Firebase Realtime Database

Navigation:

* Mapbox Directions API

Other:

* streamlit-js-eval
* streamlit-autorefresh
* pandas

---

# 📁 Project Structure

```
project/
│
├── app.py
├── serviceAccountKey.json
├── requirements.txt
└── .streamlit/
    └── secrets.toml
```

---

# 🔑 Environment Setup

Create:

```
.streamlit/secrets.toml
```

Add your Mapbox key:

```
MAPBOX_API_KEY="pk.xxxxxxxxxxxxxxxxx"
```

---

# 📦 Install Dependencies

```
pip install streamlit
pip install streamlit-js-eval
pip install pydeck
pip install pandas
pip install requests
pip install folium
pip install streamlit-folium
pip install streamlit-autorefresh
pip install firebase-admin
```

---

# ▶️ Run the App

```
streamlit run app.py
```

Open browser:

```
http://localhost:8501
```

Allow location access when prompted.

---

# 🧠 How It Works

1. Browser sends GPS coordinates
2. Coordinates stored in Firebase
3. Admin sets target point
4. Mapbox Directions API generates route
5. PyDeck renders cyber-style map layers

Pipeline:

```
GPS → Streamlit → Firebase → Mapbox → PyDeck
```

---

# ⚡ Usage

### Normal User

* Opens app
* Shares GPS
* Appears on live map

### Admin

* Clicks map to set target
* Sees navigation route
* Monitors user verification status

---

# 🔒 Security Notes

* Never upload `serviceAccountKey.json` publicly
* Keep Mapbox API key inside secrets.toml
* Add URL restrictions when deploying

---

# 🚀 Future Improvements

* ETA and travel time display
* Direction arrow based on movement
* Speed detection
* Follow-user camera mode
* Animated navigation beam
* Multi-target support

---

# 🧑‍💻 Author

Real-time tracking dashboard built using Streamlit + Mapbox integration.
