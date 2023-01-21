import logging
import os
import subprocess
import time

from util import client
from util import renderRequest


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# render worker specific configuration
WORKER_NAME = 'RENDER_MACHINE_01'
UNREAL_EXE = r'E:\Epic\UE_5.0\Engine\Binaries\Win64\UnrealEditor.exe'
UNREAL_PROJECT = r"E:\Epic\UnrealProjects\SequencerTest\SequencerTest.uproject"


def render(uid, umap_path, useq_path, uconfig_path):
    command = [
        UNREAL_EXE,
        UNREAL_PROJECT,

        umap_path,
        "-JobId={}".format(uid),
        "-LevelSequence={}".format(useq_path),
        "-MoviePipelineConfig={}".format(uconfig_path),

        # required
        "-game",
        "-MoviePipelineLocalExecutorClass=/Script/MovieRenderPipelineCore.MoviePipelinePythonHostExecutor",
        "-ExecutorPythonClass=/Engine/PythonTypes.MyExecutor",

        # render preview
        "-windowed",
        "-resX=1280",
        "-resY=720",

        # logging
        "-StdOut",
        "-FullStdOutLogOutput"
    ]
    env = os.environ.copy()
    env["UE_PYTHONPATH"] = MODULE_PATH
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    return proc.communicate()


if __name__ == '__main__':
    LOGGER.info('Starting render worker %s', WORKER_NAME)
    while True:
        rrequests = client.get_all_requests()
        uids = [rrequest.uid for rrequest in rrequests
                if rrequest.worker == WORKER_NAME and
                rrequest.status == renderRequest.RenderStatus.ready_to_start]

        # render blocks main loop
        for uid in uids:
            LOGGER.info('rendering job %s', uid)

            rrequest = renderRequest.RenderRequest.from_db(uid)
            output = render(
                uid,
                rrequest.umap_path,
                rrequest.useq_path,
                rrequest.uconfig_path
            )

            # for debugging
            # for line in str(output).split(r'\r\n'):
            #     if 'LogPython' in line:
            #         print(line)

            LOGGER.info("finished rendering job %s", uid)

        # check assigned job every 10 sec after previous job has finished
        time.sleep(10)
        LOGGER.info('current job(s) finished, searching for new job(s)')
