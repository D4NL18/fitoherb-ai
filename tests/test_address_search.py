import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_address_empty_query():
    response = client.get("/api/v1/routing/search-address?q=")
    assert response.status_code == 200
    assert response.json() == []

def test_search_address_proximity_sorting():
    # Simula base em Lauro de Freitas (-12.8992, -38.3242)
    # Item 1: Salvador Pituba (-12.99, -38.45) ~ 17 km
    # Item 2: Lauro de Freitas Centro (-12.90, -38.33) ~ 0.8 km
    # Item 3: Feira de Santana (-12.26, -38.96) ~ 90 km
    mock_photon_response = {
        "features": [
            {
                "geometry": {"coordinates": [-38.96, -12.26]},
                "properties": {
                    "name": "Farmácia Feira",
                    "city": "Feira de Santana",
                    "state": "Bahia",
                    "street": "Av Getúlio Vargas"
                }
            },
            {
                "geometry": {"coordinates": [-38.33, -12.90]},
                "properties": {
                    "name": "Farmácia Lauro Próxima",
                    "city": "Lauro de Freitas",
                    "state": "Bahia",
                    "street": "Rua Itaeté"
                }
            },
            {
                "geometry": {"coordinates": [-38.45, -12.99]},
                "properties": {
                    "name": "Farmácia Pituba",
                    "city": "Salvador",
                    "state": "Bahia",
                    "street": "Av Manoel Dias"
                }
            }
        ]
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        import json
        mock_resp.read.return_value = json.dumps(mock_photon_response).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        response = client.get("/api/v1/routing/search-address?q=farmacia&lat=-12.8992&lon=-38.3242")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # O mais próximo da base de Lauro de Freitas deve ser o primeiro!
        assert data[0]["name"] == "Farmácia Lauro Próxima"
        assert data[0]["_distance_km"] < data[1]["_distance_km"]
        assert data[1]["_distance_km"] < data[2]["_distance_km"]

def test_search_address_fuzzy_typo_tolerance():
    # Testa busca com erro de digitação ("drogazil" em vez de "drogasil")
    mock_photon_response = {
        "features": [
            {
                "geometry": {"coordinates": [-38.51, -12.97]},
                "properties": {
                    "name": "Drogasil",
                    "city": "Salvador",
                    "state": "Bahia",
                    "street": "Av Sete de Setembro"
                }
            }
        ]
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        import json
        mock_resp.read.return_value = json.dumps(mock_photon_response).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        response = client.get("/api/v1/routing/search-address?q=drogazil&lat=-12.97&lon=-38.51")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "Drogasil" in data[0]["display_name"]
        assert "lat" in data[0]
        assert "lon" in data[0]
        assert "address" in data[0]

def test_search_address_phonetic_expansion():
    # Testa se a busca por "itapuã" busca variantes fonéticas como "itapoan"
    calls = []
    def fake_urlopen(req, *args, **kwargs):
        calls.append(req.full_url)
        mock_resp = MagicMock()
        import json
        payload = {
            "features": [
                {
                    "geometry": {"coordinates": [-38.36, -12.93]},
                    "properties": {
                        "name": "Itapoan Praia",
                        "city": "Salvador",
                        "state": "Bahia",
                        "street": "Rua das Dunas"
                    }
                }
            ]
        }
        mock_resp.read.return_value = json.dumps(payload).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        return mock_resp

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        response = client.get("/api/v1/routing/search-address?q=itapuã&lat=-12.93&lon=-38.36")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "Itapoan" in data[0]["name"]
        # Verifica que url não inclui &lang=pt
        assert "lang=pt" not in calls[0]
