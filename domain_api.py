import ast
import json
import time
from dataclasses import dataclass
from typing import Dict
import urllib
from urllib.parse import urlparse
from re import sub

import numpy as np
import pandas as pd
import geopandas as gpd
import requests

from tqdm import trange

import http_methods


class Query:
    @staticmethod
    def get_suburb_id(
            api_key: str,
            suburb: str,
            state: str
            ):
        """
        Function to retrieve the Suburb ID, for use in other queries.
        :param suburb:
        :param state:
        :return:
        """
        endpoint = 'https://api.domain.com.au/v1/'
        operation = 'addressLocators'
        params = {
            'searchLevel': 'Suburb',
            'suburb': suburb,
            'state': state
            }
        headers = {
            'X-API-Key': api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
            }

        response = http_methods.Execute.get(
            endpoint=endpoint,
            operation=operation,
            params=params,
            headers=headers
            )

        if response is not None:
            contents = ast.literal_eval(str(response.json()))[0]
            if 'ids' in contents:
                return contents['ids']['id']

    @staticmethod
    def get_address_id(
            api_key: str,
            street_number: str,
            street_name: str,
            street_type: str,
            suburb: str,
            state: str,
            postcode: str = None,
            unit_number: str = None,
            ):
        """
        Function to retrieve the Address ID, for use in other queries.
        :param postcode:
        :param street_number:
        :param street_name:
        :param street_type:
        :param suburb:
        :param state:
        :param unit_number: Optional
        :return: A dictionary with 'Address', 'Street', 'Suburb', and 'Postcode' IDs
        for the specified address.
        """

        endpoint = 'https://api.domain.com.au/v1/'
        operation = 'addressLocators'
        params = {
            'searchLevel': 'Address',
            'unitNumber': unit_number,
            'streetNumber': street_number,
            'streetName': street_name,
            'streetType': street_type,
            'suburb': suburb,
            'state': state,
            'postCode': postcode
            }
        headers = {
            'X-API-Key': api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
            }

        if (not params['unitNumber']) | (params['unitNumber'] is None) | (params['unitNumber'] == '<NA>'):
            del params['unitNumber']

        if (not params['postCode']) | (params['postCode'] is None) | (params['postCode'] == '<NA>'):
            del params['postCode']

        response = http_methods.Execute.get(
            endpoint=endpoint,
            operation=operation,
            params=params,
            headers=headers
            )

        if response is not None:
            contents = ast.literal_eval(str(response.json()))[0]
            if 'ids' in contents:
                ids = contents['ids']
                result = {
                    'domain_id_' + ids[0]['level']: ids[0]['id'],
                    'domain_id_' + ids[1]['level']: ids[1]['id'],
                    'domain_id_' + ids[2]['level']: ids[2]['id'],
                    'domain_id_' + ids[3]['level']: ids[3]['id']
                    }
                params.update(result)
                return {k.lower(): v for k, v in params.items()}
        else:
            return {k.lower(): v for k, v in params.items()}

    @staticmethod
    def get_property_id(
            api_key: str,
            address: str
            ):
        """
        :param address:
        :param api_key:
        :return:
        """
        endpoint = 'https://api.domain.com.au/v1/properties/'
        operation = '_suggest'
        params = {
            'terms': address,
            'pagesize': '1',
            'channel': 'All'
            }
        headers = {
            'X-API-Key': api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
            }

        response = http_methods.Execute.get(
            endpoint=endpoint,
            operation=operation,
            params=params,
            headers=headers
            )

        if response is not None:
            contents = ast.literal_eval(str(response.json()))[0]
            if 'relativeScore' in contents:
                result = contents['addressComponents']
                result['address'] = contents['address']
                result['domain_id'] = contents['id']

                address_ids = Query.get_address_id(
                    api_key=api_key,
                    unit_number=result['unitNumber'] if 'unitNumber' in result else None,
                    street_number=result['streetNumber'] if 'streetNumber' in result else None,
                    street_name=result['streetName'] if 'streetName' in result else None,
                    street_type=result['streetTypeLong'] if 'streetTypeLong' in result else None,
                    suburb=result['suburb'] if 'suburb' in result else None,
                    state=result['state'] if 'state' in result else None,
                    postcode=result['postCode'] if 'postCode' in result else None
                    )
                result.update(address_ids)
                return result
        else:
            return None

    @staticmethod
    def get_demographics(
            api_key: str,
            suburb: str,
            postcode: str,
            state: str
            ):
        """

        :param suburb:
        :param postcode:
        :param state:
        :return:
        """
        endpoint = 'https://api.domain.com.au/v2/demographics/' + state + '/' + suburb + '/' + postcode
        operation = ''
        params = {}
        headers = {
            'X-API-Key': api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
            }

        response = http_methods.Execute.get(
            endpoint=endpoint,
            operation=operation,
            params=params,
            headers=headers
            )

        if response is not None:
            contents = ast.literal_eval(str(response.json()))
            if 'demographics' in contents:
                demographics = contents['demographics']

                topics = []
                for topic in demographics:
                    table = pd.DataFrame(topic['items']).convert_dtypes()
                    table.name = topic['type']
                    table.year = topic['year']
                    topics.append(table)
                return topics
        else:
            return None

    @staticmethod
    def get_suburb_data(
            api_key: str,
            state: str,
            suburb_id: str
            ):
        """
        Function to retrieve market statistics about the suburb given.

        :param state:
        :param suburb_id:
        :return:
        """

        endpoint = 'https://api.domain.com.au/v1/locations/profiles/' + suburb_id
        operation = ''
        headers = {
            'X-API-Key': api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
            }
        params = {}

        response = http_methods.Execute.get(
            endpoint=endpoint,
            operation=operation,
            params=params,
            headers=headers
            )

        if response is not None:
            contents = ast.literal_eval(str(response.json()))
            if 'data' in contents:
                return contents['data']
        else:
            return None

    @staticmethod
    def get_property_data(
            api_key: str,
            property_id: str
            ):
        """

        :param property_id:
        :return:
        """
        endpoint = 'https://api.domain.com.au/v1/properties/' + property_id
        operation = ''
        params = {}
        headers = {
            'X-API-Key': api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
            }

        response = http_methods.Execute.get(
            endpoint=endpoint,
            operation=operation,
            params=params,
            headers=headers
            )

        if response is not None:
            contents = ast.literal_eval(str(response.json()))
            contents = {(key, str(value)) for key, value in contents.items()}
            row = pd.DataFrame(contents)
            return contents
        else:
            return None

    @staticmethod
    def get_suburb_performance(
            api_key: str,
            state: str,
            suburb_id: str
            ):
        """
        Function to retrieve market performance data about the suburb given.

        :param state:
        :param suburb_id:
        :return:
        """

        endpoint = 'https://api.domain.com.au/v1/'
        operation = 'suburbPerformanceStatistics'
        headers = {
            'X-API-Key': api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
            }
        params = {
            'state': state,
            'suburbId': suburb_id,
            'chronologicalSpan': 3,
            'tPlusFrom': 1,
            'tPlusTo': 999
            }

        property_categories = ['house', 'unit']
        number_bedrooms = [1, 2, 3, 4, 5]

        results = []
        for prop_category in property_categories:
            for bedroom_num in number_bedrooms:
                performance_categories = {
                    'propertyCategory': prop_category,
                    'bedrooms': bedroom_num
                    }
                params.update(performance_categories)

                response = http_methods.Execute.get(
                    endpoint=endpoint,
                    operation=operation,
                    params=params,
                    headers=headers
                    )

                if response is not None:
                    try:
                        contents = ast.literal_eval(str(response.json()))
                    except Exception as e:
                        print("Error: Cannot decode response JSON: " + str(e))
                    if 'series' in contents:
                        quarterly_data = contents['series']['seriesInfo']
                        for quarter in quarterly_data:
                            row = pd.DataFrame(quarter['values'], index=[0]).convert_dtypes()
                            row['year'] = quarter['year']
                            row['month'] = quarter['month']
                            row['property_category'] = performance_categories['propertyCategory']
                            row['num_bedrooms'] = performance_categories['bedrooms']
                            results.append(row)

        land_params = {'propertyCategory': 'land'}
        land_params.update(params)
        response = http_methods.Execute.get(
            endpoint=endpoint,
            operation=operation,
            params=land_params,
            headers=headers
            )
        if response is not None:
            try:
                contents = ast.literal_eval(str(response.json()))
            except Exception as e:
                print("Error: Cannot decode response JSON: " + str(e))
            if 'series' in contents:
                quarterly_data = contents['series']['seriesInfo']
                for quarter in quarterly_data:
                    row = pd.DataFrame(quarter['values'], index=[0]).convert_dtypes()
                    row['year'] = quarter['year']
                    row['month'] = quarter['month']
                    row['property_category'] = 'land'
                    row['num_bedrooms'] = np.nan
                    results.append(row)

        results = pd.concat(results)
        results = results.set_index(pd.PeriodIndex(pd.to_datetime(
            dict(year=results['year'], month=results['month'], day=1)),
            freq='Q'))
        # results = results.set_index(results['quarter']).drop(columns=['quarter'])
        return results
