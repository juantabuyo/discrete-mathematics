"""Draw a coordinate-based route using the existing street-map and graph modules."""

import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import osmnx as ox

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import route_planner  # noqa: E402
import street_map  # noqa: E402
import weighted_graph  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=PROJECT / "madrid.graphml")
    parser.add_argument("--download", action="store_true", help="Download Madrid if the graph is absent.")
    parser.add_argument("--origin", nargs=2, type=float, required=True, metavar=("LAT", "LON"))
    parser.add_argument("--destination", nargs=2, type=float, required=True, metavar=("LAT", "LON"))
    parser.add_argument("--cost", choices=("distance", "time", "junction"), default="distance")
    parser.add_argument("--output", type=Path, default=PROJECT / "docs/images/madrid-route.png")
    args = parser.parse_args()
    if not args.graph.is_file() and not args.download:
        parser.error("Graph not found. Supply an OSMnx GraphML file or use --download.")
    for lat, lon in (args.origin, args.destination):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            parser.error("Coordinates must be latitude then longitude in decimal degrees.")
    args.graph.parent.mkdir(parents=True, exist_ok=True)
    street_map.PATH = str(args.graph.resolve())
    ox.settings.cache_folder = str(args.graph.parent / "cache")
    graph = street_map.simplify_graph(street_map.load_graph())
    origin = ox.nearest_nodes(graph, args.origin[1], args.origin[0])
    destination = ox.nearest_nodes(graph, args.destination[1], args.destination[0])
    weight, unit = {
        "distance": (route_planner.distance_cost, "metres"),
        "time": (route_planner.time_cost, "seconds"),
        "junction": (route_planner.junction_cost, "seconds"),
    }[args.cost]
    route = weighted_graph.shortest_path(graph, weight, origin, destination)
    if not route:
        raise SystemExit("No route connects the snapped endpoints; no image was saved.")
    total = sum(weight(graph, u, v) for u, v in zip(route, route[1:]))
    street_map.draw_route(graph, route)
    figure = plt.gcf()
    figure.set_size_inches(12, 12)
    figure.suptitle("Madrid driving network", fontsize=20, y=0.97)
    figure.axes[0].set_title(f"Dijkstra · {args.cost} cost · {total:,.1f} {unit}", fontsize=12)
    figure.text(0.5, 0.045, "© OpenStreetMap contributors · openstreetmap.org/copyright", ha="center", fontsize=10)
    figure.text(0.5, 0.025, "Coordinate inputs snapped to street nodes; address CSV not used", ha="center", fontsize=10)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=150, facecolor="white")
    plt.close(figure)
    print(f"Graph: {len(graph)} nodes, {graph.number_of_edges()} directed edges")
    print(f"Snapped origin: {origin}; destination: {destination}")
    print(f"Route: {len(route) - 1} edges; {total:.1f} {unit} ({args.cost})")
    print("Coordinate-based run only: addresses.csv was not read.")
    print(f"Saved {args.output.name}")


if __name__ == "__main__":
    main()
