from django.db.models.signals import post_save  # imports post_save signal.
from django.dispatch import receiver  # imports receiver decorator.
from .models import Video  # imports video model.
import django_rq  # imports django_rq for queuing.
import os  # imports os for paths.
import ffmpeg
# import ffmpeg  # imports ffmpeg-python for transcoding.

@receiver(post_save, sender=Video)  # receiver for post_save on video.
def transcode_video(sender, instance, created, **kwargs):  # signal handler.
    if created:  # if new video.
        def transcode_task():  # defines task function.
            input_path = instance.original_file.path  # gets input video path.
            base_dir = os.path.dirname(input_path)  # base directory for outputs.
            for res in ['480p', '720p', '1080p']:  # resolutions to transcode.
                output_dir = os.path.join(base_dir, res)  # output directory for resolution.
                os.makedirs(output_dir, exist_ok=True)  # creates directory if not exists.
                ffmpeg.input(input_path).output(  # ffmpeg command for hls.
                    os.path.join(output_dir, 'index.m3u8'),  # output playlist.
                    format='hls',  # hls format.
                    start_number=0,  # segment start number.
                    hls_time=10,  # segment duration in seconds.
                    hls_list_size=0,  # unlimited list size.
                    vcodec='libx264',  # video codec.
                    acodec='aac',  # audio codec.
                    video_bitrate='1000k' if res == '480p' else '2000k' if res == '720p' else '4000k',  # bitrate per resolution.
                    s=f'854x480' if res == '480p' else '1280x720' if res == '720p' else '1920x1080'  # scale resolution.
                ).run()  # runs ffmpeg command.
        django_rq.enqueue(transcode_task)  # queues the transcoding task.