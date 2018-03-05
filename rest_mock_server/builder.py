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
        try:
            if len(detail['response']) > 1:
                for resp in detail['response']:
                    parsed_resp = ast.literal_eval(resp)
                    tmp_copy_resp = deepcopy(parsed_resp)
                    cleaned_resp = {}
                    # Remove meta keys or hidden attributes from cleaned resp
                    for k, v in tmp_copy_resp.items():
                        if '__' not in k and '--' not in k:
                            cleaned_resp[k] = v
                    if parsed_resp['__key_position'] == 'url':
                        unique_key = parsed_resp['__key_name']
                        constructed_url = re.sub(r'\_\_key', str(parsed_resp[unique_key]), base_url)
                        store[constructed_url] = {
                            'data': cleaned_resp,
                            'pk': True,
                            'pkName': parsed_resp['__key_name'],
                            'position': 'url',
                            'options': parsed_resp.get('__options', '{}')
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
                            'position': 'query',
                            'options': parsed_resp.get('__options', '{}')
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
                parsed_resp = ast.literal_eval(detail['response'][0])
                tmp_copy_resp = deepcopy(parsed_resp)
                cleaned_resp = {}
                # Remove meta keys or hidden attributes from cleaned resp
                for k, v in tmp_copy_resp.items():
                    if '__' not in k and '--' not in k:
                        cleaned_resp[k] = v

                store[base_url] = {
                    'data': cleaned_resp,
                    'pk': False,
                    'options': parsed_resp.get('__options', '{}')
                }
        except KeyError:
            # PUT, PATCH, DELETE
            pass
    return store


def clean_url(full_url, store, method):
    # Check in store if the base url has individual instances
    u = urlparse(full_url)
    url = '/' + method + '__' + u.path
    query = parse_qs(u.query)
    test_url = url.replace('__key', '(.*)')
    list_url = None
    r = re.compile(test_url)
    if '__key' in url:
        count = 0
        for k, v in store.items():
            options = v.get('options', '{}')
            exclude_key = False
            options = ast.literal_eval(options)
            if options is not None:
                exclude_key = options.get('excludeKey', False)
            search = r.search(k)
            if search is not None:
                list_url = re.sub(r'\/?\_\_key', '', url)
                count += 1
                if exclude_key:
                    url = re.sub(r'\/?\_\_key', '', url)
                    break
                url = re.sub(r'\/?\_\_key', '/:id', url)
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


def build(port=8000, fixtures=None):
    extractor = Extractor()
    parser = Parser(extractor.url_details, fixtures)
    parser.parse()
    url_details = parser.results
    _store = get_store(url_details)
    store = json.dumps(_store)
    variables = str(Variable('let', 'store', store))
    functions = DATA_FINDER + GET_HANDLER + MODIFY_HANDLER + POST_HANDLER
    endpoints = []
    endpoint_uris = []
    for u in parser.results:
        endpoint = Endpoint()
        if u['method'].lower() in ['get', 'post']:
            method = u['method'].lower()
        else:
            method = 'modify'
        response = "const data = {}Handler(req);res.json(data);".format(method)

        # Check in store if the base url has individual instances
        u['url'], list_url = clean_url(u['full_url'], _store, u['method'].lower())
        if list_url is not None and u['method'].lower() == 'get':
            list_endpoint = Endpoint()
            list_endpoint.construct('get', list_url, response)
            if str(list_endpoint) not in endpoints:
                endpoints.append(str(list_endpoint))
            if list_endpoint.uri not in endpoint_uris:
                endpoint_uris.append(list_endpoint.uri)

        if method == 'modify':
            without_prefix = re.sub(r'\/(\w+)\_\_', '', u['url'])
            for k, v in _store.items():
                if without_prefix in k:
                    options = v.get('options', '{}')
                    options = ast.literal_eval(options)
                    modifiers = []
                    if options is not None:
                        modifiers = options.get('modifiers', [])
                    if modifiers:
                        for mod in modifiers:
                            if u['method'].lower() == mod:
                                mod_endpoint = Endpoint()
                                uri = without_prefix
                                if v.get('position') is not None and v['position'] == 'url':
                                    uri = re.sub(r'\/?\_\_key', '/:id', u['full_url'])
                                mod_endpoint.construct(u['method'].lower(), uri, response)
                                if str(mod_endpoint) not in endpoints:
                                    endpoints.append(str(mod_endpoint))
                                if mod_endpoint.uri not in endpoint_uris:
                                    endpoint_uris.append(mod_endpoint.uri)
        else:
            endpoint.construct(u['method'], u['url'], response)
            if str(endpoint) not in endpoints:
                endpoints.append(str(endpoint))
            if endpoint.uri not in endpoint_uris:
                endpoint_uris.append(endpoint.uri)

    endpoints = ''.join(endpoints)
    express = ExpressServer()
    express.construct(variables, functions, endpoints, port)
    return express
