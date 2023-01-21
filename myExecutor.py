import unreal

from util import client
from util import renderRequest


@unreal.uclass()
class MyExecutor(unreal.MoviePipelinePythonHostExecutor):

    pipeline = unreal.uproperty(unreal.MoviePipeline)
    job_id = unreal.uproperty(unreal.Text)

    def _post_init(self):
        self.pipeline = None
        self.queue = None
        self.job_id = None

        self.http_response_recieved_delegate.add_function_unique(
            self,
            "on_http_response_recieved"
        )

    def parse_argument(self):
        (cmd_tokens, cmd_switches, cmd_parameters) = unreal.SystemLibrary.\
            parse_command_line(unreal.SystemLibrary.get_command_line())

        self.map_path = cmd_tokens[0]
        self.job_id = cmd_parameters['JobId']
        self.seq_path = cmd_parameters['LevelSequence']
        self.preset_path = cmd_parameters['MoviePipelineConfig']

    def add_job(self):
        job = self.queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        job.map = unreal.SoftObjectPath(self.map_path)
        job.sequence = unreal.SoftObjectPath(self.seq_path)

        preset_path = unreal.SoftObjectPath(self.preset_path)
        u_preset = unreal.SystemLibrary.\
            conv_soft_obj_path_to_soft_obj_ref(preset_path)
        job.set_configuration(u_preset)

        return job

    @unreal.ufunction(override=True)
    def execute_delayed(self, queue):
        self.parse_argument()

        #
        self.pipeline = unreal.new_object(
            self.target_pipeline_class,
            outer=self.get_last_loaded_world(),
            base_type=unreal.MoviePipeline
        )
        self.pipeline.on_movie_pipeline_finished_delegate.add_function_unique(
            self,
            "on_job_finished"
        )
        self.pipeline.on_movie_pipeline_work_finished_delegate.add_function_unique(
            self,
            "on_pipeline_finished"
        )

        #
        self.queue = unreal.new_object(unreal.MoviePipelineQueue, outer=self)
        job = self.add_job()
        self.pipeline.initialize(job)

    @unreal.ufunction(override=True)
    def on_begin_frame(self):
        super(MyExecutor, self).on_begin_frame()

        if not self.pipeline:
            return

        status = renderRequest.RenderStatus.in_progress
        progress = 100 * unreal.MoviePipelineLibrary.\
            get_completion_percentage(self.pipeline)
        time_estimate = unreal.MoviePipelineLibrary.\
            get_estimated_time_remaining(self.pipeline)

        if not time_estimate:
            time_estimate = unreal.Timespan.MAX_VALUE

        days, hours, minutes, seconds, _ = time_estimate.to_tuple()
        time_estimate = '{}h:{}m:{}s'.format(hours, minutes, seconds)

        self.send_http_request(
            '{}/put/{}'.format(client.SERVER_API_URL, self.job_id),
            "PUT",
            '{};{};{}'.format(progress, time_estimate, status),
            unreal.Map(str, str)
        )

    @unreal.ufunction(ret=None, params=[int, int, str])
    def on_http_response_recieved(self, index, code, message):
        if code == 200:
            unreal.log(message)
        else:
            unreal.log_error('something wrong with the server!!')

    @unreal.ufunction(override=True)
    def is_rendering(self):
        return False

    @unreal.ufunction(ret=None, params=[unreal.MoviePipeline, bool])
    def on_job_finished(self, pipeline, error):
        self.pipeline = None
        unreal.log("Finished rendering movie!")
        self.on_executor_finished_impl()

        # update to server
        progress = 100
        time_estimate = 'N/A'
        status = renderRequest.RenderStatus.finished
        self.send_http_request(
            '{}/put/{}'.format(client.SERVER_API_URL, self.job_id),
            "PUT",
            '{};{};{}'.format(progress, time_estimate, status),
            unreal.Map(str, str)
        )

    @unreal.ufunction(ret=None, params=[unreal.MoviePipelineOutputData])
    def on_pipeline_finished(self, results):
        output_data = results
        if output_data.success:
            for shot_data in output_data.shot_data:
                render_pass_data = shot_data.render_pass_data
                for k, v in render_pass_data.items():
                    if k.name == 'FinalImage':
                        outputs = v.file_paths
                        # get all final output images
                        # unreal.log(outputs)
