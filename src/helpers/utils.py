import json, math
import networkx as nx
import matplotlib.pyplot as plt
from .constants import INSTANCES, BIG_NUMBER

def print_usage():
    usage_message = """
    Usage:
        main.py -i 'instancia'
    
    Options:
        -i    Especifique el nombre de la instancia. Los nombres de instancia válidos son: {}
    """.format(', '.join(INSTANCES))
    
    print(usage_message)

def load_instance(instance:str):
    with open('./instances/{}.json'.format(INSTANCES[instance])) as json_file:
        return json.load(json_file)

def initialize_graph(instance):
    station_codes = [station for station in instance['stations']]
    G = nx.DiGraph()
    return G, station_codes

def add_nodes_and_edges(G, instance, station_codes):
    colors = []
    labels = {}
    pos = {}
    border_colors = []
    edge_colors = {}

    for service in instance['services']:
        for stop in instance['services'][service]['stops']:
            station_index = 0 if stop['station'] == station_codes[0] else 1
            G.add_node((stop['time'], station_codes[station_index]))
            pos[(stop['time'], station_codes[station_index])] = (station_index * 0.5, stop['time'] * 10)
            labels[(stop['time'], station_codes[station_index])] = stop['time']
            if stop['type'] == 'D':
                depart = (stop['time'], station_codes[station_index])
                colors.append('#CCCCFF')
                border_colors.append('blue')
            elif stop['type'] == 'A':
                arrival = (stop['time'], station_codes[station_index])
                colors.append('#FFCCCC')
                border_colors.append('red')
        edge_colors[depart, arrival] = 'green'
        G.add_edge(
            depart,
            arrival,
            capacity=instance['rs_info']['max_rs'],
            demand=math.ceil(instance['services'][service]['demand'][0] / instance['rs_info']['capacity']),
            cost=0
        )
    return G, colors, labels, pos, border_colors, edge_colors

def add_night_edges(G, instance, station_codes, edge_colors):
    night_edges = []
    for station in station_codes:
        train_order = [(stop['time'], station) for service in instance['services'] for stop in instance['services'][service]['stops'] if stop['station'] == station]
        train_order.sort(key=lambda tup: tup[0])
        for i in range(len(train_order)):
            if i == len(train_order) - 1:
                night_edges.append((train_order[i], train_order[0]))
                edge_colors[(train_order[i], train_order[0])] = 'purple'
                G.add_edge(train_order[i], train_order[0], capacity=BIG_NUMBER, demand=0, cost=1)
            else:
                edge_colors[train_order[i], train_order[i + 1]] = 'blue'
                G.add_edge(train_order[i], train_order[i + 1], capacity=BIG_NUMBER, demand=0, cost=0)
    return G, night_edges

def adjust_graph_for_flow(G):
    G_prime = G.copy()
    capacities = nx.get_edge_attributes(G, 'capacity')
    demands = nx.get_edge_attributes(G, 'demand')
    costs = nx.get_edge_attributes(G, 'cost')
    
    for node in G.nodes():
        inbalance = 0
        out_neighbors = list(G.neighbors(node))
        
        for out_node in out_neighbors:
            new_capacity = capacities[(node, out_node)] - demands[(node, out_node)]
            G_prime.remove_edge(node, out_node)
            G_prime.add_edge(node, out_node, capacity=new_capacity, cost=costs[(node, out_node)])
            inbalance -= demands[(node, out_node)]
        
        for in_node in G.predecessors(node):
            inbalance += demands[(in_node, node)]
        
        G_prime.nodes[node]['inbalance'] = -inbalance

    return G_prime

def calculate_min_cost_flow(G_prime):
    minCost, minCostFlow = nx.network_simplex(G_prime, demand='inbalance', capacity='capacity', weight='cost')
    return minCost, minCostFlow

def visualize_graph(G_prime, colors, pos, labels, border_colors, edge_colors, night_edges, minCostFlow):
    nx.draw_networkx_nodes(G_prime, node_color=colors, pos=pos, node_size=400, node_shape='s', linewidths=G_prime.number_of_nodes() * [1], edgecolors=border_colors)
    nx.draw_networkx_labels(G_prime, pos=pos, labels=labels, font_size=8, font_family='serif')

    for edge in G_prime.edges():
        if edge in night_edges:
            nx.draw_networkx_edges(G_prime, pos=pos, edgelist=[edge], edge_color=edge_colors[edge], connectionstyle='arc3, rad=0.5')
            nx.draw_networkx_edge_labels(G_prime, pos=pos, edge_labels={edge: minCostFlow[edge[0]][edge[1]]}, label_pos=0.5, font_size=20, rotate=False, connectionstyle='arc3, rad=0.5')
        else:
            nx.draw_networkx_edges(G_prime, pos=pos, edgelist=[edge], edge_color=edge_colors[edge])
    
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.show()