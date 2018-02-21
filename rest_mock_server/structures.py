class BaseFactory:

    def __init__(self):
        self.constructed = ''
        self.options = dict(strip=True, remove_space=True, strip_newline=False, strip_tab=False)
        self.is_constructed = False

    def __str__(self):
        if self.is_constructed:
            func = self.constructed

            if self.options['strip']:
                func = func.strip()

            if self.options['remove_space']:
                func = func.replace(" ", "")

            if self.options['strip_newline']:
                func = func.replace("\n", "")

            if self.options['strip_tab']:
                func = func.replace("\t", "")

            return self.constructed.strip().replace(" ", "").replace("\n", "").replace("\t", "")
        else:
            raise Exception('Need to call construct() first')


class Variable(BaseFactory):

    def __init__(self):
        super().__init__()
        self.constructed = "{var_type} {var_name} = {var_val};"
    
    def construct(self, var_type, var_name, var_val):
        self.constructed = self.constructed.format(
            var_type=var_type,
            var_name=var_name,
            var_val=var_val
        )
        self.is_constructed = True


class Function(BaseFactory):

    def __init__(self):
        super().__init__()
        self.constructed = """
        function {func_name} () {
            {func_body}
        }
        """

    def construct(self, name, body):
        self.constructed = self.constructed.format(
            func_name=name,
            func_body=body
        )
        self.is_constructed = True


class Endpoint(BaseFactory):

    def __init__(self):
        super().__init__()
        self.constructed = 'app.%s("%s", (req, res) => {%s});\n'
        self.options['strip_newline'] = False

    def construct(self, method, uri, response):
        self.constructed = self.constructed % (method, uri, response)
        self.is_constructed = True

    def construct_response(self, method, uri, response):
        """Shortcut to construct direct response"""
        self.construct(method, uri, 'res.send(%s)' % response)
