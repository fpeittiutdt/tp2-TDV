import json, math
import networkx as nx
import matplotlib.pyplot as plt
from .constants import *


def print_usage():
    usage_message = """
    Usage:
        main.py -i 'instancia'
    
    Options:
        -i    Especifique el nombre de la instancia. Los nombres de instancia válidos son: {}
        -l1   Opcional. Si se desea agregar una limitación al limite de vagones en una cabecera durante la noche, utilizando el primer método. Especifique
        la cabecera en formato numerico (0 ó 1) y el limite a establecer.
        -l2   Opcional. Si se desea agregar una limitación al limite de vagones en una cabecera durante la noche, utilizando el segundo método. Especifique
        la cabecera en formato numerico (0 ó 1) y el limite a establecer.
        Solamente puede usarse una limitación a la vez.
    """.format(
        ", ".join(INSTANCES)
    )

    print(usage_message)


def load_instance(instance: str):
    """
    Lectura de una instancia dada en formato json.

    Parámetros:
    instance (str): El nombre de la instancia a cargar. Este nombre debe estar presente en el diccionario INSTANCES.

    Devuelve:
    El contenido estructurado de una instancia.
    """

    with open("../instances/{}.json".format(INSTANCES[instance])) as json_file:
        return json.load(json_file)


def add_services(instance):
    """
    Agrega nodos y aristas al grafo según la información proporcionada en la instancia.

    Parámetros:
    instance (dict): Un diccionario que contiene la información de la instancia.

    Devuelve:
    Una tupla que contiene:
        - El grafo actualizado con nodos y aristas.
        - colors: Una lista de colores para los nodos.
        - labels: Un diccionario que asigna etiquetas a los nodos.
        - pos: Un diccionario que asigna posiciones a los nodos.
        - border_colors: Una lista de colores de borde para los nodos.
        - edge_color: Un diccionario que asigna colores a las aristas.
        - service_by_station: Un diccionario que asigna los nodos correspondientes a cada estación
    """
    G = nx.DiGraph()

    services = instance[SERVICES]

    station_names = [instance["stations"][0], instance["stations"][1]]

    services_by_station = {station_names[0]: [], station_names[1]: []}

    pos = {}
    uniform_positions = [x for x in range(len(services) * 2)]

    colors = []
    border_colors = []
    edge_colors = {}
    labels = {}

    # Creamos los nodos y las aristas correspondientes a los servicios existentes.

    for service in services:

        depart_time = services[service][STOPS][0][TIME]
        arrival_time = services[service][STOPS][1][TIME]
        depart_station = services[service][STOPS][0][STATION]
        arrival_station = services[service][STOPS][1][STATION]
        departure = (depart_time, depart_station)
        arrival = (arrival_time, arrival_station)
        minimum_units = math.ceil(
            services[service][DEMAND][0] / instance[RS_INFO][CAPACITY]
        )

        # El imbalance asignado a los nodos y a la capacidad de las aristas ya son los obtenidos del cambio de variable necesario
        # de modo tal que el algoritmo min_cost_flow sea ejecutable.

        upper_bound_modified = instance[RS_INFO][MAX_RS] - minimum_units

        if departure in G.nodes():
            demand = G.nodes(data=True)[departure][DEMAND]
            G.nodes(data=True)[departure][DEMAND] = demand + minimum_units
        else:
            G.add_node(
                departure,
                color="blue",
                stations=depart_station,
                demand=minimum_units,
            )
            labels[departure] = departure[0]
            colors.append("#CCCCFF")
            border_colors.append("blue")

        if arrival in G.nodes():
            demand = G.nodes(data=True)[arrival][DEMAND]
            G.nodes(data=True)[arrival][DEMAND] = demand - minimum_units
        else:
            G.add_node(
                arrival,
                color="red",
                stations=arrival_station,
                demand=-minimum_units,
            )
            colors.append("#FFCCCC")
            border_colors.append("red")
            labels[arrival] = arrival[0]

        G.add_edge(
            departure,
            arrival,
            upper_bound=upper_bound_modified,
            amount_modified=minimum_units,
        )
        edge_colors[departure, arrival] = "green"

        if depart_station == station_names[0]:
            services_by_station[station_names[0]].append(departure)
            services_by_station[station_names[1]].append(arrival)
        else:
            services_by_station[station_names[1]].append(departure)
            services_by_station[station_names[0]].append(arrival)

    services_by_station[station_names[0]].sort(key=lambda x: x[0])
    services_by_station[station_names[1]].sort(key=lambda x: x[0])

    # Asignamos las posiciones correspondientes a los nodos para graficar.
    nodes = list(G.nodes())
    nodes.sort()
    for node_pos in range(len(nodes)):
        if nodes[node_pos][1] == station_names[0]:
            pos[nodes[node_pos]] = (0, uniform_positions[node_pos])
        else:
            pos[nodes[node_pos]] = (0.5, uniform_positions[node_pos])

    return G, colors, pos, labels, border_colors, edge_colors, services_by_station


