from django.db.models.signals import post_save  # imports post_save signal.
from django.dispatch import receiver  # imports receiver decorator.
from .models import Video  # imports video model.
import django_rq  # imports django_rq for queuing.
import os  # imports os for paths.
import subprocess  # imports subprocess for ffmpeg calls.
from django.conf import settings  # imports settings for MEDIA_ROOT.


def transcode_task(instance):  # top-level task function.
    input_path = instance.original_file.path  # gets input path.
    if not os.path.exists(input_path):  # checks if file exists.
        print("Error: Input file not found at", input_path)  # debug missing file.
        return
    print("Transcoding started for", input_path)  # debug start.
    base_dir = os.path.join(settings.MEDIA_ROOT, f'videos/{instance.id}')  # base dir for video ID (fix: /media/videos/id/).
    os.makedirs(base_dir, exist_ok=True)  # creates base dir.
    master_playlist = os.path.join(base_dir, 'master.m3u8')  # master playlist path.
    streams = []  # list for stream variants.

    for res in ['480p', '720p', '1080p']:  # resolutions.
        output_dir = os.path.join(base_dir, res)  # output dir.
        os.makedirs(output_dir, exist_ok=True)  # creates dir.
        segment_path = os.path.join(output_dir, '%03d.ts')  # segment pattern.
        playlist_path = os.path.join(output_dir, 'index.m3u8')  # per-resolution playlist (changed to 'index.m3u8' to match view/frontend).

        print("Transcoding to", res, "at", playlist_path)  # debug per resolution.
        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-f', 'hls',
                '-hls_time', '10',
                '-hls_list_size', '0',
                '-hls_segment_filename', segment_path,
                '-b:v', '1000k' if res == '480p' else '2000k' if res == '720p' else '4000k',
                '-s', '854x480' if res == '480p' else '1280x720' if res == '720p' else '1920x1080',
                '-y',  # overwrite output.
                playlist_path
            ]
            subprocess.call(cmd)  # runs ffmpeg binary.
            print("Transcoding complete for", res)  # debug success.
            streams.append(f'#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=854x480\n{res}/index.m3u8' if res == '480p' else f'#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720\n{res}/index.m3u8' if res == '720p' else f'#EXT-X-STREAM-INF:BANDWIDTH=4000000,RESOLUTION=1920x1080\n{res}/index.m3u8')  # adds stream to master (changed to 'index.m3u8').
        except Exception as e:
            print("FFmpeg subprocess error for", res, ":", str(e))  # debug failure.

    with open(master_playlist, 'w') as f:  # writes master m3u8.
        f.write('#EXTM3U\n#EXT-X-VERSION:3\n' + '\n'.join(streams))  # adds header and streams.
    print("Master playlist created at", master_playlist)  # debug master.

@receiver(post_save, sender=Video)  # receiver for post_save on video.
def transcode_video(sender, instance, created, **kwargs):  # signal handler.
    if created:  # if new video.
        print("Signal fired for video ID:", instance.id)  # debug: signal trigger.
        django_rq.enqueue(transcode_task, instance)  # enqueues with instance arg (fix for RQ).
        print("Task enqueued for video ID:", instance.id)  # debug enqueue.