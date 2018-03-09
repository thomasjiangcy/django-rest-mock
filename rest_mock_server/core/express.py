import os
import shutil
import subprocess
import sys

from jsmin import jsmin

class ExpressServer:

    def __init__(self):
        with open(os.path.dirname(__file__) + '/templates/express.template', 'r', encoding='utf-8') as express_template:
            self.template = express_template.read()
        self.constructed = ''

    def __str__(self):
        if self.constructed:
            return self.constructed
        raise Exception('Call construct() first')

    def to_string(self):
        return str(self)

    def construct(self, variables, functions, endpoints, port=8000):
        self.constructed = self.template % (
            variables,
            functions,
            endpoints,
            port,
            port
        )

    def _generate(self, file_path, no_minify):
        with open(file_path, 'w', encoding='utf-8') as f:
            # if we are, by chance, opening an existing index.js file - we want to remove everything first
            f.truncate()
            if no_minify:
                f.write(self.to_string())
                return
            f.write(jsmin(self.to_string()).replace('\n', ''))

    def generate(self, file_path='index.js', no_minify=False):
        if os.path.isfile(file_path):
            file_exists_override = ''
            while file_exists_override.lower() not in ['y', 'n']:
                file_exists_override = input('File "{}" exists. This will overwrite all contents in the file, continue? [y/n]'.format(file_path))
            if file_exists_override.lower() == 'y':
                self._generate(file_path, no_minify)
            else:
                print('Cancelling operation.')
                sys.exit(0)
        else:
            self._generate(file_path, no_minify)

    def start_server(self, file_path='index.js'):
        # Check if node is installed
        try:
            subprocess.check_output(['node', '-v'])
        except:
            sys.stdout.write('Node.js not installed properly.\n')
            sys.exit(0)

        # Check if Express is installed
        try:
            subprocess.check_output(['npm', 'list', 'express'])
        except:
            subprocess.call(['npm', 'install', 'express'])
            subprocess.call(['npm', 'install', 'cors'])

        try:
            subprocess.call(["node", file_path])
        except KeyboardInterrupt:
            os.remove(file_path)
            path_prefix = os.getcwd()
            os.remove(path_prefix + '/package-lock.json')
            shutil.rmtree(path_prefix + '/node_modules')
            sys.stdout.write('Mock server shutdown.\n')
