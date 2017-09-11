
Thredds Data Manager Client Documentation
=========================================

Introduction
------------

The Thredds Data Manager (TDM) API provides a custom service for uploading and
deleting datasets from a Senaps-hosted Thredds Data Server (TDS). This allows
clients to upload data into the platform's TDS instance and have that data be
protected by the same role-based security system used elsewhere in the platform.

This Python package implements a client for the TDM API.

Installation
------------

To install the TDM API client, obtain a copy of the client library from its
`BitBucket Repository <https://bitbucket.csiro.au/projects/SC/repos/tds-upload-client-python/browse>`_.
The easiest approach is to clone the Git repository locally:

.. code-block:: bash
  
  git clone https://bitbucket.csiro.au/scm/sc/tds-upload-client-python.git

Change directory into the new ``tds-upload-client-python`` directory, and run
the following command to install the client library (assumes a Unix-like
environment):

.. code-block:: bash
  
  sudo python setup.py install

This will install the client library and its sole mandatory dependency,
`Requests <http://python-requests.org>`_.

The default behaviour of the Requests package when making ``POST`` requests is
to load the entire data file into memory. While that isn't a problem for small
files, it does place a hard upper limit on the size of files that can be
uploaded. The `Requests Toolbelt <https://toolbelt.readthedocs.io/en/latest/>`_
package adds streaming upload facilities to the Requests package, allowing the
file size limit to be circumvented.

To allow files larger than the available memory to be uploaded, install the
Requests Toolbelt package with ``pip``:

.. code-block:: bash
  
    sudo pip install requests-toolbelt

Module Reference
----------------

.. autoclass:: tdm.Client
  :members:

.. autoclass:: tdm.UploadSuccess()
  :members:

Usage Example
-------------

The following is a somewhat contrived example of uploading a data file then
immediately deleting it using the client:

.. code-block:: python
  :linenos:
  
  from tdm import Client
  from requests import Session
  
  session = Session()
  session.auth = ('myusername', 'mypassword')
  
  client = Client('http://example.com/tdm', session)
  
  result = client.upload_data('/home/myuser/data.nc', 'newdata/data.nc',
	  organisation_id='acme')
  
  print result.dataset_path
  
  client.delete_data(id=result.id, organisation_id='acme_inc')

In lines 4 through 7, a new TDM client is created, using a Requests session with
`HTTP Basic Authentication <https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#Basic_authentication_scheme>`_.

.. warning::
  For the sake of brevity, this example shows a plain-text password stored 
  within the script. This is highly insecure and should **never** been done in
  practice.
  
  A good alternative is to use the built-in |getpass|_ module to obtain the
  password securely on the command line.

On line 9, the local NetCDF file ``/home/myuser/data.nc`` is uploaded using the
client. The ``organisation_id`` parameter assigns ownership of the uploaded file
to the ``acme_inc`` organisation, and the ``path`` parameter indicates that the
file's URL path should be ``newdata/data.nc`` **relative to the organisation's
own URL path**.

Note that the ``id`` and ``name`` parameters were not used. If not provided,
these values are automatically generated and returned as the ``id`` and ``name``
properties of the returned :class:`tdm.UploadSuccess` object.

On line 12 the uploaded dataset's actual URL path is printed. In this case, the
final URL path will become ``/acme_inc/newdata/data.nc`` (i.e. the supplied
``path`` is appended to the organisation ID).

Finally, in line 14 the uploaded file is deleted. The file to delete is
identified by its ID (as automatically generated when the file was uploaded).
The organisation ID is supplied again, since IDs are unique within an
organisation but not globally.

.. |getpass| replace:: ``getpass``
.. _getpass: https://docs.python.org/2/library/getpass.html
