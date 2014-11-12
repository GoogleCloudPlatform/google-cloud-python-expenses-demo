Storage Operatations
====================

.. _connect-to-bucket:

Connecting to the API Bucket
-----------------------------

The sample application uses a utility function,
:func:`gcloud_expenses._get_bucket`, to set up the connection.

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: _get_bucket

Thie function expects three environment variables to be set up, using
your project's `OAuth2 API credentials
<https://developers.google.com/console/help/new/#generatingoauth2>`_:

- :envvar:`GCLOUD_TESTS_DATASET_ID` is your Google API Project ID
- :envvar:`GCLOUD_TESTS_CLIENT_EMAIL` is your Google API email-address
- :envvar:`GCLOUD_TESTS_TESTS_KEY_FILE` is the filesystem path to your
  Google API private key.

It returns a single bucket with a fixed name, ``gcloud-python-demo-expenses``,
first creating it if the bucket does not already exist.

.. _upload-expense-receipts:

Uploading Expense Receipts
--------------------------

In the sample application, the ``upload`` subcommand of the
:program:`expense_receipts` script drives a function,
:func:`gcloud_expenses.upload_receipt`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: upload_receipt
   :linenos:

.. _list-expense-receipts:

Listing Expense Receipts
------------------------

In the sample application, the ``list`` subcommand of the
:program:`expense_receipts` script drives a function,
:func:`gcloud_expenses.list_receipts`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: list_receipts
   :linenos:

.. _download-expense-receipts:

Downloading Expense Receipts
----------------------------

In the sample application, the ``download`` subcommand of the
:program:`expense_receipts` script drives a function,
:func:`gcloud_expenses.download_receipt`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: download_receipt
   :linenos:

.. _delete-expense-receipts:

Deleting Expense Receipts
----------------------------

In the sample application, the ``delete`` subcommand of the
:program:`expense_receipts` script drives a function,
:func:`gcloud_expenses.download_receipt`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: delete_receipt
   :linenos:
