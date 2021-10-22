import requests
from typing import Dict
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class Execute:
    @staticmethod
    def post(
            endpoint: str,
            operation: str,
            params: Dict = None,
            headers: Dict = None):
        """
        Uses the requests library to send an HTTP POST request (in order to avoid server limits on url length),
        to a specified resource and endpoint. Retries 5 times on failure.

        :param endpoint: The location of the service
        :param operation: The operation to be performed (e.g. 'query?')
        :param params: Parameters to be passed to the operation
        :param headers: A dictionary of headers (incl. Authorization) to be passed along the request
        :return: The response
        """
        if endpoint[-1] != '/':
            url = endpoint + '/' + operation
        else:
            url = endpoint + operation

        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[502, 503, 504, 499],
            raise_on_redirect=True)
        session.mount('http://', HTTPAdapter(max_retries=retries))

        prepared = requests.Request(
            method='POST',
            url=url,
            headers=headers,
            params=params)

        try:
            response = session.post(
                url=url,
                data=params,
                headers=headers)
            if response.status_code == 200:
                return response
            else:
                print('HTTP POST error for url: ' + str(prepared.url) +
                      '. Params: ' + str(prepared.params) +
                      '. Response: ' + str(response.json()))
                return None

        except Exception as e:
            print(
                'HTTP POST error for url: ' + str(prepared.url) +
                '. Params: ' + str(prepared.params) +
                '. Exception: ' + str(e))
            return None

    @staticmethod
    def get(
            endpoint: str,
            operation: str,
            params: Dict = None,
            headers: Dict = None):
        """
        Uses the requests library to send an HTTP GET request (in order to avoid server limits on url length),
        to a specified resource and endpoint. Retries 5 times on failure.

        :param endpoint: The location of the service
        :param operation:
        :param params: Parameters to be passed to the operation
        :param headers: A dictionary of headers (incl. Authorization) to be passed along the request
        :return: The response
        """

        if endpoint[-1] != '/':
            url = endpoint + '/' + operation
        else:
            url = endpoint + operation

        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[502, 503, 504, 499],
            raise_on_redirect=True)
        session.mount('http://', HTTPAdapter(max_retries=retries))

        request = requests.Request(
            method='GET',
            url=url,
            headers=headers,
            params=params)
        prepared = request.prepare()

        response = session.send(request=prepared)
        if response.status_code == 200:
            return response
        else:
            print('HTTP GET error for url: ' + str(prepared.url) +
                  '. Response: ' + str(response.status_code) + ' ' + str(response))
            return response

        # except Exception as e:
        #     print(
        #         'HTTP GET error for url: ' + str(prepared.url) +
        #         'No status code. ' +
        #         '. Exception: ' + str(e))
        #     return response
