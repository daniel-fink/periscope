import ast
import json
import time
from dataclasses import dataclass
from typing import Dict

import pandas as pd
import geopandas as gpd
from shapely import geometry
from arcgis.geometry import BaseGeometry
from arcgis.geometry import Geometry
from arcgis2geojson import arcgis2geojson
from tqdm import trange

import http_methods
import geospatial


class Query:
    @dataclass
    class ObjectIds:
        object_id_field_name: str
        object_ids: [int]

    @staticmethod
    def get_object_ids(
            endpoint: str,
            params: Dict,
            headers: Dict = None
            ):
        """
        Function to retrieve ids of objects in an ArcGIS API query.
        Returns a dataclass with the object_id_field_name, and a list of  objects' ids.
        :param endpoint:
        :param params:
        :param headers:
        :return: Dataclass with the object_id_field_name, and a list of  objects' ids.
        """

        query_params = {
            'returnIdsOnly': 'true',
            'f': 'json',
            }
        object_ids_params = dict(params)
        object_ids_params.update(query_params)

        response = http_methods.Execute.post(
            endpoint=endpoint,
            operation='query?',
            params=object_ids_params,
            headers=headers
            )

        if response is not None:
            contents = ast.literal_eval(str(response.json()))
            if 'error' in contents:
                print('Error: ' + str(contents['error']))

            if 'objectIds' in contents:
                if contents['objectIds'] is None:
                    print('Error: No objects returned in response. Query: ' + str(response.request.body))
                    return None
                else:
                    return Query.ObjectIds(contents['objectIdFieldName'], contents['objectIds'])

            else:
                print('Request returned unknown response: ' + str(response.json()) + '. Query: ' + response.request.url)

        else:
            print('Error: Response is None. See http_methods.Execute error details')
            return None

    @staticmethod
    def get_contents_of_ids(
            ids: [int],
            id_field_name: str,
            endpoint: str,
            outfields: [str] = ['*'],
            headers: Dict = None
            ):
        """
        Function to retrieve contents of specific objects (features) in an ArcGIS API query, via the objects' ids.
        Returns a geopandas dataframe of the features and their geometries.
        :param ids:
        :param id_field_name:
        :param endpoint:
        :param outfields:
        :param headers:
        :return: Geopandas DataFrame of the features and their geometries.
        """

        ids = str(ids)
        ids = ids.replace('[', '(').replace(']', ')')

        params = {
            'outFields': outfields,
            'returnIdsOnly': 'false',
            'outSR': '4326',
            'f': 'json',
            }

        ids_params = {
            'where': str(id_field_name) + ' IN ' + ids
            }

        ids_contents_params = dict(params)
        ids_contents_params.update(ids_params)

        response = http_methods.Execute.post(
            endpoint=endpoint,
            operation='query',
            params=ids_contents_params,
            headers=headers
            )

        if response is not None:
            contents = ast.literal_eval(str(response.json()))
            if 'error' in contents:
                print('Error: ' + str(contents['error']))

            if 'features' in contents:
                if contents['features'] is None:
                    print('No objects returned from Query: ' + str(response.request.body))
                    return None
                else:
                    geojson = [arcgis2geojson(feature) for feature in contents['features']]
                    return geospatial.Convert.geojson_to_gdf(geojson)

            else:
                print('Request returned unknown response: ' + str(response.json()) +
                      '. Query: ' + str(response.request.body))

        else:
            print('Error: Response is None. See http_methods.Execute error details')
            return None

    @staticmethod
    def get_contents(
            endpoint: str,
            params: Dict,
            headers: Dict = None,
            chunk_size_override: int = None
            ):
        """
        Function to retrieve contents from an ArcGIS API query.
        Returns a geopandas dataframe of the features and their geometries.
        :param endpoint:
        :param params:
        :param headers:
        :param chunk_size_override:
        :return: Geopandas Dataframe of the features and their geometries.
        """

        object_ids = Query.get_object_ids(
            endpoint=endpoint,
            params=params,
            headers=headers
            )
        if object_ids is None:
            return None

        if chunk_size_override is None:
            metadata = Query.get_metadata(endpoint=endpoint, headers=headers)
            if metadata is None:
                print('Error: Resource cannot be found.')
                return None
            else:
                if "Query" not in metadata['capabilities']:
                    print('Error: Query operations not supported by service')
                    return None
                else:
                    chunk_size = metadata['maxRecordCount']
        else:
            chunk_size = chunk_size_override

        if len(object_ids.object_ids) < chunk_size:
            chunk_size = len(object_ids.object_ids)

        ids_chunked = [object_ids.object_ids[i:i + chunk_size] for i in
                       range(0, len(object_ids.object_ids), chunk_size)]

        out_fields = '*'
        if 'outFields' in params:
            out_fields = params['outFields']

        contents = []
        for i in trange(len(ids_chunked), desc='Request OK. Number of objects returned in response: ' +
                                               str(len(object_ids.object_ids)) + '. API Calls'):
            contents_of_ids = Query.get_contents_of_ids(
                ids=ids_chunked[i],
                id_field_name=object_ids.object_id_field_name,
                endpoint=endpoint,
                outfields=out_fields,
                headers=headers
                )
            contents.append(contents_of_ids)

        return geospatial.Convert.dfs_to_gdf(dfs=contents, crs=contents[0].crs)

    @staticmethod
    def get_metadata(
            endpoint: str,
            headers: Dict = None):
        """
        Function to retrieve the layer data (metadata),
        including its SRID/WKID, columns & their descriptions, etc
        :param endpoint:
        :param headers:
        :return: Dictionary with organization specified here: https://developers.arcgis.com/rest/services-reference/enterprise/layer-feature-service-.htm
        """

        metadata_operation = '?f=json'
        metadata_response = http_methods.Execute.post(
            endpoint=endpoint,
            operation=metadata_operation,
            headers=headers
            )
        if metadata_response is not None:
            metadata = ast.literal_eval(str(metadata_response.json()))
            if 'error' in metadata:
                print('Error: ' + str(metadata['error']))
                return None

            if 'capabilities' in metadata:
                return metadata

            else:
                print('Request returned unknown response: ' +
                      str(metadata_response.json()) +
                      '. Query: ' + str(metadata_response.request.body))

        else:
            print('Error: Response is None. See http_methods.Execute error details')
            return None

    @staticmethod
    def geometry_intersection_query_params(geometry, sr=4326):
        """
        Function to construct query parameters for intersection within a geometry.
        Returns a dictionary of query parameters for use in a request.
        """

        bounds = geometry.bounds
        geometry = str([str(vertex) for vertex in bounds])
        geometry_params = geometry.replace("'", "").replace('[', '').replace(']', '')
        params = {
            'geometryType': 'esriGeometryEnvelope',
            'geometry': geometry_params,
            'inSR': sr,
            'outSR': sr,
            'spatialRel': 'esriSpatialRelIntersects'
            }
        return params


class Extensions:
    @staticmethod
    def geometry_type_to_api_param(
            arcgis_geometry: BaseGeometry):
        return 'esriGeometry' + arcgis_geometry.geometry_type.capitalize()

    @classmethod
    def from_shapely(
            cls,
            shapely_geometry: geometry):
        return cls(shapely_geometry.__geo_interface__)

    BaseGeometry.from_shapely = from_shapely
