import os
import shutil
import subprocess
import sys

class ExpressServer:

    def __init__(self):
        self.template = """
        const express = require("express");\n
        const app = express();\n
        {variables}\n
        {functions}\n
        {endpoints}\n
        app.listen({port}, () => console.log("Django Rest Mock Server: Listening on port {port}"));\n
        """
        self.constructed = ''

    def __str__(self):
        if self.constructed:
            return self.constructed.strip().replace("\n", "")
        raise Exception('Call construct() first')

    def to_string(self):
        return str(self)

    def construct(self, variables, functions, endpoints, port=8000):
        self.constructed = self.template.format(
            variables=variables,
            functions=functions,
            endpoints=endpoints,
            port=port
        )

    def generate(self, file_path='index.js'):
        with open(file_path, 'w') as f:
            f.write(self.to_string())

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

        try:
            subprocess.call(["node", file_path])
        except KeyboardInterrupt:
            os.remove(file_path)
            path_prefix = os.getcwd()
            os.remove(path_prefix + '/package-lock.json')
            shutil.rmtree(path_prefix + '/node_modules')
            sys.stdout.write('Mock server shutdown.\n')
