"""
Airport, airline callsign, and timezone resolution utilities for OpenSky flight data.
"""
from datetime import datetime, timezone as dt_timezone
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Comprehensive mapping of IATA 2-letter airline codes to ICAO 3-letter callsign prefixes
# OpenSky Network uses ICAO callsigns (e.g., "BAW117" for "BA117", "UAL901" for "UA901")
IATA_TO_ICAO_AIRLINES: Dict[str, str] = {
    'AA': 'AAL',  # American Airlines
    'UA': 'UAL',  # United Airlines
    'DL': 'DAL',  # Delta Air Lines
    'WN': 'SWA',  # Southwest Airlines
    'B6': 'JBU',  # JetBlue Airways
    'AS': 'ASA',  # Alaska Airlines
    'NK': 'NKS',  # Spirit Airlines
    'F9': 'FFT',  # Frontier Airlines
    'HA': 'HAL',  # Hawaiian Airlines
    'AC': 'ACA',  # Air Canada
    'WS': 'WJA',  # WestJet
    'BA': 'BAW',  # British Airways
    'VS': 'VIR',  # Virgin Atlantic
    'U2': 'EZY',  # easyJet
    'FR': 'RYR',  # Ryanair
    'EI': 'EIN',  # Aer Lingus
    'LH': 'DLH',  # Lufthansa
    'AF': 'AFR',  # Air France
    'KL': 'KLM',  # KLM Royal Dutch Airlines
    'LX': 'SWR',  # SWISS
    'OS': 'AUA',  # Austrian Airlines
    'SN': 'BEL',  # Brussels Airlines
    'IB': 'IBE',  # Iberia
    'VY': 'VLG',  # Vueling
    'TP': 'TAP',  # TAP Air Portugal
    'AZ': 'ITY',  # ITA Airways
    'SK': 'SAS',  # SAS Scandinavian Airlines
    'AY': 'FIN',  # Finnair
    'DY': 'NOZ',  # Norwegian Air Shuttle
    'LO': 'LOT',  # LOT Polish Airlines
    'TK': 'THY',  # Turkish Airlines
    'A3': 'AEE',  # Aegean Airlines
    'EK': 'UAE',  # Emirates
    'QR': 'QTR',  # Qatar Airways
    'EY': 'ETD',  # Etihad Airways
    'SV': 'SVA',  # Saudia
    'LY': 'ELY',  # El Al
    'RJ': 'RJA',  # Royal Jordanian
    'SQ': 'SIA',  # Singapore Airlines
    'CX': 'CPA',  # Cathay Pacific
    'JL': 'JAL',  # Japan Airlines
    'NH': 'ANA',  # All Nippon Airways
    'KE': 'KAL',  # Korean Air
    'OZ': 'AAR',  # Asiana Airlines
    'CI': 'CAL',  # China Airlines
    'BR': 'EVA',  # EVA Air
    'CA': 'CCA',  # Air China
    'MU': 'CES',  # China Eastern
    'CZ': 'CSN',  # China Southern
    'AI': 'AIC',  # Air India
    '6E': 'IGO',  # IndiGo
    'TG': 'THA',  # Thai Airways
    'MH': 'MAS',  # Malaysia Airlines
    'GA': 'GIA',  # Garuda Indonesia
    'PR': 'PAL',  # Philippine Airlines
    'VN': 'HVN',  # Vietnam Airlines
    'QF': 'QFA',  # Qantas
    'VA': 'VOZ',  # Virgin Australia
    'NZ': 'ANZ',  # Air New Zealand
    'LA': 'LAN',  # LATAM Airlines
    'AV': 'AVA',  # Avianca
    'AM': 'AMX',  # Aeromexico
    'CM': 'CMP',  # Copa Airlines
    'G3': 'GLO',  # GOL
    'AD': 'AZU',  # Azul
    'ET': 'ETH',  # Ethiopian Airlines
    'MS': 'MSR',  # EgyptAir
    'AT': 'RAM',  # Royal Air Maroc
    'KQ': 'KQA',  # Kenya Airways
    'SA': 'SAA',  # South African Airways
    'FX': 'FDX',  # FedEx Express
    '5X': 'UPS',  # UPS Airlines
}

ICAO_TO_AIRLINE_NAME: Dict[str, str] = {
    'AAL': 'American Airlines',
    'UAL': 'United Airlines',
    'DAL': 'Delta Air Lines',
    'SWA': 'Southwest Airlines',
    'JBU': 'JetBlue Airways',
    'ASA': 'Alaska Airlines',
    'NKS': 'Spirit Airlines',
    'FFT': 'Frontier Airlines',
    'HAL': 'Hawaiian Airlines',
    'ACA': 'Air Canada',
    'WJA': 'WestJet',
    'BAW': 'British Airways',
    'VIR': 'Virgin Atlantic',
    'EZY': 'easyJet',
    'RYR': 'Ryanair',
    'EIN': 'Aer Lingus',
    'DLH': 'Lufthansa',
    'AFR': 'Air France',
    'KLM': 'KLM Royal Dutch Airlines',
    'SWR': 'SWISS International Air Lines',
    'AUA': 'Austrian Airlines',
    'BEL': 'Brussels Airlines',
    'IBE': 'Iberia',
    'VLG': 'Vueling',
    'TAP': 'TAP Air Portugal',
    'ITY': 'ITA Airways',
    'SAS': 'Scandinavian Airlines',
    'FIN': 'Finnair',
    'NOZ': 'Norwegian Air Shuttle',
    'LOT': 'LOT Polish Airlines',
    'THY': 'Turkish Airlines',
    'AEE': 'Aegean Airlines',
    'UAE': 'Emirates',
    'QTR': 'Qatar Airways',
    'ETD': 'Etihad Airways',
    'SVA': 'Saudia',
    'ELY': 'El Al',
    'RJA': 'Royal Jordanian',
    'SIA': 'Singapore Airlines',
    'CPA': 'Cathay Pacific',
    'JAL': 'Japan Airlines',
    'ANA': 'All Nippon Airways',
    'KAL': 'Korean Air',
    'AAR': 'Asiana Airlines',
    'CAL': 'China Airlines',
    'EVA': 'EVA Air',
    'CCA': 'Air China',
    'CES': 'China Eastern Airlines',
    'CSN': 'China Southern Airlines',
    'AIC': 'Air India',
    'IGO': 'IndiGo',
    'THA': 'Thai Airways',
    'MAS': 'Malaysia Airlines',
    'GIA': 'Garuda Indonesia',
    'PAL': 'Philippine Airlines',
    'HVN': 'Vietnam Airlines',
    'QFA': 'Qantas',
    'VOZ': 'Virgin Australia',
    'ANZ': 'Air New Zealand',
    'LAN': 'LATAM Airlines',
    'AVA': 'Avianca',
    'AMX': 'Aeromexico',
    'CMP': 'Copa Airlines',
    'ETH': 'Ethiopian Airlines',
    'MSR': 'EgyptAir',
    'RAM': 'Royal Air Maroc',
    'KQA': 'Kenya Airways',
    'SAA': 'South African Airways',
    'FDX': 'FedEx Express',
    'UPS': 'UPS Airlines',
}

