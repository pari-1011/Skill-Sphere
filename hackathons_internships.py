import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
from free_api_client import ask_ai

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "career-coach-app/1.0 (contact: contact@example.com)"}


def geocode_location(location: str):
    """Use OpenStreetMap Nominatim to geocode to lat/lon. Fallbacks for common locations."""
    try:
        params = {"q": location, "format": "json", "limit": 1}
        resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json():
            j = resp.json()[0]
            return float(j["lat"]), float(j["lon"])
    except Exception:
        pass
    # Fallbacks
    loc = (location or "").strip().lower()
    if loc in {"india"}:
        return 20.5937, 78.9629
    return 20.0, 0.0


@st.cache_data(show_spinner=False, ttl=1800)
def get_hackathons_json(location: str):
    prompt = f"""
Return a strict JSON array of up to 10 upcoming hackathons near {location} in the next 12 months.
Each item must be an object with: name, date, city, country, url.
No extra text.
"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant returning strict JSON only."},
        {"role": "user", "content": prompt}
    ]
    try:
        raw = ask_ai(messages, max_tokens=500, temperature=0.3).strip()
        data = json.loads(raw)
        if isinstance(data, list) and all(isinstance(x, dict) for x in data) and len(data) > 0:
            return data
    except Exception:
        pass
    # Fallback sample data
    return [
        {"name": "DevFest City Hackathon", "date": "2025-11-10", "city": "Mumbai", "country": "India", "url": "https://devfest.example.com"},
        {"name": "Open Source Sprint", "date": "2025-12-05", "city": "Pune", "country": "India", "url": "https://ossprint.example.com"},
        {"name": "AI Innovators Hack", "date": "2026-01-15", "city": "Bengaluru", "country": "India", "url": "https://aihack.example.com"},
        {"name": "HealthTech Buildathon", "date": "2025-11-28", "city": "Hyderabad", "country": "India", "url": "https://healthbuild.example.com"},
        {"name": "FinTech Code Jam", "date": "2025-12-20", "city": "Delhi", "country": "India", "url": "https://finjam.example.com"}
    ]


@st.cache_data(show_spinner=False, ttl=1800)
def get_internships_json(location: str):
    prompt = f"""
Return a strict JSON array of up to 10 current internship opportunities near {location}.
Each item must be an object with: title, company, city, country, url.
No extra text.
"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant returning strict JSON only."},
        {"role": "user", "content": prompt}
    ]
    try:
        raw = ask_ai(messages, max_tokens=500, temperature=0.4).strip()
        data = json.loads(raw)
        if isinstance(data, list) and all(isinstance(x, dict) for x in data) and len(data) > 0:
            return data
    except Exception:
        pass
    # Fallback sample data
    return [
        {"title": "Software Engineering Intern", "company": "TechNova", "city": "Bengaluru", "country": "India", "url": "https://jobs.technova.example.com/se-intern"},
        {"title": "Data Analyst Intern", "company": "DataWiz", "city": "Hyderabad", "country": "India", "url": "https://careers.datawiz.example.com/da-intern"},
        {"title": "Marketing Intern", "company": "Brandify", "city": "Pune", "country": "India", "url": "https://brandify.example.com/internships/marketing"},
        {"title": "Product Management Intern", "company": "ProdCraft", "city": "Mumbai", "country": "India", "url": "https://prodcraft.example.com/pm-intern"}
    ]


def run():
    st.title("📅 Hackathons & Internships")
    location_input = st.text_input("Enter your location (city, region, or country):", value="India")

    # Map style selection
    tile_options = [
        "CartoDB positron",
        "OpenStreetMap",
        "Stamen Toner",
        "Stamen Terrain",
        "CartoDB dark_matter"
    ]
    tiles_choice = st.selectbox("Map style", options=tile_options, index=0)

    if not location_input:
        return

    lat, lon = geocode_location(location_input)

    st.markdown(f"### Map: {location_input} (Lat: {lat:.4f}, Lon: {lon:.4f})")

    # Define tile providers with explicit URLs and attributions
    tile_providers = {
        "OpenStreetMap": {
            "tiles": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "attr": "&copy; OpenStreetMap contributors"
        },
        "CartoDB positron": {
            "tiles": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
            "attr": "&copy; OpenStreetMap contributors &copy; CARTO"
        },
        "CartoDB dark_matter": {
            "tiles": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            "attr": "&copy; OpenStreetMap contributors &copy; CARTO"
        },
        "Stamen Toner": {
            "tiles": "https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
            "attr": "Map tiles by Stamen Design, CC BY 3.0 — Map data &copy; OpenStreetMap contributors"
        },
        "Stamen Terrain": {
            "tiles": "https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
            "attr": "Map tiles by Stamen Design, CC BY 3.0 — Map data &copy; OpenStreetMap contributors"
        }
    }

    # Initialize map with no tiles, then add a proper TileLayer with attribution
    m = folium.Map(location=[lat, lon], zoom_start=6, control_scale=True, tiles=None)
    prov = tile_providers.get(tiles_choice) or tile_providers["OpenStreetMap"]
    folium.TileLayer(
        tiles=prov["tiles"],
        attr=prov["attr"],
        name=tiles_choice,
        overlay=False,
        control=False,
    ).add_to(m)

    folium.Marker([lat, lon], tooltip=location_input).add_to(m)
    st_folium(m, width=700, height=420)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Get Upcoming Hackathons"):
            with st.spinner("Fetching upcoming hackathons..."):
                data = get_hackathons_json(location_input)
            if not data:
                st.info("No hackathons found. Try another location.")
            else:
                for ev in data:
                    st.markdown(f"- [{ev.get('name','(name)')}]({ev.get('url','#')}) — {ev.get('date','TBA')} — {ev.get('city','')}, {ev.get('country','')}")
    with col2:
        if st.button("Get Current Internships"):
            with st.spinner("Fetching internships..."):
                data = get_internships_json(location_input)
            if not data:
                st.info("No internships found. Try another location.")
            else:
                for job in data:
                    st.markdown(f"- [{job.get('title','(title)')}]({job.get('url','#')}) — {job.get('company','')} — {job.get('city','')}, {job.get('country','')}")


if __name__ == "__main__":
    run()
