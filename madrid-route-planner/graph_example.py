"""Small weighted-graph example adapted from the coursework smoke script."""

import random

import networkx as nx
import weighted_graph


def constant_weight(graph, origin, destination):
    return 1


def stored_weight(graph, origin, destination):
    return graph[origin][destination]["weight"]


def main():
    rng = random.Random(42)
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, "a", 5, 6])
    for origin, destination in [
        (1, 2),
        (1, 3),
        (1, "a"),
        (1, 5),
        (2, "a"),
        (3, "a"),
        (3, 5),
        (5, 6),
    ]:
        graph.add_edge(origin, destination, weight=rng.randrange(1, 12))

    for label, weight in [
        ("Unit weights", constant_weight),
        ("Seeded weights", stored_weight),
    ]:
        print(label)
        print("Shortest-path parents:", weighted_graph.dijkstra(graph, weight, 1))
        print("Path from 1 to 5:", weighted_graph.shortest_path(graph, weight, 1, 5))
        print("Kruskal edges:", weighted_graph.kruskal(graph, weight))
        print("Prim parents:", weighted_graph.prim(graph, weight))


if __name__ == "__main__":
    main()
