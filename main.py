import PySimpleGUI as sg
from pytube import YouTube
import ffmpeg
import os
import pathlib

DISPLAY_FONT = 'Arial 20'

GET_AUDIO_KEY = "get_audio"
GET_VIDEO_KEY = "get_video"
VIDEO_URL_KEY = "video_url"
DOWNLOAD_TO_KEY = "download_to"
SPEED_100_KEY = "speed_100"
SPEED_125_KEY = "spped_125"
SPEED_150_KEY = "speed_150"
SPEED_175_KEY = "speed_175"
SPEED_200_KEY = "speed_200"

SPEED_UPS = {
    SPEED_100_KEY: 1.0,
    SPEED_125_KEY: 1.25,
    SPEED_150_KEY: 1.5,
    SPEED_175_KEY: 1.75,
    SPEED_200_KEY: 2.0
}

SPEED_RADIO = "SPEED_RADIO"
CURRENT_DIR = pathlib.Path(__file__).parent.absolute()

speed_up = SPEED_UPS[SPEED_100_KEY]

def download_video(url, path):

    audio_path = download_audio(url, path)
    new_audio_path = os.path.splitext(audio_path)[0] + '-audio.mp4'
    os.rename(audio_path, new_audio_path)

    yt = YouTube(url)
    video_path = yt.streams.filter(file_extension='mp4').order_by('resolution').last().download(path)

    merge_video_audio(video_path, new_audio_path)

def merge_video_audio(video_path, audio_path):
    new_path = os.path.splitext(video_path)[0] + '-result.mp4'

    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(audio_path)

    audio = audio.filter("atempo", speed_up)
    video = video.filter("setpts", f"{round(1/speed_up, 2)}*PTS")

    out = ffmpeg.output(audio, video, new_path)
    out.run(overwrite_output=True)

    os.remove(video_path)
    os.remove(audio_path)


def download_audio(url, path, speed_up=1.0):
    yt = YouTube(url)
    audio = yt.streams.get_audio_only()
    return audio.download(path)
    
def convert_to_mp3(audio_path, speed_up):
    new_path = os.path.splitext(audio_path)[0] + '.mp3'
    audio = ffmpeg.input(audio_path)
    audio = audio.filter("atempo", speed_up)
    out = ffmpeg.output(audio, new_path, acodec='mp3')
    out.run(overwrite_output=True)
    os.remove(audio_path)


sg.change_look_and_feel('Dark Blue 3')      # because gray windows suck
sg.SetOptions(font=DISPLAY_FONT)

layout = [
    [ sg.Text("Video URL: "), sg.Input("", key=VIDEO_URL_KEY) ],
    [ sg.Text("Download to: "), sg.Input(CURRENT_DIR, key=DOWNLOAD_TO_KEY), sg.FolderBrowse() ],
    [ 
        sg.Text("Speed up to: "), 
        sg.Radio("1x", SPEED_RADIO, key=SPEED_100_KEY, default=True), 
        sg.Radio("1.25x", SPEED_RADIO, key=SPEED_125_KEY, default=False),
        sg.Radio("1.5x", SPEED_RADIO, key=SPEED_150_KEY, default=False),
        sg.Radio("1.75x", SPEED_RADIO, key=SPEED_175_KEY, default=False),
        sg.Radio("2x", SPEED_RADIO, key=SPEED_200_KEY, default=False)
    ],
    [ sg.Button("Get video with audio", key=GET_VIDEO_KEY), sg.Button("Get only Audio", key=GET_AUDIO_KEY) ],
]

window = sg.Window(title="Youtube Downloader", layout=layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == GET_AUDIO_KEY or event == GET_VIDEO_KEY:
        video_url = values[VIDEO_URL_KEY]
        path = values[DOWNLOAD_TO_KEY]

        radio_item = list(filter(lambda item: 'speed' in item[0] and item[1], values.items())).pop()
        speed_up = SPEED_UPS[radio_item[0]]

        if  video_url and path:
            if event == GET_AUDIO_KEY:
                path = download_audio(video_url, path, speed_up)
                convert_to_mp3(path, speed_up)
            elif event == GET_VIDEO_KEY:
                download_video(video_url, path)
        else:
            sg.PopupOK("Enter valid url and path",title="Invalid data")

window.close()