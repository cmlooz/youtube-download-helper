import json
import os
import yt_dlp
import subprocess

def lib_download_video(video_id, video_url, video_format, folder_name):
    # Opciones para el formato de descarga
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": video_format,
        "outtmpl": os.path.join("processing", folder_name, "%(id)s.%(ext)s")
    }
    try:
        # Inicializa yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return True
    except Exception as e:
        print(f"Error downloading {video_id}. \n" + str(e))
        return False

def download_video(video_id, video_url, video_format, folder_name):

    with open("variables.json", "r") as file_json:
        content_json = json.loads(file_json.read())
    yt_dlp_ = content_json['yt_dlp']

    #cmd = f'./{yt_dlp_} {video_url} -f best -o "/output/%(id)s.%(ext)s" --merge-output-format {video_format}'
    cmd = f'{yt_dlp_} {video_url} -o "/processing/{folder_name}/%(id)s.%(ext)s" --merge-output-format {video_format}'

    try:
        #print(cmd)
        # Run the yt-dlp command
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {video_id}. \n" + str(e))
        return False