"""
Client request utility functions
"""


import logging
import requests

from . import renderRequest


LOGGER = logging.getLogger(__name__)

SERVER_URL = 'http://127.0.0.1:5000'
SERVER_API_URL = SERVER_URL + '/api'


def get_all_requests():
    """
    Call a 'GET' method for all render requests from the server

    :return: [renderRequest.RenderRequest]. request objects
    """
    try:
        response = requests.get(SERVER_API_URL+'/get')
    except requests.exceptions.ConnectionError:
        LOGGER.error('failed to connect to server %s', SERVER_API_URL)
        return

    results = response.json()['results']
    return [renderRequest.RenderRequest.from_dict(result) for result in results]


def get_request(uid):
    """
    Call a 'GET' method for a specific render request from the server
    
    :param uid: str. request uid
    :return: renderRequest.RenderRequest. request object
    """
    try:
        response = requests.get(SERVER_API_URL+'/get/{}'.format(uid))
    except requests.exceptions.ConnectionError:
        LOGGER.error('failed to connect to server %s', SERVER_API_URL)
        return

    return renderRequest.RenderRequest.from_dict(response.json())


def add_request(d):
    """
    Call a 'POST' method to add a render request to the server
    
    :param d: dict. render request represented as dictionary
    :return: renderRequest.RenderRequest. request object created
    """
    try:
        response = requests.post(SERVER_API_URL+'/post', json=d)
    except requests.exceptions.ConnectionError:
        LOGGER.error('failed to connect to server %s', SERVER_API_URL)
        return
    
    return renderRequest.RenderRequest.from_dict(response.json())


def remove_request(uid):
    """
    Call a 'DELETE' method to remove a render request to the server

    :param uid: str. render request uid
    :return: renderRequest.RenderRequest. request object created
    """
    try:
        response = requests.delete(SERVER_API_URL+'/delete/{}'.format(uid))
    except requests.exceptions.ConnectionError:
        LOGGER.error('failed to connect to server %s', SERVER_API_URL)
        return
    
    return renderRequest.RenderRequest.from_dict(response.json())


def update_request(uid, progress=0, status='', time_estimate=''):
    """
    Call a 'PUT' method to update a render request on the server

    :param uid: str. render request uid to update
    :param progress: int. updated progress
    :param status: renderRequest.RenderStatus. updated status
    :param time_estimate: str. updated estimate remaining time
    :return: renderRequest.RenderRequest. updated render request object
    """
    try:
        response = requests.put(
            SERVER_API_URL+'/put/{}'.format(uid),
            params={
                'progress': progress,
                'status': status,
                'time_estimate': time_estimate
            }
        )
    except requests.exceptions.ConnectionError:
        LOGGER.error('failed to connect to server %s', SERVER_API_URL)
        return

    return renderRequest.RenderRequest.from_dict(response.json())
