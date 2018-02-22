"""
Parser needs to make sense of:

* Query params
* Request method - whether it is a retrieval or modification (GET vs the rest)
* Data to generate (and the corresponding number of endpoints) - uses Faker to generate

"""

import json
import re
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

        key_type, key_name, key_position = None, None, None
        if '__key'in url:
            key_position = 'url'
            match = re.findall(r'\_\_key\[(.*)\]', url)
            if match is not None:
                key_details = match[0]
                key_name, key_type = key_details.split(':')
        else:
            # Check if key is in params
            for k, v in query.items():
                _vals = [x for x in v if '__key' in x]
                if _vals:
                    key_name = k
                    key_position = 'query'
                    match = re.findall(r'\_\_key\[(.*)\]', _vals[0])
                    if match is not None:
                        key_type = match[0]

        return {
            'full_url': url_string.strip(),
            'url': url.strip(),
            'query': query,
            '__key_type': key_type,
            '__key_position': key_position,
            '__key_name': key_name
        }

    @staticmethod
    def _parse_response(response):
        resp = json.loads(response)
        count = resp.get("__mockcount", 1)
        generated_responses = []
        for _ in range(count):
            response = {}
            for k, v in resp.items():
                if k == '__mockcount':
                    continue
                # Check if value fulfils the dynamic syntax
                v = str(v)  # treat the value as a string regardless of its actual data type
                has_syntax = re.findall(r'<(.*)>', v, flags=re.DOTALL)
                if has_syntax is not None:
                    fake_val = re.sub(r'<(.*)>', replace_faker_attr, v, flags=re.DOTALL)
                    response[k] = fake_val
                else:
                    response[k] = v
            generated_responses.append(json.dumps(response))
        return generated_responses
    
    def parse(self):
        results = []
        for url in self.url_details:
            url_detail = self._parse_url(url['url'])
            url_detail['url'] = '/' + url['method'].lower() + '__' + url_detail['url']
            url_detail['method'] = url['method']
            url_detail['response'] = self._parse_response(url['response'])
            results.append(url_detail)
        print(results)
        self._results = results