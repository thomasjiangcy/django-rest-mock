function dataFinder (req) {
    const path = req.path;
    const method = req.method.toLowerCase();
    const queries = req.query;
    for (let i = 0; i < Object.keys(store).length; i ++) {
        if (Object.keys(store)[i].indexOf(path) > -1 && Object.keys(store)[i] === ('/' + method + '__' + path)) {
            const key = Object.keys(store)[i];
            const resp = store[key];
            const data = resp.data;
            if (data instanceof Array) {
                return data;
            }
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
                if (pk && (pk === resp.data[keyName] || pk === resp.parentName)) {
                    const data = resp.data;
                    if (data instanceof Array) {
                        return Object.assign([], data);
                    }
                    return Object.assign({}, data);
                }
            }
        }
    }
    return {};
}
