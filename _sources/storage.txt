Storage Operations
==================

See the `Storage API overview
<https://cloud.google.com/storage/docs/overview>`_ for concepts and terms
used in this document.

.. _connect-to-bucket:

Connecting to the API Bucket
-----------------------------

The sample application uses a utility function,
:func:`gcloud_expenses._get_bucket`, to set up the connection and get
access to a storage bucket:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: _get_bucket
   :linenos:

This function expects three environment variables to be set up (lines 2-4),
using your project's `OAuth2 API credentials
<https://developers.google.com/console/help/new/#generatingoauth2>`_:

- :envvar:`GCLOUD_TESTS_DATASET_ID` is your Google API Project ID
- :envvar:`GCLOUD_TESTS_CLIENT_EMAIL` is your Google API email-address
- :envvar:`GCLOUD_TESTS_TESTS_KEY_FILE` is the filesystem path to your
  Google API private key.

Using those values, the function creates a connection object (line 5), It
returns a single bucket with a fixed name, ``gcloud-python-demo-expenses``,
first creating it if the bucket does not already exist (lines 6-9).

.. _upload-expense-receipts:

Uploading Expense Receipts
--------------------------

In the sample application, the ``upload`` subcommand of the
:program:`expense_receipts` script drives a function,
:func:`gcloud_expenses.upload_receipt`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: upload_receipt
   :linenos:

After connecting to the bucket via :func:`gcloud_expenses._get_bucket`
(line 2), :func:`gcloud_expenses.upload_receipt` spilts off the "base"
filename from the ``filename`` passed to it, in order to use the "base" as
part of the key for the receipt (lines 3-4).  It checks that no receipt
exists already with that key, raising an exception if so (lines 5-6).
Finally, it uploads the file into the bucket using that key (line 7).

.. _list-expense-receipts:

Listing Expense Receipts
------------------------

In the sample application, the ``list`` subcommand of the
:program:`expense_receipts` script drives a function,
:func:`gcloud_expenses.list_receipts`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: list_receipts
   :linenos:

After connecting to the bucket via :func:`gcloud_expenses._get_bucket`
(line 2), :func:`gcloud_expenses.list_receipts` creates a "prefix" for
retrieving onlyreceipts stored for a given expense report (line 3).  It
then searches for keys using that prefix (line 4), and returns the
"filename" portion of each retrieved key (lines 5-6).

.. _download-expense-receipts:

Downloading Expense Receipts
----------------------------

In the sample application, the ``download`` subcommand of the
:program:`expense_receipts` script drives a function,
:func:`gcloud_expenses.download_receipt`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: download_receipt
   :linenos:

After connecting to the bucket via :func:`gcloud_expenses._get_bucket`
(line 2), :func:`gcloud_expenses.dowload_receipt` spilts off the "base"
filename from the ``filename`` passed to it, in order to use the "base" as
part of the key for the receipt (lines 3-4).  It checks that the indicated
receipt already exists, raising an exception if not (lines 5-6).  Finally,
it downloads the file from the bucket using that key (line 7).

.. _delete-expense-receipts:

Deleting Expense Receipts
----------------------------

In the sample application, the ``delete`` subcommand of the
:program:`expense_receipts` script drives a function,
:func:`gcloud_expenses.delete_receipt`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: delete_receipt
   :linenos:

After connecting to the bucket via :func:`gcloud_expenses._get_bucket`
(line 2), :func:`gcloud_expenses.delete_receipt` spilts off the "base"
filename from the ``filename`` passed to it, in order to use the "base" as
part of the key for the receipt (lines 3-4).  It checks that the indicated
receipt already exists, raising an exception if not (lines 5-6).  Finally,
it deletes the key from the bucket (line 7).
