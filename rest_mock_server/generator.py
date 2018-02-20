"""
Generates mock Express server file
"""

import os

from .extractor import Extractor
from .factory import EndpointFactory


def main(output=None, port=8000):
    extractor = Extractor()
    factory = EndpointFactory(extractor.url_details)
    factory.generate()

    output_path = output if output is not None else 'index.js'

    with open(output_path, 'w') as f:
        f.write('const express = require("express");\n')
        f.write('const app = express();\n')

        for endpoint in factory.endpoints:
            f.write('app.%s("%s", (req, res) => {res.send(%s);});\n' % (
                endpoint['method'],
                endpoint['url'],
                endpoint['response']
            ))

        f.write('app.listen({port}, () => console.log("Django Mock JSON Server: Listening on port {port}"));\n'.format(port=port))
