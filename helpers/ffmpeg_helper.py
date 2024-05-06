import os
import subprocess
import re
import ffmpy

def fixed_name(name):
    regex_pattern = r'[^a-zA-Z0-9\s]'
    cleaned_string = re.sub(regex_pattern, '', name)
    return cleaned_string

def lib_convert_video_to_audio(video_id, video_format, audio_format, video_name, folder_name):
    full_video_name = f"{video_id}.{video_format}"
    full_audio_name = f"{fixed_name(video_name)}.{audio_format}"
    try:
        ff = ffmpy.FFmpeg(
        inputs = {os.path.join("processing", folder_name, full_video_name): None},
        outputs = {os.path.join("output/files", folder_name, full_audio_name): None}
        )
        ff.run()
        return True
    except Exception as e:
        print(f"Error converting file {video_id}. \n" + str(e))
        return False

def convert_video_to_audio(video_id, video_format, audio_format, video_name, folder_name):
    full_video_name = f"{video_id}.{video_format}"
    full_audio_name = f"{fixed_name(video_name)}.{audio_format}"
    input_file = os.path.join("processing", folder_name, full_video_name)
    output_file = os.path.join("output/files", folder_name, full_audio_name)
    #-acodec libmp3lame Only supports mp3 output
    cmd = f'ffmpeg -i {input_file} -vn -f {audio_format} "{output_file}"'
    try:
        #print(cmd)
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting file {video_id}. \n" + str(e))
        return False