# Discrete mathematics: number theory, RSA and routing

Three two-person coursework projects from Discrete Mathematics on the iMAT degree at ICAI, Universidad Pontificia Comillas. They move from integer arithmetic to an application of RSA and a route planner for Madrid.

| Project | Main ideas |
| --- | --- |
| [Madrid route planner](madrid-route-planner/README.md) | Dijkstra, Prim and Kruskal; address lookup; distance and estimated travel-time costs. |
| [Modular arithmetic](modular-arithmetic/README.md) | Primes, Bézout identities, modular inverses, non-coprime congruences and square roots, with a command-line calculator. |
| [RSA cryptography](rsa-cryptography/README.md) | Key generation, Unicode encoding, decimal padding and attacks on small teaching examples. |

## Getting started

Checked with Python 3.12.2 on macOS and Python 3.12.14. Each folder is self-contained, with its own README, example and tests. Run commands from the relevant project folder and use a separate virtual environment for each project.

- The calculator and RSA example need only the Python standard library; pytest is a development dependency.
- Madrid routing uses a driving graph from OpenStreetMap. The [route planner instructions](madrid-route-planner/README.md) cover a route from coordinates and the separate address-CSV interface.
- A small synthetic routing example is available to explore the three costs without a map download. It is a teaching graph, not Madrid's street network.

The Madrid project bundles a verified historical OpenStreetMap graph from
25 November 2024. Its own Dijkstra implementation produces an attributed
network overview and a Sol–Atocha route close-up without a network request.
These figures use coordinates, not the address CSV, and do not represent
current driving conditions.

## About the work

The team implemented the mathematical and graph algorithms using the coursework interfaces. The route planner uses NetworkX for graph containers and OSMnx for street-network access and nearest-node lookup. RSA reuses a local copy of the modular arithmetic library so it can run independently.

The code and command names are now in English. Course test cases have been adapted to those names and kept alongside regression tests. The original Spanish command interface is not supported by this version.

The projects include corrections made after submission. Their READMEs explain the relevant changes and limitations. RSA is a demonstration of the mathematics and weaknesses of textbook encryption; it must not be used to protect real data.
