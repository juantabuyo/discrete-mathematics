# Historical Madrid street-network data

`madrid-driving-2024-11-25.graphml.gz` contains an unchanged, compressed GraphML cache
of Madrid's driving network. The graph records its creation as
25 November 2024, using OSMnx 1.9.4. It is a historical network, not a current
download. It contains 31,003 nodes and 61,149 directed edges in EPSG:4326.

**© OpenStreetMap contributors.** The map data is available under the
[Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
See [OpenStreetMap's copyright and attribution information](https://www.openstreetmap.org/copyright).

The cache was published in
[berasteguip/GPS_Discreta_P3](https://github.com/berasteguip/GPS_Discreta_P3/blob/74b19f087d879ee7a5f7b1cf41b87b5235da11f4/madrid.graphml),
at commit `74b19f087d879ee7a5f7b1cf41b87b5235da11f4`.
The repository's loader uses OSMnx's `graph_from_place("Madrid, Spain", network_type="drive")`.
Only the map data is used here; the routing implementation belongs to this
project, and no code from that repository is included.

After decompression, the file is exactly 29,706,105 bytes:

```text
SHA-256: da7889c8da72b22a14c25e4e09ce45bfd075b4c7b6d81569fd790713754b906c
Git blob SHA-1: 472e703209132f6824dc1607447ec009b596003a
```

The pinned source file is available from
[raw.githubusercontent.com](https://raw.githubusercontent.com/berasteguip/GPS_Discreta_P3/74b19f087d879ee7a5f7b1cf41b87b5235da11f4/madrid.graphml).
When creating a figure from it, retain the OSM attribution and identify the
network as historical. Routes calculated from coordinates do not by
themselves check the separate municipal address CSV.

This notice applies to these external map data. It does not assign a general
licence to the project or to third-party teaching materials.

## Reproduce the figures offline

After installing the project requirements, run from its folder:

```bash
python scripts/render_cached_madrid.py --output-dir output/madrid-cached
```

Choose a new output directory on another run. The helper checks the decoded
file size and SHA-256 before OSMnx reads it. It calls this project's
`simplify_graph`, `distance_cost`, `shortest_path` and `draw_route`; it does not
implement another routing algorithm or contact a map service.

The example was checked with Python 3.12.14 and, separately, Python 3.12.2 on
macOS, both using OSMnx 1.9.3. The archive was created with OSMnx 1.9.4; loading
it in 1.9.3 was verified. No original dataset or saved result has been replaced.
The gzip is a pinned map dataset, not a generated HTTP cache.
