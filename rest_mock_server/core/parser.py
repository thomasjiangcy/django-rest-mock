"""
Parser needs to make sense of:

* Query params
* Request method - whether it is a retrieval or modification (GET vs the rest)
* Data to generate (and the corresponding number of endpoints) - uses Faker to generate

"""

import glob
import json
from urllib.parse import urlparse, parse_qs

from faker import Faker

from rest_mock_server.core.factory import FixtureFactory


class Parser:

    def __init__(self, url_details, fixtures=None):
        self.url_details = url_details
        self._results = None
        self.fixture_paths = fixtures
        self.fixture_data = None
        if self.fixture_paths is not None:
            fixture_data = {}
            for path in self.fixture_paths:
                if not path.endswith('/'):
                    path = path + '/'
                for f in glob.glob(path + '*.json'):
                    with open(f) as fixture_file:
                        fixture = json.load(fixture_file)
                        key_name = f.split('/')[-1][:-5]
                        fixture_data[key_name] = fixture
            self.fixture_data = fixture_data

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

    def _parse_response(self, response):
        resp = json.loads(response)
        factory = FixtureFactory(resp, self)
        return factory.generate()

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
