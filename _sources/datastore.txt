Datastore Operatations
======================

Connecting to the API Dataset
-----------------------------

The sample application uses a utility function,
:func:`gcloud_expenses._get_dataset`, to set up the connection.

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: _get_dataset

Thie function expects three environment variables to be set up, using
your project's `OAuth2 API credentials
<https://developers.google.com/console/help/new/#generatingoauth2>`_:

- :envvar:`GCLOUD_TESTS_DATASET_ID` is your Google API Project ID
- :envvar:`GCLOUD_TESTS_CLIENT_EMAIL` is your Google API email-address
- :envvar:`GCLOUD_TESTS_TESTS_KEY_FILE` is the filesystem path to your
  Google API private key.

.. _create-expense-report:

Creating a New Expense Report
-----------------------------

In the sample application, the ``create`` subcommand of the
:program:`submit_expenses` script drives a function,
:func:`gcloud_expenses.create_report`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: create_report
   :linenos:

After connecting to the dataset via :func:`gcloud_expenses._get_dataset` (line
2), :func:`gcloud_expenses.create_report` starts a transaction (line 3) to
ensure that all changes are performed atomically.  It then checks that no
report exists already for the given employee ID and report ID, raising an
exception if so (lines 4-5).  It then  delegates most of the work to the
:func:`gcloud_expenses._upsert_report` utility function (line 6), finally
setting metadata on the report itself (lines 7-11).


.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: _upsert_report
   :linenos:

The :func:`gcloud_expenses._upsert_report` function: in turn delegates to
:func:`gcloud_expenses._get_employee`, :func:`gcloud_expenses._get_report`,
and :func:`gcloud_expenses._purge_report_items` to ensure that the employee
and report exist, and that the report contains no items (lines 2-4).  It then
iterates over the rows from the CSV file, creating an item for each row (lines
5-13), finally returning the populated report object (line 14).

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: _get_employee
   :linenos:

The :func:`gcloud_expenses._get_employee` function: looks up an employee
(lines 2-3).

.. note:: Employee entities have no "parent" object: they exist at the "top"
          level.

If the employee entity does not exist, and the caller requests it, the
function creates a new employee entity and saves it.

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: _get_report
   :linenos:

The :func:`gcloud_expenses._get_employee` function: looks up an expense report
using an `"ancestor" query
<https://cloud.google.com/datastore/docs/concepts/queries#Datastore_Ancestor_queries>`_
(lines 2-3).

.. note:: Each expense report entity is expected to have an employee entity
          as its "parent".

If the expense report entity does not exist, and the caller requests it, the
function creates a new expense report entity and saves it.

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: _purge_report_items
   :linenos:

The :func:`gcloud_expenses._purge_report_items` function: delegates to
:func:`gcloud_expenses._fetch_report_items` to find expense item entities
contained within the given report (line 4), and deletes them (line 5).  It
returns a count of the deleted items.

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: _fetch_report_items
   :linenos:

The :func:`gcloud_expenses._purge_report_items` function: performs an
"ancestor" query (lines 2-3) to find expense item entities contained within a
given expense report.

.. _update-expense-report:

Updating an Existing Expense Report
-----------------------------------

In the sample application, the ``update`` subcommand of the
:program:`submit_expenses` script drives a function,
:func:`gcloud_expenses.update_report`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: update_report
   :linenos:

After connecting to the dataset via :func:`gcloud_expenses._get_dataset` (line
2), :func:`gcloud_expenses.update_report` starts a transaction (line 3) to
ensure that all changes are performed atomically.  It then checks that a
report *does* exist already for the given employee ID and report ID, and that
it is in ``pending`` status, raising an exception if not (lines 4-5).  It then
delegates most of the work to the :func:`gcloud_expenses._upsert_report`
utility function (line 6), finally updating metadata on the report itself
(lines 7-11).

.. _delete-expense-report:

Deleting an Existing Expense Report
-----------------------------------

In the sample application, the ``delete`` subcommand of the
:program:`submit_expenses` script drives a function,
:func:`gcloud_expenses.delete_report`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: delete_report
   :linenos:

