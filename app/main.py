import subprocess
from sys import platform

import gradio as gr
import openai

openai.api_key_path = '.env'

messages = [
    {"role": "system", "content": "You are a helpful assistant"},
]


def voice_reply(bot_response):
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        subprocess.call(["say", bot_response])
    elif platform == "win32":
        # Windows... Needs "wsay" in your path
        # https://github.com/p-groarke/wsay
        subprocess.call(["wsay", bot_response])


def transcribe(audio, reply_with_audio: bool = False):
    global messages

    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    messages.append({"role": "user", "content": transcript['text']})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    bot_response = response['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": bot_response})

    chat_transcript = ''
    for msg in messages:
        if msg['role'] != 'system':
            chat_transcript += f"{msg['role']}: {msg['content']}\n\n"

    if reply_with_audio:
        voice_reply(bot_response)

    return chat_transcript


app = gr.Interface(
    fn=transcribe,
    inputs=gr.Audio(source="microphone", type="filepath"),
    outputs="text"
)

app.launch()
