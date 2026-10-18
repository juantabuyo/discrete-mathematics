"""Shortest paths and minimum spanning forests for weighted NetworkX graphs.

The weight callback receives ``(graph, source, target)`` and returns an edge
cost. Dijkstra requires non-negative weights; Prim and Kruskal require an
undirected graph.
"""

import heapq
from typing import Callable, Dict, List, Tuple, Union

import networkx as nx

INFTY = float("inf")


def dijkstra(
    G: Union[nx.Graph, nx.DiGraph],
    weight: Union[
        Callable[[nx.Graph, object, object], float],
        Callable[[nx.DiGraph, object, object], float],
    ],
    origin: object,
) -> Dict[object, object]:
    """Return shortest-path parents from ``origin`` for non-negative costs.

    The origin and unreachable nodes have parent ``None``. Nodes must be
    hashable, and the origin must belong to the graph.
    """
    try:
        hash(origin)
    except TypeError:
        raise TypeError("The origin node must be hashable.") from None
    if origin not in G:
        raise nx.NodeNotFound("The origin node is not in the graph.")

    parents = {}
    dist = {}
    visited = {}

    for v in G.nodes():
        parents[v] = None
        visited[v] = False
        dist[v] = INFTY

    dist[origin] = 0

    Q = []
    counter = 0  # Break ties without comparing node labels of different types.
    heapq.heappush(Q, (0, counter, origin))
    counter += 1

    while Q:
        d_v, _, v = heapq.heappop(Q)

        if not visited[v]:
            visited[v] = True

            for x in G.neighbors(v):
                w_vx = weight(G, v, x)
                if dist[x] > dist[v] + w_vx:
                    dist[x] = dist[v] + w_vx
                    parents[x] = v

                    heapq.heappush(Q, (dist[x], counter, x))
                    counter += 1
    return parents


def shortest_path(
    G: Union[nx.Graph, nx.DiGraph],
    weight: Union[
        Callable[[nx.Graph, object, object], float],
        Callable[[nx.DiGraph, object, object], float],
    ],
    origin: object,
    destination: object,
) -> List[object]:
    """Return a shortest path, or an empty list if the destination is unreachable.

    Both endpoints must be hashable nodes in ``G``. Equal endpoints return a
    one-node path. Costs must be non-negative, as required by Dijkstra.
    """
    try:
        hash(origin)
        hash(destination)
    except TypeError:
        raise TypeError("The origin and destination must be hashable.") from None
    if destination not in G:
        raise nx.NodeNotFound("The destination node is not in the graph.")

    parents = dijkstra(G, weight, origin)
    if destination != origin and parents[destination] is None:
        return []

    path = []
    v = destination

    while v is not None:
        path.append(v)
        if v == origin:
            break
        v = parents[v]

    path.reverse()
    return path


def prim(
    G: nx.Graph, weight: Callable[[nx.Graph, object, object], float]
) -> Dict[object, object]:
    """Return parents in a minimum spanning forest of an undirected graph.

    Each connected component has one root with parent ``None``. The priority
    queue uses a counter so equally weighted nodes need not be comparable.
    """
    parents = {}
    cost = {}
    queued = {}
    Q = []

    counter = 0
    for v in G.nodes():
        parents[v] = None
        cost[v] = INFTY
        queued[v] = True
        heapq.heappush(Q, (cost[v], counter, v))
        counter += 1
    counter = 0
    while Q:
        c_v, _, v = heapq.heappop(Q)

        if not queued[v]:
            continue

        queued[v] = False

        for x in G.neighbors(v):
            if queued[x]:
                w_vx = weight(G, v, x)
                if w_vx < cost[x]:
                    cost[x] = w_vx
                    parents[x] = v
                    heapq.heappush(Q, (cost[x], counter, x))
                    counter += 1

    return parents


def kruskal(
    G: nx.Graph, weight: Callable[[nx.Graph, object, object], float]
) -> List[Tuple[object, object]]:
    """Return the edges of a minimum spanning forest of an undirected graph.

    Components are maintained as sets. Only weights are used to sort edges,
    allowing mixed node-label types when weights tie.
    """
    edges = []
    for u, v in G.edges():
        edges.append((weight(G, u, v), u, v))
    edges.sort(key=lambda x: x[0])
    C = {v: {v} for v in G.nodes()}

    result = []

    for w, u, v in edges:
        if C[u] != C[v]:
            result.append((u, v))
            merged_component = C[u] | C[v]
            for x in merged_component:
                C[x] = merged_component

    return result
