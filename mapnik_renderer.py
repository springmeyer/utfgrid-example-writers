#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mapnik

try:
    import json
except ImportError:
    import simplejson as json

if __name__ == "__main__":

    m = mapnik.Map(256,256)
    mapnik.load_map(m,'stylesheet.xml')
    box = mapnik.Box2d(-140,0,-50,90)
    m.zoom_to_box(box)
    grid = mapnik.Grid(m.width,m.height)
    mapnik.render_layer(m,grid,layer=0,fields=['NAME_FORMA','POP_EST'])
    utfgrid = grid.encode('utf',resolution=4)
    print json.dumps(utfgrid)