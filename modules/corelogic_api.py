import ast
import json
import time
from dataclasses import dataclass
from typing import Dict
import urllib
from urllib.parse import urlparse
from re import sub

import pandas as pd
import geopandas as gpd
import requests

from tqdm import trange
from bs4 import BeautifulSoup
import mechanize

import modules.http_methods


class Auth:
    @staticmethod
    def get_access_token(
            client_id: str,
            client_secret: str
            ):
        """
        Function to retrieve the token to access Corelogic APIs
        Returns the 'access_token' string
        """

        endpoint = 'https://api.corelogic.asia/access/oauth/'
        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
            }
        operation = 'token'

        response = modules.http_methods.Execute.post(
            endpoint=endpoint,
            operation=operation,
            params=params
            )

        if response is not None:
            contents = ast.literal_eval(str(response.json()))
            if 'error' in contents:
                print('Error: ' + str(contents['error']))
                return None

            if 'expires_in' in contents:
                print('Authentication OK')
                return contents['access_token']

            else:
                print('Authentication seems to have failed. Response: ' + str(contents))
                return None

        else:
            print('Error: Response is None. See http_methods.Execute error details')


class Query:
    @staticmethod
    def get_property_id(
            address: str,
            access_token: str):
        """
        Function to match an address string to a Corelogic Property ID
        Returns the Corelogic Property ID if successful, otherwise returns None
        """
        endpoint = 'https://api-uat.corelogic.asia/sandbox/search/au/matcher/'
        operation = 'address?q=' + str(urllib.parse.quote(address))
        # For some reason, Requests lib params doesn't work with the address query; instead put it in the operation...

        response = modules.http_methods.Execute.get(
            endpoint=endpoint,
            operation=operation,
            headers={"Authorization": 'Bearer ' + access_token}
            )

        if response is not None:
            contents = ast.literal_eval(str(response.json()))
            if 'matchDetails' in contents:
                match = contents['matchDetails']
                # print('Response OK, match type: ' + match['matchType'])

                if match['matchType'] == 'E' \
                        or match['matchType'] == 'A' \
                        or match['matchType'] == 'P' \
                        or match['matchType'] == 'F':
                    # print('Match Found')
                    return match['propertyId']

                else:
                    # print('Error: No Property Found')
                    return None
        else:
            print('Error: Response is None. See http_methods.Execute error details')

    @staticmethod
    def get_property_value_range(
            address: str,
            access_token: str
            ):

        property_id = Query.get_property_id(
            address=address,
            access_token=access_token
            )
        if property_id is None:
            return None, None

        formatted_address = urllib.parse.quote(address.replace(' ', '-').replace(',', ''))
        url = 'https://www.propertyvalue.com.au/property/' + formatted_address + '/' + str(property_id)

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.11 (KHTML, like Gecko) '
                          'Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
            }

        page = requests.get(url, headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        results = soup.find(id='propEstimatedPrice')
        if results == 'Estimate Unavailable' or results is None:
            return None, None
        else:
            valuation_range = results.text.split(' - ')
            if len(valuation_range) == 2:
                return int(sub(r'[^\d.]', '', (valuation_range[0]))), int(sub(r'[^\d.]', '', (valuation_range[1])))
            else:
                return None, None

    # def get_property_valuation_range(address, property_id, driver):
    #     """
    #     Function to retrieve the valuation range of a particular property from propertyvalue.com.au
    #     Returns a tuple of (low_bound, high_bound)
    #     """
    #     formatted_address = urllib.parse.quote(address.replace(' ', '-').replace(',', ''))
    #     url = 'https://www.propertyvalue.com.au/property/' + formatted_address + '/' + str(property_id)
    #
    #     # driver.get(url)
    #     page = requests.get(url)
    #     soup = BeautifulSoup(page.content, 'html.parser')
    #
    #     # try:
    #     #     element = driver.find_element_by_id('accept_cookies_modal')
    #     # except Exception as e:
    #     #     print('Cookies Model not Found')
    #
    #     # try:
    #     #     element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "accept_cookies_modal")))
    #     #     if element.is_displayed() and element.is_enabled():
    #     #         button = driver.find_element_by_id('acceptCookieButton')
    #     #         button.click()
    #     # except Exception as e:
    #     #     print(str(e))
    #
    #     try:
    #         # valuation_range = driver.find_element_by_id('propEstimatedPrice').text.split(' - ')
    #
    #         valuation_range = soup.find(id='propEstimatedPrice').text
    #         if valuation_range == 'Estimate Unavailable':
    #             return (None, None)
    #         else:
    #             return (sub(r'[^\d.]', '', (valuation_range[0])), sub(r'[^\d.]', '', (valuation_range[1])))
    #         # if len(valuation_range) != 2:
    #         #   print('Error. Could not parse valuation range: ' + str(valuation_range))
    #     except Exception as e:
    #         print(str(e))
