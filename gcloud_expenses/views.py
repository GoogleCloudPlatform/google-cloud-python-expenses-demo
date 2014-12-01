from pyramid.renderers import get_renderer
from pyramid.view import view_config


def get_main_template(request):
    main_template = get_renderer('templates/main.pt')
    return main_template.implementation()

@view_config(route_name='home', renderer='templates/home.pt')
def my_view(request):
    return {}

def includeme(config):
    config.add_request_method(callable=get_main_template,
                              name='main_template',
                              property=True,
                              reify=True,
                             )
