import json, math
import networkx as nx
import matplotlib.pyplot as plt


SERVICES: str = "services"
RS_INFO: str = "rs_info"
MAX_RS: str = "max_rs"
STOPS: str = "stops"
COST: str = "cost_per_unit"
STATION: str = "station"
CAPACITY: str = "capacity"
DEMAND: str = "demand"
TIME: str = "time"

def create_graph(datos):
    
    grafo = nx.DiGraph()

    servicios: json = datos[SERVICES]
    
    name_station_zero = datos["stations"][0]
    name_station_one = datos["stations"][1]

    servicies_zero = []
    servicies_one = []

    pos = {}

    for service in servicios:

        nombre_nodo_D = servicios[service][STOPS][0][TIME]
        nombre_nodo_A = servicios[service][STOPS][1][TIME]
        nombre_nodo_station_D = servicios[service][STOPS][0][STATION]
        nombre_nodo_station_A = servicios[service][STOPS][1][STATION]
        capacity_edge = servicios[service][DEMAND][0]/datos[RS_INFO][CAPACITY]
        upper_bound_modified = datos[RS_INFO][MAX_RS] - math.ceil(capacity_edge)
        
        if nombre_nodo_D in grafo.nodes():
            demanda_original_D = grafo.nodes(data=True)[nombre_nodo_D][DEMAND]
            grafo.add_node(nombre_nodo_D, color = "blue", stations = nombre_nodo_station_D, demand = demanda_original_D + math.ceil(capacity_edge))
        else:
            grafo.add_node(nombre_nodo_D, color = "blue", stations = nombre_nodo_station_D, demand = math.ceil(capacity_edge))

        if nombre_nodo_A in grafo.nodes():
            demanda_original_A = grafo.nodes(data=True)[nombre_nodo_A][DEMAND]
            grafo.add_node(nombre_nodo_A, color = "red", stations = nombre_nodo_station_A, demand = demanda_original_A-math.ceil(capacity_edge))
        else:
            grafo.add_node(nombre_nodo_A, color = "red", stations = nombre_nodo_station_A, demand = -math.ceil(capacity_edge))
        
        grafo.add_edge(nombre_nodo_D, nombre_nodo_A, upper_bound = upper_bound_modified, amount_modified = math.ceil(capacity_edge))
        
        if nombre_nodo_station_D == name_station_zero:
            pos[nombre_nodo_D] = (0, nombre_nodo_D * 10)
            pos[nombre_nodo_A] = (0.5, nombre_nodo_A * 10)
            servicies_zero.append(nombre_nodo_D)
            servicies_one.append(nombre_nodo_A)
        else:
            pos[nombre_nodo_D] = (0.5, nombre_nodo_A * 10)
            pos[nombre_nodo_A] = (0, nombre_nodo_D * 10)
            servicies_one.append(nombre_nodo_D)
            servicies_zero.append(nombre_nodo_A)
    
    servicies_zero.sort()
    servicies_one.sort()

    demandas = []
    night_edges = []

    for nodo in grafo.nodes(data=True):
        demandas.append((nodo[0], nodo[1][DEMAND]))
    
    for servicio_pos in range(0, len(servicies_zero)-1):
        print(servicies_zero[servicio_pos], 
            servicies_zero[servicio_pos+1])
        grafo.add_edge(
            servicies_zero[servicio_pos], 
            servicies_zero[servicio_pos+1],
            amount_modified = 0
            )
        night_edges.append((servicies_zero[servicio_pos], servicies_zero[servicio_pos+1]))
    
    for servicio_pos in range(0, len(servicies_one)-1):
        grafo.add_edge(
            servicies_one[servicio_pos],
            servicies_one[servicio_pos+1],
            amount_modified = 0
            )
        night_edges.append((servicies_one[servicio_pos], servicies_one[servicio_pos+1]))

    grafo.add_edge(
        servicies_zero[len(servicies_zero)-1], 
        servicies_zero[0], weight = datos[COST][name_station_zero],
        amount_modified = 0
        )
    night_edges.append((servicies_zero[len(servicies_zero)-1], servicies_zero[0]))

    
    grafo.add_edge(
        servicies_one[len(servicies_one)-1], 
        servicies_one[0], weight = datos[COST][name_station_one],
        amount_modified = 0
        )
    night_edges.append((servicies_one[len(servicies_one)-1], servicies_one[0]))

    print(night_edges)
    return grafo, pos, night_edges


def agregar_limitacion(grafo: nx.DiGraph, cabecera, limitacion):
    maximo = None
    minimo = None
    for nodo in grafo.nodes(data=True):
        if nodo[1]["stations"] == cabecera:
            if maximo is None or maximo < nodo[0]:
                maximo = nodo[0]
            elif minimo is None or minimo > nodo[0]:
                minimo = nodo[0]
    
    print(minimo, maximo)
    grafo[maximo][minimo]["upper_bound"] = limitacion

    return grafo