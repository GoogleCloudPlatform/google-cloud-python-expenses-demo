from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('.views')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('employees', '/employees/')
    config.add_route('employee', '/employees/{employee_id}')
    config.add_route('report', '/employees/{employee_id}/{report_id}')
    config.scan()
    return config.make_wsgi_app()