def add_night_pass_edges(G, instance, edge_colors, services_by_station):
    """
    Agrega aristas para representar conexiones de traspaso y de trasnoche entre estaciones en el grafo.

    Parámetros:
    G: El grafo al que se agregarán las aristas.
    instance: Un diccionario que contiene la información de la instancia.
    edge_colors: Un diccionario que asigna colores a las aristas.
    services_by_station: Un diccionario que asigna los nodos correspondientes a cada estación.

    Devuelve:
    Una tupla que contiene:
        - G: El grafo actualizado con las aristas nocturnas.
        - night_edges: Una lista de aristas nocturnas agregadas al grafo.
    """

    night_edges = []

    station_names = [instance["stations"][0], instance["stations"][1]]

    # Agregamos las aristas de traspaso entre servicios continuos de la misma estación.

    for service_pos in range(0, len(services_by_station[station_names[0]]) - 1):

        if (
            services_by_station[station_names[0]][service_pos]
            != services_by_station[station_names[0]][service_pos + 1]
        ):
            G.add_edge(
                services_by_station[station_names[0]][service_pos],
                services_by_station[station_names[0]][service_pos + 1],
                amount_modified=0,
            )
            edge_colors[
                (
                    services_by_station[station_names[0]][service_pos],
                    services_by_station[station_names[0]][service_pos + 1],
                )
            ] = "blue"

    for service_pos in range(0, len(services_by_station[station_names[1]]) - 1):
        if (
            services_by_station[station_names[1]][service_pos]
            != services_by_station[station_names[1]][service_pos + 1]
        ):
            G.add_edge(
                services_by_station[station_names[1]][service_pos],
                services_by_station[station_names[1]][service_pos + 1],
                amount_modified=0,
            )
            edge_colors[
                (
                    services_by_station[station_names[1]][service_pos],
                    services_by_station[station_names[1]][service_pos + 1],
                )
            ] = "blue"

    # Agregamos las aristas de trasnoche de las estaciones de cabecera.

    G.add_edge(
        services_by_station[station_names[0]][
            len(services_by_station[station_names[0]]) - 1
        ],
        services_by_station[station_names[0]][0],
        weight=instance[COST][station_names[0]],
        amount_modified=0,
    )
    night_edges.append(
        (
            services_by_station[station_names[0]][
                len(services_by_station[station_names[0]]) - 1
            ],
            services_by_station[station_names[0]][0],
        )
    )
    edge_colors[
        (
            services_by_station[station_names[0]][
                len(services_by_station[station_names[0]]) - 1
            ],
            services_by_station[station_names[0]][0],
        )
    ] = "purple"

    G.add_edge(
        services_by_station[station_names[1]][
            len(services_by_station[station_names[1]]) - 1
        ],
        services_by_station[station_names[1]][0],
        weight=instance[COST][station_names[1]],
        amount_modified=0,
    )
    night_edges.append(
        (
            services_by_station[station_names[1]][
                len(services_by_station[station_names[1]]) - 1
            ],
            services_by_station[station_names[1]][0],
        )
    )
    edge_colors[
        (
            services_by_station[station_names[1]][
                len(services_by_station[station_names[1]]) - 1
            ],
            services_by_station[station_names[1]][0],
        )
    ] = "purple"

    return G, night_edges


