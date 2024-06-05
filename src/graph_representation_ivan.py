import json, math
import networkx as nx

# Constantes

SERVICES: str = "services"
RS_INFO: str = "rs_info"
MAX_RS: str = "max_rs"
STOPS: str = "stops"
COST: str = "cost_per_unit"
STATIONS: str = "station"

def create_graph(datos):

    grafo = nx.DiGraph()

    servicios: json = datos[SERVICES]

    servicios_retiro = []
    servicios_tigre = []

    for servicio in datos[SERVICES]:
        nombre_nodo_D = servicios[servicio][STOPS][0]["time"]
        nombre_nodo_A = servicios[servicio][STOPS][1]["time"]
        upper_bound_modified = datos[RS_INFO][MAX_RS] - math.ceil(servicios[servicio]["demand"][0]/datos[RS_INFO]["capacity"])
        if nombre_nodo_D in grafo.nodes():
            demanda_original_D = grafo.nodes(data=True)[nombre_nodo_D]["demand"]
            grafo.add_nodes_from([(
                servicios[servicio][STOPS][0]["time"], {
                    "color": "blue", "stations": servicios[servicio][STOPS][0][STATIONS], "demand": demanda_original_D + math.ceil(servicios[servicio]["demand"][0]/datos[RS_INFO]["capacity"])
                    }),
                    ])
        else:
            grafo.add_nodes_from([
                (
                    servicios[servicio][STOPS][0]["time"], {
                "color": "blue", "stations": servicios[servicio][STOPS][0][STATIONS], "demand": math.ceil(servicios[servicio]["demand"][0]/datos[RS_INFO]["capacity"])
                })
            ])
        if nombre_nodo_A in grafo.nodes():
            demanda_original_A = grafo.nodes(data=True)[nombre_nodo_A]["demand"]
            grafo.add_nodes_from([
                (servicios[servicio][STOPS][1]["time"], {
                    "color": "red", "stations": servicios[servicio][STOPS][1][STATIONS], "demand": demanda_original_A-math.ceil(servicios[servicio]["demand"][0]/datos[RS_INFO]["capacity"])
                })
            ])
        else:
            grafo.add_nodes_from([
                (servicios[servicio][STOPS][1]["time"], {
                    "color": "red", "stations": servicios[servicio][STOPS][1][STATIONS], "demand": -math.ceil(servicios[servicio]["demand"][0]/datos[RS_INFO]["capacity"])
                    })])
        
        grafo.add_edge(servicios[servicio][STOPS][0]["time"], servicios[servicio][STOPS][1]["time"],
                       upper_bound = upper_bound_modified,
                       amount_modified = math.ceil(servicios[servicio]["demand"][0]/datos[RS_INFO]["capacity"])
                       )
        

        if servicios[servicio][STOPS][0][STATIONS] == "Retiro":
            servicios_retiro.append(servicios[servicio][STOPS][0]["time"])
            servicios_tigre.append(servicios[servicio][STOPS][1]["time"])
        else:
            servicios_tigre.append(servicios[servicio][STOPS][0]["time"])
            servicios_retiro.append(servicios[servicio][STOPS][1]["time"])

    servicios_retiro.sort()
    servicios_tigre.sort()

    demandas = []
    diferencia = 0
    
    for nodo in grafo.nodes(data=True):
        """if nodo[0] == servicios_retiro[0] or nodo[0] == servicios_retiro[len(servicios_retiro)-1]:
            nodo[1]["demand"] = 0
        elif nodo[0] == servicios_tigre[0]:
            nodo[1]["demand"] = 0
        elif nodo[0] == servicios_tigre[len(servicios_tigre)-1]:
            nodo[1]["demand"] = 0"""

        demandas.append((nodo[0], nodo[1]["demand"]))
        diferencia += nodo[1]["demand"]
    
    print("demandas", demandas, "diferencia: ", diferencia)

    #grafo.add_nodes_from([(0, {"color": "purple", "stations": "Tigre", "demand": -5})])

    for servicio_pos in range(0, len(servicios_retiro)-1):
        print(servicios_retiro[servicio_pos], 
            servicios_retiro[servicio_pos+1])
        grafo.add_edge(
            servicios_retiro[servicio_pos], 
            servicios_retiro[servicio_pos+1],
            amount_modified = 0
            )
    
    for servicio_pos in range(0, len(servicios_tigre)-1):
        grafo.add_edge(
            servicios_tigre[servicio_pos],
            servicios_tigre[servicio_pos+1],
            amount_modified = 0
            )

    grafo.add_edge(
        servicios_retiro[len(servicios_retiro)-1], 
        servicios_retiro[0], weight = datos[COST]["Retiro"],
        amount_modified = 0
        )
    
    grafo.add_edge(
        servicios_tigre[len(servicios_tigre)-1], 
        servicios_tigre[0], weight = datos[COST]["Tigre"],
        amount_modified = 0
        )
    
    return grafo

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