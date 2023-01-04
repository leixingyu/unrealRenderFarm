import logging
import time
import subprocess

from util import client
from util import renderRequest


logger = logging.getLogger(__name__)
WORKER_NAME = 'TEST_MACHINE_01'


def do():
    command = [
        "C:\Program Files\Epic Games\UE_5.0\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
        "uproject",

        "{}".format('path to map'),
        "-LevelSequence={}".format('path to ls'),
        "-MoviePipelineConfig={}".format('path to config'),

        "-game",
        "-MoviePipelineLocalExecutorClass=/Script/MovieRenderPipelineCore.MoviePipelinePythonHostExecutor",
        "-ExecutorPythonClass=/Engine/PythonTypes.MyExecutor",

        "-windowed",
        "-resX=1280",
        "-resY=720",

        "-Log",
        "-StdOut",
        "-allowStdOutLogVerbosity",
        "-Unattended",
    ]
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.pipe
    )
    return proc.communicate()


def work(uids):
    for uid in uids:
        for i in range(20):
            time.sleep(1)
            logger.info("rendering job %s", uid)
            client.update_request(
                uid,
                progress=5*i,
                status=renderRequest.RenderStatus.in_progress,
                time_estimate='N/A'
            )
        client.update_request(uid, 100, renderRequest.RenderStatus.finished, '00:00:00')
        logger.info("finished rendering job %s", uid)
        return True


def run():
    while True:
        rrequests = client.get_all_requests()
        uids = [rrequest.uid for rrequest in rrequests
                if rrequest.worker == WORKER_NAME and rrequest.status == renderRequest.RenderStatus.ready_to_start]
        work(uids)  # render blocks main loop

        # check assigned job every 10 sec after previous job has finished
        time.sleep(10)


if __name__ == '__main__':
    run()
