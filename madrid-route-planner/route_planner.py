"""Interactive route planning with distance and simple travel-time costs."""

import re
import sys
from typing import Any

import networkx as nx
import osmnx as ox
import street_map
import weighted_graph as gp


def prompt_address(df, endpoint) -> tuple[float | None, float | None]:
    """Prompt for an address, or return a pair of None values for an empty input."""
    while True:
        try:
            address = input(f"Enter the {endpoint} address (STREET, NUMBER): ").strip()
            if address == "":
                return None, None
            lat, lon = street_map.find_address(address, df)
            return lat, lon
        except street_map.AddressNotFoundError as e:
            print(e)
        except (EOFError, KeyboardInterrupt):
            return None, None
        except Exception as e:
            print(e)


def choose_cost() -> str:
    while True:
        try:
            mode = input(
                "Choose a route cost:\n"
                "1. Distance\n"
                "2. Estimated travel time\n"
                "3. Estimated travel time with junction delays\n"
                "9. Exit\n"
                "Option: "
            ).strip()
            if mode in {"1", "2", "3", "9"}:
                return mode
            else:
                raise ValueError(f"Invalid option: {mode}")
        except (EOFError, KeyboardInterrupt):
            return "9"
        except Exception as e:
            print(e)


# Speed units of the OpenStreetMap ``maxspeed`` tag, in km/h; no unit means km/h.
KMH_PER_UNIT = {"": 1.0, "km/h": 1.0, "kmh": 1.0, "kph": 1.0, "mph": 1.609344, "knots": 1.852}


def parse_speed(speed: Any) -> float | None:
    """Read a speed in km/h, taking the first value when given a list.

    A text value is read from its first number, with the unit written right after
    it: km/h (the default), mph or knots. A value with another unit, or without a
    number, gives None so that the road-type table applies instead of a guess.
    """
    if speed is None:
        return None
    if isinstance(speed, list):
        if not speed:
            return None
        speed = speed[0]
    if isinstance(speed, (int, float)):
        return float(speed)
    if isinstance(speed, str):
        m = re.search(r"(\d+(?:\.\d+)?)\s*([A-Za-z/]*)", speed)
        if m and m.group(2).lower() in KMH_PER_UNIT:
            return float(m.group(1)) * KMH_PER_UNIT[m.group(2).lower()]
    return None


def speed_from_data(data: dict) -> float:
    """Speed in km/h for an edge's attributes: the tag, the road-type table or 50."""
    speed_kmh = parse_speed(data.get("maxspeed"))
    if speed_kmh is not None:
        return speed_kmh
    road_type = data.get("highway")
    if isinstance(road_type, list):
        road_type = road_type[0] if road_type else None
    if road_type in street_map.MAX_SPEEDS:
        return float(street_map.MAX_SPEEDS[road_type])
    return 50.0


def travel_time_from_data(data: dict) -> float:
    """Estimate seconds at the speed limit, without congestion or acceleration."""
    distance = float(data.get("length", 0.0))
    speed_ms = speed_from_data(data) * 1000 / 3600
    if speed_ms <= 0:
        return float("inf")
    return distance / speed_ms


def edge_speed(G: nx.DiGraph, u: int, v: int) -> float:
    return speed_from_data(G[u][v])


def distance_cost(G: nx.DiGraph, u: int, v: int) -> float:
    """Return the edge length in metres; a missing length defaults to zero."""
    data = G[u][v]
    return float(data.get("length", 0.0))


def time_cost(G: nx.DiGraph, u: int, v: int) -> float:
    return edge_travel_time(G, u, v)


def junction_cost(G: nx.DiGraph, u: int, v: int) -> float:
    """Add the coursework's expected 24-second junction delay to each edge."""
    time = edge_travel_time(G, u, v)
    junction_delay = 0.8 * 30
    return time + junction_delay


def edge_travel_time(G: nx.DiGraph, u: int, v: int) -> float:
    """Estimate seconds at the speed limit, without congestion or acceleration."""
    return travel_time_from_data(G[u][v])


