import logging

from util import client


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send(d):
    rrequest = client.add_request(d)
    if rrequest:
        logger.info('request %s sent to server', rrequest.uid)


if __name__ == '__main__':
    job = {
        'name': 'test'
    }
    send(job)
