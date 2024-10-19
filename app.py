import os

import textwrap

from pytubefix import YouTube
from pytubefix.cli import on_progress
import google.generativeai as genai

from transcript import make_transcript


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_FILES_DIR = os.path.join(SCRIPT_DIR, ".tmp")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

prompt_template = """
This is transcript of the video, extract most important information from it and present summary.\n
"""


def download_video(url):
    try:
        yt = YouTube(url, on_progress_callback = on_progress)
        stream = yt.streams.filter(file_extension="mp4").first()

        print(f'title: {yt.title}')

        stream.download(TMP_FILES_DIR, filename="tmp.mp4")
    except Exception as e:
        print(f'error: {e}')


def make_prompt(file_path, join_string):
    """Read the contents of a file and join it with a given string."""
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
        result = join_string + file_contents
        return result
    except Exception as e:
        print(f'error: {e}')


def clean(file_path):
    """Check if a file exists and remove it if it does."""
    if os.path.exists(file_path):
        os.remove(file_path)


def main():
    print('Enter the url of the video: ')
    video_url = input()

    print('\ndownloading video\n')

    download_video(video_url)

    print('\nstarting transcript\n')

    make_transcript(f'{TMP_FILES_DIR}/tmp.mp4')

    print('\ntranscript finished\n')

    prompt = make_prompt(f'{TMP_FILES_DIR}/tmp.txt', prompt_template)

    print(f'\nprompt: \n {prompt} \n')

    print('\nasking chat\n')

    chat = model.start_chat(history=[])
    response = chat.send_message(prompt)
    output = textwrap.fill(response.text, width=100)

    print('\nOUTPUT:\n_________________________________________________________________\n')

    print(output)

    clean(f'{TMP_FILES_DIR}/tmp.mp4')
    clean(f'{TMP_FILES_DIR}/tmp.mp3')
    clean(f'{TMP_FILES_DIR}/tmp.txt')
    

if __name__ == '__main__':
    main()
