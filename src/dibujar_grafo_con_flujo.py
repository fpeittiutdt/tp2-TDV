import json
import networkx as nx
import matplotlib.pyplot as plt
import main_combinado as gr
from typing import Dict

def dibujar_grafo_con_flujo(grafo: nx.DiGraph, lista0, lista1, lista_colores, positions, night_edges, labels, dict_flujo: Dict):

    nx.draw_networkx_nodes(
        grafo,
        node_color=lista_colores,
        pos=positions,
        node_size=400,
        linewidths=grafo.number_of_nodes() * [1],
    )

    nx.draw_networkx_nodes(
        grafo,
        node_color=lista_colores,
        pos=positions,
        node_size=400,
        linewidths=grafo.number_of_nodes() * [1],
    )

    nx.draw_networkx_labels(
        grafo, pos=positions, labels=labels, font_size=8, font_family="serif"
    )

    #print(grafo.edges(data=True))
    for edge in grafo.edges():
        if edge in night_edges:
            nx.draw_networkx_edges(
                grafo,
                pos=positions,
                edgelist=[edge],
                connectionstyle="arc3, rad = 0.5",
            )
            nx.draw_networkx_edge_labels(
                    grafo,
                    pos=positions,
                    edge_labels={edge: dict_flujo[edge[0]][edge[1]]},
                    label_pos=0.5,
                    font_size=10,
                    rotate=False,
                    connectionstyle="arc3, rad = 0.5",
            )
        else:
            nx.draw_networkx_edges(
                grafo, edgelist=[edge], pos=positions
            )

            nx.draw_networkx_edge_labels(
                    grafo,
                    pos=positions,
                    edge_labels={edge: dict_flujo[edge[0]][edge[1]]},
                    label_pos=0.5,
                    font_size=10,
                    rotate=False,
                )
    
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.show()