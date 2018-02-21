"""
Generates fake endpoints for a specified amount and type of data
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

            self.endpoints.append({
                'url': url.strip(),
                'method': method,
                'response': json.dumps(json.loads(response))
            })
