from pyramid.renderers import get_renderer
from pyramid.view import view_config

from . import list_employees
from . import list_reports

def get_main_template(request):
    main_template = get_renderer('templates/main.pt')
    return main_template.implementation()


@view_config(route_name='home', renderer='templates/home.pt')
def home_page(request):
    return {}


@view_config(route_name='employees', renderer='templates/employees.pt')
def show_employees(request):
    return {'employees': list_employees()}


@view_config(route_name='employee', renderer='templates/employee.pt')
def show_employee(request):
    employee_id = request.matchdict['employee_id']
    return {'employee_id': employee_id,
            'reports': list_reports(employee_id),
           }


def includeme(config):
    config.add_request_method(callable=get_main_template,
                              name='main_template',
                              property=True,
                              reify=True,
                             )
