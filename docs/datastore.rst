Datastore Operations
====================

See the `Datastore API overview
<https://cloud.google.com/datastore/docs/overview>`_ for concepts and terms
used in this document.

.. _connect-to-dataset:

Connecting to the API
---------------------

The sample application uses a utility function,
:func:`gcloud_expenses.initialize_gcloud`, to set up the connection.

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: initialize_gcloud
   :linenos:

This function expects environment variables to be set up,
using your project's `OAuth2 API credentials
<https://developers.google.com/console/help/new/#generatingoauth2>`_:

- :envvar:`GCLOUD_DATASET_ID` is your Google API Project ID
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

:func:`gcloud_expenses.create_report` starts a transaction (line 2) to
ensure that all changes are performed atomically.  It then checks that no
report exists already for the given employee ID and report ID, raising an
exception if so (lines 3-4).  It then  delegates most of the work to the
:func:`gcloud_expenses._upsert_report` utility function (line 5), finally
setting metadata on the report itself (lines 6-10).


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

:func:`gcloud_expenses.update_report` starts a transaction (line 2) to
ensure that all changes are performed atomically.  It then checks that a
report *does* exist already for the given employee ID and report ID, and that
it is in ``pending`` status, raising an exception if not (lines 3.4).  It then
delegates most of the work to the :func:`gcloud_expenses._upsert_report`
utility function (line 5), finally updating metadata on the report itself
(lines 6-10).

.. _delete-expense-report:

Deleting an Existing Expense Report
-----------------------------------

In the sample application, the ``delete`` subcommand of the
:program:`submit_expenses` script drives a function,
:func:`gcloud_expenses.delete_report`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: delete_report
   :linenos:

:func:`gcloud_expenses.delete_report` starts a transaction (line 2) to
ensure that all changes are performed atomically.  It then checks that a
report *does* exist already for the given employee ID and report ID (lines
3-5), and that it is in ``pending`` status (lines 6-7), raising an exception
if either is false.

.. note::

   The function takes a ``force`` argument:  if true, it will delete the
   report even if it is not in ``pending`` status.

The function then delegates to :func:`gcloud_expenses._purge_report_items` to
delete expense item entities contained in the report (line 8), and then
deletes the report itself (line 9).  Finally, it returns a count of the
deleted items (line 10).

.. _list-expense-reports:

Listing Expense Reports
-----------------------

In the sample application, the ``list`` subcommand of the
:program:`review_expenses` script drives a function,
:func:`gcloud_expenses.list_reports`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: list_reports
   :linenos:

:func:`gcloud_expenses.list_reports` creates a
:class:`~gcloud.dataset.query.Query` instance, limited to entities of kind,
``Expense Report`` (line 2), and applies filtering based on the passed
criteria:

- If ``employee_id`` is passed, it adds an "ancestor" filter to
  restrict the results to expense reports contained in the given employee
  (lines 3-5).

- If ``status`` is passed, it adds an "attribute" filter to
  restrict the results to expense reports which have that status (lines 6-8).

.. note::

   The function does *not* set up a transaction, as it uses only
   "read" operations on the API.

Finally, the function fetches the expense report entities returned by
the query and iterates over them, passing each to
:func:`gcloud_expenses._report_info` and yielding the mapping it returns.
report (lines 8-9).

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

:func:`gcloud_expenses.get_report_info` uses :func:`exenses._get_report`
to fetch the expense report entity for the given employee ID and report ID
(line 2), raising an exeception if the report does not exist (lines 3-4):

.. note::

   The function does *not* set up a transaction, as it uses only
   "read" operations on the API.

The function delegates to :func:`gcloud_expenses._report_info` to get a mapping
describing the report (line 5), and then delegates to
:func:`gcloud_expenses._fetch_report_items` to retrieve information about the
expense item entities contained in the report (line 6).  Finally, the
function returns the mapping (line 7).

.. _approve-expense-report:

Approving an Expense Report
---------------------------

In the sample application, the ``approve`` subcommand of the
:program:`review_expenses` script drives a function,
:func:`gcloud_expenses.approve_report`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: approve_report
   :linenos:

:func:`gcloud_expenses.approve_report` starts a transaction (line 2) to
ensure that all changes are performed atomically.  It then checks that a
report *does* exist already for the given employee ID and report ID, and that
it is in ``pending`` status, raising an exception if not (lines 3-7).  It then
updates the status and other metadata on the report itself (lines 8-11).

.. _reject-expense-report:

Rejecting an Expense Report
---------------------------

In the sample application, the ``reject`` subcommand of the
:program:`review_expenses` script drives a function,
:func:`gcloud_expenses.reject_report`:

.. literalinclude:: ../gcloud_expenses/__init__.py
   :pyobject: reject_report
   :linenos:

:func:`gcloud_expenses.approve_report` starts a transaction (line 2) to
ensure that all changes are performed atomically.  It then checks that a
report *does* exist already for the given employee ID and report ID, and that
it is in ``pending`` status, raising an exception if not (lines 3-7).  It then
updates the status and other metadata on the report itself (lines 8-11).
