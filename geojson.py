"""OSM to GeoJSON conversion utilities."""

from typing import Optional


def osm_to_geojson_geometry(element: dict) -> Optional[dict]:
    """Convert OSM element to GeoJSON geometry."""
    if element["type"] == "node":
        return {
            "type": "Point",
            "coordinates": [element["lon"], element["lat"]]
        }
    elif element["type"] == "way" and "geometry" in element:
        coords = [[p["lon"], p["lat"]] for p in element["geometry"]]
        # Check if it's a closed way (polygon)
        if coords[0] == coords[-1] and len(coords) >= 4:
            return {
                "type": "Polygon",
                "coordinates": [coords]
            }
        else:
            return {
                "type": "LineString",
                "coordinates": coords
            }
    elif element["type"] == "relation" and "members" in element:
        # Handle multipolygon relations
        outer_rings = []
        for member in element["members"]:
            if member.get("role") == "outer" and "geometry" in member:
                coords = [[p["lon"], p["lat"]] for p in member["geometry"]]
                outer_rings.append(coords)

        if outer_rings:
            if len(outer_rings) == 1:
                return {
                    "type": "Polygon",
                    "coordinates": outer_rings
                }
            else:
                return {
                    "type": "MultiPolygon",
                    "coordinates": [[ring] for ring in outer_rings]
                }
    return None


def categorize_feature(element: dict) -> str:
    """Determine the feature category based on OSM tags."""
    tags = element.get("tags", {})
    aeroway = tags.get("aeroway", "")

    if aeroway == "gate":
        return "gate"
    elif aeroway == "terminal":
        return "terminal"
    elif aeroway == "apron":
        return "apron"
    elif aeroway == "parking_position":
        return "parking_stand"
    return "unknown"


def build_feature(element: dict) -> Optional[dict]:
    """Build a GeoJSON Feature from an OSM element."""
    geometry = osm_to_geojson_geometry(element)
    if not geometry:
        return None

    category = categorize_feature(element)
    tags = element.get("tags", {})

    properties = {
        "category": category,
        "osm_id": element.get("id"),
        "osm_type": element.get("type"),
    }

    # Add relevant tags as properties
    for key in ["name", "ref", "aeroway", "building", "operator"]:
        if key in tags:
            properties[key] = tags[key]

    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": properties
    }


def build_feature_collection(features: list, name: str) -> dict:
    """Build a GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "name": name,
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": features
    }


def build_categorized_geojson(elements: list, icao: str) -> dict:
    """Build GeoJSON FeatureCollections grouped by category."""
    categorized = {
        "gates": [],
        "terminals": [],
        "aprons": [],
        "parking_stands": []
    }

    category_map = {
        "gate": "gates",
        "terminal": "terminals",
        "apron": "aprons",
        "parking_stand": "parking_stands"
    }

    for element in elements:
        feature = build_feature(element)
        if not feature:
            continue

        category = feature["properties"]["category"]
        if category in category_map:
            categorized[category_map[category]].append(feature)

    return {
        name: build_feature_collection(features, f"{icao}_{name}")
        for name, features in categorized.items()
    }
