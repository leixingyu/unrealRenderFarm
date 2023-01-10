# Copyright Epic Games, Inc. All Rights Reserved.
import unreal

from util import renderRequest


SERVER_URL = 'http://localhost:5000'


@unreal.uclass()
class MyExecutor(unreal.MoviePipelinePythonHostExecutor):

    pipeline = unreal.uproperty(unreal.MoviePipeline)
    jobId = unreal.uproperty(unreal.Text)

    def _post_init(self):
        self.pipeline = None
        self.queue = None
        self.jobId = None

        self.http_response_recieved_delegate.add_function_unique(
            self,
            "on_http_response_recieved"
        )

    def parseArgument(self):
        (cmdTokens, cmdSwitches, cmdParameters) = unreal.SystemLibrary.parse_command_line(unreal.SystemLibrary.get_command_line())

        self.mapPath = cmdTokens[0]
        self.jobId = cmdParameters['JobId']
        self.seqPath = cmdParameters['LevelSequence']
        self.presetPath = cmdParameters['MoviePipelineConfig']

    def addJob(self):
        job = self.queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        job.map = unreal.SoftObjectPath(self.mapPath)
        job.sequence = unreal.SoftObjectPath(self.seqPath)

        presetPath = unreal.SoftObjectPath(self.presetPath)
        uPreset = unreal.SystemLibrary.conv_soft_obj_path_to_soft_obj_ref(presetPath)
        job.set_configuration(uPreset)

        return job

    @unreal.ufunction(override=True)
    def execute_delayed(self, inPipelineQueue):
        self.parseArgument()

        #
        self.pipeline = unreal.new_object(
            self.target_pipeline_class,
            outer=self.get_last_loaded_world(),
            base_type=unreal.MoviePipeline
        )

        self.pipeline.on_movie_pipeline_finished_delegate.add_function_unique(
            self,
            "on_movie_pipeline_finished"
        )
        self.pipeline.on_movie_pipeline_work_finished_delegate.add_function_unique(
            self,
            "on_work_pipeline_finished"
        )

        #
        self.queue = unreal.new_object(unreal.MoviePipelineQueue, outer=self)
        job = self.addJob()
        self.pipeline.initialize(job)

    @unreal.ufunction(override=True)
    def on_begin_frame(self):
        super(MyExecutor, self).on_begin_frame()

        if not self.pipeline:
            return

        status = renderRequest.RenderStatus.in_progress
        progress = 100 * unreal.MoviePipelineLibrary.get_completion_percentage(self.pipeline)
        time_estimate = unreal.MoviePipelineLibrary.get_estimated_time_remaining(self.pipeline)

        if not time_estimate:
            time_estimate = unreal.Timespan.MAX_VALUE

        days, hours, minutes, seconds, _ = time_estimate.to_tuple()
        time_estimate = '{}:{}:{}'.format(hours, minutes, seconds)

        self.send_http_request(
            '{}/api/put/{}'.format(SERVER_URL, self.jobId),
            "PUT",
            '{};{};{}'.format(progress, time_estimate, status),
            unreal.Map(str, str)
        )

    @unreal.ufunction(ret=None, params=[int, int, str])
    def on_http_response_recieved(self, inRequestIndex, inResponseCode, inMessage):
        if inResponseCode == 200:
            print(inMessage)
        else:
            print('something wrong with the server!!')

    @unreal.ufunction(override=True)
    def is_rendering(self):
        return False

    @unreal.ufunction(ret=None, params=[unreal.MoviePipeline, bool])
    def on_movie_pipeline_finished(self, inMoviePipeline, error):
        self.pipeline = None
        unreal.log("Finished rendering movie!")
        self.on_executor_finished_impl()

        # update to server
        progress = 100
        time_estimate = 'N/A'
        status = renderRequest.RenderStatus.finished
        self.send_http_request(
            '{}/api/put/{}'.format(SERVER_URL, self.jobId),
            "PUT",
            '{};{};{}'.format(progress, time_estimate, status),
            unreal.Map(str, str)
        )

    @unreal.ufunction(ret=None, params=[unreal.MoviePipelineOutputData])
    def on_work_pipeline_finished(self, results):
        unreal.log(results)
