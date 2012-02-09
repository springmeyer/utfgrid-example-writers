from rtree import index
from rtree import Rtree
from fiona import collection
from shapely.geometry import mapping, shape
from shapely.wkt import loads
from ogr_renderer import Extent, Request, CoordTransform, Grid
import json

class Renderer:
    def __init__(self,grid,ctrans):
        self.grid = grid
        self.ctrans = ctrans
        self.req = ctrans.request

    def apply(self,ds_name,field_names=[]):
        p = index.Property()
        idx = index.Index(properties=p)

        with collection(ds_name, "r") as source:
            e = ctrans.extent
            for feat in source.filter(bbox=(e.minx, e.miny, e.maxx, e.maxy)):
                geom = shape(feat['geometry'])
                attrs = feat['properties']
                saved_attrs = {}
                for field, val in attrs.iteritems():
                    if field in field_names:
                        saved_attrs[field] = val
                idx.insert(int(feat['id']), geom.bounds, obj=(geom, saved_attrs)) 

        for y in xrange(0,self.req.height,self.grid.resolution):
            row = []
            for x in xrange(0,self.req.width,self.grid.resolution):
                found = False
                minx,maxy = self.ctrans.backward(x,y)
                maxx,miny = self.ctrans.backward(x+1,y+1)
                wkt = 'POINT(%f %f)' \
                   % (minx + (maxx - minx)/2, miny + (maxy - miny)/2)
                g = loads(wkt)
                candidates = list(idx.intersection((minx,miny,maxx,maxy), objects=True))
                for f in candidates:
                    geom, attrs = f.object

                    # See if the candidate geometry contains the center point of the cell 
                    # In the interest of speed, we grab the first hit 
                    if geom.contains(g):
                        row.append(f.id)
                        self.grid.feature_cache[f.id] = attrs
                        found = True

                if not found:
                    row.append("")

            self.grid.rows.append(row)

if __name__ == "__main__":

    box = Extent(-140,0,-50,90)
    tile = Request(256,256,box)
    ctrans = CoordTransform(tile)
    grid = Grid()
    renderer = Renderer(grid,ctrans)
    renderer.apply('data/ne_110m_admin_0_countries.shp',
            field_names=['NAME_FORMA', 'POP_EST'])
    utfgrid = grid.encode()
    print json.dumps(utfgrid)
