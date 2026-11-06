"""Run all three route costs on a small, entirely synthetic street network."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import route_planner
import street_map
import weighted_graph


def example_graph():
    """Return invented roads and coordinates; no OpenStreetMap data is used."""
    graph = nx.MultiDiGraph(crs="EPSG:4326")
    for node, x, y in [
        (0, -3.70, 40.40),
        (1, -3.69, 40.40),
        (2, -3.70, 40.41),
        (3, -3.69, 40.41),
    ]:
        graph.add_node(node, x=x, y=y)
    for u, v, length, speed, name in [
        (0, 1, 100.0, 20, "Example Road"),
        (1, 3, 100.0, 20, "Example Lane"),
        (0, 2, 160.0, 60, "Sample Avenue"),
        (2, 3, 160.0, 60, "Sample Street"),
        (0, 3, 250.0, 40, "Direct Road"),
    ]:
        graph.add_edge(u, v, length=length, maxspeed=speed, name=name)
    return graph


if __name__ == "__main__":
    graph = street_map.simplify_graph(example_graph())
    origin = ox.nearest_nodes(graph, -3.70, 40.40)
    destination = ox.nearest_nodes(graph, -3.69, 40.41)

    print("Synthetic network: these are illustrative costs, not Madrid journeys.")
    for label, weight in [
        ("Distance (metres)", route_planner.distance_cost),
        ("Travel time (seconds)", route_planner.time_cost),
        ("Travel time with junction delays (seconds)", route_planner.junction_cost),
    ]:
        route = weighted_graph.shortest_path(graph, weight, origin, destination)
        cost = sum(weight(graph, u, v) for u, v in zip(route, route[1:]))
        print(f"{label}: {route}, cost {cost:.1f}")

    route = weighted_graph.shortest_path(
        graph, route_planner.distance_cost, origin, destination
    )
    for instruction in route_planner.navigation_instructions(graph, route):
        print(instruction)
    street_map.draw_route(graph, route)
    output = Path("output")
    output.mkdir(exist_ok=True)
    plt.savefig(output / "demo-route.png", dpi=120)
    plt.close("all")
    print("Saved output/demo-route.png")
