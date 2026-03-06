import streamlit as st
import osmnx as ox
import pyproj
import pandas as pd
from shapely.geometry import Point
from shapely.ops import transform, linemerge, unary_union
from geopy.distance import geodesic
import time

# --- LOGIC FUNCTIONS (From our previous iterations) ---

def convert_to_decimal(val):
    try:
        val = float(str(val).split()[0])
        degrees = int(val / 100)
        minutes = val % 100
        return round(degrees + (minutes / 60), 8)
    except: return None

def get_utm_crs(lon):
    zone = int((lon + 180) / 6) + 1
    return f"EPSG:326{zone}"

# --- STREAMLIT UI ---

st.set_page_config(page_title="Chainage-Maker Online", page_icon="🚉")
st.title("🚉 Chainage-Maker Online")
# --- ADDING THE DESCRIPTIVE IMAGE HERE ---

st.markdown("Generate track-accurate chainage from **Fog Safety Device** CSV file.")
st.markdown("Developed by **SPM Cell Hyderabad Division - SCR**")

uploaded_file = st.file_uploader("Upload Fog Device CSV", type="csv")

if uploaded_file:
    # Load and Preprocess
    raw_df = pd.read_csv(uploaded_file, header=None, usecols=[2, 5, 6])
    df = pd.DataFrame()
    df['signame'] = raw_df[2]
    df['latitude'] = raw_df[5].apply(convert_to_decimal)
    df['longitude'] = raw_df[6].apply(convert_to_decimal)
    df = df.dropna().reset_index(drop=True)

    if st.button("🚀 Start Processing"):
        distances, cumulative, offsets = [0.0], [0.0], [0.0]
        
        # UI Elements for Progress
        progress_bar = st.progress(0)
        table_placeholder = st.empty()
        
        for i in range(1, len(df)):
            p1 = (df.loc[i-1, 'latitude'], df.loc[i-1, 'longitude'])
            p2 = (df.loc[i, 'latitude'], df.loc[i, 'longitude'])
            
            # Distance Logic (Curvature + Fallback)
            geo_dist = geodesic(p1, p2).meters
            utm_code = get_utm_crs(p1[1])
            project = pyproj.Transformer.from_crs("EPSG:4326", utm_code, always_xy=True).transform
            
            try:
                # Spatial Processing
                bbox = (min(p1[1], p2[1])-0.02, min(p1[0], p2[0])-0.02, 
                        max(p1[1], p2[1])+0.02, max(p1[0], p2[0])+0.02)
                rail = ox.features_from_bbox(bbox=bbox, tags={"railway": ["rail", "main"]})
                lines = [transform(project, g) for g in rail.geometry if g.geom_type in ['LineString', 'MultiLineString']]
                merged = linemerge(unary_union(lines))
                best_line = max(merged.geoms, key=lambda x: x.length) if merged.geom_type == 'MultiLineString' else merged
                
                # Projection & Offset
                p1_m, p2_m = transform(project, Point(p1[1], p1[0])), transform(project, Point(p2[1], p2[0]))
                track_dist = abs(best_line.project(p1_m) - best_line.project(p2_m))
                offset = best_line.distance(p2_m)
                
                final_dist = track_dist if (track_dist > 1.0 and track_dist >= geo_dist) else geo_dist
                
                distances.append(round(final_dist, 2))
                cumulative.append(round(cumulative[-1] + final_dist, 2))
                offsets.append(round(offset, 2))
            except:
                distances.append(round(geo_dist, 2))
                cumulative.append(round(cumulative[-1] + geo_dist, 2))
                offsets.append(None)

            # Update Live Table in UI
            progress_bar.progress(i / (len(df)-1))
            temp_df = df.head(i+1).copy()
            temp_df['distance'] = distances
            temp_df['cumulative'] = cumulative
            table_placeholder.dataframe(temp_df)

        # Final Download
        df['distance'], df['cumulative'], df['track_offset_dist'] = distances, cumulative, offsets
        st.success("✅ Chainage Generated Successfully!")
        st.download_button("📥 Download Result CSV", df.to_csv(index=False), "chainage_results.csv")
        
st.image("track_curvature.png", 
         caption="Linear Referencing: Why we calculate distance along the track path (10.4km) vs. straight line (8.8km).",
         use_container_width=True)
