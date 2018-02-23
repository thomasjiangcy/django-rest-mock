import re

class BaseFactory:

    def __init__(self):
        self.constructed = ''
        self.options = dict(strip=True, remove_space=True, strip_newline=False, strip_tab=False)
        self.is_constructed = False

    def __str__(self):
        if self.is_constructed:
            return self.constructed
        else:
            raise Exception('Need to call construct() first')


class Variable(BaseFactory):

    def __init__(self, var_type, var_name, var_val):
        super().__init__()
        self.constructed = "%s %s = %s;"
        self.construct(var_type, var_name, var_val)
    
    def construct(self, var_type, var_name, var_val):
        self.constructed = self.constructed % (
            var_type,
            var_name,
            var_val
        )
        self.is_constructed = True


class Function(BaseFactory):

    def __init__(self):
        super().__init__()
        self.constructed = "function %s(%s) {%s};"

    def construct(self, name, args, body):
        self.constructed = self.constructed % (
            name,
            args,
            body
        )
        self.is_constructed = True


class Endpoint(BaseFactory):

    def __init__(self):
        super().__init__()
        self.constructed = 'app.%s("%s", (req, res) => {%s});\n'
        self.uri = None

    def construct(self, method, uri, response):
        cleaned_uri = re.findall(r'\/\w+\_\_(\/.*)', uri)
        if cleaned_uri:
            uri = cleaned_uri[0]
        self.constructed = self.constructed % (method, uri, response)
        self.uri = uri
        self.is_constructed = True
