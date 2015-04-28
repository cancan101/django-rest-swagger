import json

from django.core.management.base import BaseCommand

from rest_framework_swagger.urlparser import UrlParser
from rest_framework_swagger import SWAGGER_SETTINGS
from rest_framework_swagger.docgenerator import DocumentationGenerator


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--path',
                    action='store',
                    default=None)
        parser.add_argument('--urlconf',
                    action='store',
                    default=None)

    def handle(self, path=None, urlconf=None, *args, **options):
        if path is None:
            data = self.get_resource_listing(urlconf=urlconf)
        else:
            data = self.get_api_declaration(path, urlconf=urlconf)
        print json.dumps(data, indent=2, sort_keys=True)

    def get_resource_listing(self, urlconf):
        apis = self.get_apis(urlconf=urlconf)
        data = {
            'apiVersion': SWAGGER_SETTINGS.get('api_version', ''),
            'swaggerVersion': '1.2',
            'apis': apis,
            'info': SWAGGER_SETTINGS.get('info', {
                # 'contact': '',
                'description': '',
                'license': '',
                'licenseUrl': '',
                'termsOfServiceUrl': '',
                'title': '',
            }),
        }
        return data

    def get_apis(self, urlconf):
        apis = []
        resources = self.get_resources(urlconf=urlconf)

        for path in resources:
            apis.append({
                'path': "/%s" % path,
            })
        return apis

    def get_resources(self, urlconf):
        urlparser = UrlParser()
        apis = urlparser.get_apis(exclude_namespaces=SWAGGER_SETTINGS.get('exclude_namespaces'), urlconf=urlconf)
        resources = urlparser.get_top_level_apis(apis)
        return resources

    def get_api_declaration(self, path, urlconf):
        api_full_uri = SWAGGER_SETTINGS.get('api_full_uri')

        apis = self.get_api_for_resource(path, urlconf=urlconf)
        generator = DocumentationGenerator()

        return {
            'apiVersion': SWAGGER_SETTINGS.get('api_version', ''),
            'swaggerVersion': '1.2',
            'basePath': api_full_uri.rstrip('/'),
            'resourcePath': '/' + path,
            'apis': generator.generate(apis),
            'models': generator.get_models(apis),
        }

    def get_api_for_resource(self, filter_path, urlconf):
        urlparser = UrlParser()
        return urlparser.get_apis(filter_path=filter_path, urlconf=urlconf)
