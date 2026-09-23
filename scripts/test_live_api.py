import requests
import json

def test_api():
    payload = {
        'depot': {
            'id': 'base-1',
            'name': 'Base Matriz',
            'lat': -12.8992,
            'lon': -38.3242,
            'address': {
                'street': 'Rua Itaete',
                'number': '434',
                'neighborhood': 'Pitangueiras',
                'city': 'Lauro de Freitas',
                'state': 'BA',
                'postal_code': '42701-430'
            }
        },
        'stops': [
            {
                'id': 'stop-1',
                'name': 'Cliente Farma 1',
                'lat': -12.9714,
                'lon': -38.5014,
                'priority': 'HIGH',
                'fixed_order': None,
                'address': {
                    'street': 'Av. Sete de Setembro',
                    'number': '100',
                    'neighborhood': 'Centro',
                    'city': 'Salvador',
                    'state': 'BA',
                    'postal_code': '40060-001'
                }
            },
            {
                'id': 'stop-2',
                'name': 'Cliente Farma 2',
                'lat': -12.9800,
                'lon': -38.4500,
                'priority': 'REGULAR',
                'fixed_order': 1,
                'address': {
                    'street': 'Av. Tancredo Neves',
                    'number': '500',
                    'neighborhood': 'Caminho das Arvores',
                    'city': 'Salvador',
                    'state': 'BA',
                    'postal_code': '41820-020'
                }
            }
        ],
        'return_to_depot': True
    }

    res = requests.post('http://127.0.0.1:8000/api/v1/routing/optimize', json=payload)
    print('STATUS CODE:', res.status_code)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    print('Total Distance (km):', data.get('total_distance_km'))
    print('Total Time (min):', data.get('total_time_minutes'))
    print('Stops count:', data.get('stops_count'))
    print('Ordered stops:')
    for stop in data.get('ordered_stops', []):
        print(f"  Step {stop['step']}: {stop['name']} ({stop['action']}) - Fixed: {stop['is_fixed']} (Order: {stop['fixed_order']})")
    
    # Check that Step 1 has fixed_order 1
    assert data['ordered_stops'][1]['name'] == 'Cliente Farma 2', "Fixed stop should be in step 1"
    assert data['ordered_stops'][1]['is_fixed'] is True
    print("\nSUCCESS: Genetic Algorithm optimized route with locked-order guarantee verified over live HTTP API!")

if __name__ == "__main__":
    test_api()
