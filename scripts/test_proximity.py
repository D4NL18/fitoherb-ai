import urllib.request
import urllib.parse
import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def test():
    q = 'farmacia'
    base_lat, base_lon = -12.2664, -38.9663 # Feira de Santana
    delta = 1.5
    min_lon = base_lon - delta
    max_lon = base_lon + delta
    min_lat = base_lat - delta
    max_lat = base_lat + delta

    encoded_q = urllib.parse.quote(q)
    viewbox_str = f"{min_lon},{max_lat},{max_lon},{min_lat}"
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_q}&addressdetails=1&countrycodes=br&viewbox={viewbox_str}&bounded=0&limit=10"
    req = urllib.request.Request(url, headers={'User-Agent': 'FitoherbCommercialRouting/1.0'})

    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode())
        print('Total items returned:', len(data))
        for item in data:
            ilat, ilon = float(item['lat']), float(item['lon'])
            item['_dist'] = haversine(base_lat, base_lon, ilat, ilon)
        data.sort(key=lambda x: x['_dist'])
        for item in data[:4]:
            print(f"Dist: {item['_dist']:.1f} km -> {item.get('display_name')}")

if __name__ == '__main__':
    test()
