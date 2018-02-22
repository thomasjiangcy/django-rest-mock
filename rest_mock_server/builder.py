import ast
import json
import re

from .core.express import ExpressServer
from .core.extractor import Extractor
from .core.functions import DATA_FINDER, GET_HANDLER, MODIFY_HANDLER, POST_HANDLER
from .core.parser import Parser
from .core.structures import Endpoint, Variable


def get_store(url_details):
    """
    The state of the mock server will be stored in the resulting
    object created here
    """
    store = {}
    for detail in url_details:
        base_url = detail['url'].strip()
        if len(detail['response']) > 1:
            if detail['__key_position'] == 'url':
                for resp in detail['response']:
                    unique_key = detail['__key_name']
                    constructed_url = re.sub(r'\_\_key\[.*\]', str(ast.literal_eval(resp)[unique_key]), base_url)
                    store[constructed_url] = {
                        'data': resp,
                        'pk': True,
                        'pkName': detail['__key_name'],
                        'position': 'url'
                    }
            elif detail['__key_position'] == 'query':
                for resp in detail['response']:
                    unique_key = detail['__key_name']
                    if not base_url[-1] == '/':
                        base_url = base_url + '/'
                    constructed_url = base_url + '__pk/' + str(ast.literal_eval(resp)[unique_key])
                    store[constructed_url] = {
                        'data': resp,
                        'pk': True,
                        'pkName': detail['__key_name'],
                        'position': 'query'
                    }
        else:
            store[base_url] = {
                'data': detail['response'][0],
                'pk': False
            }
    return store

def build(port=8000):
    extractor = Extractor()
    parser = Parser(extractor.url_details)
    parser.parse()
    url_details = parser.results
    store = json.dumps(get_store(url_details))
    variables = str(Variable('let', 'store', store))
    functions = DATA_FINDER + GET_HANDLER + MODIFY_HANDLER + POST_HANDLER
    endpoints = []
    for u in parser.results:
        endpoint = Endpoint()
        if u['method'].lower() in ['get', 'post']:
            method = u['method'].lower()
        else:
            method = 'modify'
        response = "const data = {}Handler(req);res.json(data);".format(method)
        endpoint.construct(u['method'], u['url'], response)
        endpoints.append(str(endpoint))
    endpoints = ''.join(endpoints)
    express = ExpressServer()
    express.construct(variables, functions, endpoints, port)
    return express
