
import posixpath, requests, warnings
from collections.abc import Sequence

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    str_type = (str, basestring)
except NameError:
    str_type = str # basestring doesn't exist in Python 3

# If possible, use the MultipartEncoded from the Requests toolbelt to allow for
# streaming upload.
try:
    from requests_toolbelt import MultipartEncoder

    def _prepare_multipart_request(fields):
        m = MultipartEncoder(fields=fields)

        return {
            'data': m,
            'headers': {
                'Content-Type': m.content_type
            }
        }
# Otherwise, fall back to Request's default behaviour.
except ImportError:
    warnings.warn('Using default multipart request encoder - upload size will be limited by available RAM.')

    def _prepare_multipart_request(fields):
        return { 'files': fields }


class Client(object):
    def __init__(self, url, session=None):
        """
        A client class for the Thredds Data Manager (TDM) API.

        :param url: The URL of the of the TDM API.
        :type url: str
        :param session: A requests Session object to use when making HTTP requests to the TDM API.
        :type session: requests.Session
        """

        self._url = url
        self._session = session or requests.Session()

        # If the requests-toolbelt is available, use it to enable TCP keep-alive
        # for large file uploads.
        # NOTE: requests-toolbelt is installed with the 'large_files' 'extras_require' in setup.py.
        try:
            from requests_toolbelt.adapters import socket_options
            tcp = socket_options.TCPKeepAliveAdapter(idle=120, interval=10)
            session.mount('https://', tcp)
        except ImportError:
            warnings.warn("TCP Keepalive not enabled. requests_toolbelt package unavailable.")


    def create_data(self, data, path, id=None, name=None, organisation_id=None, group_ids=None):
        """
        Upload a data file to Thredds. This may create a new dataset, or replace
        an existing dataset including all its properties.

        :param data: The path on disk of the file to upload.
        :type data: str
        :param path: The URL path of the dataset that is to be created or
            updated.

            If the ``organisation_id`` parameter is supplied, the final URL path
            of the dataset will have an organisation-specific component
            prepended to it.
        :type path: str
        :param id: The ID to assign to the dataset.

            If omitted, the dataset's ID is computed as the hexadecimal
            representation of the MD5 hash of the supplied ``path``.
        :type id: str
        :param name: The name to assign to the dataset.

            If omitted, the dataset's name is derived from the last component of
            the supplied ``path``.
        :type name: str
        :param organisation_id: The ID of the Senaps organisation that owns the
            dataset.

            If omitted, the organisation ID will be derived from the first
            component of the supplied ``path``.
        :type organisation_id: str
        :param group_ids: A list of the IDs of the Senaps groups that should
            contain the dataset. May be supplied either as a list, or as a
            comma-separated string.
        :type group_ids: str|list
        :return: An object describing the attributes of the uploaded dataset.
        :rtype: tdm.UploadSuccess
        :raises requests.exceptions.HTTPError: if an HTTP error occurs.
        """

        return self._handle_put_post("POST", data, path, id=id, name=name, organisation_id=organisation_id, group_ids=group_ids)

    def upload_data(self, data, path, name=None, organisation_id=None, group_ids=None):
        """
        Upload a data replacement data file to Thredds. The dataset at the path must already exist.

        :param data: The path on disk of the file to upload.
        :type data: str

        :param path: The URL path of the dataset that is to be updated.
            If the ``organisation_id`` parameter is supplied, the final URL path
            of the dataset will have an organisation-specific component
            prepended to it.
        :type path: str

        :param name: The name to assign to the dataset.
            If omitted, the existing dataset name will be retained.
        :type name: str

        :param organisation_id: The ID of the Senaps organisation that owns the
            dataset.
            If omitted, the organisation ID will be derived from the first
            component of the supplied ``path``.
        :type organisation_id: str

        :param group_ids: A list of the IDs of the Senaps groups that should
            contain the dataset, this will replace any existing group membership.
            May be supplied either as a list, or as a comma-separated string.
            If omitted the existing groups will be retained.
        :type group_ids: str|list

        :raises requests.exceptions.HTTPError: if an HTTP error occurs.
        """

        self._handle_put_post("PUT", data, path, id=None, name=name, organisation_id=organisation_id, group_ids=group_ids)

    def _handle_put_post(self, method, data, path, id=None, name=None, organisation_id=None, group_ids=None):

        if not isinstance(group_ids, str_type) and isinstance(group_ids, Sequence):
            group_ids = ','.join(group_ids)

        fields = {
            'id': id,
            'name': name,
            'organisationid': organisation_id,
            'groupids': group_ids,
            'path': path
        }

        # Remove null fields
        fields = {k: v for k, v in fields.items() if v is not None}

        if data is not None:
            with open(data, 'rb') as f:
                fields['data'] = f
                return self._do_upload(method, fields)
        else:
            return self._do_upload(method, fields)

    def _do_upload(self, method, fields):
        request = _prepare_multipart_request(fields)
        response = self._session.request(method, self._get_endpoint('data'), **request)
        response.raise_for_status()
        

        if response.status_code in [200, 201]:
            # Expect content in response
            return UploadSuccess(response.json())


    def delete_data(self, path=None, id=None, organisation_id=None):
        """
        Delete a data file from Thredds. The file to delete may be identified by
        its URL path, or by its ID.

        :param path: The URL path of the dataset that is to be deleted.

            If the ``organisation_id`` parameter is omitted, this path **must**
            have the organisation ID as its first component.

            Must not be supplied if the ``id`` parameter is supplied.
        :type path: str
        :param id: The ID of the dataset that is to be deleted.

            Must not be supplied if the ``path`` parameter is supplied.
        :type id: str
        :param organisation_id: The ID of the organisation that owns the dataset
            that is to be deleted.

            Must be supplied if the ``id`` parameter is supplied, but is
            otherwise optional. If supplied alongside the ``path`` parameter,
            then the ``path`` value **must not** contain the organisation ID as
            its first component.
        :type organisation_id: str
        :raises requests.exceptions.HTTPError: if an HTTP error occurs.
        """

        if (path is None) == (id is None):
            raise ValueError('One (and only one) of the `path` and `id` parameters must be given.')
        if (id is not None) and (organisation_id is None):
            raise ValueError('If the dataset ID is given, then the organisation ID must be given too.')

        params = {
            'path': path,
            'id': id,
            'organisationid': organisation_id
        }
        params = { k:v for k,v in params.items() if v is not None }

        self._session.delete(self._get_endpoint('data'), params=params).raise_for_status()

    def _get_endpoint(self, endpoint):
        parts = list(urlparse.urlparse(self._url))
        parts[2] = posixpath.join(parts[2], endpoint)
        return urlparse.urlunparse(parts)

class UploadSuccess(object):
    """
    Representation of the response to a successful data upload request.

    NOTE: this class is not intended to be instantiated directly, and is used
    only for the purpose of relaying the response to the
    :meth:`tdm.Client.upload_data` method.
    """

    def __init__(self, json):
        self._organisation_id = json['organisationId']
        self._group_ids = set(json['groupIds'])
        self._dataset_path = json['datasetPath']
        self._name = json['name']
        self._id = json['id']

    @property
    def organisation_id(self):
        """The ID of the Senaps organisation which owns the dataset"""
        return self._organisation_id

    @property
    def group_ids(self):
        """The IDs of the Senaps groups which the dataset is contained within"""
        return self._group_ids

    @property
    def dataset_path(self):
        """The URL path of the dataset"""
        return self._dataset_path

    @property
    def name(self):
        """The dataset's name"""
        return self._name

    @property
    def id(self):
        """The dataset's ID"""
        return self._id