ICAO_TO_IATA_AIRLINES: Dict[str, str] = {v: k for k, v in IATA_TO_ICAO_AIRLINES.items()}

# Airport database indexed by ICAO code (also cross-indexed by IATA below)
AIRPORTS_BY_ICAO: Dict[str, Dict[str, Any]] = {
    # North America
    'KJFK': {
        'icao': 'KJFK', 'iata': 'JFK',
        'name': 'John F. Kennedy International Airport',
        'city': 'New York', 'country': 'United States',
        'lat': 40.6413, 'lon': -73.7781, 'tz': 'America/New_York',
    },
    'KEWR': {
        'icao': 'KEWR', 'iata': 'EWR',
        'name': 'Newark Liberty International Airport',
        'city': 'Newark', 'country': 'United States',
        'lat': 40.6895, 'lon': -74.1745, 'tz': 'America/New_York',
    },
    'KLGA': {
        'icao': 'KLGA', 'iata': 'LGA',
        'name': 'LaGuardia Airport',
        'city': 'New York', 'country': 'United States',
        'lat': 40.7769, 'lon': -73.8740, 'tz': 'America/New_York',
    },
    'KBOS': {
        'icao': 'KBOS', 'iata': 'BOS',
        'name': 'Boston Logan International Airport',
        'city': 'Boston', 'country': 'United States',
        'lat': 42.3656, 'lon': -71.0096, 'tz': 'America/New_York',
    },
    'KIAD': {
        'icao': 'KIAD', 'iata': 'IAD',
        'name': 'Washington Dulles International Airport',
        'city': 'Washington, D.C.', 'country': 'United States',
        'lat': 38.9531, 'lon': -77.4565, 'tz': 'America/New_York',
    },
    'KDCA': {
        'icao': 'KDCA', 'iata': 'DCA',
        'name': 'Ronald Reagan Washington National Airport',
        'city': 'Washington, D.C.', 'country': 'United States',
        'lat': 38.8512, 'lon': -77.0402, 'tz': 'America/New_York',
    },
    'KPHL': {
        'icao': 'KPHL', 'iata': 'PHL',
        'name': 'Philadelphia International Airport',
        'city': 'Philadelphia', 'country': 'United States',
        'lat': 39.8744, 'lon': -75.2424, 'tz': 'America/New_York',
    },
    'KATL': {
        'icao': 'KATL', 'iata': 'ATL',
        'name': 'Hartsfield-Jackson Atlanta International Airport',
        'city': 'Atlanta', 'country': 'United States',
        'lat': 33.6407, 'lon': -84.4277, 'tz': 'America/New_York',
    },
    'KMIA': {
        'icao': 'KMIA', 'iata': 'MIA',
        'name': 'Miami International Airport',
        'city': 'Miami', 'country': 'United States',
        'lat': 25.7959, 'lon': -80.2870, 'tz': 'America/New_York',
    },
    'KMCO': {
        'icao': 'KMCO', 'iata': 'MCO',
        'name': 'Orlando International Airport',
        'city': 'Orlando', 'country': 'United States',
        'lat': 28.4312, 'lon': -81.3081, 'tz': 'America/New_York',
    },
    'KCLT': {
        'icao': 'KCLT', 'iata': 'CLT',
        'name': 'Charlotte Douglas International Airport',
        'city': 'Charlotte', 'country': 'United States',
        'lat': 35.2144, 'lon': -80.9473, 'tz': 'America/New_York',
    },
    'KDTW': {
        'icao': 'KDTW', 'iata': 'DTW',
        'name': 'Detroit Metropolitan Wayne County Airport',
        'city': 'Detroit', 'country': 'United States',
        'lat': 42.2162, 'lon': -83.3554, 'tz': 'America/Detroit',
    },
    'KORD': {
        'icao': 'KORD', 'iata': 'ORD',
        'name': "Chicago O'Hare International Airport",
        'city': 'Chicago', 'country': 'United States',
        'lat': 41.9742, 'lon': -87.9073, 'tz': 'America/Chicago',
    },
    'KMDW': {
        'icao': 'KMDW', 'iata': 'MDW',
        'name': 'Chicago Midway International Airport',
        'city': 'Chicago', 'country': 'United States',
        'lat': 41.7868, 'lon': -87.7522, 'tz': 'America/Chicago',
    },
    'KDFW': {
        'icao': 'KDFW', 'iata': 'DFW',
        'name': 'Dallas/Fort Worth International Airport',
        'city': 'Dallas-Fort Worth', 'country': 'United States',
        'lat': 32.8998, 'lon': -97.0403, 'tz': 'America/Chicago',
    },
    'KIAH': {
        'icao': 'KIAH', 'iata': 'IAH',
        'name': 'George Bush Intercontinental Airport',
        'city': 'Houston', 'country': 'United States',
        'lat': 29.9902, 'lon': -95.3368, 'tz': 'America/Chicago',
    },
    'KMSP': {
        'icao': 'KMSP', 'iata': 'MSP',
        'name': 'Minneapolis-Saint Paul International Airport',
        'city': 'Minneapolis', 'country': 'United States',
        'lat': 44.8848, 'lon': -93.2223, 'tz': 'America/Chicago',
    },
    'KDEN': {
        'icao': 'KDEN', 'iata': 'DEN',
        'name': 'Denver International Airport',
        'city': 'Denver', 'country': 'United States',
        'lat': 39.8561, 'lon': -104.6737, 'tz': 'America/Denver',
    },
    'KSLC': {
        'icao': 'KSLC', 'iata': 'SLC',
        'name': 'Salt Lake City International Airport',
        'city': 'Salt Lake City', 'country': 'United States',
        'lat': 40.7899, 'lon': -111.9791, 'tz': 'America/Denver',
    },
    'KPHX': {
        'icao': 'KPHX', 'iata': 'PHX',
        'name': 'Phoenix Sky Harbor International Airport',
        'city': 'Phoenix', 'country': 'United States',
        'lat': 33.4373, 'lon': -112.0078, 'tz': 'America/Phoenix',
    },
    'KLAS': {
        'icao': 'KLAS', 'iata': 'LAS',
        'name': 'Harry Reid International Airport',
        'city': 'Las Vegas', 'country': 'United States',
        'lat': 36.0840, 'lon': -115.1537, 'tz': 'America/Los_Angeles',
    },
    'KLAX': {
        'icao': 'KLAX', 'iata': 'LAX',
        'name': 'Los Angeles International Airport',
        'city': 'Los Angeles', 'country': 'United States',
        'lat': 33.9416, 'lon': -118.4085, 'tz': 'America/Los_Angeles',
    },
    'KSFO': {
        'icao': 'KSFO', 'iata': 'SFO',
        'name': 'San Francisco International Airport',
        'city': 'San Francisco', 'country': 'United States',
        'lat': 37.6213, 'lon': -122.3790, 'tz': 'America/Los_Angeles',
    },
    'KSAN': {
        'icao': 'KSAN', 'iata': 'SAN',
        'name': 'San Diego International Airport',
        'city': 'San Diego', 'country': 'United States',
        'lat': 32.7338, 'lon': -117.1933, 'tz': 'America/Los_Angeles',
    },
    'KSEA': {
        'icao': 'KSEA', 'iata': 'SEA',
        'name': 'Seattle-Tacoma International Airport',
        'city': 'Seattle', 'country': 'United States',
        'lat': 47.4502, 'lon': -122.3088, 'tz': 'America/Los_Angeles',
    },
    'PHNL': {
        'icao': 'PHNL', 'iata': 'HNL',
        'name': 'Daniel K. Inouye International Airport',
        'city': 'Honolulu', 'country': 'United States',
        'lat': 21.3187, 'lon': -157.9225, 'tz': 'Pacific/Honolulu',
    },
    'PANC': {
        'icao': 'PANC', 'iata': 'ANC',
        'name': 'Ted Stevens Anchorage International Airport',
        'city': 'Anchorage', 'country': 'United States',
        'lat': 61.1743, 'lon': -149.9962, 'tz': 'America/Anchorage',
    },
    'CYYZ': {
        'icao': 'CYYZ', 'iata': 'YYZ',
        'name': 'Toronto Pearson International Airport',
        'city': 'Toronto', 'country': 'Canada',
        'lat': 43.6777, 'lon': -79.6248, 'tz': 'America/Toronto',
    },
    'CYUL': {
        'icao': 'CYUL', 'iata': 'YUL',
        'name': 'Montreal-Pierre Elliott Trudeau International Airport',
        'city': 'Montreal', 'country': 'Canada',
        'lat': 45.4706, 'lon': -73.7408, 'tz': 'America/Toronto',
    },
    'CYVR': {
        'icao': 'CYVR', 'iata': 'YVR',
        'name': 'Vancouver International Airport',
        'city': 'Vancouver', 'country': 'Canada',
        'lat': 49.1967, 'lon': -123.1815, 'tz': 'America/Vancouver',
    },
    'CYYC': {
        'icao': 'CYYC', 'iata': 'YYC',
        'name': 'Calgary International Airport',
        'city': 'Calgary', 'country': 'Canada',
        'lat': 51.1215, 'lon': -114.0076, 'tz': 'America/Edmonton',
    },
    'MMMX': {
        'icao': 'MMMX', 'iata': 'MEX',
        'name': 'Mexico City International Airport',
        'city': 'Mexico City', 'country': 'Mexico',
        'lat': 19.4363, 'lon': -99.0721, 'tz': 'America/Mexico_City',
    },
    'MMUN': {
        'icao': 'MMUN', 'iata': 'CUN',
        'name': 'Cancun International Airport',
        'city': 'Cancun', 'country': 'Mexico',
        'lat': 21.0365, 'lon': -86.8771, 'tz': 'America/Cancun',
    },
    # Europe
    'EGLL': {
        'icao': 'EGLL', 'iata': 'LHR',
        'name': 'London Heathrow Airport',
        'city': 'London', 'country': 'United Kingdom',
        'lat': 51.4700, 'lon': -0.4543, 'tz': 'Europe/London',
    },
    'EGKK': {
        'icao': 'EGKK', 'iata': 'LGW',
        'name': 'London Gatwick Airport',
        'city': 'London', 'country': 'United Kingdom',
        'lat': 51.1537, 'lon': -0.1821, 'tz': 'Europe/London',
    },
    'EGSS': {
        'icao': 'EGSS', 'iata': 'STN',
        'name': 'London Stansted Airport',
        'city': 'London', 'country': 'United Kingdom',
        'lat': 51.8860, 'lon': 0.2389, 'tz': 'Europe/London',
    },
    'EGCC': {
        'icao': 'EGCC', 'iata': 'MAN',
        'name': 'Manchester Airport',
        'city': 'Manchester', 'country': 'United Kingdom',
        'lat': 53.3537, 'lon': -2.2750, 'tz': 'Europe/London',
    },
    'EGPH': {
        'icao': 'EGPH', 'iata': 'EDI',
        'name': 'Edinburgh Airport',
        'city': 'Edinburgh', 'country': 'United Kingdom',
        'lat': 55.9508, 'lon': -3.3615, 'tz': 'Europe/London',
    },
    'EIDW': {
        'icao': 'EIDW', 'iata': 'DUB',
        'name': 'Dublin Airport',
        'city': 'Dublin', 'country': 'Ireland',
        'lat': 53.4264, 'lon': -6.2499, 'tz': 'Europe/Dublin',
    },
    'LFPG': {
        'icao': 'LFPG', 'iata': 'CDG',
        'name': 'Paris Charles de Gaulle Airport',
        'city': 'Paris', 'country': 'France',
        'lat': 49.0097, 'lon': 2.5479, 'tz': 'Europe/Paris',
    },
    'LFPO': {
        'icao': 'LFPO', 'iata': 'ORY',
        'name': 'Paris Orly Airport',
        'city': 'Paris', 'country': 'France',
        'lat': 48.7262, 'lon': 2.3652, 'tz': 'Europe/Paris',
    },
    'LFMN': {
        'icao': 'LFMN', 'iata': 'NCE',
        'name': "Nice Cote d'Azur Airport",
        'city': 'Nice', 'country': 'France',
        'lat': 43.6584, 'lon': 7.2159, 'tz': 'Europe/Paris',
    },
    'EDDF': {
        'icao': 'EDDF', 'iata': 'FRA',
        'name': 'Frankfurt Airport',
        'city': 'Frankfurt', 'country': 'Germany',
        'lat': 50.0379, 'lon': 8.5622, 'tz': 'Europe/Berlin',
    },
    'EDDM': {
        'icao': 'EDDM', 'iata': 'MUC',
        'name': 'Munich Airport',
        'city': 'Munich', 'country': 'Germany',
        'lat': 48.3537, 'lon': 11.7750, 'tz': 'Europe/Berlin',
    },
    'EDDB': {
        'icao': 'EDDB', 'iata': 'BER',
        'name': 'Berlin Brandenburg Airport',
        'city': 'Berlin', 'country': 'Germany',
        'lat': 52.3667, 'lon': 13.5033, 'tz': 'Europe/Berlin',
    },
    'EHAM': {
        'icao': 'EHAM', 'iata': 'AMS',
        'name': 'Amsterdam Airport Schiphol',
        'city': 'Amsterdam', 'country': 'Netherlands',
        'lat': 52.3105, 'lon': 4.7683, 'tz': 'Europe/Amsterdam',
    },
    'EBBR': {
        'icao': 'EBBR', 'iata': 'BRU',
        'name': 'Brussels Airport',
        'city': 'Brussels', 'country': 'Belgium',
        'lat': 50.9010, 'lon': 4.4856, 'tz': 'Europe/Brussels',
    },
    'LSZH': {
        'icao': 'LSZH', 'iata': 'ZRH',
        'name': 'Zurich Airport',
        'city': 'Zurich', 'country': 'Switzerland',
        'lat': 47.4582, 'lon': 8.5555, 'tz': 'Europe/Zurich',
    },
    'LSGG': {
        'icao': 'LSGG', 'iata': 'GVA',
        'name': 'Geneva Airport',
        'city': 'Geneva', 'country': 'Switzerland',
        'lat': 46.2381, 'lon': 6.1090, 'tz': 'Europe/Zurich',
    },
    'LOWW': {
        'icao': 'LOWW', 'iata': 'VIE',
        'name': 'Vienna International Airport',
        'city': 'Vienna', 'country': 'Austria',
        'lat': 48.1103, 'lon': 16.5697, 'tz': 'Europe/Vienna',
    },
    'LEMD': {
        'icao': 'LEMD', 'iata': 'MAD',
        'name': 'Adolfo Suarez Madrid-Barajas Airport',
        'city': 'Madrid', 'country': 'Spain',
        'lat': 40.4983, 'lon': -3.5676, 'tz': 'Europe/Madrid',
    },
    'LEBL': {
        'icao': 'LEBL', 'iata': 'BCN',
        'name': ' Josep Tarradellas Barcelona-El Prat Airport',
        'city': 'Barcelona', 'country': 'Spain',
        'lat': 41.2974, 'lon': 2.0833, 'tz': 'Europe/Madrid',
    },
    'LPPT': {
        'icao': 'LPPT', 'iata': 'LIS',
        'name': 'Humberto Delgado Airport',
        'city': 'Lisbon', 'country': 'Portugal',
        'lat': 38.7756, 'lon': -9.1354, 'tz': 'Europe/Lisbon',
    },
    'LIRF': {
        'icao': 'LIRF', 'iata': 'FCO',
        'name': 'Leonardo da Vinci-Fiumicino Airport',
        'city': 'Rome', 'country': 'Italy',
        'lat': 41.8003, 'lon': 12.2389, 'tz': 'Europe/Rome',
    },
    'LIMC': {
        'icao': 'LIMC', 'iata': 'MXP',
        'name': 'Milan Malpensa Airport',
        'city': 'Milan', 'country': 'Italy',
        'lat': 45.6301, 'lon': 8.7255, 'tz': 'Europe/Rome',
    },
    'EKCH': {
        'icao': 'EKCH', 'iata': 'CPH',
        'name': 'Copenhagen Airport',
        'city': 'Copenhagen', 'country': 'Denmark',
        'lat': 55.6180, 'lon': 12.6508, 'tz': 'Europe/Copenhagen',
    },
    'ESSA': {
        'icao': 'ESSA', 'iata': 'ARN',
        'name': 'Stockholm Arlanda Airport',
        'city': 'Stockholm', 'country': 'Sweden',
        'lat': 59.6498, 'lon': 17.9238, 'tz': 'Europe/Stockholm',
    },
    'ENGM': {
        'icao': 'ENGM', 'iata': 'OSL',
        'name': 'Oslo Airport, Gardermoen',
        'city': 'Oslo', 'country': 'Norway',
        'lat': 60.1976, 'lon': 11.1004, 'tz': 'Europe/Oslo',
    },
    'EFHK': {
        'icao': 'EFHK', 'iata': 'HEL',
        'name': 'Helsinki-Vantaa Airport',
        'city': 'Helsinki', 'country': 'Finland',
        'lat': 60.3172, 'lon': 24.9633, 'tz': 'Europe/Helsinki',
    },
    'EPWA': {
        'icao': 'EPWA', 'iata': 'WAW',
        'name': 'Warsaw Chopin Airport',
        'city': 'Warsaw', 'country': 'Poland',
        'lat': 52.1672, 'lon': 20.9679, 'tz': 'Europe/Warsaw',
    },
    'LGAV': {
        'icao': 'LGAV', 'iata': 'ATH',
        'name': 'Athens International Airport',
        'city': 'Athens', 'country': 'Greece',
        'lat': 37.9364, 'lon': 23.9445, 'tz': 'Europe/Athens',
    },
    'LTFM': {
        'icao': 'LTFM', 'iata': 'IST',
        'name': 'Istanbul Airport',
        'city': 'Istanbul', 'country': 'Turkey',
        'lat': 41.2753, 'lon': 28.7519, 'tz': 'Europe/Istanbul',
    },
    # Middle East
    'OMDB': {
        'icao': 'OMDB', 'iata': 'DXB',
        'name': 'Dubai International Airport',
        'city': 'Dubai', 'country': 'United Arab Emirates',
        'lat': 25.2532, 'lon': 55.3657, 'tz': 'Asia/Dubai',
    },
    'OMAA': {
        'icao': 'OMAA', 'iata': 'AUH',
        'name': 'Zayed International Airport',
        'city': 'Abu Dhabi', 'country': 'United Arab Emirates',
        'lat': 24.4330, 'lon': 54.6511, 'tz': 'Asia/Dubai',
    },
    'OTHH': {
        'icao': 'OTHH', 'iata': 'DOH',
        'name': 'Hamad International Airport',
        'city': 'Doha', 'country': 'Qatar',
        'lat': 25.2731, 'lon': 51.6081, 'tz': 'Asia/Qatar',
    },
    'OERK': {
        'icao': 'OERK', 'iata': 'RUH',
        'name': 'King Khalid International Airport',
        'city': 'Riyadh', 'country': 'Saudi Arabia',
        'lat': 24.9576, 'lon': 46.6988, 'tz': 'Asia/Riyadh',
    },
    'OEJN': {
        'icao': 'OEJN', 'iata': 'JED',
        'name': 'King Abdulaziz International Airport',
        'city': 'Jeddah', 'country': 'Saudi Arabia',
        'lat': 21.6796, 'lon': 39.1565, 'tz': 'Asia/Riyadh',
    },
    'LLBG': {
        'icao': 'LLBG', 'iata': 'TLV',
        'name': 'Ben Gurion Airport',
        'city': 'Tel Aviv', 'country': 'Israel',
        'lat': 32.0055, 'lon': 34.8854, 'tz': 'Asia/Jerusalem',
    },
    # Asia-Pacific
    'RJTT': {
        'icao': 'RJTT', 'iata': 'HND',
        'name': 'Tokyo Haneda Airport',
        'city': 'Tokyo', 'country': 'Japan',
        'lat': 35.5494, 'lon': 139.7798, 'tz': 'Asia/Tokyo',
    },
    'RJAA': {
        'icao': 'RJAA', 'iata': 'NRT',
        'name': 'Narita International Airport',
        'city': 'Tokyo', 'country': 'Japan',
        'lat': 35.7720, 'lon': 140.3929, 'tz': 'Asia/Tokyo',
    },
    'RJBB': {
        'icao': 'RJBB', 'iata': 'KIX',
        'name': 'Kansai International Airport',
        'city': 'Osaka', 'country': 'Japan',
        'lat': 34.4320, 'lon': 135.2304, 'tz': 'Asia/Tokyo',
    },
    'RKSI': {
        'icao': 'RKSI', 'iata': 'ICN',
        'name': 'Incheon International Airport',
        'city': 'Seoul', 'country': 'South Korea',
        'lat': 37.4602, 'lon': 126.4407, 'tz': 'Asia/Seoul',
    },
    'VHHH': {
        'icao': 'VHHH', 'iata': 'HKG',
        'name': 'Hong Kong International Airport',
        'city': 'Hong Kong', 'country': 'China',
        'lat': 22.3080, 'lon': 113.9185, 'tz': 'Asia/Hong_Kong',
    },
    'RCTP': {
        'icao': 'RCTP', 'iata': 'TPE',
        'name': 'Taiwan Taoyuan International Airport',
        'city': 'Taipei', 'country': 'Taiwan',
        'lat': 25.0797, 'lon': 121.2342, 'tz': 'Asia/Taipei',
    },
    'ZBAA': {
        'icao': 'ZBAA', 'iata': 'PEK',
        'name': 'Beijing Capital International Airport',
        'city': 'Beijing', 'country': 'China',
        'lat': 40.0799, 'lon': 116.6031, 'tz': 'Asia/Shanghai',
    },
    'ZSPD': {
        'icao': 'ZSPD', 'iata': 'PVG',
        'name': 'Shanghai Pudong International Airport',
        'city': 'Shanghai', 'country': 'China',
        'lat': 31.1443, 'lon': 121.8083, 'tz': 'Asia/Shanghai',
    },
    'ZGGG': {
        'icao': 'ZGGG', 'iata': 'CAN',
        'name': 'Guangzhou Baiyun International Airport',
        'city': 'Guangzhou', 'country': 'China',
        'lat': 23.3924, 'lon': 113.2988, 'tz': 'Asia/Shanghai',
    },
    'WSSS': {
        'icao': 'WSSS', 'iata': 'SIN',
        'name': 'Singapore Changi Airport',
        'city': 'Singapore', 'country': 'Singapore',
        'lat': 1.3644, 'lon': 103.9915, 'tz': 'Asia/Singapore',
    },
    'WMKK': {
        'icao': 'WMKK', 'iata': 'KUL',
        'name': 'Kuala Lumpur International Airport',
        'city': 'Kuala Lumpur', 'country': 'Malaysia',
        'lat': 2.7456, 'lon': 101.7099, 'tz': 'Asia/Kuala_Lumpur',
    },
    'VTBS': {
        'icao': 'VTBS', 'iata': 'BKK',
        'name': 'Suvarnabhumi Airport',
        'city': 'Bangkok', 'country': 'Thailand',
        'lat': 13.6900, 'lon': 100.7501, 'tz': 'Asia/Bangkok',
    },
    'RPLL': {
        'icao': 'RPLL', 'iata': 'MNL',
        'name': 'Ninoy Aquino International Airport',
        'city': 'Manila', 'country': 'Philippines',
        'lat': 14.5086, 'lon': 121.0194, 'tz': 'Asia/Manila',
    },
    'WIII': {
        'icao': 'WIII', 'iata': 'CGK',
        'name': 'Soekarno-Hatta International Airport',
        'city': 'Jakarta', 'country': 'Indonesia',
        'lat': -6.1256, 'lon': 106.6559, 'tz': 'Asia/Jakarta',
    },
    'VIDP': {
        'icao': 'VIDP', 'iata': 'DEL',
        'name': 'Indira Gandhi International Airport',
        'city': 'New Delhi', 'country': 'India',
        'lat': 28.5562, 'lon': 77.1000, 'tz': 'Asia/Kolkata',
    },
    'VABB': {
        'icao': 'VABB', 'iata': 'BOM',
        'name': 'Chhatrapati Shivaji Maharaj International Airport',
        'city': 'Mumbai', 'country': 'India',
        'lat': 19.0896, 'lon': 72.8656, 'tz': 'Asia/Kolkata',
    },
    'VOBL': {
        'icao': 'VOBL', 'iata': 'BLR',
        'name': 'Kempegowda International Airport',
        'city': 'Bengaluru', 'country': 'India',
        'lat': 13.1986, 'lon': 77.7066, 'tz': 'Asia/Kolkata',
    },
    'YSSY': {
        'icao': 'YSSY', 'iata': 'SYD',
        'name': 'Sydney Kingsford Smith Airport',
        'city': 'Sydney', 'country': 'Australia',
        'lat': -33.9399, 'lon': 151.1753, 'tz': 'Australia/Sydney',
    },
    'YMML': {
        'icao': 'YMML', 'iata': 'MEL',
        'name': 'Melbourne Airport',
        'city': 'Melbourne', 'country': 'Australia',
        'lat': -37.6690, 'lon': 144.8410, 'tz': 'Australia/Melbourne',
    },
    'YBBN': {
        'icao': 'YBBN', 'iata': 'BNE',
        'name': 'Brisbane Airport',
        'city': 'Brisbane', 'country': 'Australia',
        'lat': -27.3942, 'lon': 153.1218, 'tz': 'Australia/Brisbane',
    },
    'YPPH': {
        'icao': 'YPPH', 'iata': 'PER',
        'name': 'Perth Airport',
        'city': 'Perth', 'country': 'Australia',
        'lat': -31.9385, 'lon': 115.9672, 'tz': 'Australia/Perth',
    },
    'NZAA': {
        'icao': 'NZAA', 'iata': 'AKL',
        'name': 'Auckland Airport',
        'city': 'Auckland', 'country': 'New Zealand',
        'lat': -37.0082, 'lon': 174.7850, 'tz': 'Pacific/Auckland',
    },
    # South America & Africa
    'SBGR': {
        'icao': 'SBGR', 'iata': 'GRU',
        'name': 'Sao Paulo/Guarulhos International Airport',
        'city': 'Sao Paulo', 'country': 'Brazil',
        'lat': -23.4356, 'lon': -46.4731, 'tz': 'America/Sao_Paulo',
    },
    'SAEZ': {
        'icao': 'SAEZ', 'iata': 'EZE',
        'name': 'Ministro Pistarini International Airport',
        'city': 'Buenos Aires', 'country': 'Argentina',
        'lat': -34.8222, 'lon': -58.5358, 'tz': 'America/Argentina/Buenos_Aires',
    },
    'SCEL': {
        'icao': 'SCEL', 'iata': 'SCL',
        'name': 'Arturo Merino Benitez International Airport',
        'city': 'Santiago', 'country': 'Chile',
        'lat': -33.3930, 'lon': -70.7858, 'tz': 'America/Santiago',
    },
    'SKBO': {
        'icao': 'SKBO', 'iata': 'BOG',
        'name': 'El Dorado International Airport',
        'city': 'Bogota', 'country': 'Colombia',
        'lat': 4.7016, 'lon': -74.1469, 'tz': 'America/Bogota',
    },
    'FAOR': {
        'icao': 'FAOR', 'iata': 'JNB',
        'name': 'O. R. Tambo International Airport',
        'city': 'Johannesburg', 'country': 'South Africa',
        'lat': -26.1367, 'lon': 28.2411, 'tz': 'Africa/Johannesburg',
    },
    'FACT': {
        'icao': 'FACT', 'iata': 'CPT',
        'name': 'Cape Town International Airport',
        'city': 'Cape Town', 'country': 'South Africa',
        'lat': -33.9715, 'lon': 18.6021, 'tz': 'Africa/Johannesburg',
    },
    'HECA': {
        'icao': 'HECA', 'iata': 'CAI',
        'name': 'Cairo International Airport',
        'city': 'Cairo', 'country': 'Egypt',
        'lat': 30.1219, 'lon': 31.4056, 'tz': 'Africa/Cairo',
    },
    'GMMN': {
        'icao': 'GMMN', 'iata': 'CMN',
        'name': 'Mohammed V International Airport',
        'city': 'Casablanca', 'country': 'Morocco',
        'lat': 33.3675, 'lon': -7.5898, 'tz': 'Africa/Casablanca',
    },
    'HAAB': {
        'icao': 'HAAB', 'iata': 'ADD',
        'name': 'Addis Ababa Bole International Airport',
        'city': 'Addis Ababa', 'country': 'Ethiopia',
        'lat': 8.9779, 'lon': 38.7993, 'tz': 'Africa/Addis_Ababa',
    },
    'HKJK': {
        'icao': 'HKJK', 'iata': 'NBO',
        'name': 'Jomo Kenyatta International Airport',
        'city': 'Nairobi', 'country': 'Kenya',
        'lat': -1.3192, 'lon': 36.9278, 'tz': 'Africa/Nairobi',
    },
}

