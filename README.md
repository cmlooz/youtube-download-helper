# youtube-download-helper
El archivo variables.json tiene los siguientes campos:
•	Api_key: Token del Google cloud console Youtube Data API V3
•	Max_results: Cantidad de videos a descargar por canal
•	Num_threads: Cantidad de hilos o procesos para ejecutar el programa
•	Video_format y audio_format: Formatos de salida para la descarga de los videos y conversión a audio
•	Channels: Lista de las url de los canales de YouTube de los cuales se van a descargar los últimos videos subidos
•	Last_execution: guarda el registro de la última ejecución

En la carpeta processing se crea una carpeta usando como nombre el timestamp del inicio de la ejecución del programa para descargar ahí los videos, los videos se llaman por su id (última parte del link) en el formato suministrado en el archivo variables.json. 
En la carpeta output se crea el registro timestamp.txt con la información de los videos descargados en esa ejecución y la carpeta timestamp que tiene dichos archivos que se llaman por el titulo del video en el formato suministrado en el archivo variables.json.
Una vez convertido a audio el video se elimina de la carpeta processing.

Dentro del archivo de salida de la ejecución se encuentra la siguiente estructura:
•	EL tipo y tiempo de procesamiento
•	Arreglo json con la información de los videos descargados
o	Titulo
o	Fecha de publicación
o	Nombre del canal
o	Url
o	Ruta física
o	Fecha de descarga

Dentro de la carpeta helpers están los archivos para consultar los videos dado el canal (usando Youtube Data API V3), para llamar por consola al programa yt-dlp(se usa el .exe portable) y ffmpeg (instalado con pip)

Para ejecutar el programa se ejecuta el comando Python program.py, el programa solicita por terminal la opción de ejecución, 1 para un solo hilo, 2 para usar múltiples hilos y 3 para usar múltiples procesos