def visualize_graph(
    G, colors, pos, labels, border_colors, edge_colors, night_edges, minCostFlow
):
    """
    Grafica el grafo con los colores, posiciones y etiquetas proporcionados.

    Parámetros:
        G: El grafo a visualizar.
        colors: Una lista de colores para los nodos.
        pos: Un diccionario que asigna posiciones a los nodos.
        labels: Un diccionario que asigna etiquetas a los nodos.
        border_colors: Una lista de colores de borde para los nodos.
        edge_colors: Un diccionario que asigna colores a las aristas.
        night_edges: Una lista de aristas de trasnoche.
        minCostFlow: Un diccionario que contiene el flujo de costo mínimo en el grafo.
    """

    nx.draw_networkx_nodes(
        G,
        node_color=colors,
        pos=pos,
        node_size=400,
        node_shape="s",
        linewidths=G.number_of_nodes() * [1],
        edgecolors=border_colors,
    )
    nx.draw_networkx_labels(G, pos=pos, labels=labels, font_size=8, font_family="serif")

    for edge in G.edges():
        if edge in night_edges:
            rad = -0.5 if pos[edge[0]][0] != 0 else 0.5

            nx.draw_networkx_edges(
                G,
                pos=pos,
                edgelist=[edge],
                edge_color=edge_colors[edge],
                connectionstyle="arc3, rad={}".format(rad),
            )
            nx.draw_networkx_edge_labels(
                G,
                pos=pos,
                edge_labels={edge: minCostFlow[edge[0]][edge[1]]},
                font_size=20,
                rotate=False,
                connectionstyle="arc3, rad={}".format(rad),
            )
        else:
            nx.draw_networkx_edges(
                G, pos=pos, edgelist=[edge], edge_color=edge_colors[edge]
            )

    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.show()


