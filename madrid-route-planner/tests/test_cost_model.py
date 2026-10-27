"""Regression tests: speed units, parallel roads and empty directory columns.

Speeds with a unit other than km/h were read as km/h, the single reduced graph could discard
the fastest of several parallel roads, and an all-empty VIA_PAR column raised a pandas warning."""

import contextlib
import io
import random
import runpy
import unittest
from unittest.mock import patch
import warnings

import networkx as nx
import pandas as pd
import route_planner
import street_map
import weighted_graph as gp


class SpeedParsing(unittest.TestCase):
    def test_units_are_converted_to_km_per_hour(self):
        for value, expected in [
            ("30", 30.0), ("50 km/h", 50.0), ("50km/h", 50.0), ("40 kph", 40.0),
            ("30 mph", 30 * 1.609344), ("30mph", 30 * 1.609344), ("20 MPH", 20 * 1.609344),
            ("10 knots", 18.52), ("22.5", 22.5), ("50;30", 50.0), ("ES:30", 30.0),
            (30, 30.0), (22.5, 22.5), (["30 mph", "50"], 30 * 1.609344), ("50 (conditional)", 50.0),
        ]:
            with self.subTest(value=value):
                self.assertAlmostEqual(route_planner.parse_speed(value), expected)

    def test_unknown_units_and_non_numbers_give_none(self):
        for value in ("30 furlongs", "walk", "none", "signals", "", None, [], "ES:urban"):
            with self.subTest(value=value):
                self.assertIsNone(route_planner.parse_speed(value))

    def test_an_unreadable_unit_falls_back_to_the_road_type_table(self):
        graph = nx.DiGraph()
        graph.add_edge(0, 1, length=100.0, maxspeed="30 furlongs", highway="motorway")
        self.assertEqual(route_planner.edge_speed(graph, 0, 1), 100.0)

    def test_travel_time_uses_the_converted_speed(self):
        graph = nx.DiGraph()
        graph.add_edge(0, 1, length=1609.344, maxspeed="60 mph")
        graph.add_edge(1, 2, length=1609.344, maxspeed="96.56064 km/h")
        self.assertAlmostEqual(route_planner.time_cost(graph, 0, 1), 60.0)
        self.assertAlmostEqual(route_planner.time_cost(graph, 1, 2), 60.0)


def parallel_roads():
    """Two roads between the same nodes: short and slow, long and fast."""
    graph = nx.MultiDiGraph(crs="EPSG:4326")
    graph.add_node(0, x=-3.70, y=40.40)
    graph.add_node(1, x=-3.69, y=40.40)
    graph.add_edge(0, 1, length=100.0, maxspeed=10, name="Slow Lane")
    graph.add_edge(0, 1, length=150.0, maxspeed=90, name="Fast Road")
    graph.add_edge(1, 1, length=5.0, maxspeed=50)
    return graph


class ParallelRoads(unittest.TestCase):
    def test_default_simplification_is_unchanged(self):
        graph = street_map.simplify_graph(parallel_roads())
        self.assertEqual(graph[0][1]["length"], 100.0)
        self.assertFalse(graph.has_edge(1, 1))
        self.assertEqual(graph.graph["crs"], "EPSG:4326")
        self.assertEqual(graph.nodes[1]["x"], -3.69)

    def test_time_graph_keeps_the_fastest_parallel_road(self):
        graph = street_map.simplify_graph(parallel_roads(), route_planner.travel_time_from_data)
        self.assertEqual(graph[0][1]["name"], "Fast Road")
        self.assertAlmostEqual(route_planner.time_cost(graph, 0, 1), 150 / (90 / 3.6))
        self.assertAlmostEqual(route_planner.junction_cost(graph, 0, 1), 150 / (90 / 3.6) + 24)
        self.assertFalse(graph.has_edge(1, 1))
        self.assertEqual(graph.graph["crs"], "EPSG:4326")
        self.assertEqual(graph.nodes[0]["y"], 40.40)

    def test_time_costs_are_never_worse_than_on_the_distance_graph(self):
        multi = parallel_roads()
        distance_graph = street_map.simplify_graph(multi)
        time_graph = street_map.simplify_graph(multi, route_planner.travel_time_from_data)
        self.assertGreater(route_planner.time_cost(distance_graph, 0, 1),
                           route_planner.time_cost(time_graph, 0, 1))

    def test_time_routes_match_the_best_parallel_edges_on_random_networks(self):
        for seed in range(40):
            rng = random.Random(seed)
            multi = nx.MultiDiGraph()
            multi.add_nodes_from(range(7))
            for _ in range(30):
                u, v = rng.sample(range(7), 2)
                multi.add_edge(u, v, length=rng.uniform(50, 500), maxspeed=rng.choice([10, 30, 50, 90]))

            def best_time(u, v, edges):
                return min(route_planner.travel_time_from_data(data) for data in edges.values())

            graph = street_map.simplify_graph(multi, route_planner.travel_time_from_data)
            for source in range(7):
                reference = nx.single_source_dijkstra_path_length(multi, source, weight=best_time)
                for target in range(7):
                    route = gp.shortest_path(graph, route_planner.time_cost, source, target)
                    if target not in reference:
                        self.assertEqual(route, [] if source != target else [source])
                        continue
                    cost = sum(route_planner.time_cost(graph, a, b) for a, b in zip(route, route[1:]))
                    with self.subTest(seed=seed, source=source, target=target):
                        self.assertAlmostEqual(cost, reference[target])


class InteractiveModes(unittest.TestCase):
    def test_each_cost_is_searched_on_its_own_graph(self):
        addresses = pd.DataFrame({
            "VIA_CLASE": ["CALLE", "CALLE"], "VIA_PAR": [None, None], "VIA_NOMBRE": ["MAYOR", "ALCALA"],
            "NUMERO": [1, 2], "LATITUD": [40.40, 40.40], "LONGITUD": [-3.70, -3.69],
        })
        # Distance (option 1), then travel time (option 2), then an empty origin to leave.
        answers = ["Calle Mayor, 1", "Calle Alcala, 2", "1", "Calle Mayor, 1", "Calle Alcala, 2", "2", ""]
        output = io.StringIO()
        with (
            patch.object(street_map, "load_addresses", return_value=addresses),
            patch.object(street_map, "load_graph", return_value=parallel_roads()),
            patch.object(street_map, "draw_route"),
            patch("builtins.input", side_effect=answers),
            contextlib.redirect_stdout(output),
            self.assertRaises(SystemExit),
        ):
            runpy.run_module("route_planner", run_name="__main__")
        text = output.getvalue()
        self.assertIn("along Slow Lane for 100 metres", text)
        self.assertIn("along Fast Road for 150 metres", text)
        self.assertLess(text.index("Slow Lane"), text.index("Fast Road"))


class EmptyDirectoryColumn(unittest.TestCase):
    def test_all_empty_particle_column_gives_no_pandas_warning(self):
        directory = pd.DataFrame({
            "VIA_CLASE": ["CALLE", "CALLE"], "VIA_PAR": [float("nan"), float("nan")],
            "VIA_NOMBRE": ["MAYOR", "ALCALA"], "NUMERO": [1, 2],
            "LATITUD": [40.4, 40.5], "LONGITUD": [-3.7, -3.6],
        })
        self.assertEqual(directory["VIA_PAR"].dtype, "float64")
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.assertEqual(street_map.find_address("Calle Mayor, 1", directory), (40.4, -3.7))
            self.assertEqual(street_map.find_address("calle  alcala, 2", directory), (40.5, -3.6))


if __name__ == "__main__":
    unittest.main()
