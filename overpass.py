"""Overpass API client for querying OpenStreetMap data."""

import sys
import time
from typing import Optional, Tuple

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def query_overpass(query: str) -> dict:
    """Execute an Overpass API query with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(OVERPASS_URL, data={"data": query}, timeout=120)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)
                print(f"Request failed, retrying in {wait_time}s... ({e})", file=sys.stderr)
                time.sleep(wait_time)
            else:
                raise


def get_airport_bbox(icao: str) -> Optional[Tuple[float, float, float, float]]:
    """Get the bounding box of an airport by ICAO code."""
    query = f"""
    [out:json][timeout:30];
    (
      way["aeroway"="aerodrome"]["icao"="{icao}"];
      relation["aeroway"="aerodrome"]["icao"="{icao}"];
    );
    out geom;
    """
    result = query_overpass(query)

    if not result.get("elements"):
        return None

    # Calculate bounding box from the airport geometry
    min_lat, max_lat = 90.0, -90.0
    min_lon, max_lon = 180.0, -180.0

    for element in result["elements"]:
        if element["type"] == "way" and "geometry" in element:
            for point in element["geometry"]:
                min_lat = min(min_lat, point["lat"])
                max_lat = max(max_lat, point["lat"])
                min_lon = min(min_lon, point["lon"])
                max_lon = max(max_lon, point["lon"])
        elif element["type"] == "relation" and "members" in element:
            for member in element["members"]:
                if "geometry" in member:
                    for point in member["geometry"]:
                        min_lat = min(min_lat, point["lat"])
                        max_lat = max(max_lat, point["lat"])
                        min_lon = min(min_lon, point["lon"])
                        max_lon = max(max_lon, point["lon"])

    if min_lat == 90.0:
        return None

    # Add small buffer around the airport
    buffer = 0.005
    return (min_lat - buffer, min_lon - buffer, max_lat + buffer, max_lon + buffer)


def get_airport_features(bbox: Tuple[float, float, float, float]) -> dict:
    """Query all airport features within the bounding box."""
    south, west, north, east = bbox
    bbox_str = f"{south},{west},{north},{east}"

    query = f"""
    [out:json][timeout:60];
    (
      // Gates
      node["aeroway"="gate"]({bbox_str});

      // Terminals
      way["aeroway"="terminal"]({bbox_str});
      relation["aeroway"="terminal"]({bbox_str});

      // Aprons (plane parking areas)
      way["aeroway"="apron"]({bbox_str});
      relation["aeroway"="apron"]({bbox_str});

      // Parking positions/stands
      node["aeroway"="parking_position"]({bbox_str});
      way["aeroway"="parking_position"]({bbox_str});
    );
    out geom;
    """
    return query_overpass(query)
