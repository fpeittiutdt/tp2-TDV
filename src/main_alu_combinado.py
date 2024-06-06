import json
import networkx as nx
import matplotlib.pyplot as plt
import main_combinado as gr

def main():

    filename = "instances/toy_instance.json"
    with open(filename) as json_file:
        data = json.load(json_file)
    

    name_station_zero = data["stations"][0]
    name_station_one = data["stations"][1]

    graph_representation, positions, night_edges = gr.create_graph(data)
    
    list_one = []
    list_zero = []
    list_colors = []
    labels = {}

    for nodo in graph_representation.nodes(data=True):

        list_colors.append(nodo[1]["color"])
        labels[nodo[0]] = nodo[0]

        if nodo[1]["stations"] == name_station_zero:
            list_zero.append(nodo[0])
        else:
            list_one.append(nodo[0])

    list_zero.sort()
    list_one.sort()

    nx.draw_networkx_nodes(
        graph_representation,
        node_color=list_colors,
        pos=positions,
        node_size=400,
        node_shape="s",
        linewidths=graph_representation.number_of_nodes() * [1],
    )

    nx.draw_networkx_nodes(
        graph_representation,
        node_color=list_colors,
        pos=positions,
        node_size=400,
        node_shape="s",
        linewidths=graph_representation.number_of_nodes() * [1],
    )

    nx.draw_networkx_labels(
        graph_representation, pos=positions, labels=labels, font_size=8, font_family="serif"
    )

    print(graph_representation.edges(data=True))
    for edge in graph_representation.edges():
        if edge in night_edges:
            nx.draw_networkx_edges(
                graph_representation,
                pos=positions,
                edgelist=[edge],
                connectionstyle="arc3, rad = 0.5",
            )
            if edge == (list_zero[len(list_zero)-1], list_zero[0]) or edge == (list_one[len(list_one)-1], list_one[0]):
                nx.draw_networkx_edge_labels(
                    graph_representation,
                    pos=positions,
                    edge_labels={edge: graph_representation[edge[0]][edge[1]]["weight"]},
                    label_pos=0.5,
                    font_size=10,
                    rotate=False,
                    connectionstyle="arc3, rad = 0.5",
                )
        else:
            nx.draw_networkx_edges(
                graph_representation, edgelist=[edge], pos=positions
            )
    
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.show()

    solucion = nx.min_cost_flow(graph_representation, capacity="upper_bound")
    costo_minimo = nx.cost_of_flow(graph_representation, solucion)
    print("solucion: ", solucion, "costo minimo: ", costo_minimo)

    for nodo1 in solucion:
        for nodo2 in solucion[nodo1]:
            solucion[nodo1][nodo2] += graph_representation[nodo1][nodo2]["amount_modified"]

    print("solucion modificada: ", solucion)

    flow_zero = solucion[list_zero[len(list_zero)-1]][list_zero[0]]
    flow_one = solucion[list_one[len(list_one)-1]][list_one[0]]
    first_zero = (list_zero[0], flow_zero)
    first_one = (list_one[0], flow_one)

    print(f"{name_station_zero}: {first_zero} y {name_station_one}: {first_one}")

    costo_minimo = nx.cost_of_flow(graph_representation, solucion)
    print("costo minimo: ", costo_minimo)

    print("AGREGANDO MODIFICACION")



if __name__ == "__main__":
	main()