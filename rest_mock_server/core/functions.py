"""
Core functions to be placed in Express Server
"""

import os


BASE_PATH = os.path.dirname(__file__) + '/js/'


def data_finder():
    with open(BASE_PATH + 'datafinder.js', 'r') as datafinder:
        func = datafinder.read()
        return func

def get_handler():
    with open(BASE_PATH + 'gethandler.js', 'r') as gethandler:
        func = gethandler.read()
        return func

def modify_handler():
    with open(BASE_PATH + 'modifyhandler.js', 'r') as modifyhandler:
        func = modifyhandler.read()
        return func

def post_handler():
    with open(BASE_PATH + 'posthandler.js', 'r') as posthandler:
        func = posthandler.read()
        return func

DATA_FINDER = data_finder()
GET_HANDLER = get_handler()
MODIFY_HANDLER = modify_handler()
POST_HANDLER = post_handler()
