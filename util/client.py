import logging
import requests


from . import renderRequest


logger = logging.getLogger(__name__)
HOST_URL = 'http://127.0.0.1:5000/api'


def get_all_requests():
    try:
        response = requests.get(HOST_URL + '/get')
    except requests.exceptions.ConnectionError:
        logger.error('failed to connect to server %s', HOST_URL)
        return

    results = response.json()['results']
    return [renderRequest.RenderRequest.from_dict(result) for result in results]


def get_request(uid):
    try:
        response = requests.get(HOST_URL + '/get/{}'.format(uid))
    except requests.exceptions.ConnectionError:
        logger.error('failed to connect to server %s', HOST_URL)
        return

    return renderRequest.RenderRequest.from_dict(response.json())


def add_request(d):
    try:
        response = requests.post(HOST_URL + '/post', json=d)
    except requests.exceptions.ConnectionError:
        logger.error('failed to connect to server %s', HOST_URL)
        return
    return renderRequest.RenderRequest.from_dict(response.json())


def remove_request(uid):
    try:
        response = requests.delete(HOST_URL + '/delete/{}'.format(uid))
    except requests.exceptions.ConnectionError:
        logger.error('failed to connect to server %s', HOST_URL)
        return
    return renderRequest.RenderRequest.from_dict(response.json())


def update_request(
        uid,
        progress=0,
        status='',
        time_estimate=''
):
    try:
        response = requests.put(
            HOST_URL + '/put/{}'.format(uid),
            params={
                'progress': progress,
                'status': status,
                'time_estimate': time_estimate
            }
        )
    except requests.exceptions.ConnectionError:
        logger.error('failed to connect to server %s', HOST_URL)
        return

    return renderRequest.RenderRequest.from_dict(response.json())