AIRPORTS_BY_IATA: Dict[str, Dict[str, Any]] = {
    info['iata']: info for info in AIRPORTS_BY_ICAO.values() if info.get('iata')
}

# Prefix-based fallback metadata for ICAO airport codes not explicitly in AIRPORTS_BY_ICAO
ICAO_PREFIX_DEFAULTS: List[Tuple[str, Dict[str, Any]]] = [
    ('EG', {'country': 'United Kingdom', 'tz': 'Europe/London', 'lat': 51.5074, 'lon': -0.1278}),
    ('EI', {'country': 'Ireland', 'tz': 'Europe/Dublin', 'lat': 53.3498, 'lon': -6.2603}),
    ('LF', {'country': 'France', 'tz': 'Europe/Paris', 'lat': 48.8566, 'lon': 2.3522}),
    ('ED', {'country': 'Germany', 'tz': 'Europe/Berlin', 'lat': 50.1109, 'lon': 8.6821}),
    ('ET', {'country': 'Germany', 'tz': 'Europe/Berlin', 'lat': 52.5200, 'lon': 13.4050}),
    ('EH', {'country': 'Netherlands', 'tz': 'Europe/Amsterdam', 'lat': 52.3676, 'lon': 4.9041}),
    ('EB', {'country': 'Belgium', 'tz': 'Europe/Brussels', 'lat': 50.8503, 'lon': 4.3517}),
    ('LS', {'country': 'Switzerland', 'tz': 'Europe/Zurich', 'lat': 47.3769, 'lon': 8.5417}),
    ('LO', {'country': 'Austria', 'tz': 'Europe/Vienna', 'lat': 48.2082, 'lon': 16.3738}),
    ('LE', {'country': 'Spain', 'tz': 'Europe/Madrid', 'lat': 40.4168, 'lon': -3.7038}),
    ('LP', {'country': 'Portugal', 'tz': 'Europe/Lisbon', 'lat': 38.7223, 'lon': -9.1393}),
    ('LI', {'country': 'Italy', 'tz': 'Europe/Rome', 'lat': 41.9028, 'lon': 12.4964}),
    ('EK', {'country': 'Denmark', 'tz': 'Europe/Copenhagen', 'lat': 55.6761, 'lon': 12.5683}),
    ('ES', {'country': 'Sweden', 'tz': 'Europe/Stockholm', 'lat': 59.3293, 'lon': 18.0686}),
    ('EN', {'country': 'Norway', 'tz': 'Europe/Oslo', 'lat': 59.9139, 'lon': 10.7522}),
    ('EF', {'country': 'Finland', 'tz': 'Europe/Helsinki', 'lat': 60.1699, 'lon': 24.9384}),
    ('EP', {'country': 'Poland', 'tz': 'Europe/Warsaw', 'lat': 52.2297, 'lon': 21.0122}),
    ('LG', {'country': 'Greece', 'tz': 'Europe/Athens', 'lat': 37.9838, 'lon': 23.7275}),
    ('LT', {'country': 'Turkey', 'tz': 'Europe/Istanbul', 'lat': 41.0082, 'lon': 28.9784}),
    ('OM', {'country': 'United Arab Emirates', 'tz': 'Asia/Dubai', 'lat': 25.2048, 'lon': 55.2708}),
    ('OT', {'country': 'Qatar', 'tz': 'Asia/Qatar', 'lat': 25.2854, 'lon': 51.5310}),
    ('OE', {'country': 'Saudi Arabia', 'tz': 'Asia/Riyadh', 'lat': 24.7136, 'lon': 46.6753}),
    ('LL', {'country': 'Israel', 'tz': 'Asia/Jerusalem', 'lat': 32.0853, 'lon': 34.7818}),
    ('RJ', {'country': 'Japan', 'tz': 'Asia/Tokyo', 'lat': 35.6762, 'lon': 139.6503}),
    ('RK', {'country': 'South Korea', 'tz': 'Asia/Seoul', 'lat': 37.5665, 'lon': 126.9780}),
    ('VH', {'country': 'Hong Kong', 'tz': 'Asia/Hong_Kong', 'lat': 22.3193, 'lon': 114.1694}),
    ('RC', {'country': 'Taiwan', 'tz': 'Asia/Taipei', 'lat': 25.0330, 'lon': 121.5654}),
    ('ZB', {'country': 'China', 'tz': 'Asia/Shanghai', 'lat': 39.9042, 'lon': 116.4074}),
    ('ZS', {'country': 'China', 'tz': 'Asia/Shanghai', 'lat': 31.2304, 'lon': 121.4737}),
    ('ZG', {'country': 'China', 'tz': 'Asia/Shanghai', 'lat': 23.1291, 'lon': 113.2644}),
    ('WS', {'country': 'Singapore', 'tz': 'Asia/Singapore', 'lat': 1.3521, 'lon': 103.8198}),
    ('WM', {'country': 'Malaysia', 'tz': 'Asia/Kuala_Lumpur', 'lat': 3.1390, 'lon': 101.6869}),
    ('VT', {'country': 'Thailand', 'tz': 'Asia/Bangkok', 'lat': 13.7563, 'lon': 100.5018}),
    ('RP', {'country': 'Philippines', 'tz': 'Asia/Manila', 'lat': 14.5995, 'lon': 120.9842}),
    ('WI', {'country': 'Indonesia', 'tz': 'Asia/Jakarta', 'lat': -6.2088, 'lon': 106.8456}),
    ('VI', {'country': 'India', 'tz': 'Asia/Kolkata', 'lat': 28.6139, 'lon': 77.2090}),
    ('VA', {'country': 'India', 'tz': 'Asia/Kolkata', 'lat': 19.0760, 'lon': 72.8777}),
    ('VO', {'country': 'India', 'tz': 'Asia/Kolkata', 'lat': 12.9716, 'lon': 77.5946}),
    ('YS', {'country': 'Australia', 'tz': 'Australia/Sydney', 'lat': -33.8688, 'lon': 151.2093}),
    ('YM', {'country': 'Australia', 'tz': 'Australia/Melbourne', 'lat': -37.8136, 'lon': 144.9631}),
    ('YB', {'country': 'Australia', 'tz': 'Australia/Brisbane', 'lat': -27.4705, 'lon': 153.0260}),
    ('YP', {'country': 'Australia', 'tz': 'Australia/Perth', 'lat': -31.9523, 'lon': 115.8613}),
    ('NZ', {'country': 'New Zealand', 'tz': 'Pacific/Auckland', 'lat': -36.8485, 'lon': 174.7633}),
    ('SB', {'country': 'Brazil', 'tz': 'America/Sao_Paulo', 'lat': -23.5505, 'lon': -46.6333}),
    ('SA', {'country': 'Argentina', 'tz': 'America/Argentina/Buenos_Aires', 'lat': -34.6037, 'lon': -58.3816}),
    ('SC', {'country': 'Chile', 'tz': 'America/Santiago', 'lat': -33.4489, 'lon': -70.6693}),
    ('SK', {'country': 'Colombia', 'tz': 'America/Bogota', 'lat': 4.7110, 'lon': -74.0721}),
    ('MM', {'country': 'Mexico', 'tz': 'America/Mexico_City', 'lat': 19.4326, 'lon': -99.1332}),
    ('FA', {'country': 'South Africa', 'tz': 'Africa/Johannesburg', 'lat': -26.2041, 'lon': 28.0473}),
    ('HE', {'country': 'Egypt', 'tz': 'Africa/Cairo', 'lat': 30.0444, 'lon': 31.2357}),
    ('GM', {'country': 'Morocco', 'tz': 'Africa/Casablanca', 'lat': 33.5731, 'lon': -7.5898}),
    ('HA', {'country': 'Ethiopia', 'tz': 'Africa/Addis_Ababa', 'lat': 9.0320, 'lon': 38.7469}),
    ('HK', {'country': 'Kenya', 'tz': 'Africa/Nairobi', 'lat': -1.2921, 'lon': 36.8219}),
    ('CY', {'country': 'Canada', 'tz': 'America/Toronto', 'lat': 43.6532, 'lon': -79.3832}),
    ('PH', {'country': 'United States (Hawaii)', 'tz': 'Pacific/Honolulu', 'lat': 21.3069, 'lon': -157.8583}),
    ('PA', {'country': 'United States (Alaska)', 'tz': 'America/Anchorage', 'lat': 61.2181, 'lon': -149.9003}),
    ('K', {'country': 'United States', 'tz': 'America/New_York', 'lat': 39.8283, 'lon': -98.5795}),
]


