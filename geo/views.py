from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import Geo
import json
from collections import deque
import math

POINTS_VALUES_REAL = {
    1: [(19.669142152782285, -103.4850291181504),(5700, 1727)],
    2: [(19.668903636258346, -103.48515576597272),(5495, 1776)],
    3: [(19.6690074959822, -103.48537941735819),(5453, 1581)],
    4: [(19.66876570742316, -103.48562640584151),(5189, 1590)],
    5: [(19.668758799171282, -103.48606046978146),(4955, 1331)],
    6: [(19.668382299091487, -103.48625610423406),(4598, 1408)],
    7: [(19.668399569756236, -103.48644317966944),(4523, 1288)],
    8: [(19.66830400538788, -103.48649331099527),(4452, 1303)],
    9: [(19.668118633378356, -103.48640283006574),(4913, 1458)],
    10: [(19.667998889854527, -103.48641994807943),(4286, 1498)],
    11: [(19.668267245208593, -103.48696499584712),(4189, 1034)],
    12: [(19.667845253880387, -103.48623626668095),(4284, 1693)],
    13: [(19.667317713742666, -103.48660760975531),(3739, 1737)],
    14: [(19.667364439041013, -103.4868681147658),(3650, 1576)],
    15: [(19.66702464198608, -103.4869724079272),(3397, 1700)],
    16: [(19.66744252694668, -103.4878779144182),(3186, 915)],
    17: [(19.666615729223732, -103.48809676354544),(2554, 1246)],
    18: [(19.666913130089515, -103.48927356897892),(2146, 398)],
    19: [(19.666510836668817, -103.48738648679283),(2854, 1723)],
    20: [(19.666425688546664, -103.48737076110827),(2790, 1780)],
}

GRAPH = {
    1: [2],
    2: [1, 3],
    3: [2, 4],
    4: [3, 5],
    5: [4, 6],
    6: [5, 7, 9],
    7: [6, 8],
    8: [7, 9, 11],
    9: [6, 8, 10, 12],
    10: [9, 11, 12, 14],
    11: [8, 10, 16],
    12: [9, 10, 14],
    13: [14],
    14: [10, 13, 15, 16, 19],
    15: [14, 16, 19],
    16: [11, 15, 17],
    17: [11, 16, 18, 19, 20],
    18: [17, 19, 20],
    19: [14, 15, 20],
    20: [17, 18, 19],
}

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def closest_point(x1, y1, points):
    closest_point = None
    closest_distance = float('inf')
    for key, point in points.items():
        dist = distance(x1, y1, point[0][0], point[0][1])
        if dist < closest_distance:
            closest_point = key
            closest_distance = dist
    return closest_point


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
            distance = math.sqrt((points[neighbor][0][0] - points[current_node][0][0])**2 + (points[neighbor][0][1] - points[current_node][0][1])**2)
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
def magia(lat, lon, final):
    start = closest_point(lat, lon, POINTS_VALUES_REAL)
    print("Mas cercano:", start)
    end = int(final)
    shortest_path = shortest_route(GRAPH, POINTS_VALUES_REAL, start, end)
    print(f'La ruta más corta desde {start} hasta {end} es: {shortest_path}')

    return_points = [(round(POINTS_VALUES_REAL[p][1][0]), round(POINTS_VALUES_REAL[p][1][1])) for p in shortest_path]
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
            lon=float(jd['lon'])
        )

        points = magia(float(jd['lat']),float(jd['lon']),jd['final'])

        datos = {'message':"Sucess", 'ruta': points}

        return JsonResponse(datos)

    def put(self, request, id):
       pass

    def delete(self, request, id):
        pass
