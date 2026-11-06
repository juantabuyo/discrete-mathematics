"""Independent graph, address and local integration regressions."""

import contextlib
import io
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import pandas as pd
import route_planner
import street_map
import weighted_graph as gp
from demo import example_graph


def weight(graph, u, v):
    return graph[u][v]["weight"]


class GraphTests(unittest.TestCase):
    def test_disconnected_destination_and_equal_endpoints(self):
        graph = nx.DiGraph()
        graph.add_weighted_edges_from([(0, 1, 2)])
        graph.add_node(2)
        self.assertEqual(gp.shortest_path(graph, weight, 0, 2), [])
        self.assertEqual(gp.shortest_path(graph, weight, 1, 0), [])
        self.assertEqual(gp.shortest_path(graph, weight, 0, 0), [0])

    def test_invalid_nodes(self):
        graph = nx.path_graph(3)
        with self.assertRaises(nx.NodeNotFound):
            gp.shortest_path(graph, weight, 0, 8)
        with self.assertRaises(nx.NodeNotFound):
            gp.dijkstra(graph, weight, 8)
        with self.assertRaises(TypeError):
            gp.shortest_path(graph, weight, [], 0)

    def test_mixed_node_labels_and_zero_weights(self):
        graph = nx.Graph()
        graph.add_weighted_edges_from([(0, "a", 0), (0, (1, 2), 0), ("a", "end", 2)])
        self.assertEqual(gp.shortest_path(graph, weight, 0, "end"), [0, "a", "end"])
        self.assertEqual(
            sum(weight(graph, u, v) for u, v in gp.kruskal(graph, weight)), 2
        )
        parents = gp.prim(graph, weight)
        self.assertEqual(
            sum(weight(graph, u, v) for u, v in parents.items() if v is not None), 2
        )

    def test_empty_graphs(self):
        self.assertEqual(gp.prim(nx.Graph(), weight), {})
        self.assertEqual(gp.kruskal(nx.Graph(), weight), [])

    def test_integer_weights_above_the_float_range(self):
        graph = nx.Graph()
        graph.add_edge(0, "target", weight=10**309)
        self.assertEqual(gp.shortest_path(graph, weight, 0, "target"), [0, "target"])
        parents = gp.prim(graph, weight)
        self.assertEqual(
            sum(weight(graph, u, v) for u, v in parents.items() if v is not None),
            10**309,
        )

    def test_shortest_paths_against_networkx(self):
        rng = random.Random(104)
        for directed in (False, True):
            for seed in range(10):
                graph = nx.gnp_random_graph(9, 0.25, seed=seed, directed=directed)
                for u, v in graph.edges():
                    graph[u][v]["weight"] = rng.randint(0, 25)
                for origin in graph:
                    expected = nx.single_source_dijkstra_path_length(graph, origin)
                    for destination in graph:
                        with self.subTest(
                            directed=directed,
                            seed=seed,
                            origin=origin,
                            destination=destination,
                        ):
                            route = gp.shortest_path(graph, weight, origin, destination)
                            if destination not in expected:
                                self.assertEqual(route, [])
                            else:
                                self.assertEqual(route[0], origin)
                                self.assertEqual(route[-1], destination)
                                self.assertEqual(
                                    sum(
                                        weight(graph, u, v)
                                        for u, v in zip(route, route[1:])
                                    ),
                                    expected[destination],
                                )

    def test_spanning_forests_against_networkx(self):
        rng = random.Random(72)
        for seed in range(20):
            graph = nx.gnp_random_graph(10, 0.2, seed=seed)
            for u, v in graph.edges():
                graph[u][v]["weight"] = rng.randint(-5, 20)
            expected = nx.minimum_spanning_tree(graph)
            parents = gp.prim(graph, weight)
            for edges in (
                [(u, v) for u, v in parents.items() if v is not None],
                gp.kruskal(graph, weight),
            ):
                with self.subTest(seed=seed):
                    actual = nx.Graph()
                    actual.add_nodes_from(graph)
                    actual.add_edges_from(edges)
                    self.assertTrue(nx.is_forest(actual))
                    self.assertEqual(
                        nx.number_connected_components(actual),
                        nx.number_connected_components(graph),
                    )
                    self.assertEqual(
                        sum(weight(graph, u, v) for u, v in edges),
                        expected.size(weight="weight"),
                    )