def add_limitation(
    instance, G, target_station, upper_bound, colors, edge_colors, border_colors
):
    """
    Asigna una capacidad a la arista de trasnoche de la cabecera recibida y se agregan dos nuevos servicios:
        -Un servicio final (posterior a todos los demas) entre la cabecera recibida y la opuesta
        -Un servicio inicial (previo a todos los demas) entre la cabecera opuesta y la recibida

    Parámetros:
        G: El grafo al que se le modificará la arista correspondiente.
        target_station: La cabecera a la que se le modificará la arista de trasnoche.
        upper_bound: La capacidad que se le asignará a la arista de trasnoche.
        colors: Una lista de colores para los nodos.
        border_colors: Una lista de colores de borde para los nodos.
        edge_colors: Un diccionario que asigna colores a las aristas.


    Devuelve:
        G: El grafo actualizado con la nueva capacidad en la arista de trasnoche
        y los nuevos nodos.
        - pos: Un diccionario que asigna posiciones a los nodos.
        - night_edges: Una lista de aristas nocturnas agregadas al grafo.
        - colors: Una lista de colores para los nodos.
        - border_colors: Una lista de colores de borde para los nodos.
        - edge_colors: Un diccionario que asigna colores a las aristas.
    """

    station_names = [instance["stations"][0], instance["stations"][1]]

    G_prime = G

    last_trains = [(None, None), (None, None)]
    first_trains = [(None, None), (None, None)]
    night_edges = []

    for node in G.nodes(data=True):
        if node[1]["stations"] == station_names[0]:
            if last_trains[0][0] is None and first_trains[0][0] is None:
                last_trains[0] = node[0]
                first_trains[0] = node[0]
            elif last_trains[0][0] < node[0][0]:
                last_trains[0] = node[0]
            elif first_trains[0][0] > node[0][0]:
                first_trains[0] = node[0]
        else:
            if last_trains[1][0] is None and first_trains[1][0] is None:
                last_trains[1] = node[0]
                first_trains[1] = node[0]
            elif last_trains[1][0] < node[0][0]:
                last_trains[1] = node[0]
            elif first_trains[1][0] > node[0][0]:
                first_trains[1] = node[0]

    new_nodes = [
        (last_trains[0][0] + 1, station_names[0]),
        (first_trains[0][0] - 1, station_names[0]),
        (last_trains[1][0] + 1, station_names[1]),
        (first_trains[1][0] - 1, station_names[1]),
    ]

    # Creamos los nodos correspondientes a los nuevos servicios.

    G_prime.add_node(new_nodes[1], stations=station_names[0])
    colors.append("yellow")
    border_colors.append("orange")
    G_prime.add_node(new_nodes[3], stations=station_names[1])
    colors.append("yellow")
    border_colors.append("orange")
    G_prime.add_node(new_nodes[0], stations=station_names[0])
    colors.append("yellow")
    border_colors.append("orange")
    G_prime.add_node(new_nodes[2], stations=station_names[1])
    colors.append("yellow")
    border_colors.append("orange")

    night_edges.append((new_nodes[0], new_nodes[1]))
    night_edges.append((new_nodes[2], new_nodes[3]))

    # Agregamos las aristas que corresponden a esos servicios:
    #   -En el servicio final, hay una arista desde target_station hasta la estación opuesta.
    #   -En el servicio inicial, hay una arista desde la estación opuesta hasta target_station.
    # Reasignamos las aristas de trasnoche.

    if target_station == station_names[0]:
        G_prime.add_edge(
            new_nodes[0],
            new_nodes[1],
            weight=instance[COST][station_names[0]],
            amount_modified=0,
            upper_bound=upper_bound,
        )
        edge_colors[new_nodes[0], new_nodes[1]] = "purple"
        G_prime.add_edge(
            new_nodes[2],
            new_nodes[3],
            weight=instance[COST][station_names[1]],
            amount_modified=0,
        )
        edge_colors[new_nodes[2], new_nodes[3]] = "purple"
        G_prime.add_edge(new_nodes[3], new_nodes[1], amount_modified=0)
        edge_colors[new_nodes[3], new_nodes[1]] = "orange"
        G_prime.add_edge(new_nodes[0], new_nodes[2], amount_modified=0)
        edge_colors[new_nodes[0], new_nodes[2]] = "orange"
    else:
        G_prime.add_edge(
            new_nodes[0],
            new_nodes[1],
            weight=instance[COST][station_names[0]],
            amount_modified=0,
        )
        edge_colors[new_nodes[0], new_nodes[1]] = "purple"
        G_prime.add_edge(
            new_nodes[2],
            new_nodes[3],
            weight=instance[COST][station_names[1]],
            amount_modified=0,
            upper_bound=upper_bound,
        )
        edge_colors[new_nodes[2], new_nodes[3]] = "purple"
        G_prime.add_edge(new_nodes[1], new_nodes[3], amount_modified=0)
        edge_colors[new_nodes[1], new_nodes[3]] = "orange"
        G_prime.add_edge(new_nodes[2], new_nodes[0], amount_modified=0)
        edge_colors[new_nodes[2], new_nodes[0]] = "orange"

    G_prime.remove_edges_from(
        [(last_trains[0], first_trains[0]), (last_trains[1], first_trains[1])]
    )

    # Conectamos los servicios existentes a los nuevos.

    G_prime.add_edge(new_nodes[1], first_trains[0], amount_modified=0)
    edge_colors[new_nodes[1], first_trains[0]] = "orange"
    G_prime.add_edge(new_nodes[3], first_trains[1], amount_modified=0)
    edge_colors[new_nodes[3], first_trains[1]] = "orange"
    G_prime.add_edge(last_trains[0], new_nodes[0], amount_modified=0)
    edge_colors[last_trains[0], new_nodes[0]] = "orange"
    G_prime.add_edge(last_trains[1], new_nodes[2], amount_modified=0)
    edge_colors[last_trains[1], new_nodes[2]] = "orange"

    # Asignamos las nuevas posiciones de los nodos.

    pos = {}
    servicios: json = instance[SERVICES]

    uniform_positions = [x for x in range(len(servicios) * 2 + 4)]

    nodes = list(G_prime.nodes())
    nodes.sort(key=lambda x: x[0])
    nodes_by_station = {station_names[0]: [], station_names[1]: []}

    for node_pos in range(len(nodes)):
        if nodes[node_pos][1] == station_names[0]:
            nodes_by_station[station_names[0]].append(nodes[node_pos])
            pos[nodes[node_pos]] = (0, uniform_positions[node_pos])
        else:
            nodes_by_station[station_names[1]].append(nodes[node_pos])
            pos[nodes[node_pos]] = (0.5, uniform_positions[node_pos])

    return G_prime, pos, night_edges, colors, edge_colors, border_colors
