"""
Core functions to be placed in Express Server
"""

import os

from jsmin import jsmin


BASE_PATH = os.path.dirname(__file__) + '/__functions__/'


def data_finder():
    with open(BASE_PATH + 'datafinder.js', 'r') as datafinder:
        func = jsmin(datafinder.read())
        return func

def get_handler():
    with open(BASE_PATH + 'gethandler.js', 'r') as gethandler:
        func = jsmin(gethandler.read())
        return func

def modify_handler():
    with open(BASE_PATH + 'modifyhandler.js', 'r') as modifyhandler:
        func = jsmin(modifyhandler.read())
        return func

def post_handler():
    with open(BASE_PATH + 'posthandler.js', 'r') as posthandler:
        func = jsmin(posthandler.read())
        return func

DATA_FINDER = data_finder()
GET_HANDLER = get_handler()
MODIFY_HANDLER = modify_handler()
POST_HANDLER = post_handler()
