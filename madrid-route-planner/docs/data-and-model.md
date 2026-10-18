# Data and model notes

## Madrid address directory

Download **Callejero vigente. Relación de direcciones vigentes, con coordenadas**
from the [Madrid City Council dataset](https://datos.madrid.es/dataset/213605-0-callejero-oficial-madrid/downloads).
Use the current-address resource, not the street-name list or historical file.
Save the CSV as `addresses.csv` beside `route_planner.py` and run the programme from that
folder.

The loader expects a semicolon-separated file in ISO-8859-1 with these original
column names:

| Column | Use |
| --- | --- |
| `VIA_CLASE` | Street type, such as `CALLE` |
| `VIA_PAR` | Optional particle, such as `DE` or `DE LA` |
| `VIA_NOMBRE` | Street name |
| `NUMERO` | Integer street number |
| `LATITUD`, `LONGITUD` | Degrees, minutes and seconds, such as `40°25'30''N` |

The council's [field description](https://datos.madrid.es/FWProjects/egob/Catalogo/UrbanismoInfraestructura/Ficheros/Callejero%20oficial%20-%20descripci%C3%B3n%20de%20ficheros.pdf)
documents the address schema. The downloaded release must match the loader's
encoding and coordinate format; the current full download has not been tested
here. Check a few rows before a city-wide run. A conversion to a different
upstream format is not performed automatically.

Address matching ignores case and repeated whitespace, but not accents. Use the
name as stored in `VIA_NOMBRE`, including its street type and particle. Multiple
records for the same street and number resolve to the first row. Letters or
other suffixes on house numbers are not supported.

The [resource page](https://datos.madrid.es/dataset/213605-0-callejero-oficial-madrid/resource/213605-4-callejero-oficial-madrid-csv)
lists CC BY 4.0. Retain attribution to **Ayuntamiento de Madrid** and follow its
[reuse conditions](https://datos.madrid.es/pages/condiciones-de-uso) if you share
the data or derived material. No council data is distributed in this project.

## Street network

With no local `madrid.graphml`, `load_graph()` calls
`osmnx.graph_from_place("Madrid, Spain", network_type="drive")` and saves the
result using OSMnx's GraphML writer. This requires access to the geocoding and
Overpass services used by OSMnx. A city-wide download can be slow and may fail
because of service availability or rate limits. A later run uses the saved graph.

A compatible GraphML cache created with OSMnx can also be placed beside
`route_planner.py`. A corrupt cache is not silently replaced. Rename or remove it only if
you intend to make a fresh download. The project uses **OSMnx 1.9.3** and
**NetworkX 3.3**, as specified in `requirements.txt`.

Street-network data comes from **© OpenStreetMap contributors**, under the
[Open Database Licence](https://www.openstreetmap.org/copyright). If you export
maps or distribute a downloaded graph, include the required attribution and
licence information. The included demo is entirely synthetic and contains no
OpenStreetMap data.

## Cost assumptions

Distances use edge `length` in metres. Missing lengths default to zero, so an
incomplete graph can produce misleading routes. Speeds are interpreted as km/h;
the first list entry or first numeric part of a text value is used. This parser
does not interpret conditional speed limits or convert mph. Missing speeds use
the coursework road-type table, then a 50 km/h fallback; these are modelling
assumptions, not a current legal speed-limit reference.

The graph conversion keeps the shortest parallel edge and removes self-loops.
All searches use this same reduced graph. The junction model adds `0.8 × 30 = 24`
seconds to every traversed edge, regardless of actual signal locations. It does
not model congestion, turns, vehicle restrictions or changing traffic. Dijkstra
requires non-negative costs; Prim and Kruskal are for undirected graphs. An
unreachable destination returns an empty route.

## References

The academic report cited the following methods and tools:

- Dijkstra, E. W. (1959), *A Note on Two Problems in Connexion with Graphs*.
- Boeing, G. (2017), *OSMnx: New Methods for Acquiring, Constructing, Analyzing,
  and Visualizing Complex Street Networks*; [OSMnx](https://osmnx.readthedocs.io/).
- Hagberg, A., Schult, D. and Swart, P., [NetworkX](https://networkx.org/).
- Hunter, J. D. (2007), *Matplotlib: A 2D Graphics Environment*;
  [Matplotlib](https://matplotlib.org/).
- Pedregosa et al. (2011), *Scikit-learn: Machine Learning in Python*;
  [scikit-learn](https://scikit-learn.org/).
- McKinney, W. (2010), *Data Structures for Statistical Computing in Python*;
  [pandas](https://pandas.pydata.org/).
- Friedl, J. (2006), *Mastering Regular Expressions*, third edition.
- Snyder, J. P. (1987), *Map Projections — A Working Manual*.
- Van Rossum, G. and Drake Jr, F. L., *The Python Language Reference*;
  [Python](https://docs.python.org/3/reference/).

The graph algorithms and routing logic are the team's implementation; the
libraries supply data access, graph containers, nearest-node lookup, tables and
plotting.
