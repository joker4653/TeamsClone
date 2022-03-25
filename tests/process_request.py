import requests
from src import config

def process_test_request(route, method, inputs=None):
    # Return result of request.
    if method == 'post':
        return requests.post(config.url + route, json = inputs)
    elif method == 'delete':
        return requests.delete(config.url + route)
    elif method == 'get':
        return requests.get(config.url + route, params = inputs)
    elif method == 'put':
        return requests.put(config.url + route, json = inputs)
    