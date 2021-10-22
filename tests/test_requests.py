import pandas as pd
import os

import corelogic_api
import http_methods
import arcgis_api
import domain_api

# import importlib
# importlib.import_module('request', __name__)
# Pytests file.
# Note: gathers tests according to a naming convention.
# By default any file that is to contain tests must be named starting with 'test_',
# classes that hold tests must be named starting with 'Test',
# and any function in a file that should be treated as a test must also start with 'test_'.

endpoint = 'https://portal.spatial.nsw.gov.au/server/rest/services/NSW_Administrative_Boundaries_Theme/FeatureServer/8'
object_ids = [63, 420, 608, 611, 634, 831, 1098, 1991, 1992, 2051]
object_ids_field_name = 'rid'
params = {
    'where': '1=1',
    'objectIds': str(object_ids).replace("'", "").replace('[', '').replace(']', '')
    }


class TestExecute:
    post_params = {
        'returnIdsOnly': 'true',
        'f': 'json',
        }
    request_params = dict(params)
    request_params.update(post_params)

    response = http_methods.Execute.post(
        endpoint=endpoint,
        operation='query?',
        params=request_params)

    def test_correct_response(self):
        assert str(
            TestExecute.response.json()) == "{'objectIdFieldName': 'rid', 'objectIds': [63, 420, 608, 611, 634, 831, 1098, 1991, 1992, 2051]}"


class TestArcGisAPI:
    response_metadata = arcgis_api.Query.get_metadata(
        endpoint=endpoint)

    def test_get_metadata(self):
        assert TestArcGisAPI.response_metadata['maxRecordCount'] == 250

    response_object_ids = arcgis_api.Query.get_object_ids(
        endpoint=endpoint,
        params=params)

    def test_get_object_ids(self):
        assert TestArcGisAPI.response_object_ids.object_ids == object_ids
        assert TestArcGisAPI.response_object_ids.object_id_field_name == object_ids_field_name

    response_contents_of_ids = arcgis_api.Query.get_contents_of_ids(
        endpoint=endpoint,
        ids=response_object_ids.object_ids[:10],
        id_field_name=response_object_ids.object_id_field_name)

    # def test_get_contents_of_ids(self):
    #     print(TestArcGisAPI.response_contents_of_ids['cadid'].to_markdown())
    #     assert TestArcGisAPI.response_contents_of_ids['cadid'].equals(pd.Series(
    #         data=[108012460, 108012388, 173919536, 173953134, 108012499, 173953566,
    #               108012403, 108012380, 108012474, 108012548]))


class TestCorelogicAPI:
    response_access_token = corelogic_api.Auth.get_access_token(
        client_id=os.environ['CORELOGIC_CLIENT_ID'],
        client_secret=os.environ['CORELOGIC_CLIENT_SECRET'])

    def test_get_access_token(self):
        assert TestCorelogicAPI.response_access_token is not None

    response_property_id = corelogic_api.Query.get_property_id(
        address="63 Boronia Rd Bellevue Hill NSW 2023",
        access_token=response_access_token)

    def test_get_property_id(self):
        assert TestCorelogicAPI.response_property_id == 1368488

    property_value_range = corelogic_api.Query.get_property_value_range(
        address="63 Boronia Rd Bellevue Hill NSW 2023",
        access_token=response_access_token)

    def test_get_property_valuerange(self):
        print(TestCorelogicAPI.property_value_range)


class TestDomainAPI:
    def test_get_property_id(self):
        id = domain_api.Query.get_property_id(api_key=os.environ['DOMAIN_API_KEY'],
                                              address='63 Boronia Rd Bellevue Hill NSW 2023')
        assert id['domain_id'] == 'ZE-8704-SB'
        assert id['domain_id_address'] == 4954725
