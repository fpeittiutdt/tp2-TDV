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
    posiciones_equiprobables = [x for x in range(len(servicios)*2)]
    pos_prev = (0, 0)
    distance_minimum_nodes = 0

    for service in servicios:
        
        tiempo_nodo_D = servicios[service][STOPS][0][TIME]
        tiempo_nodo_A = servicios[service][STOPS][1][TIME]
        nombre_nodo_station_D = servicios[service][STOPS][0][STATION]
        nombre_nodo_station_A = servicios[service][STOPS][1][STATION]
        nombre_nodo_D = (tiempo_nodo_D, nombre_nodo_station_D)
        nombre_nodo_A = (tiempo_nodo_A, nombre_nodo_station_A)
        capacity_edge = servicios[service][DEMAND][0]/datos[RS_INFO][CAPACITY]
        upper_bound_modified = datos[RS_INFO][MAX_RS] - math.ceil(capacity_edge)

        if nombre_nodo_D in grafo.nodes():
            demanda_original_D = grafo.nodes(data=True)[nombre_nodo_D][DEMAND]
            grafo.nodes(data=True)[nombre_nodo_D][DEMAND] = demanda_original_D + math.ceil(capacity_edge)
            grafo.nodes(data=True)[nombre_nodo_D]["color"] = "purple"
        else:
            grafo.add_node(nombre_nodo_D, color = "blue", stations = nombre_nodo_station_D, demand = math.ceil(capacity_edge))

        if nombre_nodo_A in grafo.nodes():
            demanda_original_A = grafo.nodes(data=True)[nombre_nodo_A][DEMAND]
            grafo.nodes(data=True)[nombre_nodo_A][DEMAND] = demanda_original_A-math.ceil(capacity_edge)
            grafo.nodes(data=True)[nombre_nodo_A]["color"] = "purple"
        else:
            grafo.add_node(nombre_nodo_A, color = "red", stations = nombre_nodo_station_A, demand = -math.ceil(capacity_edge))
        
        grafo.add_edge(nombre_nodo_D, nombre_nodo_A, upper_bound = upper_bound_modified, amount_modified = math.ceil(capacity_edge))
        
        if nombre_nodo_station_D == name_station_zero:
            if nombre_nodo_D[0] * 10 < pos_prev[0] and nombre_nodo_D[0] * 10 - pos_prev[0] < distance_minimum_nodes:
                pos[nombre_nodo_D] = (0, nombre_nodo_D[0] * 10 - distance_minimum_nodes)
            elif nombre_nodo_D[0] * 10 > pos_prev[0] and nombre_nodo_D[0] * 10 - pos_prev[0] < distance_minimum_nodes:
                pos[nombre_nodo_D] = (0, nombre_nodo_D[0] * 10 + distance_minimum_nodes)
            else:
                pos[nombre_nodo_D] = (0, nombre_nodo_D[0] * 10)
            
            if nombre_nodo_A[0] * 10 < pos_prev[1] and nombre_nodo_A[0] * 10 - pos_prev[1] < distance_minimum_nodes:
                pos[nombre_nodo_A] = (0.5, nombre_nodo_A[0] * 10 - distance_minimum_nodes)
            elif nombre_nodo_A[0] * 10 > pos_prev[1] and nombre_nodo_A[0] * 10 - pos_prev[1] < distance_minimum_nodes:
                pos[nombre_nodo_A] = (0.5, nombre_nodo_A[0] * 10 + distance_minimum_nodes)
            else:
                pos[nombre_nodo_A] = (0.5, nombre_nodo_A[0] * 10)
            
            pos_prev = (pos[nombre_nodo_D][1], pos[nombre_nodo_A][1])
            servicies_zero.append(nombre_nodo_D)
            servicies_one.append(nombre_nodo_A)
        else:
            if nombre_nodo_D[0] * 10 < pos_prev[1] and nombre_nodo_D[0] * 10 - pos_prev[1] < distance_minimum_nodes:
                pos[nombre_nodo_D] = (0.5, nombre_nodo_D[0] * 10 - distance_minimum_nodes)
            elif nombre_nodo_D[0] * 10 > pos_prev[1] and nombre_nodo_D[0] * 10 - pos_prev[1] < distance_minimum_nodes:
                pos[nombre_nodo_D] = (0.5, nombre_nodo_D[0] * 10 + distance_minimum_nodes)
            else:
                pos[nombre_nodo_D] = (0.5, nombre_nodo_D[0] * 10)
            
            if nombre_nodo_A[0] * 10 < pos_prev[0] and nombre_nodo_A[0] * 10 - pos_prev[0] < distance_minimum_nodes:
                pos[nombre_nodo_A] = (0, nombre_nodo_A[0] * 10 - distance_minimum_nodes)
            elif nombre_nodo_A[0] * 10 > pos_prev[0] and nombre_nodo_A[0] * 10 - pos_prev[0] < distance_minimum_nodes:
                pos[nombre_nodo_A] = (0, nombre_nodo_A[0] * 10 + distance_minimum_nodes)
            else:
                pos[nombre_nodo_A] = (0, nombre_nodo_A[0] * 10)

            pos_prev = (pos[nombre_nodo_A][1], pos[nombre_nodo_D][1])
            servicies_one.append(nombre_nodo_D)
            servicies_zero.append(nombre_nodo_A)
    
    servicies_zero.sort(key = lambda x : x[0])
    servicies_one.sort(key = lambda x : x[0])

    nodos = list(grafo.nodes())
    nodos.sort()
    for nodo_pos in range(len(nodos)):
        if nodos[nodo_pos][1] == name_station_zero:
            pos[nodos[nodo_pos]] = (0, posiciones_equiprobables[nodo_pos])
        else:
            pos[nodos[nodo_pos]] = (0.5, posiciones_equiprobables[nodo_pos])

    demandas = []
    night_edges = []

    for nodo in grafo.nodes(data=True):
        demandas.append((nodo[0], nodo[1][DEMAND]))
    
    for servicio_pos in range(0, len(servicies_zero)-1):

        if servicies_zero[servicio_pos] != servicies_zero[servicio_pos+1]:
            grafo.add_edge(
                servicies_zero[servicio_pos], 
                servicies_zero[servicio_pos+1],
                amount_modified = 0
                )
            night_edges.append((servicies_zero[servicio_pos], servicies_zero[servicio_pos+1]))
    
    for servicio_pos in range(0, len(servicies_one)-1):
        if servicies_one[servicio_pos] != servicies_one[servicio_pos+1]:
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
    
    grafo[maximo][minimo]["upper_bound"] = limitacion

    return grafo

