# UTFGrid Example Writers

Sample implementations for writing UTFGrids.

For details on the UTFGrid spec see:

https://github.com/mapbox/utfgrid-spec


## Background

These examples are designed to be simple and with few dependencies.

Currently the only production-ready write implementation for UTFGrids is found inside Mapnik's
[grid_renderer](https://github.com/mapnik/mapnik/tree/master/include/mapnik/grid) which
which uses AGG rendering to quickly render a feature hit grid in a single pass over geometries.
Mapnik's [python](https://github.com/mapnik/mapnik/blob/master/bindings/python/python_grid_utils.hpp)
or [node.js](https://github.com/mapnik/node-mapnik/blob/master/src/js_grid_utils.hpp)
bindings can then be used to encode to UTFGrid format as JSON objects.

Because this Mapnik implementation is complex, and written in C++, simpler examples are needed
that prioritize simplicity and ease of understanding over rendering speed.


## Reference Implementations

1) ogr_renderer.py

This uses the [OGR library](http://www.gdal.org/ogr) and its python bindings to query
a polygon shapefile, build a pixel buffer of feature ids, and then encode those
ids in UTFGrid format.


2) TODO: shapely/fiona/libspatialindex implementation


3) TODO: gdal_rasterize implemenation