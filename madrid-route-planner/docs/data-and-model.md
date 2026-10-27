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
| `LATITUD`, `LONGITUD` | Degrees, minutes and seconds, such as `40°25'30''N`; minutes and seconds must be below 60, latitude at most 90° and longitude at most 180° (otherwise loading the directory raises `ValueError`) |

The council's [downloads page](https://datos.madrid.es/dataset/213605-0-callejero-oficial-madrid/downloads)
separates the current-address directory from street-name and historical resources,
and links to resource pages with a data dictionary listing the released fields. The required
columns are listed above. The downloaded release must match the loader's
encoding and coordinate format. The current-address CSV retrieved on 23 October
2026 was loaded through the unchanged `load_addresses()` function: 214,676
rows loaded, and `find_address("Calle Mayor, 1", directory)` returned
`(40.4164694, -3.7046556)`. This verifies loading and that lookup, not every
individual address or a complete route. A conversion to a different upstream
format is not performed automatically.

Address matching ignores case and repeated whitespace, but not accents. Use the
name as stored in `VIA_NOMBRE`, including its street type and particle. Multiple
records for the same street and number resolve to the first row. Letters or
other suffixes on house numbers are not supported.

The [resource page](https://datos.madrid.es/dataset/213605-0-callejero-oficial-madrid/resource/213605-4-callejero-oficial-madrid-csv)
lists CC BY 4.0. Retain attribution to **Ayuntamiento de Madrid** and follow its
[reuse conditions](https://datos.madrid.es/pages/condiciones-de-uso) if you share
the data or derived material. No council data is distributed in this project.

## Bundled historical street graph

`data/madrid-driving-2024-11-25.graphml.gz` contains an unchanged compressed
OSMnx GraphML archive of Madrid's driving network. Its creation metadata says
25 November 2024 and OSMnx 1.9.4. Loading this archive with the project's OSMnx
1.9.3 was checked. The data source, exact checksum and ODbL attribution are in
[data/README.md](../data/README.md).

```bash
python scripts/render_cached_madrid.py --output-dir output/madrid-cached
```

The helper bounds decompression at 40 MiB and requires the documented decoded
size and SHA-256 before parsing. It calls the existing project implementation;
only view extent, labels and plotting styles are adjusted for the figures.
There is no network request. The archive is data, not an implementation copied
from its source repository.

The coordinate route from the Sol area to the Atocha area contains 25 edges and
has a stored-length cost of 1,805.254 m. The requested endpoints snap roughly
101 m and 77 m to nearby street nodes; those connections are not added to the
route cost. The original renderer draws straight segments between graph nodes,
so it is a graph illustration rather than an exact road-geometry basemap.
The images do not establish current vehicle access or validate the address CSV.

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
licence information. The four-node demo is entirely synthetic and contains no
OpenStreetMap data. The separately attributed historical graph does contain
real OSM data, and is not a substitute for checking current street conditions. `scripts/make_madrid_figure.py` uses the existing loader,
Dijkstra implementation and route renderer to produce an attributed map from
a compatible graph. It reads explicit coordinates and does not load the address
CSV; its inputs must therefore be checked separately from the interactive interface.

## Cost assumptions

Distances use edge `length` in metres. Missing lengths default to zero, so an
incomplete graph can produce misleading routes. Speeds are interpreted as km/h;
the first list entry or first number of a text value is used, and a unit written
right after it is honoured: `km/h`, `kmh`, `kph`, `mph` (×1.609344) or `knots`
(×1.852). A text value with another unit is not guessed: it is treated as missing.
Conditional speed limits are not interpreted. Missing speeds use the coursework
road-type table, then a 50 km/h fallback; these are modelling assumptions, not a
current legal speed-limit reference.

The graph conversion removes self-loops and keeps one edge for each ordered pair of
nodes: the shortest for the distance cost (`simplify_graph(multigraph)`) and the
fastest for the two time costs (`simplify_graph(multigraph, travel_time_from_data)`),
so a longer but faster parallel road is no longer discarded when minimising time.
Each cost is searched on the graph reduced for it. In the archived 2024 graph 277
node pairs have parallel edges and four edges of the time graph differ from the
distance graph, so the effect there is small; it was checked on invented networks.
The junction model adds `0.8 × 30 = 24`
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
