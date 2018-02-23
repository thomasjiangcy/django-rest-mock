"""
Parser needs to make sense of:

* Query params
* Request method - whether it is a retrieval or modification (GET vs the rest)
* Data to generate (and the corresponding number of endpoints) - uses Faker to generate

"""

import ast
import json
import re
from copy import deepcopy
from urllib.parse import urlparse, parse_qs

from faker import Faker


PYTHON_DATATYPES = ['str', 'int', 'float', 'decimal', 'set', 'dict', 'list', 'tuple', 'bool']
fake = Faker()


def validate_fake_val(fake_val, fake_func, minimum, maximum):
    if (type(fake_val) == 'int' or type(fake_val) == 'float' or type(fake_val) == 'decimal') and\
        (minimum or maximum):
        if minimum and not maximum:
            while fake_val < minimum:
                fake_val = fake_func()  # keep trying until fake_val > minimum
        elif minimum and maximum:
            while fake_val < minimum or fake_val > maximum:
                fake_val = fake_func()  # keep trying until minimum <= fake_val <= maximum
        elif not minimum and maximum:
            while fake_val > maximum:
                fake_val = fake_func()  # keep trying until fake_val <= maximum

    elif type(fake_val) == 'str' and (minimum or maximum):
        if minimum and not maximum:
            fake_val = fake_val[minimum:]
        elif minimum and maximum:
            fake_val = fake_val[minimum:maximum]
        elif not minimum and maximum:
            fake_val = fake_val[:maximum]

    # For all other data types, min/max attributes will have no effect
    return str(fake_val)  # make sure to return a 'str' type


def replace_faker_attr(matchobj):
    attr = matchobj.group(0).replace('<', '').replace('>', '')
    # Check if optional arguments are specified - syntax is <attr:min:max>
    _split = attr.split(":")
    if len(_split) > 1:
        # Get the attr and value range (min/max)
        attr, val_range = _split[0], _split[1:]
        if len(val_range) > 1:
            minimum, maximum = val_range
        else:
            minimum, maximum = val_range[0], 0
    else:
        attr, minimum, maximum = _split[0], 0, 0
    # Min, max will be applied in a slice function if the data is a string
    if attr in PYTHON_DATATYPES:
        attr = 'py' + attr

    try:
        fake_func = getattr(fake, attr)
        fake_val = fake_func()
        fake_val = validate_fake_val(fake_val, fake_func, minimum, maximum)
        return fake_val
    except AttributeError:
        return attr


class Parser:
    
    def __init__(self, url_details):
        self.url_details = url_details
        self._results = None
    
    @property
    def results(self):
        if self._results is not None:
            return self._results
        raise Exception('URL details need to be parsed first, call parse() to generate results.')
    
    @staticmethod
    def _parse_url(url_string):
        u = urlparse(url_string)
        url = u.path
        query = parse_qs(u.query)

        return {
            'full_url': url_string.strip(),
            'url': url.strip(),
            'query': query
        }

    @staticmethod
    def _parse_response(response):
        resp = json.loads(response)
        count = resp.get("__mockcount", 1)
        generated_responses = []
        for _ in range(count):
            response = {}
            key_type, key_name, key_position = [None] * 3
            for k, v in resp.items():
                if k == '__mockcount' or k == '__key_position':
                    continue
                if k == '__key':
                    try:
                        key_position = resp['__key_position']
                    except KeyError:
                        raise Exception("'__key_position' must be present if '__key' is present")
                    v = v.replace('<', '').replace('>', '')
                    key_name, key_type = v.split(':')
                    
                # Check if value fulfils the dynamic syntax
                v_type = type(deepcopy(v)).__name__
                v = str(v)  # treat the value as a string regardless of its actual data type
                has_syntax = re.findall(r'<\w+(\d+)?(\:)?(\d+)?(\:)?(\d+)?>', v, flags=re.DOTALL)

                if has_syntax:
                    fake_val = re.sub(r'<\w+(\d+)?(\:)?(\d+)?(\:)?(\d+)?>', replace_faker_attr, v, flags=re.DOTALL)
                    if v_type in ['list', 'dict', 'tuple', 'set']:
                        response[k] = ast.literal_eval(fake_val)
                    else:
                        response[k] = fake_val
                else:
                    if k == '__key': continue
                    response[k] = v

            response['__key_type'] = key_type
            response['__key_position'] = key_position
            response['__key_name'] = key_name
            generated_responses.append(str(response))
        return generated_responses
    
    def parse(self):
        results = []
        for url in self.url_details:
            url_detail = self._parse_url(url['url'])
            method = 'get' if url['method'].lower() in ['get', 'put', 'patch', 'delete'] else 'post'
            url_detail['url'] = '/' + method + '__' + url_detail['url']
            url_detail['method'] = url['method']
            try:
                url_detail['response'] = self._parse_response(url['response'])
            except KeyError:
                pass
            results.append(url_detail)
        self._results = results
