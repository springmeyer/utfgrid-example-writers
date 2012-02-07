#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ogr

try:
    import json
except ImportError:
    import simplejson as json

class Extent:
    def __init__(self,minx,miny,maxx,maxy):
        self.minx = float(minx)
        self.miny = float(miny)
        self.maxx = float(maxx)
        self.maxy = float(maxy)

    def width(self):
        return self.maxx - self.minx

    def height(self):
        return self.maxy - self.miny

    def __repr__(self):
        return 'Extent(%s,%s,%s,%s)' % (self.minx,self.miny,self.maxx,self.maxy)


class Request:
    def __init__(self,width,height,extent):
        assert isinstance(extent,Extent)
        assert isinstance(width,int)
        assert isinstance(height,int)
        self.width = width
        self.height = height
        self.extent = extent


class CoordTransform:
    def __init__(self,request,offset_x=0.0,offset_y=0.0):
        assert isinstance(request,Request)
        assert isinstance(offset_x,float)
        assert isinstance(offset_y,float)
        self.request = request
        self.extent = request.extent
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.sx = (float(request.width) / self.extent.width())
        self.sy = (float(request.height) / self.extent.height())

    def forward(self,x,y):
        """Lon/Lat to pixmap"""
        x0 = (x - self.extent.minx) * self.sx - self.offset_x
        y0 = (self.extent.maxy - y) * self.sy - self.offset_y
        return x0,y0

    def backward(self,x,y):
        """Pixmap to Lon/Lat"""
        x0 = self.extent.minx + (x + self.offset_x) / self.sx
        y0 = self.extent.maxy - (y + self.offset_y) / self.sy
        return x0,y0

class Grid:
    def __init__(self,resolution=4):
        self.rows = []
        self.feature_cache = {}
        self.resolution = resolution

    def width(self):
        return len(self.rows)

    def height(self):
        return len(self.rows)
    
    def encode(self):
        keys = {}
        key_order = []
        data = {}
        utf_rows = []
        codepoint = 31
        for y in xrange(0,self.height()):
            row_utf = u''
            row = self.rows[y]
            for x in xrange(0,self.width()):
                feature_id = row[x]
                if feature_id in keys:
                    row_utf += unichr(keys[feature_id])
                else:
                    # Create a new entry for this key. Skip the codepoints that
                    # cannot be encoded directly in JSON.
                    codepoint += 1
                    if codepoint == 34:
                        codepoint += 1 # skip "
                    elif codepoint == 92:
                        codepoint += 1 # Skip backslash
                    keys[feature_id] = codepoint
                    key_order.append(feature_id)
                    if self.feature_cache.get(feature_id):
                        data[feature_id] = self.feature_cache[feature_id]
                    row_utf += unichr(codepoint)
            utf_rows.append(row_utf)

        utf = {}
        utf['grid'] = utf_rows
        utf['keys'] = key_order
        utf['data'] = data
        return utf

class Renderer:
    def __init__(self,grid,ctrans):
        self.grid = grid
        self.ctrans = ctrans
        self.req = ctrans.request

    def apply(self,layer,fields=[]):
        for y in xrange(0,self.req.height+1,self.grid.resolution):
            row = []
            for x in xrange(0,self.req.width+1,self.grid.resolution):
                lon,lat = self.ctrans.backward(x,y)
                wkt = 'POINT(%s %s)' % (lon,lat)
                g = ogr.CreateGeometryFromWkt(wkt)
                #wkt = 'POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))' \
                #   % (minx, miny, minx, maxy, maxx, maxy, maxx, miny, minx, miny)
                #g = ogr.CreateGeometryFromWkt(wkt)
                layer.SetSpatialFilter(g)
                found = False
                if layer.GetFeatureCount() > 0:
                    feat = layer.GetNextFeature()
                    if feat is not None:
                        geom = feat.GetGeometryRef()
                        if geom.Contains(g):
                            feature_id = feat.GetFID()
                            row.append(feature_id)
                            attr = {}
                            for x in xrange(0,feat.GetFieldCount()):
                                field_def = feat.GetFieldDefnRef(x)
                                if field_def.GetName() in fields:
                                    field_type = field_def.GetTypeName()
                                    if field_type == "Integer":
                                        attr[field_def.GetName()] = feat.GetFieldAsInteger(x)
                                    elif field_type == "Real":
                                        attr[field_def.GetName()] = feat.GetFieldAsDouble(x)
                                    else:
                                        attr[field_def.GetName()] = feat.GetFieldAsString(x)
                            self.grid.feature_cache[feature_id] = attr
                            found = True
                if not found:
                    row.append("")
            self.grid.rows.append(row)
            #layer.SetSpatialFilter(None)
            #layer.ResetReading()

def resolve(grid,row,col):
    """ Resolve the attributes for a given pixel in a grid.
    """
    row = grid['grid'][row]
    utf_val = row[col]
    codepoint = ord(utf_val)
    if (codepoint >= 93):
        codepoint-=1
    if (codepoint >= 35):
        codepoint-=1
    codepoint -= 32
    key = grid['keys'][codepoint]
    return grid['data'].get(key)
    
    
if __name__ == "__main__":

    ds = ogr.Open('data/ne_110m_admin_0_countries.shp')
    layer = ds.GetLayer(0)
    box = Extent(-180,-180,180,180)
    tile = Request(256,256,box)
    ctrans = CoordTransform(tile)
    grid = Grid()
    renderer = Renderer(grid,ctrans)
    renderer.apply(layer,fields=['NAME_FORMA'])
    utfgrid = grid.encode()
    assert resolve(utfgrid,26,12) == {'NAME_FORMA': 'United States of America'}
    print json.dumps(utfgrid)