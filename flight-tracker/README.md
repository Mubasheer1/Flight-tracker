# SkyTrace — Django OpenSky Flight Lookup & Real-Time Path Tracker

A Django web application that looks up flights by flight number or ICAO callsign using the **OpenSky Network API**, displays a list of matching flights directly under the search input, and renders an interactive real-time map tracing the airplane's trajectory.

## Features

- **Flight Number Search**: Supports both IATA flight numbers (e.g., `BA117`, `UA901`, `AA100`, `AF006`, `EK201`) and ICAO callsigns (e.g., `BAW117`, `UAL901`, `DLH400`, `AAL100`).
- **Search Results Under Form Input**: Displays matching flights immediately below the search bar, including:
  - **Start Time** (local departure timestamp + UTC)
  - **End Time** (local arrival / estimated arrival timestamp + UTC)
  - **Time Zones** (IANA timezone name, abbreviation, and UTC offset for both origin and destination)
  - **Start Location** (origin airport name, city, country, IATA/ICAO codes, and coordinates)
  - **End Location** (destination airport name, city, country, IATA/ICAO codes, and coordinates)
- **Real-Time Map Path Tracing**:
  - Interactive Leaflet.js map displaying the origin airport, destination airport, solid flown trajectory polyline, dashed remaining route, and a rotating airplane marker.
  - Polls `/api/flights/track/` (`OpenSky /api/states/all` and `/api/tracks/all`) and interpolates aircraft movement in real time.

## Quick Start

```powershell
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver
```

Then open `http://127.0.0.1:8000/` in your browser.

## Optional OpenSky Network Credentials

Anonymous requests to the OpenSky Network API are supported out of the box. For higher rate limits, set your OpenSky credentials via environment variables:

```powershell
$env:OPENSKY_USERNAME="your_username"
$env:OPENSKY_PASSWORD="your_password"
```
