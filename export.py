"""File export utilities for GeoJSON data."""

import json
import os
import sys

from geojson import build_feature_collection


def write_airport_data(categorized: dict, icao: str, output_dir: str) -> None:
    """Write categorized airport data to GeoJSON files."""
    os.makedirs(output_dir, exist_ok=True)

    # Write each category to a separate file
    all_features = []
    for category, geojson in categorized.items():
        filename = os.path.join(output_dir, f"{category}.geojson")
        with open(filename, "w") as f:
            json.dump(geojson, f, indent=2)
        print(f"Wrote {len(geojson['features'])} features to {filename}", file=sys.stderr)
        all_features.extend(geojson["features"])

    # Write combined file without formatting
    all_data = build_feature_collection(all_features, icao)
    all_filename = os.path.join(output_dir, f"{icao}.geojson")
    with open(all_filename, "w") as f:
        json.dump(all_data, f)
    print(f"Wrote {len(all_features)} features to {all_filename}", file=sys.stderr)
