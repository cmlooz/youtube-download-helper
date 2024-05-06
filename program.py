import json
import os
import time
import threading
import multiprocessing
from tkinter import messagebox

from helpers.yt_stats import YTstats
from helpers.yt_dlp_helper import download_video
from helpers.ffmpeg_helper import convert_video_to_audio

API_KEY = ""
MAX_RESULTS = 0
VIDEO_FORMAT = ""
AUDIO_FORMAT = ""
NUM_THREADS = 0
NUM_PROCESSES = 0
TIMESTAMP = ""
processed_videos_multithreading = []


def get_channel_name(url):
    parts = url.split('/')
    return parts[-1]


def get_last_videos(yt, channel_url):
    tmp_result = []
    yt.extract(channel_url)
    links = yt.dump()
    for id, link in links.items():
        link_ = link.copy()
        link_['id'] = id
        link_['channel'] = get_channel_name(channel_url)
        tmp_result.append(link_)
    return tmp_result


def delete_tmp_video(filename):
    file_path = os.path.join('processing', filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
    else:
        print(f'File {filename} not found.')


def process_video(link, video_format, audio_format, folder_name):
    video_url = f"https://www.youtube.com/watch?v={link['id']}"
    # Descargar el video usando yt-dlp
    downloaded = download_video(
        link['id'], video_url, video_format, folder_name)
    if (downloaded == False):
        raise Exception(f"No se descargó el video {
                        link['title']}, Url: {video_url}")
    # Convertir a MP3 usando ffmpeg
    converted = convert_video_to_audio(
        link['id'], video_format, audio_format, link['title'], folder_name)
    if (converted == False):
        raise Exception(f"No se convirtió el video {
                        link['title']} a {audio_format}")
    audio_name = f"{link['title']}.{audio_format}"
    # Eliminar el video
    delete_tmp_video(f"{folder_name}/{link['id']}.{video_format}")
    print(f"***Video processed {audio_name}\n")
    return os.path.join("output", "files", folder_name, audio_name)

# ejecución secuencial


def process_single_thread(tmp_result):
    processed_videos = []
    for link in tmp_result:
        video_url = f"https://www.youtube.com/watch?v={link['id']}"
        audio_path = process_video(link, VIDEO_FORMAT, AUDIO_FORMAT, TIMESTAMP)
        processed_videos.append({'title': link['title'], 'date': link['publishedAt'], 'channel': link['channel'],
                                'url': video_url, 'path': audio_path, 'downloaded': time.strftime("%Y-%m-%dT%H:%M:%SZ")})
    return processed_videos

# ejecucion con hilos


def process_multithreading_chunk(tmp_chunk, num_thread):
    for link in tmp_chunk:
        if link is None:
            continue
        video_url = f"https://www.youtube.com/watch?v={link['id']}"
        audio_path = process_video(link, VIDEO_FORMAT, AUDIO_FORMAT, TIMESTAMP)
        processed_videos_multithreading.append({'title': link['title'], 'date': link['publishedAt'], 'channel': link['channel'],
                                               'url': video_url, 'path': audio_path, 'downloaded': time.strftime("%Y-%m-%dT%H:%M:%SZ"), 'processed_by_thread': str(num_thread)})

# ejecucion con hilos


def process_multithreading(tmp_result):
    chunk_size = int((len(tmp_result) + NUM_THREADS)/NUM_THREADS)
    threads = []
    # Se divide el tmp_result en chunks de igual tamaño y crean los hilos
    for i in range(0, NUM_THREADS):
        init_position = i * chunk_size
        final_position = (init_position + chunk_size)-1
        chunk = tmp_result[init_position:final_position]
        thread = threading.Thread(
            target=process_multithreading_chunk, args=(chunk, i))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    return processed_videos_multithreading

# ejecucion con procesos


def process_video_multiprocessing(link):
    with open("variables.json", "r") as file_json:
        content_json = json.loads(file_json.read())
    video_format = content_json["video_format"]
    audio_format = content_json["audio_format"]
    folder_name_ = content_json["last_execution"]
    return process_video(link, video_format, audio_format, folder_name_)

# ejecucion con procesos


def process_multiprocessing(tmp_result):
    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        results = pool.map(process_video_multiprocessing, tmp_result)
    processed_videos = []
    for link, audio_path in zip(tmp_result, results):
        video_url = f"https://www.youtube.com/watch?v={link['id']}"
        processed_videos.append(
            {'title': link['title'], 'date': link['publishedAt'], 'channel': link['channel'], 'url': video_url,
             'path': audio_path, 'downloaded': time.strftime("%Y-%m-%dT%H:%M:%SZ")})
    return processed_videos

# crear las carpetas temporales y guardar el inicio de la ejecución


def setup():
    with open("variables.json", "r") as file_json:
        content_json = json.loads(file_json.read())
    # Guardar en el archivo de configuracion la última ejecución
    content_json['last_execution'] = TIMESTAMP
    with open("variables.json", 'w') as f:
        json.dump(content_json, f, indent=4)
    # Carpeta tmp para descargar los videos
    if not os.path.exists(f"processing/{TIMESTAMP}"):
        os.makedirs(f"processing/{TIMESTAMP}")
    # Carpeta para convertir los audios
    if not os.path.exists(f"output/files/{TIMESTAMP}"):
        os.makedirs(f"output/files/{TIMESTAMP}")

# función principal que ejecuta el procesamiento seleccionado


def process_channels(channels, execution_option):
    processed_videos = []
    execution_mode = ""
    tmp_result = []
    filename = f'{TIMESTAMP}.txt'
    # Objeto para consultar los links de los videos a descargar de los canales
    yt = YTstats(API_KEY, MAX_RESULTS)
    for channel in channels:
        # Consultar los últimos vídeos de cada canal
        tmp_result.extend(get_last_videos(yt, channel))
    if tmp_result is None or len(tmp_result) == 0:
        raise Exception("There are no videos to process!")
    setup()
    # Dependiendo del la opcion ejecuta la funcion correspondiente
    if (execution_option == 1):
        execution_mode = "Execution by single process"
        print(f"{execution_mode}\n")
        processed_videos = process_single_thread(tmp_result)
    elif (execution_option == 2):
        execution_mode = f"Execution by {NUM_THREADS} threads"
        print(f"{execution_mode}\n")
        processed_videos = process_multithreading(tmp_result)
    elif (execution_option == 3):
        execution_mode = f"Execution by {NUM_PROCESSES} processes"
        print(f"\n{execution_mode}\n")
        processed_videos = process_multiprocessing(tmp_result)
    # guardar el archivo
    if processed_videos != None and len(processed_videos) > 0:
        with open(f"./output/{filename}", 'a') as f:
            f.write(f'#{execution_mode} took {
                    time.time() - start_time} seconds\n')
            json.dump(processed_videos, f, indent=4)
        messagebox.showinfo("Execution finished", f"File {
                            filename} created successfully!")
    print(f'\n================================\nprocess time: {
          time.time() - start_time}')

# Capturador de la opción de ejecución


def capture_integer():
    while True:
        try:
            value = input(
                "Ingrese la opción para ejecutar: 1. Single Process, 2. Multithread, 3. Multiprocess")
            number = int(value)
            if number <= 0 or number > 3:
                raise ValueError
            return number
        except ValueError:
            print("El valor ingresado no es un entero válido. Intente nuevamente.")


if __name__ == "__main__":
    # Leer el archivo con los parámetros del programa
    with open("variables.json", "r") as file_json:
        content_json = json.loads(file_json.read())
    API_KEY = content_json['api_key']
    MAX_RESULTS = content_json['max_results']
    VIDEO_FORMAT = content_json['video_format']
    AUDIO_FORMAT = content_json['audio_format']
    NUM_THREADS = content_json['num_threads']
    NUM_PROCESSES = NUM_THREADS
    channels = content_json['channels']
    number = capture_integer()
    start_time = time.time()
    TIMESTAMP = time.strftime("%Y%m%d_%H%M%S")
    # Ejecutar programa
    process_channels(channels, number)