class AddressTests(unittest.TestCase):
    def setUp(self):
        self.directory = pd.DataFrame(
            [
                ["CALLE", None, "MAYOR", 1, 40.4, -3.7],
                ["CALLE", "DE", "ALBERTO AGUILERA", 23, 40.42, -3.71],
                ["CALLE", "DE LA", "PALMA", 2, 40.43, -3.72],
            ],
            columns=[
                "VIA_CLASE",
                "VIA_PAR",
                "VIA_NOMBRE",
                "NUMERO",
                "LATITUD",
                "LONGITUD",
            ],
        )

    def test_address_without_particle(self):
        self.assertEqual(
            street_map.find_address("Calle Mayor, 1", self.directory), (40.4, -3.7)
        )

    def test_one_word_and_multiword_particles(self):
        self.assertEqual(
            street_map.find_address("Calle de Alberto Aguilera, 23", self.directory),
            (40.42, -3.71),
        )
        self.assertEqual(
            street_map.find_address("Calle de la Palma, 2", self.directory),
            (40.43, -3.72),
        )

    def test_whitespace_and_case(self):
        self.assertEqual(
            street_map.find_address("  calle  mayor,1  ", self.directory), (40.4, -3.7)
        )

    def test_absent_and_malformed_addresses(self):
        for address in ("Calle Mayor, 900", "Calle Mayor", "Calle Mayor, 1 trailing"):
            with (
                self.subTest(address=address),
                self.assertRaises(street_map.AddressNotFoundError),
            ):
                street_map.find_address(address, self.directory)

    def test_coordinates_and_malformed_input(self):
        self.assertEqual(street_map.dms_to_decimal("40°25'30''N"), 40.425)
        self.assertEqual(street_map.dms_to_decimal("3°42'0''W"), -3.7)
        with self.assertRaises(ValueError):
            street_map.dms_to_decimal("not a coordinate")

    def test_csv_loading(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "addresses.csv"
            path.write_text(
                "VIA_CLASE;VIA_PAR;VIA_NOMBRE;NUMERO;LATITUD;LONGITUD\nCALLE;;MAYOR;1;40°25'30''N;3°42'0''W\n",
                encoding="ISO-8859-1",
            )
            with patch.object(street_map, "STREET_FILE_NAME", str(path)):
                loaded = street_map.load_addresses()
            self.assertEqual(
                street_map.find_address("Calle Mayor, 1", loaded), (40.425, -3.7)
            )


class LocalIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.graph = street_map.simplify_graph(example_graph())

    def tearDown(self):
        plt.close("all")

    def test_terminal_end_of_input_and_interrupt_exit(self):
        # A fallback input keeps a regression bounded if the prompt loops again.
        for interruption in (EOFError, KeyboardInterrupt):
            with patch("builtins.input", side_effect=[interruption, ""]) as read:
                self.assertEqual(
                    route_planner.prompt_address(None, "origin"), (None, None)
                )
                self.assertEqual(read.call_count, 1)
            with patch("builtins.input", side_effect=[interruption, "9"]) as read:
                self.assertEqual(route_planner.choose_cost(), "9")
                self.assertEqual(read.call_count, 1)

    def test_real_osmnx_conversion_and_nearest_node(self):
        graph = example_graph()
        graph.add_edge(0, 1, length=999, maxspeed=20)
        graph.add_edge(0, 0, length=1, maxspeed=20)
        processed = street_map.simplify_graph(graph)
        self.assertFalse(processed.is_multigraph())
        self.assertEqual(processed[0][1]["length"], 100)
        self.assertFalse(processed.has_edge(0, 0))
        self.assertEqual(ox.nearest_nodes(processed, -3.70, 40.40), 0)

    def test_real_graphml_cache_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "madrid.graphml"
            ox.save_graphml(example_graph(), path)
            with patch.object(street_map, "PATH", str(path)):
                loaded = street_map.load_graph()
            self.assertEqual(set(loaded), {0, 1, 2, 3})
            self.assertEqual(loaded[0][1][0]["length"], 100)

    def test_three_costs_choose_different_routes(self):
        for cost, expected in (
            (route_planner.distance_cost, [0, 1, 3]),
            (route_planner.time_cost, [0, 2, 3]),
            (route_planner.junction_cost, [0, 3]),
        ):
            self.assertEqual(gp.shortest_path(self.graph, cost, 0, 3), expected)
        self.assertAlmostEqual(
            route_planner.junction_cost(self.graph, 0, 1)
            - route_planner.time_cost(self.graph, 0, 1),
            24,
        )

    def test_single_edge_instructions(self):
        instructions = route_planner.navigation_instructions(self.graph, [0, 1])
        self.assertEqual(
            instructions,
            ["Continue along Example Road for 100 metres to your destination."],
        )
        self.assertEqual(route_planner.navigation_instructions(self.graph, [0]), [])

    def test_turns_and_grouped_street_distances(self):
        self.assertEqual(route_planner.describe_turn(self.graph, 0, 1, 3), "Turn left")
        self.assertEqual(route_planner.describe_turn(self.graph, 0, 2, 3), "Turn right")
        self.graph[1][3]["name"] = "Example Road"
        self.assertEqual(
            route_planner.navigation_instructions(self.graph, [0, 1, 3]),
            ["Continue along Example Road for 200 metres to your destination."],
        )

    def test_missing_speed_and_empty_highway(self):
        self.graph[0][1].pop("maxspeed")
        self.graph[0][1]["highway"] = []
        self.assertEqual(route_planner.edge_speed(self.graph, 0, 1), 50)
        self.graph[0][1]["highway"] = "residential"
        self.assertEqual(route_planner.edge_speed(self.graph, 0, 1), 30)
        self.graph[0][1]["maxspeed"] = 0
        self.assertEqual(route_planner.time_cost(self.graph, 0, 1), float("inf"))

    def test_empty_and_single_node_routes_can_be_plotted(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            street_map.draw_route(self.graph, [])
        self.assertIn("No route", output.getvalue())
        street_map.draw_route(self.graph, [0])
        plt.gcf().canvas.draw()
        self.assertEqual(len(plt.gcf().axes), 1)

    def test_multi_edge_route_can_be_rendered(self):
        street_map.draw_route(self.graph, [0, 1, 3])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "route.png"
            plt.savefig(path)
            self.assertGreater(path.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