def agregar_limitacion2(datos, grafo: nx.DiGraph, cabecera, limitacion):
    name_station_zero = datos["stations"][0]
    name_station_one = datos["stations"][1]

    grafo_modificado: nx.DiGraph = agregar_limitacion(grafo, cabecera, limitacion)
    maximo = [(None, None), (None, None)]
    minimo = [(None, None), (None, None)]
    for nodo in grafo.nodes(data=True):
        if nodo[1]["stations"] == name_station_zero:
            if maximo[0][0] is None and minimo[0][0] is None:
                maximo[0] = nodo[0]
                minimo[0] = nodo[0]
            elif maximo[0][0] < nodo[0][0]:
                maximo[0] = nodo[0]
            elif minimo[0][0] > nodo[0][0]:
                minimo[0] = nodo[0]
        else:
            print("retiro for", maximo[1], minimo[1], nodo[0])
            if maximo[1][0] is None and minimo[1][0] is None:
                maximo[1] = nodo[0]
                minimo[1] = nodo[0]
            elif maximo[1][0] < nodo[0][0]:
                maximo[1] = nodo[0]
            elif minimo[1][0] > nodo[0][0]:
                minimo[1] = nodo[0]
    
    name_nodo_max_zero_new = (maximo[0][0]+1, name_station_zero)
    name_nodo_min_zero_new = (minimo[0][0]-1, name_station_zero)
    name_nodo_max_one_new = (maximo[1][0]+1, name_station_one)
    name_nodo_min_one_new = (minimo[1][0]-1, name_station_one)

    grafo_modificado.add_node(name_nodo_min_zero_new, color = "red", stations = name_station_zero)
    grafo_modificado.add_node(name_nodo_min_one_new, color = "blue", stations = name_station_one)
    
    grafo_modificado.add_node(name_nodo_max_zero_new, color = "red", stations = name_station_zero)
    grafo_modificado.add_node(name_nodo_max_one_new, color = "blue", stations = name_station_one)

    grafo_modificado.add_edge(name_nodo_min_zero_new, name_nodo_min_one_new, amount_modified = 0)
    grafo_modificado.add_edge(name_nodo_min_one_new, name_nodo_min_zero_new, amount_modified = 0)
    
    grafo_modificado.add_edge(name_nodo_max_zero_new, name_nodo_max_one_new, amount_modified = 0)
    grafo_modificado.add_edge(name_nodo_max_one_new, name_nodo_max_zero_new, amount_modified = 0)

    if cabecera == name_station_zero:
        grafo_modificado.add_edge(name_nodo_max_zero_new, name_nodo_min_zero_new, weight = datos[COST][name_station_zero], amount_modified = 0, upper_bound = grafo_modificado[maximo[0]][minimo[0]]["upper_bound"])
        grafo_modificado.add_edge(name_nodo_max_one_new, name_nodo_min_one_new, weight = datos[COST][name_station_one], amount_modified = 0)
    else:
        grafo_modificado.add_edge(name_nodo_max_zero_new, name_nodo_min_zero_new, weight = datos[COST][name_station_zero], amount_modified = 0)
        grafo_modificado.add_edge(name_nodo_max_one_new, name_nodo_min_one_new, weight = datos[COST][name_station_one], amount_modified = 0, upper_bound = grafo_modificado[maximo[1]][minimo[1]]["upper_bound"])

    
    grafo_modificado.remove_edges_from([(maximo[0], minimo[0]), (maximo[1], minimo[1])])

    grafo_modificado.add_edge(name_nodo_min_zero_new, minimo[0], amount_modified = 0)
    grafo_modificado.add_edge(name_nodo_min_one_new, minimo[1], amount_modified = 0)
    grafo_modificado.add_edge(maximo[0], name_nodo_max_zero_new, amount_modified = 0)
    grafo_modificado.add_edge(maximo[1], name_nodo_max_one_new, amount_modified = 0)

    pos = {}
    servicios: json = datos[SERVICES]

    posiciones_equiprobables = [x for x in range(len(servicios)*2+4)]

    nodos = list(grafo_modificado.nodes())
    nodos.sort(key=lambda x: x[0])
    nodos_station_zero = []
    nodos_station_one = []
    night_edges = []

    for nodo_pos in range(len(nodos)):
        if nodos[nodo_pos][1] == name_station_zero:
            nodos_station_zero.append(nodos[nodo_pos])
            pos[nodos[nodo_pos]] = (0, posiciones_equiprobables[nodo_pos])
        else:
            nodos_station_one.append(nodos[nodo_pos])
            pos[nodos[nodo_pos]] = (0.5, posiciones_equiprobables[nodo_pos])

    for nodo_pos in range(len(nodos_station_zero)-1):
        if nodos_station_zero[nodo_pos] != nodos_station_zero[nodo_pos+1]:
            night_edges.append((nodos_station_zero[nodo_pos], nodos_station_zero[nodo_pos+1]))
    
    for nodo_pos in range(len(nodos_station_one)-1):
        if nodos_station_one[nodo_pos] != nodos_station_one[nodo_pos+1]:
            night_edges.append((nodos_station_one[nodo_pos], nodos_station_one[nodo_pos+1]))

    night_edges.append((nodos_station_zero[len(nodos_station_zero)-1], nodos_station_zero[0]))
    night_edges.append((nodos_station_one[len(nodos_station_one)-1], nodos_station_one[0]))
    
    night_edges.append((nodos_station_zero[0], nodos_station_one[0]))
    night_edges.append((nodos_station_one[0], nodos_station_zero[0]))
    
    night_edges.append((nodos_station_zero[len(nodos_station_zero)-1], nodos_station_one[len(nodos_station_one)-1]))
    night_edges.append((nodos_station_one[len(nodos_station_one)-1], nodos_station_zero[len(nodos_station_zero)-1]))
    
    return grafo_modificado, pos, night_edges