import ast
import json
import re
from copy import deepcopy
from urllib.parse import urlparse, parse_qs

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
        has_instances = False
        if len(detail['response']) > 1:
            for resp in detail['response']:
                parsed_resp = ast.literal_eval(resp)
                tmp_copy_resp = deepcopy(parsed_resp)
                cleaned_resp = {}
                # Remove meta keys from cleaned resp
                for k, v in tmp_copy_resp.items():
                    if '__' not in k:
                        cleaned_resp[k] = v

                if parsed_resp['__key_position'] == 'url':
                    unique_key = parsed_resp['__key_name']
                    constructed_url = re.sub(r'\_\_key', str(parsed_resp[unique_key]), base_url)
                    store[constructed_url] = {
                        'data': cleaned_resp,
                        'pk': True,
                        'pkName': parsed_resp['__key_name'],
                        'position': 'url'
                    }
                    has_instances = True
                elif parsed_resp['__key_position'] == 'query':
                    unique_key = parsed_resp['__key_name']
                    if not base_url[-1] == '/':
                        url_with_slash = base_url + '/'
                    constructed_url = url_with_slash + '__pk/' + str(parsed_resp[unique_key])
                    constructed_url = re.sub(r'\_\_key', '', constructed_url)  # if '__key' hasn't already been replaced, remove it
                    store[constructed_url] = {
                        'data': cleaned_resp,
                        'pk': True,
                        'pkName': parsed_resp['__key_name'],
                        'position': 'query'
                    }
                    has_instances = True
            
            if has_instances:
                # This endpoint has multiple instances
                # we will need to create a new endpoint to list all
                # these instances
                list_url = re.sub(r'\/?\_\_key', '', base_url)
                instances = []
                for k, v in store.items():
                    if list_url in k:
                        instances.append(v['data'])
                store[list_url] = {'data': instances}

        else:
            base_url = re.sub(r'\/?\_\_key', '', base_url)  # if '__key' hasn't already been replaced, remove it
            parsed_resp = json.loads(detail['response'][0])
            tmp_copy_resp = deepcopy(parsed_resp)
            cleaned_resp = {}
            # Remove meta keys from cleaned resp
            for k, v in tmp_copy_resp.items():
                if '__' not in k:
                    cleaned_resp[k] = v

            store[base_url] = {
                'data': cleaned_resp,
                'pk': False
            }
    return store


def clean_url(full_url, store):
    # Check in store if the base url has individual instances
    u = urlparse(full_url)
    url = u.path
    query = parse_qs(u.query)

    test_url = url.replace('__key', '(.*)')
    list_url = None
    r = re.compile(test_url)
    if '__key' in url:
        count = 0
        for k in store.keys():
            if r.match(k) is not None:
                list_url = re.sub(r'\/?\_\_key', '', url)
                url = re.sub(r'\/?\_\_key', '/:id', url)
                count += 1
                break
        if not count:
            url = re.sub(r'\/?\_\_key', '', url)
    elif query and '__key' in full_url:
        count = 0
        for k in store.keys():
            if r.search(k) is not None:
                list_url = url
                count += 1
                break
    return url, list_url


def build(port=8000):
    extractor = Extractor()
    parser = Parser(extractor.url_details)
    parser.parse()
    url_details = parser.results
    _store = get_store(url_details)
    store = json.dumps(_store)
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

        # Check in store if the base url has individual instances
        u['url'], list_url = clean_url(u['full_url'], _store)

        if list_url is not None and u['method'].lower == 'get':
            list_endpoint = Endpoint()
            list_endpoint.construct('get', list_url, response)
            if str(list_endpoint) not in endpoints:
                endpoints.append(str(list_endpoint))

        endpoint.construct(u['method'], u['url'], response)
        if str(endpoint) not in endpoints:
            endpoints.append(str(endpoint))
    endpoints = ''.join(endpoints)
    express = ExpressServer()
    express.construct(variables, functions, endpoints, port)
    return express