After connecting to the dataset via :func:`gcloud_expenses._get_dataset` (line
2), :func:`gcloud_expenses.delete_report` starts a transaction (line 3) to
ensure that all changes are performed atomically.  It then checks that a
report *does* exist already for the given employee ID and report ID (lines
4-6), and that it is in ``pending`` status (lines 7-8), raising an exception
if either is false.

.. note::

   The function takes a ``force`` argument:  if true, it will delete the
   report even if it is not in ``pending`` status.

The function then delegates to :func:`gcloud_expenses._purge_report_items` to
delete expense item entities contained in the report (line 9), and then
deletes the report itself (line 10).  Finally, it returns a count of the
deleted items.

.. _list-expense-reports:

Listing Expense Reports
-----------------------

In the sample application, the ``list`` subcommand of the
:program:`review_expenses` script drives a function,
:func:`gcloud_expenses.list_reports`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: list_reports
   :linenos:

After connecting to the dataset via :func:`gcloud_expenses._get_dataset` (line
2), :func:`gcloud_expenses.list_reports` creates a
:class:`~gcloud.dataset.query.Query` instance, limited to entities of kind,
``Expense Report`` (line 3), and applies filtering based on the passed
criteria:

- If ``employee_id`` is passed, it adds an "ancestor" filter to
  restrict the results to expense reports contained in the given employee
  (lines 4-6).

- If ``status`` is passed, it adds an "attribute" filter to
  restrict the results to expense reports which have that status (lines 7-8).

.. note::

   The function does *not* set up a transaction, as it uses only
   "read" operations on the API.

Finally, the function fetches the expense report entities returned by
the query and iterates over them, passing each to
:func:`gcloud_expenses._report_info` and yielding the mapping it returns.
report (lines 9-10).

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: _report_info
   :linenos:

The :func:`gcloud_expenses._report_info` utility function uses the expense
report entity's key to determine the report's employee ID (line 3), and its
report ID (line 4).  It then uses these values and the entityy's properties to
generate and return a mapping describing the report (lines 5-22).

.. _show-expense-report:

Showing an Expense Report
-------------------------

In the sample application, the ``show`` subcommand of the
:program:`review_expenses` script drives a function,
:func:`gcloud_expenses.get_report_info`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: get_report_info
   :linenos:

After connecting to the dataset via :func:`gcloud_expenses._get_dataset` (line
2), :func:`gcloud_expenses.get_report_info` uses :func:`exenses._get_report`
to fetch the expense report entity for the given employee ID and report ID
(line 3), raising an exeception if the report does not exist (line 4):

.. note::

   The function does *not* set up a transaction, as it uses only
   "read" operations on the API.

The function delegates to :func:`gcloud_expenses._report_info` to get a mapping
describing the report (line 6), and then delegates to
:func:`gcloud_expenses._fetch_report_items` to retrieve information about the
expense item entities contained in the report (line 7).  Finally, the
function returns the mapping.

.. _approve-expense-report:

Approving an Expense Report
---------------------------

In the sample application, the ``approve`` subcommand of the
:program:`review_expenses` script drives a function,
:func:`gcloud_expenses.approve_report`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: approve_report
   :linenos:

After connecting to the dataset via :func:`gcloud_expenses._get_dataset` (line
2), :func:`gcloud_expenses.approve_report` starts a transaction (line 3) to
ensure that all changes are performed atomically.  It then checks that a
report *does* exist already for the given employee ID and report ID, and that
it is in ``pending`` status, raising an exception if not (lines 4-5).  It then
updates the status and other metadata on the report itself (lines 9-12).

.. _reject-expense-report:

Rejecting an Expense Report
---------------------------

In the sample application, the ``reject`` subcommand of the
:program:`review_expenses` script drives a function,
:func:`gcloud_expenses.reject_report`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: reject_report
   :linenos:

After connecting to the dataset via :func:`gcloud_expenses._get_dataset` (line
2), :func:`gcloud_expenses.approve_report` starts a transaction (line 3) to
ensure that all changes are performed atomically.  It then checks that a
report *does* exist already for the given employee ID and report ID, and that
it is in ``pending`` status, raising an exception if not (lines 4-5).  It then
updates the status and other metadata on the report itself (lines 9-12).
