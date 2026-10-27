"""Address lookup, street-network loading and route plots for Madrid."""

import math
import os
import re
from typing import Tuple

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import pandas as pd

STREET_FILE_NAME = "addresses.csv"
PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME = "madrid.graphml"

MAX_SPEEDS = {
    "living_street": "20",
    "residential": "30",
    "primary_link": "40",
    "unclassified": "40",
    "secondary_link": "40",
    "trunk_link": "40",
    "secondary": "50",
    "tertiary": "50",
    "primary": "50",
    "trunk": "50",
    "tertiary_link": "50",
    "busway": "50",
    "motorway_link": "70",
    "motorway": "100",
}


class ServiceNotAvailableError(Exception):
    """The street network could not be retrieved."""


class AddressNotFoundError(Exception):
    """An address could not be matched to the street directory."""


def dms_to_decimal(coord: str) -> float:
    """Convert the directory's degrees/minutes/seconds format to decimal degrees.

    For example, ``40°25'30''N`` becomes ``40.425``. Southern and western
    coordinates are negative; the result is rounded to seven decimal places.
    """
    pattern = r"(\d+)°(\d+)'(\d+\.?\d*)''\s*([NSEW])"
    match = re.fullmatch(pattern, coord.strip())
    if match is None:
        raise ValueError("Expected a coordinate such as 40°25'30''N.")

    degrees, minutes, seconds, hemisphere = match.groups()
    degrees, minutes, seconds = float(degrees), float(minutes), float(seconds)
    if minutes >= 60 or seconds >= 60:
        raise ValueError(f"Minutes and seconds must be below 60 in {coord!r}.")
    dec = degrees + minutes / 60 + seconds / 3600
    if dec > (90 if hemisphere in {"N", "S"} else 180):
        raise ValueError(
            f"Latitude must not exceed 90 degrees and longitude 180 degrees in {coord!r}."
        )

    if hemisphere in {"S", "W"}:
        dec = -dec

    return round(dec, 7)


def load_addresses() -> pd.DataFrame:
    """Read ``addresses.csv`` and convert its coordinates to decimal degrees.

    The expected municipal CSV uses semicolons, ISO-8859-1 encoding and the
    original Spanish column names. A missing file raises FileNotFoundError.
    """
    df = pd.read_csv(
        STREET_FILE_NAME,
        usecols=["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE", "NUMERO", "LATITUD", "LONGITUD"],
        encoding="ISO-8859-1",
        sep=";",
    )
    df["LATITUD"] = df["LATITUD"].apply(dms_to_decimal)
    df["LONGITUD"] = df["LONGITUD"].apply(dms_to_decimal)
    return df


def _text(column: pd.Series) -> pd.Series:
    """Return a column as text with missing values empty.

    A directory column that is empty in every row is read as float64; filling that
    with a string is deprecated in pandas, so the values are converted first.
    """
    return column.astype(object).where(column.notna(), "")


def find_address(address: str, street_map: pd.DataFrame) -> Tuple[float, float]:
    """Return latitude and longitude for ``street type and name, number``.

    Matching ignores case and repeated whitespace, but preserves accents.
    Street particles come from the directory and may be absent or contain
    multiple words. If several records match, the first one is used.
    """
    match = re.fullmatch(r"([^,]+),\s*(\d+)", address.strip())
    if match is None:
        raise AddressNotFoundError(f"Could not interpret the address: {address}")

    name, number = match.groups()
    name = " ".join(name.upper().split())
    # Match the complete street name: assuming a one-word particle rejects
    # valid names such as Calle Mayor and Calle de la Palma.
    names = (
        (
            _text(street_map["VIA_CLASE"])
            + " "
            + _text(street_map["VIA_PAR"])
            + " "
            + _text(street_map["VIA_NOMBRE"])
        )
        .str.upper()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    matches = street_map[(names == name) & (street_map["NUMERO"] == int(number))]

    if matches.empty:
        raise AddressNotFoundError(f"The address '{address}' is not in the directory.")

    row = matches.iloc[0]
    return row["LATITUD"], row["LONGITUD"]


PATH = MAP_FILE_NAME


def load_graph() -> nx.MultiDiGraph:
    """Load the local GraphML cache, or download and cache Madrid's driving graph.

    A fresh download requires network access to the services used by OSMnx.
    Download failures raise ServiceNotAvailableError; corrupt local files are
    reported by OSMnx rather than silently replaced.
    """
    if os.path.isfile(PATH):
        return ox.load_graphml(PATH)
    try:
        G_multi = ox.graph_from_place(PLACE_NAME, network_type="drive")
    except Exception as exc:
        raise ServiceNotAvailableError(
            "Could not retrieve the OpenStreetMap graph."
        ) from exc
    ox.save_graphml(G_multi, filepath=PATH)
    return G_multi


def simplify_graph(multigraph: nx.MultiDiGraph, edge_cost=None) -> nx.DiGraph:
    """Keep one edge between each ordered pair of nodes and remove self-loops.

    By default the shortest parallel edge is kept. With ``edge_cost``, a function
    of an edge's attribute dictionary, the cheapest parallel edge under that cost
    is kept instead, so a longer but faster road is not discarded when searching
    for the shortest travel time. A graph simplified for one cost is not
    guaranteed to contain the best edges for another.
    """
    if edge_cost is None:
        G = ox.convert.to_digraph(multigraph)
    else:
        G = nx.DiGraph()
        G.add_nodes_from(multigraph.nodes(data=True))
        G.graph.update(multigraph.graph)
        best = {}
        for u, v, data in multigraph.edges(data=True):
            cost = edge_cost(data)
            if (u, v) not in best or cost < best[(u, v)][0]:
                best[(u, v)] = (cost, data)
        G.add_edges_from((u, v, dict(data)) for (u, v), (_, data) in best.items())
    G.remove_edges_from(nx.selfloop_edges(G))
    return G


def draw_graph(G: nx.DiGraph) -> None:
    """Plot a graph using its nodes' ``x`` and ``y`` coordinates."""
    pos = {n: (data["x"], data["y"]) for n, data in G.nodes(data=True)}
    fig, ax = plt.subplots(figsize=(8, 8))
    nx.draw(G, pos=pos, node_size=0, width=0.5, arrows=True, ax=ax)
    ax.set_aspect("equal")
    ax.set_axis_off()
    plt.show()


def draw_route(G: nx.DiGraph, route_nodes) -> None:
    """Highlight a route; report an empty route without attempting to draw it."""
    if not route_nodes:
        print("No route is available.")
        return
    route_edges = list(zip(route_nodes, route_nodes[1:]))
    pos = {n: (data["x"], data["y"]) for n, data in G.nodes(data=True)}
    fig, ax = plt.subplots(figsize=(8, 8))
    nx.draw(
        G, pos=pos, node_size=0, width=0.5, edge_color="lightgrey", arrows=False, ax=ax
    )
    nx.draw_networkx_nodes(
        G,
        pos=pos,
        node_size=15,
        nodelist=route_nodes,
        node_color="black",
        alpha=0.7,
        ax=ax,
    )
    nx.draw_networkx_edges(
        G, pos=pos, edgelist=route_edges, width=3, arrows=False, edge_color="red", ax=ax
    )
    # Approximate longitude/latitude scale correction at Madrid's latitude.
    madrid_latitude = 40.435
    aspect_ratio = 1 / math.cos(math.radians(madrid_latitude))
    ax.set_aspect(aspect_ratio)
    ax.set_axis_off()
    plt.show()
