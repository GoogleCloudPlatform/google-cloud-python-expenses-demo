from pyramid.config import Configurator

from . import _get_bucket
from . import _get_dataset
from .pool import ResourcePool

datasets = ResourcePool()
buckets = ResourcePool()

def _get_create_dataset(self):
    dataset = datasets.check_out()
    if dataset is None:
        dataset = _get_dataset()
        datasets.add(dataset, checked_out=True)
    def _return(self):
        datasets.check_in(dataset)
    self.add_finished_callback(_return)
    return dataset

def _get_create_bucket(self):
    bucket = buckets.check_out()
    if bucket is None:
        bucket = _get_bucket()
        buckets.add(bucket, checked_out=True)
    def _return(self):
        buckets.check_in(bucket)
    self.add_finished_callback(_return)
    return bucket

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_request_method(_get_create_dataset, 'dataset', reify=True)
    config.add_request_method(_get_create_bucket, 'bucket', reify=True)
    config.include('pyramid_chameleon')
    config.include('.views')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('employees', '/employees/')
    config.add_route('employee', '/employees/{employee_id}')
    config.add_route('report', '/employees/{employee_id}/{report_id}')
    config.scan()
    return config.make_wsgi_app()
