from pyramid.renderers import get_renderer
from pyramid.view import view_config

from . import get_employee_info
from . import get_report_info
from . import list_employees

def get_main_template(request):
    main_template = get_renderer('templates/main.pt')
    return main_template.implementation()


@view_config(route_name='home', renderer='templates/home.pt')
def home_page(request):
    return {}


@view_config(route_name='employees', renderer='templates/employees.pt')
def show_employees(request):
    return {'employees': list_employees()}


def fixup_report(report):
    if report['status'] == 'paid':
        report['status'] = 'paid, check #%s' % report.pop('memo')
    elif report['status'] == 'rejected':
        report['status'] = 'rejected, #%s' % report.pop('memo')
    return report

@view_config(route_name='employee', renderer='templates/employee.pt')
def show_employee(request):
    employee_id = request.matchdict['employee_id']
    info = get_employee_info(employee_id)
    info['reports'] = [fixup_report(report) for report in info['reports']]
    return info

@view_config(route_name='report', renderer='templates/report.pt')
def show_report(request):
    employee_id = request.matchdict['employee_id']
    report_id = request.matchdict['report_id']
    return {'report':
            fixup_report(get_report_info(employee_id, report_id))}


def includeme(config):
    config.add_request_method(callable=get_main_template,
                              name='main_template',
                              property=True,
                              reify=True,
                             )
