def get_key(req, key):
    value = None
    req_body = req.get_json()
    value = req_body.get(key)
    return value