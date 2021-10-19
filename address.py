from typing import TypeVar, Union

from postal import parser
import pandas as pd
import geopandas as gpd

import arcgis_api


class Parse:
    @staticmethod
    def parse_address_components(address: str):
        components = dict(parser.parse_address(address))
        components = dict((v, k) for k, v in components.items())

        # if '/' in str(components['house_number']):
        #     unit_house = components['house_number'].split('/')
        #     components['unit_number'] = unit_house[0]
        #     components['house_number'] = unit_house[1]
        #
        # road_components = str(components['road']).rsplit(' ', 1)
        # if len(road_components) > 1:
        #     components['road_type'] = road_components[1]
        #     components['road'] = road_components[0]

        return {key: value.strip().upper() for key, value in components.items()}


class Query:
    PandasSeriesString = TypeVar('pandas.core.series.Series(str)')
    nsw_guras_endpoint = 'https://portal.spatial.nsw.gov.au/server/rest/services/NSW_Geocoded_Addressing_Theme/FeatureServer/3/'

    @staticmethod
    def from_nsw_propid(propid: str):
        params = {
            'where': 'propid = ' + propid,
            'outFields': '*'
            }
        return arcgis_api.Query.get_contents(
            endpoint=Query.nsw_guras_endpoint,
            params=params,
            )

    @staticmethod
    def from_nsw_propids(propids: PandasSeriesString):
        params = {
            'where': 'propid IN ' + str(propids.to_list()).replace("'", "").replace('[', '(').replace(']', ')'),
            'outFields': '*'
            }
        return arcgis_api.Query.get_contents(
            endpoint=Query.nsw_guras_endpoint,
            params=params,
            )
