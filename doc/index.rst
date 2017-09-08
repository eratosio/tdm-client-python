
Welcome to Thredds Data Manager Client's documentation!
=======================================================

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

Class Reference
---------------

.. autoclass:: tdm.Client
  :members:
