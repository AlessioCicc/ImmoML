import random

def process_data(location=None, min_space=None, max_space=None, min_rooms=None, max_rooms=None, min_bathrooms=None, max_bathrooms=None, condition=None, floor=None, elevator=None, garage=None, energy_efficiency=None, min_year=None, max_year=None):
    # Qui inserisci la logica per elaborare i dati in base agli input
    processed_results = {
        'location': location if location else "Non specificato",
        # ... altri campi processati
    }
    return data


def generate_dummy_heatmap_data(lat=41.8797737, lon=12.4674504, num_points=100, spread=0.01):
    data = []
    for _ in range(num_points):
        dummy_lat = lat + random.uniform(-spread, spread)
        dummy_lon = lon + random.uniform(-spread, spread)
        value = random.uniform(0, 1)
        data.append({'lat': dummy_lat, 'lon': dummy_lon, 'value': value})
    return data
