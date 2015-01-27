import datetime
import os
import urllib

from gcloud import datastore
from gcloud.datastore.key import Key
from gcloud.datastore.entity import Entity
from gcloud.datastore.query import Query
from gcloud.datastore.transaction import Transaction
from gcloud import storage
from gcloud.storage.exceptions import NotFound


BUCKET_NAME = 'gcloud-python-demo-expenses'


class NoSuchEmployee(Exception):
    """Attempt to update / delete a report which does not already exist."""


class DuplicateReport(Exception):
    """Attempt to create a report which already exists."""


class NoSuchReport(Exception):
    """Attempt to update / delete a report which does not already exist."""


class BadReportStatus(Exception):
    """Attempt to update / delete an already-approved/rejected report."""


class DuplicateReceipt(Exception):
    """Attempt to create a receipt which already exists."""


class NoSuchReceipt(Exception):
    """Attempt to download a receipt which does not already exist."""


def _get_bucket():
    project = os.environ['GCLOUD_PROJECT_ID']
    try:
        return storage.get_bucket(BUCKET_NAME, project)
    except NotFound:
        conn = storage.get_connection(project)
        return conn.create_bucket(BUCKET_NAME)


def _get_employee(employee_id, create=True):
    key = Key('Employee',  employee_id)
    employees = datastore.get([key])
    if len(employees) == 0:
        if not create:
            return None
        employee = Entity(key)
        employee['created'] = employee['updated'] = datetime.datetime.utcnow()
        datastore.put([employee])
    else:
        employee, = employees
    return employee


def _employee_info(employee):
    path = employee.key.path
    employee_id = path[0]['name']
    first_name = employee.get('first_name')
    last_name = employee.get('last_name')
    created = employee.get('created')
    updated = employee.get('updated')
    return {
        'employee_id': employee_id,
        'name': ((first_name and last_name) and
                    '%s %s' % (first_name, last_name) or employee_id),
        'created': created and created.strftime('%Y-%m-%d'),
        'updated': updated and updated.strftime('%Y-%m-%d'),
        }


def _fetch_reports(employee):
    query = Query(kind='Expense Report')
    query.ancestor = employee.key
    for item in query.fetch():
        yield item


def _get_report(employee_id, report_id, create=True):
    key = Key('Employee', employee_id, 'Expense Report', report_id)
    reports = datastore.get([key])
    if len(reports) == 0:
        if not create:
            return None
        report = Entity(key)
        datastore.put([report])
    else:
        report, = reports
    return report


def _fetch_report_items(report):
    query = Query(kind='Expense Item')
    query.ancestor = report.key
    for item in query.fetch():
        yield item


def _report_info(report):
    path = report.key.path
    employee_id = path[0]['name']
    report_id = path[1]['name']
    status = report['status']
    if status == 'paid':
        memo = report['check_number']
    elif status == 'rejected':
        memo = report['reason']
    else:
        memo = ''
    return {
        'employee_id': employee_id,
        'report_id': report_id,
        'created': report['created'].strftime('%Y-%m-%d'),
        'updated': report['updated'].strftime('%Y-%m-%d'),
        'status': status,
        'description': report.get('description', ''),
        'memo': memo,
        }


def _purge_report_items(report):
    # Delete any existing items belonging to report
    count = 0
    for item in _fetch_report_items(report):
        datastore.delete([item.key])
        count += 1
    return count


def _upsert_report(employee_id, report_id, rows):
    _get_employee(employee_id)  # force existence
    report = _get_report(employee_id, report_id)
    _purge_report_items(report)
    # Add items based on rows.
    report_path = list(report.key.flat_path)
    for i, row in enumerate(rows):
        path = report_path + ['Expense Item', i + 1]
        key = Key(*path)
        item = Entity(key)
        for k, v in row.items():
            item[k] = v
        datastore.put([item])
    return report


def initialize_gcloud():
    datastore.set_defaults()
    storage.set_defaults()


def list_employees():
    query = Query(kind='Employee')
    for employee in query.fetch():
        yield _employee_info(employee)


