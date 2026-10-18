# Discrete mathematics

Three two-person coursework projects from Discrete Mathematics on the iMAT degree at ICAI, Universidad Pontificia Comillas. They move from integer arithmetic to an application of RSA and a route planner for Madrid.

| Project | Main ideas |
| --- | --- |
| [Madrid route planner](madrid-route-planner/README.md) | Dijkstra, Prim and Kruskal; address lookup; distance and estimated travel-time costs. |
| [Modular arithmetic](modular-arithmetic/README.md) | Primes, Bézout identities, modular inverses, congruences and square roots, with a command-line calculator. |
| [RSA cryptography](rsa-cryptography/README.md) | Key generation, encoding, decimal padding and attacks on small teaching examples. |

## Getting started

Use Python 3.12. Each folder is self-contained, with its own README, example and tests. Run commands from the relevant project folder. Separate virtual environments keep the mapping dependencies apart from the standard-library arithmetic and RSA code.

The route planner is the most direct starting point: `demo.py` compares three routes on a small synthetic network and draws the result. A journey on Madrid's real network needs an external address CSV and an OpenStreetMap graph. Neither dataset is bundled.

## About the work

The team implemented the mathematical and graph algorithms using the coursework interfaces. The route planner uses NetworkX for graph containers and OSMnx for street-network access and nearest-node lookup. RSA reuses a local copy of the modular arithmetic library so it can run independently.

The code and command names are now in English. Course test cases have been adapted to those names and kept alongside regression tests. The original Spanish command interface is not supported by this version.

The projects include corrections made after submission. Their READMEs explain the relevant changes and limitations. RSA is a demonstration of the mathematics and weaknesses of textbook encryption; it must not be used to protect real data.
