
import collections, os, posixpath, requests, warnings

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

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

def _is_str(val):
    try:
        return isinstance(val, basestring)
    except NameError:
        return isinstance(val, str)

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
    
    def upload_data(self, data, path, id=None, name=None, organisation_id=None, group_ids=None):
        """
        Upload a data file to Thredds. This may create a new dataset, or replace
        the data for an existing dataset.
        
        :param data: The path on disk of the file to upload.
        :type data: str
        :param path: The URL path of the dataset that is to be created or
            updated. If the ``organisation_id`` parameter is supplied, the final
            URL path of the dataset will have an organisation-specific component
            prepended to it.
        :type path: str
        :param id: The ID to assign to the dataset. If omitted, the dataset's ID
            is computed as the hexadecimal representation of the MD5 hash of the
            supplied ``path``.
        :type id: str
        :param name: The name to assign to the dataset. If omitted, the
            dataset's name is derived from the last component of the supplied
            ``path``.
        :type name: str
        :param organisation_id: The ID of the Senaps organisation that owns the
            dataset. If omitted, the organisation ID will be derived from the
            first component of the supplied ``path``.
        :type organisation_id: str
        :param group_ids: A list of the IDs of the Senaps groups that should
            contain the dataset. May be supplied either as a list, or as a
            comma-separated string.
        :type group_ids: str|list
        :raises requests.exceptions.HTTPError: if an HTTP error occurs.
        """
        
        if not _is_str(group_ids) and isinstance(group_ids, collections.Sequence):
            group_ids = ','.join(group_ids)
        
        with open(data, 'rb') as f:
            fields = {
                'id': id,
                'name': name,
                'organisationid': organisation_id,
                'groupids': group_ids,
                'path': path,
                'data': f
            }
            
            fields = { k:v for k,v in fields.iteritems() if v is not None }
            
            request = _prepare_multipart_request(fields)
            
            response = self._session.post(self._get_endpoint('data'), **request)
            response.raise_for_status()
    
    def _get_endpoint(self, endpoint):
        parts = list(urlparse.urlparse(self._url))
        parts[2] = posixpath.join(parts[2], endpoint)
        return urlparse.urlunparse(parts)
