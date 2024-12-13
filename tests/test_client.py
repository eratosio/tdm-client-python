import unittest
import requests
import os
from pathlib import Path
from tdm import Client, UploadSuccess

FILE_PATH = Path(__file__).parent.resolve()
RESOURCES_PATH = FILE_PATH / 'resources'
TEST_FILE = RESOURCES_PATH / 'sresa1b_ncar_ccsm3-example.nc'
TEST_ORG = 'eratos-internal'

class TdmClientTests(unittest.TestCase):

    def setUp(self):
        session = requests.Session()
        senaps_apikey = os.environ.get('SENAPS_KEY') or os.environ.get('SENAPS_APIKEY') or ''
        senaps_username = os.environ.get('SENAPS_USERNAME', '')
        senaps_password = os.environ.get('SENAPS_PASSWORD', '')

        if senaps_password and senaps_username:
            session.auth = requests.auth.HTTPBasicAuth(senaps_username, senaps_password)
        elif senaps_apikey:
            session.headers.update({'apikey' : senaps_apikey})
        else:
            raise ValueError("No auth provided, specify senaps login or apikey in environment")
        assert os.environ.get('API_BASE'), "Provide an API endpoint in the environment variable API_BASE"
        self.client = Client('https://staging.senaps.eratos.com/tdm', session)

    def test_post_missing_data(self):

        response = self.client.create_data(None, f'{TEST_ORG}/test_create_empty.nc')
        self.assertIsInstance(response, UploadSuccess)
        self.client.delete_data(f'{TEST_ORG}/test_create_empty.nc')

    def test_post_replace_data(self):
        print(TEST_FILE.as_posix())
        self.client.create_data(None, f'{TEST_ORG}/replace_test.nc')
        self.client.create_data(TEST_FILE.as_posix(), f'{TEST_ORG}/replace_test.nc')
        self.client.delete_data(f'{TEST_ORG}/replace_test.nc')

    def test_put_replace_data(self):

        self.client.create_data(None, f'{TEST_ORG}/replace_test.nc')
        self.client.upload_data(TEST_FILE.as_posix(), f'{TEST_ORG}/replace_test.nc')
        self.client.delete_data(f'{TEST_ORG}/replace_test.nc')

    def test_delete_data(self):

        self.client.create_data(None, f'{TEST_ORG}/test_create_empty.nc')
        self.client.delete_data(f'{TEST_ORG}/test_create_empty.nc')

    def test_delete_unknown_data_raises_error(self):
        with self.assertRaises(requests.exceptions.HTTPError):
            self.client.delete_data(f'{TEST_ORG}/blah.nc')