def resolve_airport(code: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Resolves an ICAO or IATA airport code to detailed location and timezone metadata.
    """
    if not code:
        return None
    cleaned = code.strip().upper()
    if not cleaned:
        return None

    if cleaned in AIRPORTS_BY_ICAO:
        return dict(AIRPORTS_BY_ICAO[cleaned])

    if cleaned in AIRPORTS_BY_IATA:
        return dict(AIRPORTS_BY_IATA[cleaned])

    # Fallback using ICAO regional prefix
    for prefix, meta in ICAO_PREFIX_DEFAULTS:
        if cleaned.startswith(prefix):
            return {
                'icao': cleaned,
                'iata': cleaned[-3:] if len(cleaned) == 4 and cleaned.startswith('K') else cleaned,
                'name': f'{cleaned} Regional Airport',
                'city': meta['country'],
                'country': meta['country'],
                'lat': meta['lat'],
                'lon': meta['lon'],
                'tz': meta['tz'],
            }

    return {
        'icao': cleaned,
        'iata': cleaned,
        'name': f'Airport {cleaned}',
        'city': cleaned,
        'country': 'International',
        'lat': 20.0,
        'lon': 0.0,
        'tz': 'UTC',
    }


def infer_timezone_from_coordinates(lat: Optional[float], lon: Optional[float]) -> str:
    """
    Approximates an IANA timezone name from geographic coordinates when an airport is unknown.
    """
    if lat is None or lon is None:
        return 'UTC'

    # Find nearest known airport within 12 degrees to borrow accurate regional IANA timezone
    best_tz = None
    best_dist_sq = 144.0
    for airport in AIRPORTS_BY_ICAO.values():
        dlat = lat - airport['lat']
        dlon = lon - airport['lon']
        dist_sq = dlat * dlat + dlon * dlon
        if dist_sq < best_dist_sq:
            best_dist_sq = dist_sq
            best_tz = airport['tz']

    if best_tz:
        return best_tz

    # Longitude-based UTC offset fallback
    offset_hours = int(round(lon / 15.0))
    offset_hours = max(-12, min(14, offset_hours))
    if offset_hours == 0:
        return 'UTC'
    # Note: Etc/GMT sign convention is inverted in IANA tzdb (Etc/GMT-2 is UTC+2)
    sign = '-' if offset_hours > 0 else '+'
    return f'Etc/GMT{sign}{abs(offset_hours)}'


def format_timestamp_in_tz(unix_ts: Optional[int], tz_name: str) -> Dict[str, str]:
    """
    Formats a Unix timestamp in the specified IANA timezone and returns structured display strings.
    """
    if not unix_ts:
        return {
            'formatted': 'In Progress / TBD',
            'local_time': 'TBD',
            'local_date': '',
            'utc_time': 'TBD',
            'tz_name': tz_name or 'UTC',
            'tz_abbrev': 'UTC',
            'utc_offset': 'UTC+00:00',
            'tz_display': f'{tz_name or "UTC"} (UTC+00:00)',
        }

    utc_dt = datetime.fromtimestamp(unix_ts, tz=dt_timezone.utc)
    try:
        tz = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError, Exception):
        tz = dt_timezone.utc
        tz_name = 'UTC'

    local_dt = utc_dt.astimezone(tz)
    tz_abbrev = local_dt.strftime('%Z') or 'UTC'
    raw_offset = local_dt.strftime('%z')  # e.g. -0400 or +0100
    if len(raw_offset) == 5:
        utc_offset = f'UTC{raw_offset[:3]}:{raw_offset[3:]}'
    else:
        utc_offset = 'UTC+00:00'

    tz_display = f'{tz_name} ({tz_abbrev}, {utc_offset})'
    return {
        'formatted': f"{local_dt.strftime('%b %d, %Y %H:%M:%S')} {tz_abbrev}",
        'local_time': local_dt.strftime('%H:%M:%S'),
        'local_date': local_dt.strftime('%b %d, %Y'),
        'utc_time': f"{utc_dt.strftime('%Y-%m-%d %H:%M:%S')} UTC",
        'tz_name': tz_name,
        'tz_abbrev': tz_abbrev,
        'utc_offset': utc_offset,
        'tz_display': tz_display,
    }


def normalize_flight_query(raw_query: str) -> Dict[str, Any]:
    """
    Normalizes user input (e.g., "BA 117", "BA117", "BAW117", "UA901", "UAL901")
    into candidate callsigns (ICAO & IATA), flight number digits, and airline info.
    """
    cleaned = ''.join(ch for ch in (raw_query or '').upper() if ch.isalnum())
    if not cleaned:
        return {
            'raw': '',
            'cleaned': '',
            'candidates': [],
            'icao_callsign': '',
            'iata_flight': '',
            'airline_name': '',
            'number_part': '',
        }

    candidates = [cleaned]
    icao_callsign = cleaned
    iata_flight = cleaned
    airline_name = ''
    number_part = ''

    # Check if starts with 3 letters + digits (ICAO format, e.g., BAW117, UAL901)
    if len(cleaned) >= 4 and cleaned[:3].isalpha() and cleaned[3:].isdigit():
        icao_prefix = cleaned[:3]
        number_part = cleaned[3:].lstrip('0') or '0'
        icao_callsign = f'{icao_prefix}{cleaned[3:]}'
        icao_trimmed = f'{icao_prefix}{number_part}'
        airline_name = ICAO_TO_AIRLINE_NAME.get(icao_prefix, '')
        if icao_trimmed not in candidates:
            candidates.append(icao_trimmed)
        if icao_prefix in ICAO_TO_IATA_AIRLINES:
            iata_prefix = ICAO_TO_IATA_AIRLINES[icao_prefix]
            iata_flight = f'{iata_prefix}{number_part}'
            if iata_flight not in candidates:
                candidates.append(iata_flight)

    # Check if starts with 2 alphanumeric IATA prefix + digits (e.g., BA117, UA901, B6123, U245)
    elif len(cleaned) >= 3 and cleaned[:2] in IATA_TO_ICAO_AIRLINES and cleaned[2:].isdigit():
        iata_prefix = cleaned[:2]
        number_part = cleaned[2:].lstrip('0') or '0'
        icao_prefix = IATA_TO_ICAO_AIRLINES[iata_prefix]
        airline_name = ICAO_TO_AIRLINE_NAME.get(icao_prefix, '')
        icao_callsign = f'{icao_prefix}{cleaned[2:]}'
        icao_trimmed = f'{icao_prefix}{number_part}'
        iata_flight = f'{iata_prefix}{number_part}'
        for cand in (icao_callsign, icao_trimmed, iata_flight):
            if cand not in candidates:
                candidates.append(cand)

    # General letter prefix + digits
    else:
        idx = 0
        while idx < len(cleaned) and cleaned[idx].isalpha():
            idx += 1
        prefix = cleaned[:idx]
        rest = cleaned[idx:]
        if prefix and rest.isdigit():
            number_part = rest.lstrip('0') or '0'
            if prefix in IATA_TO_ICAO_AIRLINES:
                icao_prefix = IATA_TO_ICAO_AIRLINES[prefix]
                icao_callsign = f'{icao_prefix}{number_part}'
                airline_name = ICAO_TO_AIRLINE_NAME.get(icao_prefix, '')
                if icao_callsign not in candidates:
                    candidates.insert(0, icao_callsign)
            elif prefix in ICAO_TO_AIRLINE_NAME:
                airline_name = ICAO_TO_AIRLINE_NAME[prefix]
        elif cleaned.isdigit():
            number_part = cleaned.lstrip('0') or '0'

    return {
        'raw': raw_query.strip(),
        'cleaned': cleaned,
        'candidates': candidates,
        'icao_callsign': icao_callsign,
        'iata_flight': iata_flight,
        'airline_name': airline_name,
        'number_part': number_part,
    }
