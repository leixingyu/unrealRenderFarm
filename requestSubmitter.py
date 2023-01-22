"""
Client to submit new render request to server
"""

import logging

from util import client


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def send(d):
    """
    Send/Submit a new render request

    :param d: dict. a render request serialized as dictionary
    """
    rrequest = client.add_request(d)
    if rrequest:
        LOGGER.info('request %s sent to server', rrequest.uid)


if __name__ == '__main__':
    test_job_a = {
        'name': 'street_seq01',
        'owner': 'TEST_SUBMITTER_01',
        'umap_path': '/Game/Cinematics/Street/Level_Cin_Street.Level_Cin_Street',
        'useq_path': '/Game/Cinematics/Street/Shots/Shot01/LS_Shot_Street_Shot01.LS_Shot_Street_Shot01',
        'uconfig_path': '/Game/Cinematics/Preset/Test.Test'
    }

    test_job_b = {
        'name': 'street_seq02',
        'owner': 'TEST_SUBMITTER_01',
        'umap_path': '/Game/Cinematics/Street/Level_Cin_Street.Level_Cin_Street',
        'useq_path': '/Game/Cinematics/Street/Shots/Shot02/LS_Shot_Street_Shot02.LS_Shot_Street_Shot02',
        'uconfig_path': '/Game/Cinematics/Preset/Test.Test'
    }

    for job in [test_job_a, test_job_b]:
        send(job)
