import sys
from helpers.utils import *
from helpers.constants import INSTANCES

def print_usage():
    usage_message = """
    Usage:
        main.py -i 'instancia'
    
    Options:
        -i    Especifique el nombre de la instancia. Los nombres de instancia válidos son: {}
    """.format(', '.join(INSTANCES))
    
    print(usage_message)

def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ('-i', '--instance') or sys.argv[2] in ('-h', '--help'):
        print_usage()
        sys.exit(1)

    instance_name = sys.argv[2]

    if instance_name not in INSTANCES:
        print(f"Error: '{instance_name}' no es un nombre de instancia válido.")
        print_usage()
        sys.exit(1)

    instance = load_instance(instance_name)

    G, station_codes = initialize_graph(instance)
    G, colors, labels, pos, border_colors, edge_colors = add_nodes_and_edges(G, instance, station_codes)
    G, night_edges = add_night_edges(G, instance, station_codes, edge_colors)
    G_prime = adjust_graph_for_flow(G)
    minCost, minCostFlow = calculate_min_cost_flow(G_prime)

    print('minCostFlow: {}\nminCost: {}'.format(minCostFlow, minCost))

    visualize_graph(G_prime, colors, pos, labels, border_colors, edge_colors, night_edges, minCostFlow)


if __name__ == '__main__':
    main()