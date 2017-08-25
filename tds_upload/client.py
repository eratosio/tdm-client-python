
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
        return isinstance(val basestring)
    except NameError:
        return isinstance(val, str)

class Client(object):
    def __init__(self, url, session=None):
        self._url = url
        self._session = session or requests.Session()
    
    def upload_data(self, data, path, id=None, name=None, organisation_id=None, group_ids=None):
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
