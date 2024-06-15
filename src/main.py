import sys
from helpers.utils import *
from helpers.constants import INSTANCES
import networkx as nx


def main():
    if (
        len(sys.argv) != 3
        or sys.argv[1] not in ("-i", "--instance")
        or sys.argv[2] in ("-h", "--help")
    ):
        print_usage()
        sys.exit(1)

    instance_name = sys.argv[2]

    if instance_name not in INSTANCES:
        print(f"Error: '{instance_name}' no es un nombre de instancia válido.")
        print_usage()
        sys.exit(1)

    instance = load_instance(instance_name)

    G, colors, pos, labels, border_colors, edge_colors, services_by_station = (
        add_services(instance)
    )
    G, night_edges = add_night_pass_edges(G, instance, edge_colors, services_by_station)
    minCostFlow = nx.min_cost_flow(
        G, demand="demand", capacity="upper_bound", weight="weight"
    )
    minCost = nx.cost_of_flow(G, minCostFlow)

    print("minCostFlow: {}\nminCost: {}".format(minCostFlow, minCost))

    visualize_graph(
        G,
        colors,
        pos,
        labels,
        border_colors,
        edge_colors,
        night_edges,
        minCostFlow,
    )


if __name__ == "__main__":
    main()
