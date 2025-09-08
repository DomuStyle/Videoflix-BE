"""Signal handlers for the video content application.

This module defines signals to transcode newly created videos into HLS format,
using FFmpeg and RQ for asynchronous processing.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video
from django.conf import settings
import django_rq
import os
import subprocess


def transcode_task(instance):
    """Transcode a video into HLS format for multiple resolutions.

    Args:
        instance: The Video instance to transcode.
    """
    input_path = instance.original_file.path
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        return
    print(f"Transcoding started for {input_path}")
    base_dir = os.path.join(settings.MEDIA_ROOT, f'videos/{instance.id}')
    os.makedirs(base_dir, exist_ok=True)
    master_playlist = os.path.join(base_dir, 'master.m3u8')
    streams = []

    for res in ['480p', '720p', '1080p']:
        output_dir = os.path.join(base_dir, res)
        os.makedirs(output_dir, exist_ok=True)
        segment_path = os.path.join(output_dir, '%03d.ts')
        playlist_path = os.path.join(output_dir, 'index.m3u8')

        print(f"Transcoding to {res} at {playlist_path}")
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
                '-y',  # Overwrite output files
                playlist_path
            ]
            subprocess.call(cmd)
            print(f"Transcoding complete for {res}")
            streams.append(
                f'#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=854x480\n{res}/index.m3u8'
                if res == '480p' else
                f'#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720\n{res}/index.m3u8'
                if res == '720p' else
                f'#EXT-X-STREAM-INF:BANDWIDTH=4000000,RESOLUTION=1920x1080\n{res}/index.m3u8'
            )
        except Exception as e:
            print(f"FFmpeg subprocess error for {res}: {str(e)}")

    with open(master_playlist, 'w') as f:
        f.write('#EXTM3U\n#EXT-X-VERSION:3\n' + '\n'.join(streams))
    print(f"Master playlist created at {master_playlist}")


@receiver(post_save, sender=Video)
def transcode_video(sender, instance, created, **kwargs):
    """Handle post-save signal for Video model to queue transcoding task.

    Args:
        sender: The model class that sent the signal (Video).
        instance: The Video instance being saved.
        created (bool): True if the instance was newly created.
        **kwargs: Additional signal arguments.
    """
    if created:
        print(f"Signal fired for video ID: {instance.id}")
        django_rq.enqueue(transcode_task, instance)  # Queue transcoding task
        print(f"Task enqueued for video ID: {instance.id}")