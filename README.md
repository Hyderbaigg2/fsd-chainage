# 🚉 Chainage-Maker Online

**Chainage-Maker Online** is an open-source, browser-based tool designed to help Railway Signaling Engineers and Crew Management teams convert raw GPS data from **Fog Safety Devices** into precise, track-following chainage.



## 🚀 Features
* **Track-Aware Distance:** Uses real-world railway geometry to account for track curvature, not just straight-line distance.
* **Fog Device Compatibility:** Directly handles raw NMEA-style coordinates (`DDMM.MMMM`) commonly exported by locomotive fog units.
* **Multi-Region Accuracy:** Automatically detects and switches between UTM Zones (e.g., 43N and 44N) to maintain precision across India and beyond.
* **Track Offset Analysis:** Calculates the distance from the GPS marker to the center of the nearest track to validate coordinate accuracy.
* **Cumulative Chainage:** Automatically generates a running total (chainage) from the first signal in the sequence.
* **Open Source & Free:** No installation required; runs entirely in your web browser via Streamlit.

## 🛠️ How It Works
1.  **Coordinate Conversion:** Converts raw Fog Device input using the formula:  
    $$Decimal Degrees = Degrees + (Minutes / 60)$$
2.  **Linear Referencing:** Instead of point-to-point math, the tool "snaps" each signal to the nearest railway line string downloaded from OpenStreetMap.
3.  **Geodesic Fallback:** If map data is missing or a track segment is disconnected, the tool safely falls back to high-precision Geodesic (WGS84) calculations to ensure no data gaps.



## 📋 Input Format
The tool expects a headerless CSV (standard Fog Device export) with the following columns:
* **Column C (Index 2):** Signal/Station Name
* **Column F (Index 5):** Latitude (Format: 1726.021)
* **Column G (Index 6):** Longitude (Format: 7830.228)

## 🖥️ Installation (For Developers)
If you wish to run this locally or contribute to the code:

1. Clone the repository:
   ```bash
   git clone [https://github.com/dgtel/chainage-maker.git](https://github.com/dgtel/chainage-maker.git)
