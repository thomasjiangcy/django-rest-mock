"""
Core functions to be placed in Express Server
"""

from .structures import Function


def data_finder():
    # If there are query params, first check if any of the queries match the pkName
    func_builder = Function()
    func_args = 'req'
    func_body = """
const path = req.path;
const method = req.method.toLowerCase();
const queries = req.query;
for (let i = 0; i < Object.keys(store).length; i ++) {
    if (Object.keys(store)[i].indexOf(path) > -1 && Object.keys(store)[i] === ('/' + method + '__' + path)) {
        const key = Object.keys(store)[i];
        const resp = store[key];
        const data = resp.data;
        return Object.assign({}, data);
    } else if (Object.keys(store)[i].indexOf('/' + method + '__' + path) > -1) {
        const key = Object.keys(store)[i];
        const resp = store[key];
        if (resp.pk && resp.position === 'query') {
            const keyName = resp.pkName;
            const query = req.query;
            let pk;
            if (Object.keys(query).length > 0 && query.constructor === Object) {
                pk = query[keyName];
            }
            if (pk && pk === resp.data[keyName]) {
                const data = resp.data;
                return Object.assign({}, data);
            }
        }
    }
}
return {};""".strip().replace('\n','')
    func_builder.construct('dataFinder', func_args, func_body)
    return str(func_builder.constructed) + ';'


def get_handler():
    """
    function getHandler (req) {
        const resp = dataFinder(req);
        return resp;
    }
    """
    func_builder = Function()
    func_args = 'req'
    func_body = "const resp = dataFinder(req);return resp;".strip().replace('\n','')
    func_builder.construct('getHandler', func_args, func_body)
    return str(func_builder.constructed) + ';'


def modify_handler():
    """
    function modifyHandler (req) {
        const path = req.path;
        const _newData = req.body;
        const newData = JSON.stringify(_newData);
        const storeCopy = Object.assign({}, store);
        const method = 'get';
        for (let i = 0; i < Object.keys(storeCopy).length; i ++) {
            if (Object.keys(storeCopy)[i].indexOf(path) > -1 && Object.keys(storeCopy)[i] === ('/' + method + '__' + path)) {
                const key = Object.keys(storeCopy)[i];
                if (req.method.toLowerCase() !== 'delete') {
                    storeCopy[key].data = Object.assign({}, storeCopy[key].data, newData);
                } else {
                    storeCopy[key].data = {};
                }
                store = Object.assign({}, store, storeCopy);
                const data = storeCopy[key].data;
                return data;
            } else if (Object.keys(storeCopy)[i].indexOf('/' + method + '__' + path) > -1) {
                const key = Object.keys(storeCopy)[i];
                const resp = storeCopy[key];
                if (resp.pk && resp.position === 'query') {
                    const keyName = resp.pkName;
                    const query = req.query;
                    let pk;
                    if (Object.keys(query).length > 0 && query.constructor === Object) {
                        pk = query[keyName];
                    }
                    if (pk && pk === resp.data[keyName]) {
                        if (req.method.toLowerCase() !== 'delete') {
                            storeCopy[key].data = Object.assign({}, storeCopy[key].data, newData);
                        } else {
                            storeCopy[key].data = {};
                        }
                        store = Object.assign({}, store, storeCopy);
                        const data = storeCopy[key].data;
                        return data;
                    }
                }
            }
        }
        return {};
    }
    """
    func_builder = Function()
    func_args = 'req'
    func_body = """
const path = req.path;
const newData = req.body;
const storeCopy = Object.assign({}, store);
const method = 'get';
for (let i = 0; i < Object.keys(storeCopy).length; i ++) {
    if (Object.keys(storeCopy)[i].indexOf(path) > -1 && Object.keys(storeCopy)[i] === ('/' + method + '__' + path)) {
        const key = Object.keys(storeCopy)[i];
        if (req.method.toLowerCase() !== 'delete') {
            storeCopy[key].data = Object.assign({}, storeCopy[key].data, newData);
        } else {
            storeCopy[key].data = {};
        }
        store = Object.assign({}, store, storeCopy);
        const data = storeCopy[key].data;
        return data;
    } else if (Object.keys(storeCopy)[i].indexOf('/' + method + '__' + path) > -1) {
        const key = Object.keys(storeCopy)[i];
        const resp = storeCopy[key];
        if (resp.pk && resp.position === 'query') {
            const keyName = resp.pkName;
            const query = req.query;
            let pk;
            if (Object.keys(query).length === 0 && query.constructor === Object) {
                pk = query[keyName];
            }
            if (pk && pk === resp.data.keyName) {
                if (req.method.toLowerCase() !== 'delete') {
                    storeCopy[key].data = Object.assign({}, storeCopy[key].data, newData);
                } else {
                    storeCopy[key].data = {};
                }
                store = Object.assign({}, store, storeCopy);
                const data = storeCopy[key].data;
                return data;
            }
        }
    }
}
return {};
    """.strip().replace('\n','')
    func_builder.construct('modifyHandler', func_args, func_body)
    return str(func_builder.constructed) + ';'


def post_handler():
    """
    function postHandler (req) {
        const resp = dataFinder(req);
        return resp;
    }
    """
    func_builder = Function()
    func_args = 'req'
    func_body = "const resp = dataFinder(req);return resp;".strip().replace('\n','')
    func_builder.construct('postHandler', func_args, func_body)
    return str(func_builder.constructed) + ';'

DATA_FINDER = data_finder()
GET_HANDLER = get_handler()
MODIFY_HANDLER = modify_handler()
POST_HANDLER = post_handler()
