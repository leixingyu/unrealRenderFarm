import logging

from util import client


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def send(d):
    rrequest = client.add_request(d)
    if rrequest:
        LOGGER.info('request %s sent to server', rrequest.uid)


if __name__ == '__main__':
    job = {
        'name': 'test',
        'owner': 'TEST_SUBMITTER_01',
        'umap_path': '/Game/Cinematics/Street/Level_Cin_Street.Level_Cin_Street',
        'useq_path': '/Game/Cinematics/Street/LS_Master_Street.LS_Master_Street',
        'uconfig_path': '/Game/Cinematics/Preset/Test.Test'
    }
    send(job)
