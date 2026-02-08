# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python tool for extracting airport data from OpenStreetMap and exporting it as GeoJSON format files.

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the tool
python main.py <ICAO_CODE>

# Examples
python main.py EGGW                      # Creates ./exports/EGGW/
python main.py EGGW -o /path/to/dir      # Creates /path/to/dir/EGGW/
```

## Output Structure

```
<ICAO>/
├── gates.geojson          # Gate locations (points)
├── terminals.geojson      # Terminal buildings (polygons)
├── aprons.geojson         # Plane parking areas (polygons)
├── parking_stands.geojson # Individual parking stands (points/lines)
└── <ICAO>.geojson         # All features combined (minified)
```

## Architecture

```
main.py      # CLI entry point
overpass.py  # Overpass API client (queries, retry logic)
geojson.py   # OSM → GeoJSON conversion
export.py    # File I/O
```

The script queries the Overpass API in two stages:
1. Find the airport boundary by ICAO code (`aeroway=aerodrome` + `icao` tag) to get a bounding box
2. Query all airport features within that bounding box

OSM tags queried: `aeroway=gate`, `aeroway=terminal`, `aeroway=apron`, `aeroway=parking_position`