def get_employee_info(employee_id):
    employee = _get_employee(employee_id, False)
    if employee is None:
        raise NoSuchEmployee()
    info = _employee_info(employee)
    info['reports'] = [_report_info(report)
                       for report in _fetch_reports(employee)]
    return info

def list_reports(employee_id=None, status=None):
    query = Query(kind='Expense Report')
    if employee_id is not None:
        key = Key('Employee', employee_id)
        query.ancestor = key
    if status is not None:
        query.add_filter('status', '=', status)
    for report in query.fetch():
        yield _report_info(report)


def get_report_info(employee_id, report_id):
    report = _get_report(employee_id, report_id, False)
    if report is None:
        raise NoSuchReport()
    info = _report_info(report)
    info['items'] = [dict(x) for x in _fetch_report_items(report)]
    return info


def create_report(employee_id, report_id, rows, description):
    with Transaction():
        if _get_report(employee_id, report_id, False) is not None:
            raise DuplicateReport()
        report = _upsert_report(employee_id, report_id, rows)
        report['status'] = 'pending'
        if description is not None:
            report['description'] = description
        report['created'] = report['updated'] = datetime.datetime.utcnow()
        datastore.put([report])


def update_report(employee_id, report_id, rows, description):
    with Transaction():
        report = _get_report(employee_id, report_id, False)
        if report is None:
            raise NoSuchReport()
        if report['status'] != 'pending':
            raise BadReportStatus(report['status'])
        _upsert_report(employee_id, report_id, rows)
        if description is not None:
            report['description'] = description
        report['updated'] = datetime.datetime.utcnow()
        datastore.put([report])


def delete_report(employee_id, report_id, force):
    with Transaction():
        report = _get_report(employee_id, report_id, False)
        if report is None:
            raise NoSuchReport()
        if report['status'] != 'pending' and not force:
            raise BadReportStatus(report['status'])
        count = _purge_report_items(report)
        datastore.delete([report.key])
    return count


def approve_report(employee_id, report_id, check_number):
    with Transaction():
        report = _get_report(employee_id, report_id, False)
        if report is None:
            raise NoSuchReport()
        if report['status'] != 'pending':
            raise BadReportStatus(report['status'])
        report['updated'] = datetime.datetime.utcnow()
        report['status'] = 'paid'
        report['check_number'] = check_number
        datastore.put([report])


def reject_report(employee_id, report_id, reason):
    with Transaction():
        report = _get_report(employee_id, report_id, False)
        if report is None:
            raise NoSuchReport()
        if report['status'] != 'pending':
            raise BadReportStatus(report['status'])
        report['updated'] = datetime.datetime.utcnow()
        report['status'] = 'rejected'
        report['reason'] = reason
        datastore.put([report])


def upload_receipt(employee_id, report_id, filename, bucket=None):
    if bucket is None:
        bucket = _get_bucket()
    basename = os.path.split(filename)[1]
    blob = bucket.new_blob('%s/%s/%s' % (employee_id, report_id, basename))
    if blob in bucket:
        raise DuplicateReceipt(blob.name)
    blob.upload_from_filename(filename)


def delete_receipt(employee_id, report_id, filename, bucket=None):
    if bucket is None:
        bucket = _get_bucket()
    basename = os.path.split(filename)[1]
    blob = bucket.new_blob('%s/%s/%s' % (employee_id, report_id, basename))
    if blob not in bucket:
        raise NoSuchReceipt(blob.name)
    blob.delete()


def list_receipts(employee_id, report_id, bucket=None):
    if bucket is None:
        bucket = _get_bucket()
    prefix = '%s/%s/' % (employee_id, report_id)
    for key in bucket.iterator(prefix=prefix, delimiter='/'):
        name = urllib.unquote(key.name)
        yield name.rsplit('/', 1)[-1]


def download_receipt(employee_id, report_id, filename, bucket=None):
    if bucket is None:
        bucket = _get_bucket()
    basename = os.path.split(filename)[1]
    blob = bucket.new_blob('%s/%s/%s' % (employee_id, report_id, basename))
    if blob not in bucket:
        raise NoSuchReceipt(blob.name)
    blob.download_to_filename(filename)
