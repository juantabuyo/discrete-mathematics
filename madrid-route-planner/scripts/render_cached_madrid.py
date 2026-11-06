"""Render a local historical OSM graph with the project's route implementation."""

import argparse
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PathCollection
import osmnx as ox

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import route_planner  # noqa: E402
import street_map  # noqa: E402
import weighted_graph  # noqa: E402

EXPECTED_BYTES = 29_706_105
EXPECTED_SHA256 = "da7889c8da72b22a14c25e4e09ce45bfd075b4c7b6d81569fd790713754b906c"
MAX_DECODED_BYTES = 40 * 1024 * 1024


def load_verified_graph(path):
    """Bound decompression and verify the exact historical cache before parsing."""
    opener = gzip.open if path.suffix == ".gz" else open
    chunks = []
    total = 0
    digest = hashlib.sha256()
    with opener(path, "rb") as source:
        while chunk := source.read(1024 * 1024):
            total += len(chunk)
            if total > MAX_DECODED_BYTES:
                raise ValueError("The decoded graph exceeds the 40 MiB limit.")
            digest.update(chunk)
            chunks.append(chunk)
    if total != EXPECTED_BYTES or digest.hexdigest() != EXPECTED_SHA256:
        raise ValueError("Graph size or SHA-256 does not match the documented historical cache.")
    # OSMnx 1.9.3 accepts GraphML text directly; no temporary dataset is written.
    return ox.load_graphml(graphml_str=b"".join(chunks).decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path,
                        default=PROJECT / "data/madrid-driving-2024-11-25.graphml.gz",
                        help="Documented historical cache, raw or gzip; never downloaded.")
    parser.add_argument("--output-dir", "--outputdir", type=Path, required=True)
    args = parser.parse_args()
    graph_file = args.graph.expanduser().resolve()
    if not graph_file.is_file():
        parser.error("--graph must be an existing local GraphML file.")
    outputs = [args.output_dir / "madrid-cached-network.png",
               args.output_dir / "madrid-sol-atocha-route.png"]
    if any(path.exists() or path.is_symlink() for path in outputs):
        parser.error("An output image already exists; choose a new --output-dir.")

    multigraph = load_verified_graph(graph_file)
    created = str(multigraph.graph.get("created_date", "unknown"))
    graph = street_map.simplify_graph(multigraph)
    # Public addresses from the previously checked municipal directory.
    origin_coordinates = (40.41655, -3.7038)  # Puerta del Sol, 7.
    destination_coordinates = (40.4076833, -3.6918472)  # Emperador Carlos V, 3.
    origin = ox.nearest_nodes(graph, origin_coordinates[1], origin_coordinates[0])
    destination = ox.nearest_nodes(graph, destination_coordinates[1], destination_coordinates[0])
    route = weighted_graph.shortest_path(graph, route_planner.distance_cost, origin, destination)
    if not route:
        raise SystemExit("The cached graph has no route between the snapped nodes; no image was saved.")
    distance = sum(route_planner.distance_cost(graph, u, v) for u, v in zip(route, route[1:]))
    calculated = date.today().isoformat()
    xs = [graph.nodes[node]["x"] for node in route]
    ys = [graph.nodes[node]["y"] for node in route]
    margin = 0.003
    zoom = [min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin]

    # Both views use the original renderer. Only axes, labels and size change.
    street_map.draw_route(graph, route)
    figure = plt.gcf()
    try:
        figure.set_size_inches(12, 12)
        figure.subplots_adjust(left=0.03, right=0.97, bottom=0.12, top=0.88)
        title = figure.suptitle("Madrid street network · historical OSM cache", fontsize=18, y=0.97)
        axes = figure.axes[0]
        # Restyle the existing artists; keep every edge and coordinate unchanged.
        network_lines, route_lines = [item for item in axes.collections if isinstance(item, LineCollection)]
        route_markers = [item for item in axes.collections
                         if isinstance(item, PathCollection) and any(item.get_sizes() > 0)][0]
        network_lines.set_color("#adb5bf")
        route_lines.set_linewidth(1.5)
        route_markers.set_sizes([2])
        axes.set_title(f"Extent of supplied graph · {len(graph):,} nodes · {graph.number_of_edges():,} directed edges", fontsize=11)
        figure.text(0.5, 0.085, f"Graph cached {created[:10]} · route calculated {calculated}", ha="center", fontsize=10)
        figure.text(0.5, 0.06, "© OpenStreetMap contributors · openstreetmap.org/copyright", ha="center", fontsize=10)
        figure.text(0.5, 0.035, "Coordinate inputs snapped to street nodes; address CSV not read", ha="center", fontsize=10)
        figure.text(0.5, 0.015, "Straight segments join graph nodes; costs use stored road lengths", ha="center", fontsize=10)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        figure.savefig(outputs[0], dpi=150, facecolor="white")

        title.set_text("Sol–Atocha · route on the historical Madrid graph")
        route_lines.set_linewidth(3)
        route_markers.set_sizes([15])
        axes.set_title(f"Original Dijkstra implementation · shortest distance · {distance:,.1f} metres", fontsize=11)
        axes.set_xlim(zoom[0], zoom[2])
        axes.set_ylim(zoom[1], zoom[3])
        for node, label in [(origin, "Sol · snapped start"), (destination, "Atocha · snapped end")]:
            attributes = graph.nodes[node]
            axes.annotate(label, (attributes["x"], attributes["y"]), xytext=(9, 10),
                          textcoords="offset points", fontsize=10,
                          bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": "0.7", "alpha": 0.95})
        figure.savefig(outputs[1], dpi=150, facecolor="white")
    finally:
        plt.close(figure)

    def endpoint(node, coordinates):
        attributes = graph.nodes[node]
        return {"input_lat_lon": coordinates, "node": int(node),
                "snapped_lat_lon": [attributes["y"], attributes["x"]]}

    report = {
        "source_sha256": EXPECTED_SHA256,
        "graph_created": created, "graph_created_with": multigraph.graph.get("created_with"),
        "graph_crs": str(multigraph.graph.get("crs")), "route_calculated": calculated,
        "input_graph_nodes": len(multigraph), "input_graph_edges": multigraph.number_of_edges(),
        "route_graph_nodes": len(graph), "route_graph_edges": graph.number_of_edges(),
        "origin": endpoint(origin, origin_coordinates), "destination": endpoint(destination, destination_coordinates),
        "route_nodes": [int(node) for node in route], "route_edges": len(route) - 1,
        "distance_metres": distance, "zoom_bbox_wsen": zoom, "addresses_csv_read": False,
        "outputs": [path.name for path in outputs],
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
