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
    """.format(
        ", ".join(INSTANCES)
    )

    print(usage_message)


def load_instance(instance: str):
    """
    Lectura de una instancia dada en formato json.

    Parámetros:
    instance (str): El nombre de la instancia a cargar. Este nombre debe estar presente en el diccionario INSTANCES.

    Retorna:
    dict: El contenido estructurado de una instancia.
    """

    with open("./instances/{}.json".format(INSTANCES[instance])) as json_file:
        return json.load(json_file)


def add_services(instance):
    """
    Agrega nodes y aristas al G G según la información proporcionada en la instancia.

    Parámetros:
    G (networkx.Graph): El G al que se agregarán los nodes y aristas.
    instance (dict): Un diccionario que contiene la información de la instancia.
    station_codes (list): Una lista de códigos de estaciones.

    Retorna:
    tuple: Una tupla que contiene:
        - G (networkx.Graph): El G actualizado con nodes y aristas.
        - colors (list): Una lista de colores para los nodes.
        - labels (dict): Un diccionario que asigna etiquetas a los nodes.
        - pos (dict): Un diccionario que asigna posiciones a los nodes.
        - border_colors (list): Una lista de colores de borde para los nodes.
        - edge_colors (dict): Un diccionario que asigna colores a las aristas.
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
        # Para el camnbio de variable
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
    Agrega aristas para representar conexiones nocturnas entre estaciones en el G G.

    Parámetros:
    G (networkx.Graph): El G al que se agregarán las aristas.
    instance (dict): Un diccionario que contiene la información de la instancia.
    station_codes (list): Una lista de códigos de estaciones.
    edge_colors (dict): Un diccionario que asigna colores a las aristas.

    Retorna:
    tuple: Una tupla que contiene:
        - G (networkx.Graph): El G actualizado con las aristas nocturnas.
        - night_edges (list): Una lista de aristas nocturnas agregadas al G.
    """

    night_edges = []

    station_names = [instance["stations"][0], instance["stations"][1]]

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
    G_prime, colors, pos, labels, border_colors, edge_colors, night_edges, minCostFlow
):
    """
    Visualiza el G G_prime con los colores, posiciones y etiquetas proporcionados.
    Parámetros:
        G_prime (networkx.Graph): El G a visualizar.
        colors (list): Una lista de colores para los nodes.
        pos (dict): Un diccionario que asigna posiciones a los nodes.
        labels (dict): Un diccionario que asigna etiquetas a los nodes.
        border_colors (list): Una lista de colores de borde para los nodes.
        edge_colors (dict): Un diccionario que asigna colores a las aristas.
        night_edges (list): Una lista de aristas nocturnas.
        minCostFlow (dict): Un diccionario que contiene el flujo de costo mínimo en el G.
    """

    nx.draw_networkx_nodes(
        G_prime,
        node_color=colors,
        pos=pos,
        node_size=400,
        node_shape="s",
        linewidths=G_prime.number_of_nodes() * [1],
        edgecolors=border_colors,
    )
    nx.draw_networkx_labels(
        G_prime, pos=pos, labels=labels, font_size=8, font_family="serif"
    )

    for edge in G_prime.edges():
        if edge in night_edges:
            rad = -0.5 if pos[edge[0]][0] != 0 else 0.5

            nx.draw_networkx_edges(
                G_prime,
                pos=pos,
                edgelist=[edge],
                edge_color=edge_colors[edge],
                connectionstyle="arc3, rad={}".format(rad),
            )
            nx.draw_networkx_edge_labels(
                G_prime,
                pos=pos,
                edge_labels={edge: minCostFlow[edge[0]][edge[1]]},
                label_pos=0.5,
                font_size=20,
                rotate=False,
                connectionstyle="arc3, rad=0.5",
            )
        else:
            nx.draw_networkx_edges(
                G_prime, pos=pos, edgelist=[edge], edge_color=edge_colors[edge]
            )

    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.show()
