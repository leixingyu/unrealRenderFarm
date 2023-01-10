"""
Host the HTTP Server, provide REST API

Also assigns render request to worker
"""

import logging
import time
import os

from flask import Flask
from flask import request
from flask import render_template

from util import renderRequest


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
HTML_FOLDER = os.path.join(MODULE_PATH, 'html')

# region HTTP REST API

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route('/')
def index_page():
    rrequests = renderRequest.read_all()
    if not rrequests:
        return 'Welcome!'

    jsons = [rrequest.to_dict() for rrequest in rrequests]

    return render_template('index.html', requests=jsons)


@app.get('/api/get')
def get_all_requests():
    rrequests = renderRequest.read_all()
    jsons = [rrequest.to_dict() for rrequest in rrequests]

    # before = request.args.get('before') or '9999'
    # after = request.args.get('after') or '0'
    #
    # filtered = list(
    #     filter(lambda item: int(before) > item['publication_year'] > int(after), STORAGE.values())
    # )
    return {"results": jsons}


@app.get('/api/get/<uid>')
def get_request(uid):
    rr = renderRequest.RenderRequest.from_db(uid)
    return rr.to_dict()


@app.delete('/api/delete/<uid>')
def delete_request(uid):
    return renderRequest.remove_db(uid)


@app.post('/api/post')
def create_request():
    data = request.get_json(force=True)
    rrequest = renderRequest.RenderRequest.from_dict(data)
    rrequest.write_json()
    new_request_trigger(rrequest)

    return rrequest.to_dict()


@app.put('/api/put/<uid>')
def update_request(uid):
    # unreal sends plain text
    content = request.data.decode('utf-8')
    progress, time_estimate, status = content.split(';')

    rr = renderRequest.RenderRequest.from_db(uid)
    rr.update(
        progress=int(float(progress)),
        time_estimate=time_estimate,
        status=status
    )

    return rr.to_dict()


# endregion


def new_request_trigger(rrequest):
    """
    Triggers when a client post a new render request to the server

    :return:
    """
    if rrequest.worker:
        return

    # currently, as a test, assigns all job to one worker
    worker = 'RENDER_MACHINE_01'
    assign_request(rrequest, worker)

    # minimal interval between assigning idle jobs
    time.sleep(2)
    logger.info('assigned job %s to %s', rrequest.uid, worker)


def assign_request(rrequest, worker):
    """
    Assign render request to worker

    :param rrequest:
    :param worker:
    :return:
    """
    rrequest.assign(worker)
    rrequest.update(status=renderRequest.RenderStatus.ready_to_start)


if __name__ == '__main__':
    import subprocess
    import os

    env = os.environ.copy()
    env['PYTHONPATH'] += os.pathsep + MODULE_PATH

    flask_exe = r'E:\Epic\UE_5.0\Engine\Binaries\ThirdParty\Python3\Win64\Scripts\flask.exe'

    # need to activate env
    proc = subprocess.Popen('{flask} --app requestManager.py --debug run -h localhost -p 5000'.format(flask=flask_exe), env=env)
    logger.info(proc.communicate())
