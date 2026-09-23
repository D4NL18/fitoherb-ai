# Contrato de API: Fitoherb AI Roteirização Comercial

Serviço: `fitoherb-ai` (FastAPI)  
Porta Padrão: `8000`  
Prefixo: `/api/v1/routing`

---

### 1. `POST /api/v1/routing/optimize`
Executa o Algoritmo Genético de Vendedor Único com Trava de Ordem (Locked-Order GA) sobre a matriz viária OSRM.

**Request Body (`OptimizeRouteRequest`):**
```json
{
  "depot": {
    "id": "base-vendedor",
    "name": "Minha Residência (Base)",
    "lat": -12.8992,
    "lon": -38.3242,
    "address": {
      "street": "Rua Itaeté",
      "number": "434",
      "neighborhood": "Pitangueiras",
      "city": "Lauro de Freitas",
      "state": "BA",
      "postal_code": "42701-360",
      "full_address": "Rua Itaeté, 434, Pitangueiras, Lauro de Freitas - BA"
    }
  },
  "stops": [
    {
      "id": "stop-1",
      "name": "Drogaria São Paulo - Pituba",
      "lat": -12.9984,
      "lon": -38.4908,
      "priority": "HIGH",
      "fixed_order": 1,
      "address": {
        "street": "Av. Manoel Dias",
        "number": "1500",
        "neighborhood": "Pituba",
        "city": "Salvador",
        "state": "BA",
        "postal_code": "41830-000",
        "full_address": "Av. Manoel Dias, 1500, Pituba, Salvador - BA"
      }
    },
    {
      "id": "stop-2",
      "name": "Farmácia Central - Barra",
      "lat": -13.0090,
      "lon": -38.5300,
      "priority": "REGULAR",
      "fixed_order": null,
      "address": {
        "street": "Av. Oceânica",
        "number": "300",
        "neighborhood": "Barra",
        "city": "Salvador",
        "state": "BA",
        "postal_code": "40140-130",
        "full_address": "Av. Oceânica, 300, Barra, Salvador - BA"
      }
    }
  ],
  "return_to_depot": true
}
```

**Response 200 OK (`OptimizeRouteResponse`):**
```json
{
  "total_time_minutes": 48.5,
  "total_distance_km": 24.2,
  "stops_count": 2,
  "ordered_stops": [
    {
      "step": 0,
      "id": "base-vendedor",
      "name": "Minha Residência (Base)",
      "action": "DEPARTURE",
      "is_fixed": true,
      "arrival_time_minutes": 0.0,
      "address": {
        "street": "Rua Itaeté",
        "number": "434",
        "neighborhood": "Pitangueiras",
        "city": "Lauro de Freitas",
        "state": "BA",
        "postal_code": "42701-360",
        "full_address": "Rua Itaeté, 434, Pitangueiras, Lauro de Freitas - BA"
      }
    },
    {
      "step": 1,
      "id": "stop-1",
      "name": "Drogaria São Paulo - Pituba",
      "action": "VISIT",
      "is_fixed": true,
      "arrival_time_minutes": 22.4,
      "address": {
        "street": "Av. Manoel Dias",
        "number": "1500",
        "neighborhood": "Pituba",
        "city": "Salvador",
        "state": "BA",
        "postal_code": "41830-000",
        "full_address": "Av. Manoel Dias, 1500, Pituba, Salvador - BA"
      }
    },
    {
      "step": 2,
      "id": "stop-2",
      "name": "Farmácia Central - Barra",
      "action": "VISIT",
      "is_fixed": false,
      "arrival_time_minutes": 35.1,
      "address": {
        "street": "Av. Oceânica",
        "number": "300",
        "neighborhood": "Barra",
        "city": "Salvador",
        "state": "BA",
        "postal_code": "40140-130",
        "full_address": "Av. Oceânica, 300, Barra, Salvador - BA"
      }
    },
    {
      "step": 3,
      "id": "base-vendedor",
      "name": "Minha Residência (Base)",
      "action": "RETURN",
      "is_fixed": true,
      "arrival_time_minutes": 48.5,
      "address": {
        "street": "Rua Itaeté",
        "number": "434",
        "neighborhood": "Pitangueiras",
        "city": "Lauro de Freitas",
        "state": "BA",
        "postal_code": "42701-360",
        "full_address": "Rua Itaeté, 434, Pitangueiras, Lauro de Freitas - BA"
      }
    }
  ],
  "geojson_geometry": {
    "type": "LineString",
    "coordinates": [[-38.3242, -12.8992], [-38.4908, -12.9984], [-38.5300, -13.0090], [-38.3242, -12.8992]]
  },
  "fitness_history": [120.4, 98.2, 85.1, 74.3]
}
```

---

### 2. `POST /api/v1/routing/export-pdf`
Gera o relatório em PDF com imagem do mapa, tabela sequencial e dados de visita.

---

### 3. `GET /api/v1/health`
Healthcheck do microserviço.
