function modifyHandler (req) {
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
}
