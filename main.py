#!/usr/bin/env python3
"""Extract airport data from OpenStreetMap by ICAO code and export as GeoJSON."""

import argparse
import os
import sys
from typing import Optional

from overpass import get_airport_bbox, get_airport_features
from geojson import build_categorized_geojson
from export import write_airport_data


def extract_airport_data(icao: str) -> Optional[dict]:
    """Extract airport data for the given ICAO code, grouped by category."""
    icao = icao.upper()

    print(f"Looking up airport {icao}...", file=sys.stderr)
    bbox = get_airport_bbox(icao)

    if not bbox:
        print(f"Airport {icao} not found in OpenStreetMap", file=sys.stderr)
        return None

    print(f"Found airport, querying features...", file=sys.stderr)
    result = get_airport_features(bbox)

    elements = result.get("elements", [])
    print(f"Found {len(elements)} features", file=sys.stderr)

    return build_categorized_geojson(elements, icao)


def main():
    parser = argparse.ArgumentParser(
        description="Extract airport data from OpenStreetMap by ICAO code"
    )
    parser.add_argument("icao", help="Airport ICAO code (e.g., KJFK, EGLL)")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_export_dir = os.path.join(script_dir, "exports")
    parser.add_argument(
        "-o", "--output-dir",
        default=default_export_dir,
        help=f"Output directory (default: {default_export_dir})"
    )
    args = parser.parse_args()
    icao = args.icao.upper()

    categorized = extract_airport_data(icao)

    if not categorized:
        sys.exit(1)

    output_dir = os.path.join(args.output_dir, icao)
    write_airport_data(categorized, icao, output_dir)


if __name__ == "__main__":
    main()
