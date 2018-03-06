import os
import shutil
import subprocess
import sys

class ExpressServer:

    def __init__(self):
        self.template = """
const express = require("express");
const cors = require("cors");
const bodyParser = require('body-parser');
const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
%s
%s
%s
app.listen(%s, () => console.log("Django Rest Mock Server: Listening on port %s"));""".strip()
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
            subprocess.call(['npm', 'install', 'cors'])

        try:
            subprocess.call(["node", file_path])
        except KeyboardInterrupt:
            os.remove(file_path)
            path_prefix = os.getcwd()
            os.remove(path_prefix + '/package-lock.json')
            shutil.rmtree(path_prefix + '/node_modules')
            sys.stdout.write('Mock server shutdown.\n')
