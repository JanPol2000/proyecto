from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import Geo
import json
from collections import deque
import math

def convertir_coordenadas(width1, height1, width2, height2, x1, y1):
    x2 = x1 * width2 / width1
    y2 = y1 * height2 / height1
    return x2, y2

def convertir_puntos(puntos, width1, height1, width2, height2):
    nuevo = {}
    for k, v in puntos.items():
        nuevo[k] = convertir_coordenadas(width1, height1, width2, height2,v[0],v[1])
    return nuevo

POINTS_VALUES_REAL = {
    'A': (1, 1), 
    'B': (5, 1), 
    'C': (3, 2), 
    'D': (1, 4),
    'E': (3, 3),
    'F': (5, 3),
    'G': (5, 4),
    'H': (7, 4),
    'I': (7, 3),
    'J': (9, 3),
    'K': (7, 1),
    'L': (9, 1),
}

GRAPH = {
    'A': ['B', 'D'],
    'B': ['A', 'C', 'K'],
    'C': ['B', 'D', 'E'],
    'D': ['A', 'C', 'G'],
    'E': ['C', 'F'],
    'F': ['E', 'G', 'I'],
    'G': ['D', 'F'],
    'H': ['G', 'I'],
    'I': ['F', 'H', 'J', 'K'],
    'J': ['I'],
    'K': ['B', 'I', 'L'],
    'L': ['K'],
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
    WIDTH_REAL = 10
    HEIGHT_REAL = 5
    LATITUDE = lat
    LONGITUDE = lon

    new_width = w
    new_height = h

    x2, y2 = convertir_coordenadas(WIDTH_REAL,HEIGHT_REAL,new_width,new_height,LATITUDE,LONGITUDE)
    points_values = convertir_puntos(POINTS_VALUES_REAL, WIDTH_REAL,HEIGHT_REAL,new_width,new_height)

    print(x2, y2)

    points = [v for k, v in points_values.items()]
    point_value = closest_point(x2, y2, points)
    print(point_value) # Output: (0, 0)

    start = get_key(points_values, point_value)
    end = final
    shortest_path = shortest_route(GRAPH, points_values, start, end)
    print(f'La ruta más corta desde {start} hasta {end} es: {shortest_path}')

    return_points = [points_values[p] for p in shortest_path]
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
