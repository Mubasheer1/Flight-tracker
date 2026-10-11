from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .airports import format_timestamp_in_tz, normalize_flight_query, resolve_airport
from .opensky import OpenSkyClient


class AirportAndQueryUtilsTests(TestCase):
    def test_normalize_iata_to_icao_flight_query(self):
        info = normalize_flight_query('ba 117')
        self.assertEqual(info['icao_callsign'], 'BAW117')
        self.assertEqual(info['iata_flight'], 'BA117')
        self.assertIn('BAW117', info['candidates'])
        self.assertIn('BA117', info['candidates'])
        self.assertEqual(info['airline_name'], 'British Airways')

    def test_resolve_airport_and_timezone_formatting(self):
        jfk = resolve_airport('KJFK')
        self.assertEqual(jfk['iata'], 'JFK')
        self.assertEqual(jfk['city'], 'New York')
        self.assertEqual(jfk['tz'], 'America/New_York')

        ts_info = format_timestamp_in_tz(1700000000, jfk['tz'])
        self.assertIn('America/New_York', ts_info['tz_display'])
        self.assertIn('UTC', ts_info['utc_offset'])


class OpenSkyClientTests(TestCase):
    @patch.object(OpenSkyClient, 'fetch_all_states')
    @patch.object(OpenSkyClient, 'fetch_aircraft_flights')
    @patch.object(OpenSkyClient, 'fetch_flight_track')
    def test_search_flights_with_live_opensky_data(
        self, mock_track, mock_aircraft_flights, mock_states
    ):
        mock_states.return_value = [
            [
                '4009f1',          # icao24
                'BAW117  ',        # callsign
                'United Kingdom',  # origin_country
                1728660000,        # time_position
                1728660002,        # last_contact
                -32.5,             # longitude
                49.2,              # latitude
                10972.8,           # baro_altitude
                False,             # on_ground
                245.0,             # velocity
                262.5,             # true_track
            ]
        ]
        mock_aircraft_flights.return_value = [
            {
                'icao24': '4009f1',
                'firstSeen': 1728648000,
                'estDepartureAirport': 'EGLL',
                'lastSeen': 1728676800,
                'estArrivalAirport': 'KJFK',
                'callsign': 'BAW117  ',
            }
        ]
        mock_track.return_value = {
            'icao24': '4009f1',
            'callsign': 'BAW117  ',
            'startTime': 1728648000,
            'endTime': 1728660000,
            'path': [
                [1728648000, 51.47, -0.4543, 300.0, 270.0, False],
                [1728654000, 50.8, -15.2, 10600.0, 265.0, False],
                [1728660000, 49.2, -32.5, 10972.8, 262.5, False],
            ],
        }

        client = OpenSkyClient()
        flights, meta = client.search_flights('BA117')

        self.assertGreaterEqual(len(flights), 1)
        flight = flights[0]
        self.assertEqual(flight['callsign'], 'BAW117')
        self.assertEqual(flight['origin_airport']['icao'], 'EGLL')
        self.assertEqual(flight['destination_airport']['icao'], 'KJFK')
        self.assertIn('Europe/London', flight['origin_timezone'])
        self.assertIn('America/New_York', flight['destination_timezone'])
        self.assertTrue(len(flight['path']) >= 3)
        self.assertFalse(meta['used_fallback'])


class FlightViewsTests(TestCase):
    def test_index_page_renders_search_form_and_map(self):
        response = self.client.get(reverse('flights:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'flight-search-form')
        self.assertContains(response, 'search-results')
        self.assertContains(response, 'flight-map')

    @patch.object(OpenSkyClient, 'fetch_all_states', return_value=[])
    @patch.object(OpenSkyClient, 'fetch_recent_flights', return_value=[])
    def test_search_flight_displays_results_under_form(self, _mock_recent, _mock_states):
        response = self.client.get(reverse('flights:index'), {'flight_number': 'BA117'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BAW117')
        self.assertContains(response, 'Start Location (Origin)')
        self.assertContains(response, 'End Location (Destination)')
        self.assertContains(response, 'Start Time (Departure)')
        self.assertContains(response, 'End Time (Arrival / Est.)')
        self.assertContains(response, 'Time Zones (Origin &amp; Destination)')
        self.assertContains(response, 'Europe/London')
        self.assertContains(response, 'America/New_York')

    @patch.object(OpenSkyClient, 'fetch_all_states', return_value=[])
    def test_api_flight_track_endpoint(self, _mock_states):
        response = self.client.get(
            reverse('flights:api_track'),
            {'icao24': '4009f1', 'callsign': 'BAW117', 'dep_icao': 'EGLL', 'arr_icao': 'KJFK'},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('flight', payload)
        self.assertEqual(payload['flight']['callsign'], 'BAW117')
        self.assertTrue(len(payload['flight']['path']) >= 2)
