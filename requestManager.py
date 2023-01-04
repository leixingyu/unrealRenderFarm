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

from renderFarm.util import renderRequest


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
HTML_FOLDER = os.path.join(MODULE_PATH, 'html')

# region HTTP REST API

# https://stackoverflow.com/questions/31002890/how-to-reference-a-html-template-from-a-different-directory-in-python-flask
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
logger = logging.getLogger(__name__)


@app.route('/')
def index_page():
    import json
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
    progress = request.args.get('progress') or 0
    status = request.args.get('status') or ''
    time_estimate = request.args.get('time_estimate') or ''

    request_dict = get_request(uid)

    if progress:
        request_dict['progress'] = progress
    if status:
        request_dict['status'] = status
    if time_estimate:
        request_dict['time_estimate'] = time_estimate

    rr = renderRequest.RenderRequest.from_dict(request_dict)
    rr.write_json()

    return request_dict


# endregion


def new_request_trigger(rrequest):
    """
    Triggers when a client post a new render request to the server

    :return:
    """
    if rrequest.worker:
        return

    # currently, as a test, assigns all job to one worker
    worker = 'TEST_MACHINE_01'
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

    # need to activate env
    proc = subprocess.Popen('flask --app requestManager.py run')
    logger.info(proc.communiate())
