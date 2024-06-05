
from helpers.utils import *

def main():
    instance = load_instance('toy')

    G, station_codes = initialize_graph(instance)
    G, colors, labels, pos, border_colors, edge_colors = add_nodes_and_edges(G, instance, station_codes)
    G, night_edges = add_night_edges(G, instance, station_codes, edge_colors)
    G_prime = adjust_graph_for_flow(G)
    minCost, minCostFlow = calculate_min_cost_flow(G_prime)

    print('minCostFlow: {}\nminCost: {}'.format(minCostFlow, minCost))

    visualize_graph(G_prime, colors, pos, labels, border_colors, edge_colors, night_edges, minCostFlow)


if __name__ == '__main__':
    main()