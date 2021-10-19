import ast

import arcgis
import geopandas as gpd


# import importlib
# importlib.import_module('request', __name__)
# Pytests file.
# Note: gathers tests according to a naming convention.
# By default any file that is to contain tests must be named starting with 'test_',
# classes that hold tests must be named starting with 'Test',
# and any function in a file that should be treated as a test must also start with 'test_'.

class TestConversion:
    geojson = '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[102,0.5]},"properties":{"prop0":"value0"}},{"type":"Feature","geometry":{"type":"LineString","coordinates":[[102,0],[103,1],[104,0],[105,1]]},"properties":{"propA":"valueA","prop1":0}},{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[100,0],[101,0],[101,1],[100,1],[100,0]]]},"properties":{"propB":"valueB","prop2":{"this":{"that":"other"}}}}]}'
    simple_features = ast.literal_eval(str(geojson))
    gdf = gpd.GeoDataFrame.from_features(simple_features['features'], crs=4326)

    point = gdf['geometry'][0]
    linestring = gdf['geometry'][1]
    polygon = gdf['geometry'][2]

    arc_point = arcgis.geometry.Geometry.from_shapely(shapely_geometry=point, spatial_reference={'wkid' : 4326})
    arc_linestring = arcgis.geometry.Geometry.from_shapely(shapely_geometry=linestring, spatial_reference={'wkid': 4326})
    arc_polygon = arcgis.geometry.Geometry.from_shapely(shapely_geometry=polygon, spatial_reference={'wkid': 4326})


# class TestArcGISAPI:
#
#     print(point.x)
#     def test_conversion(self):



