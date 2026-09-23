import requests
import json

def test_pdf_export():
    payload = {
        'seller_name': 'Vendedor Exemplo Fitoherb',
        'date': '23/09/2026',
        'total_time_minutes': 58.8,
        'total_distance_km': 54.4,
        'ordered_stops': [
            {
                'step': 0,
                'id': 'base-1',
                'name': 'Base Matriz',
                'action': 'DEPARTURE',
                'is_fixed': True,
                'priority': 'REGULAR',
                'arrival_time_minutes': 0.0,
                'address': {
                    'street': 'Rua Itaete',
                    'number': '434',
                    'neighborhood': 'Pitangueiras',
                    'city': 'Lauro de Freitas',
                    'state': 'BA',
                    'postal_code': '42701-430'
                }
            },
            {
                'step': 1,
                'id': 'stop-2',
                'name': 'Cliente Farma 2',
                'action': 'VISIT',
                'is_fixed': True,
                'fixed_order': 1,
                'priority': 'REGULAR',
                'arrival_time_minutes': 25.4,
                'address': {
                    'street': 'Av. Tancredo Neves',
                    'number': '500',
                    'neighborhood': 'Caminho das Arvores',
                    'city': 'Salvador',
                    'state': 'BA',
                    'postal_code': '41820-020'
                }
            },
            {
                'step': 2,
                'id': 'stop-1',
                'name': 'Cliente Farma 1',
                'action': 'VISIT',
                'is_fixed': False,
                'priority': 'HIGH',
                'arrival_time_minutes': 40.2,
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
                'step': 3,
                'id': 'base-1',
                'name': 'Base Matriz',
                'action': 'RETURN',
                'is_fixed': True,
                'priority': 'REGULAR',
                'arrival_time_minutes': 58.8,
                'address': {
                    'street': 'Rua Itaete',
                    'number': '434',
                    'neighborhood': 'Pitangueiras',
                    'city': 'Lauro de Freitas',
                    'state': 'BA',
                    'postal_code': '42701-430'
                }
            }
        ]
    }

    res = requests.post('http://127.0.0.1:8000/api/v1/routing/export-pdf', json=payload)
    print('PDF EXPORT STATUS:', res.status_code)
    print('Content-Type:', res.headers.get('content-type'))
    print('Byte size of PDF:', len(res.content))
    assert res.status_code == 200
    assert 'application/pdf' in res.headers.get('content-type', '')
    assert len(res.content) > 1000
    print('SUCCESS: PDF export generated successfully!')

if __name__ == '__main__':
    test_pdf_export()