def street_name(G: nx.DiGraph, u: int, v: int) -> str:
    data = G[u][v]
    street_name = data.get("name")
    if isinstance(street_name, list):
        if street_name:
            street_name = street_name[0]
        else:
            street_name = None
    if not street_name:
        street_name = "Unnamed street"
    return str(street_name)


def describe_turn(
    G: nx.DiGraph, previous_node: int, current_node: int, next_node: int
) -> str:
    """Describe a turn from the cross product of consecutive coordinate vectors."""

    x_prev, y_prev = G.nodes[previous_node]["x"], G.nodes[previous_node]["y"]
    current_x, current_y = G.nodes[current_node]["x"], G.nodes[current_node]["y"]
    next_x, next_y = G.nodes[next_node]["x"], G.nodes[next_node]["y"]

    p1, p2 = (current_x - x_prev, current_y - y_prev)
    q1, q2 = (next_x - current_x, next_y - current_y)

    cross_product = q1 * p2 - q2 * p1
    tolerance = (
        1e-7  # Ignore small deviations caused by rounding or nearly straight roads.
    )

    if cross_product < -tolerance:
        return "Turn left"
    elif cross_product > tolerance:
        return "Turn right"
    else:
        return "Continue straight"


def navigation_instructions(G: nx.DiGraph, route_nodes: list[int] | None) -> list[str]:
    """Group consecutive edges on the same street into navigation instructions."""
    instructions = []
    if route_nodes is None or len(route_nodes) < 2:
        return instructions

    u = route_nodes[0]
    v = route_nodes[1]
    current_street = street_name(G, u, v)
    distance_travelled = float(G[u][v].get("length", 0.0))

    for i in range(1, len(route_nodes) - 1):
        u = route_nodes[i]
        v = route_nodes[i + 1]
        next_street = street_name(G, u, v)
        segment_length = float(G[u][v].get("length", 0.0))
        if next_street == current_street:
            distance_travelled += segment_length
        else:
            if current_street != "Unnamed street":
                instructions.append(
                    f"Continue along {current_street} for {distance_travelled:.0f} metres."
                )
            else:
                instructions.append(f"Continue for {distance_travelled:.0f} metres.")
            turn = describe_turn(
                G, route_nodes[i - 1], route_nodes[i], route_nodes[i + 1]
            )
            if next_street != "Unnamed street":
                instructions.append(f"{turn} onto {next_street}.")
            else:
                instructions.append(f"{turn}.")
            current_street = next_street
            distance_travelled = segment_length

    if current_street != "Unnamed street":
        instructions.append(
            f"Continue along {current_street} for {distance_travelled:.0f} metres to your destination."
        )
    else:
        instructions.append(
            f"Continue for {distance_travelled:.0f} metres to your destination."
        )

    return instructions


if __name__ == "__main__":
    addresses = street_map.load_addresses()
    G_multi = street_map.load_graph()
    # Distance keeps the shortest parallel edge; both time costs keep the fastest one
    # (the junction delay is the same constant on every edge).
    G_distance = street_map.simplify_graph(G_multi)
    G_time = street_map.simplify_graph(G_multi, travel_time_from_data)

    while True:
        origin_lat, origin_lon = prompt_address(addresses, "origin")
        if origin_lat is None or origin_lon is None:
            print("No origin entered. Exiting.")
            sys.exit(0)
        destination_lat, destination_lon = prompt_address(addresses, "destination")
        if destination_lat is None or destination_lon is None:
            print("No destination entered. Exiting.")
            sys.exit(0)

        origin_node = ox.nearest_nodes(G_distance, origin_lon, origin_lat)
        destination_node = ox.nearest_nodes(G_distance, destination_lon, destination_lat)

        mode = choose_cost()

        if mode == "9":
            print("Exiting.")
            sys.exit(0)
        elif mode == "1":
            G, cost = G_distance, distance_cost
        elif mode == "2":
            G, cost = G_time, time_cost
        elif mode == "3":
            G, cost = G_time, junction_cost
        else:
            sys.exit(1)
        route = gp.shortest_path(G, cost, origin_node, destination_node)

        instructions = navigation_instructions(G, route)
        print("\nNavigation instructions:")
        for inst in instructions:
            print(" ->", inst)
        street_map.draw_route(G, route)
