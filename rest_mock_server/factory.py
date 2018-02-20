"""
Generates fake endpoints for a specified amount and type of data

The factory can generate dynamic values for endpoints if necessary.
e.g. { "id": <int:10> } would translate into 10 random integers

Possible dynamic values are:
- int
- str
- sha256
- name
- uri
"""

import json
import re

from faker import Faker


class EndpointFactory:

    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.endpoints = []

    def generate(self):
        for details in self.raw_data:
            url = details['url']
            method = details['method']
            response = details['response']

            # TODO: Parse JSON response and see if any dynamic values are present
            # parsed_response = json.loads(response)
            # for k, v in parsed_response:
            #     reg = re.findall(r'<(.*)>', v, flags=re.DOTALL)
            #     endpoint = {}
            #     if reg:
            #         for r in reg:
            #             if ':' in r:
            #                 dynamic_type, instances = r.split(':')
            #                 self._factory_generate(dynamic_type, instances)
            #                 continue
            self.endpoints.append({
                'url': url.strip(),
                'method': method,
                'response': json.dumps(json.loads(response))
            })

    # def _factory_generate(self, dynamic_type, instances):
