import json
from typing import Any, Dict, List, Optional

from django.db import OperationalError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from .forms import FlightSearchForm
from .models import FlightSearchQuery
from .opensky import OpenSkyClient


def index(request: HttpRequest) -> HttpResponse:
    """
    Main flight lookup view:
    - Displays the flight number search form input
    - Queries the OpenSky Network API for matching flights
    - Displays the list of matching flights directly under the form input with:
      Start Time, End Time, Time Zones (Origin & Destination), Start Location, and End Location
    - Renders the real-time flight path map tracing the airplane's trajectory
    """
    raw_query = (
        request.GET.get('flight_number')
        or request.POST.get('flight_number')
        or ''
    ).strip()

    form = FlightSearchForm(initial={'flight_number': raw_query} if raw_query else None)
    matching_flights: List[Dict[str, Any]] = []
    search_meta: Dict[str, Any] = {}
    selected_flight: Optional[Dict[str, Any]] = None
    error_message: str = ''

    if raw_query:
        form = FlightSearchForm(data={'flight_number': raw_query})
        if form.is_valid():
            cleaned_number = form.cleaned_data['flight_number']
            client = OpenSkyClient()
            matching_flights, search_meta = client.search_flights(cleaned_number)

            if matching_flights:
                selected_idx = 0
                try:
                    req_idx = int(request.GET.get('selected', '0'))
                    if 0 <= req_idx < len(matching_flights):
                        selected_idx = req_idx
                except ValueError:
                    selected_idx = 0
                selected_flight = matching_flights[selected_idx]

            try:
                FlightSearchQuery.objects.create(
                    flight_number=cleaned_number,
                    results_count=len(matching_flights),
                )
            except OperationalError:
                pass
        else:
            error_message = 'Please enter a valid flight number or callsign.'

    recent_searches = []
    try:
        recent_searches = list(
            FlightSearchQuery.objects.values_list('flight_number', flat=True)
            .distinct()[:6]
        )
    except OperationalError:
        recent_searches = []

    context = {
        'form': form,
        'query': raw_query.upper(),
        'flights': matching_flights,
        'selected_flight': selected_flight,
        'search_meta': search_meta,
        'error_message': error_message,
        'recent_searches': recent_searches,
        'flights_json': json.dumps(matching_flights),
    }
    return render(request, 'flights/index.html', context)


def api_search_flights(request: HttpRequest) -> JsonResponse:
    """
    JSON endpoint returning matching flights from the OpenSky Network API.
    GET /api/flights/search/?flight_number=BA117
    """
    flight_number = (request.GET.get('flight_number') or '').strip()
    if not flight_number:
        return JsonResponse(
            {'error': 'Missing required query parameter: flight_number', 'flights': []},
            status=400,
        )

    client = OpenSkyClient()
    flights, meta = client.search_flights(flight_number)
    return JsonResponse({
        'query': flight_number.upper(),
        'count': len(flights),
        'meta': meta,
        'flights': flights,
    })


def api_flight_track(request: HttpRequest) -> JsonResponse:
    """
    JSON endpoint polled by the map in real time to fetch updated OpenSky state vectors
    and trajectory waypoints for an active aircraft.
    GET /api/flights/track/?icao24=...&callsign=...
    """
    icao24 = (request.GET.get('icao24') or '').strip()
    callsign = (request.GET.get('callsign') or '').strip()
    dep_icao = (request.GET.get('dep_icao') or '').strip() or None
    arr_icao = (request.GET.get('arr_icao') or '').strip() or None

    first_seen = None
    last_seen = None
    try:
        if request.GET.get('first_seen'):
            first_seen = int(request.GET['first_seen'])
        if request.GET.get('last_seen'):
            last_seen = int(request.GET['last_seen'])
    except (ValueError, TypeError):
        pass

    if not icao24 and not callsign:
        return JsonResponse(
            {'error': 'Provide at least icao24 or callsign parameter.'},
            status=400,
        )

    client = OpenSkyClient()
    updated_flight = client.get_realtime_track_update(
        icao24=icao24,
        callsign=callsign,
        dep_icao=dep_icao,
        arr_icao=arr_icao,
        first_seen=first_seen,
        last_seen=last_seen,
    )
    return JsonResponse({'flight': updated_flight})
