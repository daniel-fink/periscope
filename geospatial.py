from typing import Union

import pandas as pd
import geopandas as gpd


class Convert:
    @staticmethod
    def geojson_to_gdf(geojson: Union[str, list[str]]):
        """
        Function to convert a GeoJSON string to a GeoPandas GeoDataFrame,
        with some checks to make sure column types are accurate
        :param geojson: GeoJSON string
        :return: GeoPandas GeoDataFrame
        """
        gdf = gpd.GeoDataFrame.from_features(geojson, crs="EPSG:4326")
        df = gdf.convert_dtypes()
        gdf = gpd.GeoDataFrame(data=df.drop(columns=['geometry']), geometry=df['geometry'], crs="EPSG:4326")
        return gdf

    @staticmethod
    def dfs_to_gdf(dfs: list[pd.DataFrame], crs: str):
        """
        Function to convert a set of pandas DataFrames (with 'geometry' columns)
        to a singular GeoPandas GeoDataFrame,
        with some checks to make sure column types are accurate
        :param dfs: list of pandas DataFrames
        :param crs: the SRID in format accepted by :meth:`pyproj.CRS.from_user_input()`, e.g.: "EPSG:4326", or a WKT string.
        :return: GeoPandas GeoDataFrame
        """
        df = pd.concat(dfs, ignore_index=True)
        df = df.convert_dtypes()
        gdf = gpd.GeoDataFrame(data=df.drop(columns=['geometry']), geometry=df['geometry'], crs="EPSG:4326")
        return gdf
