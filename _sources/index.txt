Cloud Datastore Narrative / Example Application
===============================================

Overview
--------

In order to give a better feel for how a Python application might use the
:mod:`gcloud.datastore` API, let's look at building an example application
which stores its data using the API.  In order to focus on the API, the
sample application will be built as a set of command-line scripts.

For our example, let's build an employee expense reporting system.  An example
set of interactions might look like the following scenario.

Returning from a trip to the Bay Area, Sally creates a CSV file,
``expenses-20140901.csv``, containing one row for each line item in her
expense report:

.. code-block:: none

   "Date","Vendor","Type","Quantity","Price","Memo"
   "2014-08-26","United Airlines","Travel",1,425.00,"Airfaire, IAD <-> SFO"
   "2014-08-27","Yellow Cab","Travel",32.00,"Taxi to IAD"
   ...

Sally then submits her expense report from the command line using our
:program:`submit_expenses` script (see :ref:`create-expense-report`):

.. code-block:: bash

   $ submit_expenses create --employee-id=sally --description="Frotz project kickoff, San Jose" expenses-20140901.csv
   Processed 15 rows.
   Created report: sally/expenses-20140901

Sally can upload photos of receipts for her expense report using our
:program:`expense_receipts` script (see :ref:`upload-expense-receipts`):

.. code-block:: bash

   $ expense_receipts upload sally expenses-20140901 yellow_cab-20140827.jpg
   Employee-ID: sally
   Report-ID: expenses-20140901

   Uploaded: sally/expenses-20140901/yellow_cab-20140827.jpg

Sally can list receipts for her expense report
(see :ref:`list-expense-receipts`):

.. code-block:: bash

   $ expense_receipts list sally expenses-20140901
   Employee-ID: sally
   Report-ID: expenses-20140901

   Receipt: yellow_cab-20140827.jpg

and download one of them (see :ref:`download-expense-receipts`):

.. code-block:: bash

   $ expense_receipts download sally expenses-20140901 yellow_cab-20140827.jpg
   Saved to file:  yellow_cab-20140827.jpg

or delete one of them (see :ref:`delete-expense-receipts`):

.. code-block:: bash

   $ expense_receipts delete sally expenses-20140901 yellow_cab-20140827.jpg
   Deleted:  yellow_cab-20140827.jpg

Sally can list all her submitted expense reports using our
:program:`review_expenses` script (see :ref:`list-expense-reports`):

.. code-block:: bash

   $ review_expenses list --employee-id=sally

   "Employee ID", "Report ID","Created","Updated","Description","Status","Memo"
   "sally","expenses-2013-11-19","2013-12-01","2013-12-01","Onsite Training, Mountain View","Paid","Check #3715"
   "sally","expenses-2014-04-19","2014-04-21","2014-04-22","PyCon 2014, Montreal","Paid","Check #3992"
   "sally","expenses-2014-09-01","2014-09-04","2014-09-04","Frotz project kickoff, San Jose","pending",""

Sally can review a submitted expense report using the its ID
(see :ref:`show-expense-report`):

.. code-block:: bash

   $ review_expenses show sally expenses-20140901
   Employee-ID: sally
   Report-ID: expenses-20140901
   Report-Status: pending
   Created: 2014-09-04
   Updated: 2014-09-04
   Description: Frotz project kickoff, San Jose

   "Date","Vendor","Type","Quantity","Price","Memo"
   "2014-08-26","United Airlines","Travel",1,425.00,"Airfaire, IAD <-> SFO"
   "2014-08-27","Yellow Cab","Travel",32.00,"Taxi to IAD"
   ...

While in "pending" status, Sally can edit the CSV and resubmit it
(see :ref:`update-expense-report`):

.. code-block:: bash

   $ submit_expenses update expenses-20140901.csv
   Updated report: sally/expenses-20140901
   Processed 15 rows.

While it remains in "pending" status, Sally can also delete the report
(see :ref:`delete-expense-report`):

.. code-block:: bash

   $ submit_expenses delete expenses-20140901
   Deleted report: sally/expenses-20140901
   Removed 15 items.

Sally's boss, Pat, can review all open expense reports
(see :ref:`list-expense-reports`):

.. code-block:: bash

   $ review_expenses list --status=pending

   "Employee ID","Report ID","Created","Updated","Description","Status","Memo"
   "sally","expenses-2014-09-01","2014-09-04","2014-09-04","Frotz project kickoff, San Jose","pending",""


Pat can download Sally's report
(see :ref:`show-expense-report`):

.. code-block:: bash

   $ review_expenses show sally expenses-20140901
   Report-ID: sally/expenses-20140901
   Report-Status: pending
   Employee-ID: sally
   Description: Frotz project kickoff, San Jose

   "Date","Vendor","Type","Quantity","Price","Memo"
   "2014-08-26","United Airlines","Travel",1,425.00,"Airfaire, IAD <-> SFO"
   "2014-08-27","Yellow Cab","Travel",32.00,"Taxi to IAD"

Pat can approve Sally's expense report
(see :ref:`approve-expense-report`):

.. code-block:: bash

   $ review_expenses approve --check-number=4093 sally expenses-20140901
   Approved, report: sally/expenses-20140901, check #4093

or reject it
(see :ref:`reject-expense-report`):

.. code-block:: bash

   $ review_expenses reject --reason="Travel not authorized by client" sally expenses-20140901
   Rejected, report: sally/expenses-20140901, reason: Travel not authorized by client

Implementation Review
---------------------

.. toctree::
   :maxdepth: 2

   datastore
   storage
