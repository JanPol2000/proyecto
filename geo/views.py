from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import Geo
import json
from collections import deque
import math

def lat_lon_to_pixels(lat, lon, lat_min, lat_max, lon_min, lon_max, width, height):
    x = (lon - lon_min) / (lon_max - lon_min) * width
    y = (lat_max - lat) / (lat_max - lat_min) * height
    return (x, y)


def lat_lon_to_pixels_points(puntos, lat, lon, lat_min, lat_max, lon_min, lon_max, width, height):
    nuevo = {}
    for k, v in puntos.items():
        nuevo[k] = lat_lon_to_pixels(v[0],v[1], lat_min, lat_max, lon_min, lon_max, width, height)
    return nuevo

POINTS_VALUES_REAL = {
    1: (19.66858432131808, -103.48490634413994),
    2: (19.6687395879138, -103.48524151746365),
    3: (19.668767370761707, -103.48531661931247),
    4: (19.66880778216824, -103.48536758128131),
    5: (19.668827987867694, -103.4854319542946),
    6: (19.66885071927653, -103.48550973835232),
    7: (19.668881027816624, -103.48539172116129),
    8: (19.669019941885402, -103.48542390766792),
    9: (19.669055301810978, -103.48540244999684),
    10: (19.669019941885402, -103.48532734814803),
    11: (19.668989633371584, -103.48534075919245),
    12: (19.668901233506837, -103.48515300457039)
}

GRAPH = {
    1: [2],
    2: [1, 3, 12],
    3: [2, 4],
    4: [3, 5],
    5: [4, 6, 7],
    6: [5, 8],
    7: [5, 8],
    8: [7, 9, 10, 11],
    9: [8, 10, 11],
    10: [8, 9, 11],
    11: [8, 9, 10, 12],
    12: [2, 11],
}

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def closest_point(x1, y1, points):
    closest_point = None
    closest_distance = float('inf')
    for point in points:
        dist = distance(x1, y1, point[0], point[1])
        if dist < closest_distance:
            closest_point = point
            closest_distance = dist
    return closest_point


def get_key(dictionary, value):
    for key in dictionary:
        if dictionary[key] == value:
            return key
    return None

def shortest_route(graph, points, start, end):
    distances = {node: float('inf') for node in graph} # diccionario para almacenar las distancias desde el punto de inicio a cada punto
    distances[start] = 0
    
    previous = {node: None for node in graph} # diccionario para almacenar el nodo anterior a cada nodo en la ruta más corta
    
    unvisited = list(graph.keys()) # lista para almacenar los nodos no visitados
    
    current_node = start
    while current_node != end:
        for neighbor in graph[current_node]:
            if neighbor not in unvisited:
                continue
            distance = math.sqrt((points[neighbor][0] - points[current_node][0])**2 + (points[neighbor][1] - points[current_node][1])**2)
            if distances[neighbor] > distances[current_node] + distance:
                distances[neighbor] = distances[current_node] + distance
                previous[neighbor] = current_node
        
        unvisited.remove(current_node)
        
        if not unvisited:
            break
        
        candidates = {node: distances[node] for node in unvisited}
        current_node = min(candidates, key=candidates.get)
    
    if current_node != end:
        return None # no se encontró una ruta hasta el punto final
    
    route = []
    while current_node is not None:
        route.append(current_node)
        current_node = previous[current_node]
    
    route.reverse()
    
    return route

# Ejemplo de uso
def magia(lat, lon, w, h, final):
    lat_max, lon_min = 19.66938888061274, -103.48554695545846
    lat_min, lon_max = 19.668493770892493, -103.48482643008987
    # Dimensiones del rectángulo en pixeles
    width = w
    height = h

    x2, y2 = lat_lon_to_pixels(lat, lon, lat_min, lat_max, lon_min, lon_max, width, height)
    points_values = lat_lon_to_pixels_points(POINTS_VALUES_REAL, lat, lon, lat_min, lat_max, lon_min, lon_max, width, height)

    print(x2, y2)

    points = [v for k, v in points_values.items()]
    point_value = closest_point(x2, y2, points)
    print(point_value) # Output: (0, 0)

    start = get_key(points_values, point_value)
    end = int(final)
    shortest_path = shortest_route(GRAPH, points_values, start, end)
    print(f'La ruta más corta desde {start} hasta {end} es: {shortest_path}')

    return_points = [(round(points_values[p][0]), round(points_values[p][1])) for p in shortest_path]
    print(return_points)

    return return_points



# Create your views here.
class GeoView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id=0):
        if id > 0:
            companies = list(Geo.objects.filter(id=id).values())
            if len(companies) > 0:
                company = companies[0]
                datos = {'message':"Success", 'companies':company}
            else:
                datos = {'message':"Company not found..."}
        else:
            companies = list(Geo.objects.values())
            if len(companies) > 0:
                datos = {'message':"Success", 'companies':companies}
            else:
                datos = {'message':"Companies not found..."}

        return JsonResponse(datos)
    
    def post(self, request):
        jd = json.loads(request.body)
        Geo.objects.create(
            lat=float(jd['lat']), 
            lon=float(jd['lon']), 
            w=float(jd['w']),
            h=float(jd['h'])
        )

        points = magia(float(jd['lat']),float(jd['lon']),float(jd['w']),float(jd['h']),jd['final'])

        datos = {'message':"Sucess", 'ruta': points}

        return JsonResponse(datos)

    def put(self, request, id):
       pass

    def delete(self, request, id):
        pass
