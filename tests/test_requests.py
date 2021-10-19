import pytest
import pandas as pd
from modules import http_methods, arcgis_api, corelogic_api

# import importlib
# importlib.import_module('modules.request', __name__)
# Pytests file.
# Note: gathers tests according to a naming convention.
# By default any file that is to contain tests must be named starting with 'test_',
# classes that hold tests must be named starting with 'Test',
# and any function in a file that should be treated as a test must also start with 'test_'.

endpoint = 'https://portal.spatial.nsw.gov.au/server/rest/services/NSW_Administrative_Boundaries_Theme/FeatureServer/8'
params = {
    'where': '1=1',
    }
object_ids = [63, 420, 608, 611, 634, 831, 1098, 1991, 1992, 2051, 2522, 2637, 2660, 3108, 3109, 3173, 3184, 3317, 3504,
              3505, 3508, 3509, 3512, 3543, 3673, 3674, 3782, 3827, 3897, 3970, 4001, 4021, 4022, 4114, 4198, 4235,
              4236, 4264, 4274, 4278, 4287, 4292, 4298, 4299, 4316, 4331, 4339, 4340, 4341, 4350, 4372, 4389, 4390,
              4393, 4397, 4398, 4417, 4421, 4458, 4459, 4473, 4505, 4508, 4511, 4512, 4520, 4521, 4559, 4592, 4609,
              4625, 4629, 4638, 4645, 4663, 4669, 4691, 4693, 4708, 4710, 4715, 4736, 4737, 4771, 4772, 4787, 4790,
              4829, 4830, 4831, 4835, 4849, 4860, 4861, 4890, 4891, 4894, 4895, 4896, 4897, 4902, 4903, 4912, 4920,
              4922, 4934, 4935, 4938, 4939, 4943, 4955, 4974, 4975, 4978, 5002, 5004, 5006, 5007, 5018, 5019, 5034,
              5035, 5040, 5041, 5044, 5056, 5057, 5070, 5071, 5072, 5073]
object_ids_field_name = 'rid'


class TestExecute:
    post_params = {
        'returnIdsOnly': 'true',
        'f': 'json'
        }
    request_params = dict(params)
    request_params.update(post_params)

    response = http_methods.Execute.post(
        endpoint=endpoint,
        operation='query?',
        params=request_params)

    def test_correct_response(self):
        assert str(
            TestExecute.response.json()) == "{'objectIdFieldName': 'rid', 'objectIds': [63, 420, 608, 611, 634, 831, 1098, 1991, 1992, 2051, 2522, 2637, 2660, 3108, 3109, 3173, 3184, 3317, 3504, 3505, 3508, 3509, 3512, 3543, 3673, 3674, 3782, 3827, 3897, 3970, 4001, 4021, 4022, 4114, 4198, 4235, 4236, 4264, 4274, 4278, 4287, 4292, 4298, 4299, 4316, 4331, 4339, 4340, 4341, 4350, 4372, 4389, 4390, 4393, 4397, 4398, 4417, 4421, 4458, 4459, 4473, 4505, 4508, 4511, 4512, 4520, 4521, 4559, 4592, 4609, 4625, 4629, 4638, 4645, 4663, 4669, 4691, 4693, 4708, 4710, 4715, 4736, 4737, 4771, 4772, 4787, 4790, 4829, 4830, 4831, 4835, 4849, 4860, 4861, 4890, 4891, 4894, 4895, 4896, 4897, 4902, 4903, 4912, 4920, 4922, 4934, 4935, 4938, 4939, 4943, 4955, 4974, 4975, 4978, 5002, 5004, 5006, 5007, 5018, 5019, 5034, 5035, 5040, 5041, 5044, 5056, 5057, 5070, 5071, 5072, 5073]}"


class TestArcGisAPI:
    response_metadata = arcgis_api.Query.get_metadata(
        endpoint=endpoint)

    def test_get_metadata(self):
        assert TestArcGisAPI.response_metadata['maxRecordCount'] == 50

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

    def test_get_contents_of_ids(self):
        assert TestArcGisAPI.response_contents_of_ids['cadid'].equals(pd.Series(
            data=[108012460, 108012388, 173919536, 173953134, 108012499, 173953566, 108012403, 108012380, 108012474, 108012548]))


class TestCorelogicAPI:
    response_access_token = corelogic_api.Auth.get_access_token(
        client_id='IezWLp3g7sXmvlO5lrs9heJG8xAG7hTB',
        client_secret='vm908mrRAsVkHycf')

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

    print(property_value_range)
