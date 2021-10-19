import ast
import json
import time
from dataclasses import dataclass
from typing import Dict

import pandas as pd
import geopandas as gpd
import sodapy
from tqdm import trange

from modules import http_methods


class Query:
    @staticmethod
    def get_contents_from_keys(client, resource, keys, chunk_size, content_type):
        """
        Function to retrieve contents from a Socrata API by querying for matches against keys.
        Chunks keys list into digestible API calls of size chunk_size.
        Specify 'json' or 'geojson' for content_type.
        Returns a pandas dataframe of the features
        """
        chunks = [keys[i * chunk_size:(i + 1) * chunk_size] for i in range((len(keys) + chunk_size - 1) // chunk_size)]
        #display('Number of API calls: ' + str(len(chunks)))

        dataframes = []

        for i in trange(len(chunks), desc='API Calls: '):
            query = str(chunks[i]).replace('[', '(').replace(']', ')')
            query = 'AIN IN ' + query

            if content_type == 'geojson':
                try:
                    geojson = client.get(resource, content_type="geojson", limit=500000, where=query)
                    gdf = gpd.GeoDataFrame.from_features(geojson["features"], crs=4326)
                    dataframes.append(gdf)
                except Exception as e:
                    print('Exception on query: ' + query + '. Error:' + str(e))
            if content_type == 'json':
                try:
                    json = client.get(resource, content_type="json", limit=500000, where=query)
                    df = pd.read_json(str(json))
                    dataframes.append(df)
                except Exception as e:
                    print('Exception on query: ' + query + '. Error:' + str(e))

        dataframe = pd.concat(dataframes)
        return dataframe
