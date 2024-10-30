import unittest
import requests
from pathlib import Path
from tdm import Client, UploadSuccess

FILE_PATH = Path(__file__).parent.absolute()
RESOURCES_PATH = FILE_PATH / 'resources'

class TdmClientTests(unittest.TestCase):

    def setUp(self):
        session = requests.Session()
        session.auth = requests.auth.HTTPBasicAuth('tests@dev.senaps.io', 'tests')

        self.client = Client('https://dev.senaps.io/tdm', session)

    def test_post_missing_data(self):

        response = self.client.create_data(None, 'test/test_create_empty.nc')
        self.assertIsInstance(response, UploadSuccess)
        self.client.delete_data('test/test_create_empty.nc')

    def test_post_replace_data(self):

        self.client.create_data(None, 'test/replace_test.nc')
        self.client.create_data(RESOURCES_PATH.as_posix(), 'test/replace_test.nc')
        self.client.delete_data('test/replace_test.nc')

    def test_put_replace_data(self):

        self.client.create_data(None, 'test/replace_test.nc')
        self.client.upload_data(RESOURCES_PATH.as_posix(), 'test/replace_test.nc')
        self.client.delete_data('test/replace_test.nc')

    def test_delete_data(self):

        self.client.create_data(None, 'test/test_create_empty.nc')
        self.client.delete_data('test/test_create_empty.nc')

    def test_delete_unknown_data_raises_error(self):
        with self.assertRaises(requests.exceptions.HTTPError):
            self.client.delete_data('test/blah.nc')
