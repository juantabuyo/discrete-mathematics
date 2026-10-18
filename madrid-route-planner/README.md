# Madrid route planner

We built this route planner as a two-person Discrete Mathematics project. It looks up Madrid addresses, maps them to a street graph and uses our Dijkstra implementation to find a route. The graph module also implements Prim and Kruskal for minimum spanning forests.

NetworkX provides graph containers. OSMnx downloads and converts street networks and locates the nearest nodes. The shortest-path and spanning-tree algorithms are in [weighted_graph.py](weighted_graph.py).

## Install and run

Use Python 3.12. Run these commands from this folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python demo.py
```

On Windows, activate with `.venv\Scripts\activate`. The demo uses four invented nodes and artificial road lengths and speeds. It runs the routing and OSMnx functions without downloaded data, then saves `output/demo-route.png`. Re-running it replaces that image.

| Cost | Route | Total |
| --- | --- | --- |
| Distance | `0 → 1 → 3` | 200 metres |
| Estimated travel time | `0 → 2 → 3` | 19.2 seconds |
| Estimated time with junction delays | `0 → 3` | 46.5 seconds |

These are synthetic examples, not measured journeys.

For the interactive Madrid programme, obtain the CSV described in [Data and model notes](docs/data-and-model.md), save it as `addresses.csv`, then run:

```bash
python route_planner.py
```

It loads `madrid.graphml` if available; otherwise it downloads Madrid's driving network through OSMnx and caches it. Enter an address such as `Calle Mayor, 1`, matching the directory. A blank address exits.

## Tests

```bash
python -m unittest discover -s tests -v
python graph_example.py
```

Tests compare paths and spanning forests with NetworkX and cover disconnected graphs, mixed node labels, large integer weights, addresses and navigation instructions. Local integration tests exercise OSMnx conversion, nearest-node lookup, GraphML and Matplotlib on synthetic data. `graph_example.py` is a separate, seeded demonstration.

## Limitations

Travel time assumes speed-limit travel. The third cost adds the assignment's expected 24 seconds per edge; it does not use live traffic. Parallel roads are reduced to the shortest edge before all searches, so time-based routes are optimal only within that reduced graph. Turn instructions use approximate coordinate geometry.

The full Madrid CSV and a city-wide journey have not been tested here. The data notes describe the expected format, sources and model assumptions.

The project follows the coursework algorithms. Post-submission fixes cover unreachable destinations, short routes, address particles, terminal exit and the infinity sentinel used for large weights. Code and interfaces are now in English.
