"""
Generates mock Express server file
"""

import os

from .extractor import Extractor
from .factory import EndpointFactory


INDEX_FILE = os.getenv('INDEX_FILE', 'index.js')
MOCK_SERVER_PORT = os.getenv('MOCK_SERVER_PORT', '8000')


def main():
    extractor = Extractor()
    factory = EndpointFactory(extractor.url_details)
    factory.generate()

    with open(INDEX_FILE, 'w') as f:
        f.write('const express = require("express");\n')
        f.write('const app = express();\n')

        for endpoint in factory.endpoints:
            f.write('app.{method}({url}, (req, res) => {res.send({response});});\n'.format(
                method=endpoint['method'],
                url=endpoint['url'],
                response=endpoint['response']
            ))

        f.write('app.listen({port}, () => console.log("Listening on port {port}"));\n'.format(port=MOCK_SERVER_PORT))

if __name__ == '__main__':
    main()
