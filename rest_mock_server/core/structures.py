import os
import re


BASE_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'templates')


class BaseFactory:

    def __init__(self):
        self.constructed = ''
        self.options = dict(strip=True, remove_space=True, strip_newline=False, strip_tab=False)

    def __str__(self):
        if self.is_constructed:
            return self.constructed
        else:
            raise Exception('Need to call construct() first')
    
    @property
    def is_constructed(self):
        return bool(self.constructed)


class Variable(BaseFactory):

    def __init__(self, var_type, var_name, var_val):
        super().__init__()
        with open(os.path.join(BASE_TEMPLATE_PATH, 'variable.template'), 'r', encoding='utf-8') as f:
            self.constructed = f.read()
        self.construct(var_type, var_name, var_val)
    
    def construct(self, var_type, var_name, var_val):
        self.constructed = self.constructed % (
            var_type,
            var_name,
            var_val
        )


class ResponseBody(BaseFactory):

    def __init__(self, method):
        super().__init__()
        with open(os.path.join(BASE_TEMPLATE_PATH, 'response.template'), 'r', encoding='utf-8') as f:
            self.constructed = f.read()
        self.construct(method)
    
    def construct(self, method):
        self.constructed = self.constructed % method


class Endpoint(BaseFactory):

    def __init__(self):
        super().__init__()
        with open(os.path.join(BASE_TEMPLATE_PATH, 'endpoint.template'), 'r', encoding='utf-8') as f:
            self.constructed = f.read()
        self.uri = None

    def construct(self, method, uri, response):
        cleaned_uri = re.findall(r'\/\w+\_\_(\/.*)', uri)
        if cleaned_uri:
            uri = cleaned_uri[0]
        self.constructed = self.constructed % (method, uri, response)
        self.uri = uri
