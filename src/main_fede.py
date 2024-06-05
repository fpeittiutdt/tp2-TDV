import json
import networkx as nx
import matplotlib.pyplot as plt
import math

BIG_NUMBER = 1e10


def main():
    filename = "instances/toy_instance.json"
    #filename = "instances/retiro-tigre-semana.json"

    with open(filename) as json_file:
        data = json.load(json_file)

    # Station parts
    station_codes = []
    i = 0
    for station in data["stations"]:
        station_codes.append(i)
        i += 1

    # Construcción de grafo modelo
    G = nx.DiGraph()
    colors = []
    pos = {}
    border_colors = []
    edge_colors = {}

    first_service_for_station = []
    last_service_for_station = []

    # Nodos y arcos de salidad y llegadas
    for service in data["services"]:
        for stop in data["services"][service]["stops"]:

            # Create the nodes
            if stop["station"] == data["stations"][0]:
                G.add_node(stop["time"])
                pos[stop["time"]] = (0, stop["time"] * 10)
                if stop["type"] == "D":
                    depart = stop["time"]
                    colors.append("#CCCCFF")
                    border_colors.append("blue")
                elif stop["type"] == "A":
                    arrival = stop["time"]
                    colors.append("#FFCCCC")
                    border_colors.append("red")
            else:
                G.add_node(stop["time"] + 0.5)
                pos[stop["time"] + 0.5] = (0.5, stop["time"] * 10)
                if stop["type"] == "D":
                    depart = stop["time"] + 0.5
                    colors.append("#CCCCFF")
                    border_colors.append("blue")
                elif stop["type"] == "A":
                    arrival = stop["time"] + 0.5
                    colors.append("#FFCCCC")
                    border_colors.append("red")
        edge_colors[depart, arrival] = "green"
        G.add_edge(
            depart,
            arrival,
            capacity=data["rs_info"]["max_rs"],
            demand=math.ceil(
                data["services"][service]["demand"][0] / data["rs_info"]["capacity"]
            ),
            cost=0,
        )

    night_edges = []
    # Arcos para cada estación
    station_index = 0
    for station in data["stations"]:
        train_order = []
        for service in data["services"]:
            for stop in data["services"][service]["stops"]:
                if stop["station"] == station:
                    train_order.append(stop["time"] + station_index / 2)
        train_order.sort()
        i = 0

        first_service_for_station.append(train_order[0])
        last_service_for_station.append(train_order[len(train_order) - 1])
        while i < len(train_order):
            # caso trasnoche
            if i == len(train_order) - 1:
                night_edges.append((train_order[i], train_order[0]))
                edge_colors[(train_order[i], train_order[0])] = "purple"
                G.add_edge(
                    train_order[i],
                    train_order[0],
                    capacity=BIG_NUMBER,
                    demand=0,
                    cost=1,
                )
            # Caso traspaso
            else:
                edge_colors[train_order[i], train_order[i + 1]] = "blue"
                G.add_edge(
                    train_order[i],
                    train_order[i + 1],
                    capacity=BIG_NUMBER,
                    demand=0,
                    cost=0,
                )
            i += 1
        station_index += 1

    # Una vez con el grafo del modelo, basta con convertirlo a un problema de flujo máximo costo mínimo

    G_prime = G.copy()

    for node in G.nodes():
        inbalance: int = 0
        out_neighbors = G.neighbors(node)
        capacities = nx.get_edge_attributes(G, "capacity")
        demands = nx.get_edge_attributes(G, "demand")
        costs = nx.get_edge_attributes(G, "cost")

        for out_node in out_neighbors:
            new_capacity = capacities[node, out_node] - demands[node, out_node]
            G_prime.remove_edge(node, out_node)
            G_prime.add_edge(
                node, out_node, capacity=new_capacity, cost=costs[node, out_node]
            )
            inbalance -= demands[node, out_node]

        for inner_edge in G.predecessors(node):
            inbalance += demands[inner_edge, node]

        G_prime.add_node(node, inbalance=-inbalance)

    minCost, minCostFlow = nx.network_simplex(
        G_prime, demand="inbalance", capacity="capacity", weight="cost"
    )
    print(minCostFlow)
    print(minCost)

    nx.draw_networkx_nodes(
        G_prime,
        node_color=colors,
        pos=pos,
        node_size=400,
        node_shape="s",
        linewidths=G_prime.number_of_nodes() * [1],
        edgecolors=border_colors,
    )

    nx.draw_networkx_labels(G_prime, pos=pos, font_size=8, font_family="serif")

    i = 0
    for edge in G_prime.edges():
        if edge in night_edges:
            nx.draw_networkx_edges(
                G_prime,
                pos=pos,
                edgelist=[edge],
                edge_color=edge_colors[edge],
                connectionstyle="arc3, rad = 0.5",
            )
            nx.draw_networkx_edge_labels(
                G_prime,
                pos=pos,
                edge_labels={edge: minCostFlow[edge[0]][edge[1]]},
                label_pos=0.5,
                font_size=20,
                rotate=False,
                connectionstyle="arc3, rad = 0.5",
            )
        else:
            nx.draw_networkx_edges(
                G_prime, edgelist=[edge], pos=pos, edge_color=edge_colors[edge]
            )
        i += 1

    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.show()


if __name__ == "__main__":
    main()
