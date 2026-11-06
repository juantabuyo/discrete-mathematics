"""Plot the demo network using the project's three route costs."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx

import route_planner
import street_map
import weighted_graph
from demo import example_graph


def main():
    graph = street_map.simplify_graph(example_graph())
    positions = {node: (data["x"], data["y"]) for node, data in graph.nodes(data=True)}
    choices = [
        ("Shortest distance", route_planner.distance_cost, "metres", "#176b9c"),
        ("Shortest estimated time", route_planner.time_cost, "seconds", "#24785b"),
        ("Time with junction delays", route_planner.junction_cost, "seconds", "#b45d22"),
    ]
    figure, axes = plt.subplots(1, 3, figsize=(15, 5.4), layout="constrained")
    for axis, (title, weight, unit, colour) in zip(axes, choices):
        route = weighted_graph.shortest_path(graph, weight, 0, 3)
        cost = sum(weight(graph, source, target) for source, target in zip(route, route[1:]))
        nx.draw_networkx_edges(
            graph, positions, ax=axis, edge_color="#c6d0d9", width=1.5,
            arrows=True, arrowsize=16, node_size=680,
        )
        nx.draw_networkx_edges(
            graph, positions, ax=axis, edgelist=list(zip(route, route[1:])),
            edge_color=colour, width=4, arrows=True, arrowsize=22, node_size=680,
        )
        nx.draw_networkx_nodes(
            graph, positions, ax=axis, node_color="#f4f7fa", edgecolors=colour,
            linewidths=2, node_size=680,
        )
        nx.draw_networkx_labels(graph, positions, ax=axis, font_size=12, font_weight="bold")
        axis.set_title(title, fontsize=12, fontweight="bold", pad=18)
        axis.text(
            0.5, -0.08, " → ".join(map(str, route)) + f"   |   {cost:g} {unit}",
            transform=axis.transAxes, ha="center", fontsize=11, color=colour,
        )
        axis.text(0.01, 0.01, "0 = start · 3 = destination", transform=axis.transAxes, fontsize=9)
        axis.set_xlim(-3.7025, -3.6875)
        axis.set_ylim(40.3975, 40.4125)
        axis.set_aspect("equal")
        axis.set_axis_off()
        print(f"{title}: {route}; {cost:g} {unit}")
    figure.suptitle("One network, three route costs", fontsize=17, fontweight="bold")
    figure.supxlabel(
        "Synthetic roads and coordinates · routes computed by the project's Dijkstra implementation",
        fontsize=10,
    )
    output = Path(__file__).parent / "docs/images/route-comparison.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=140, facecolor="white", bbox_inches="tight")
    plt.close(figure)
    print(f"Saved {output.relative_to(Path(__file__).parent)}")


if __name__ == "__main__":
    main()

