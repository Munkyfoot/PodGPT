import asyncio
import os
from io import BytesIO
from time import time
from enum import Enum

import pyaudio
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment

load_dotenv()


class Agent:
    def __init__(self):
        self.agent = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.messages = []
        self.token_limit = 4096
        self.model = "gpt-4-1106-preview"
        self.token_encoder = tiktoken.encoding_for_model(self.model)

        self.speaking = False
        self.speak_prompt_queue = []
        self.speak_audio_queue = []

    def get_message_token_usage(self, message):
        role_tokens = 3
        name_tokens = 1

        total_tokens = 0
        total_tokens += role_tokens
        for key, value in message.items():
            total_tokens += len(self.token_encoder.encode(value))
            if key == "name":
                total_tokens += name_tokens
        total_tokens += role_tokens
        return total_tokens

    def get_total_token_usage(self, messages):
        total_tokens = 0
        for message in messages:
            total_tokens += self.get_message_token_usage(message)
        return total_tokens

    def get_messages_in_token_limit(self):
        messages = self.messages.copy()
        token_usage = 0
        for i in range(len(messages)):
            token_usage += self.get_message_token_usage(messages[-(i + 1)])
            if token_usage > self.token_limit:
                print(
                    f"In-context Tokens: {self.get_total_token_usage(messages[-i:])} / {self.token_limit}. Total Tokens: {self.get_total_token_usage(messages)}"
                )
                return messages[-i:]
        return messages

    def add_message(self, role, content, name=None):
        if name is not None:
            self.messages.append({"role": role, "content": content, "name": name})
        else:
            self.messages.append({"role": role, "content": content})

    def reply(self, text, stream=False):
        if text == "":
            raise ValueError("Text cannot be empty.")

        self.add_message("user", text)
        messages = self.get_messages_in_token_limit()

        response = self.agent.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1024,
            stream=stream,
        )

        if stream:
            response_text = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    response_text += chunk.choices[0].delta.content
                    yield chunk.choices[0].delta.content
            self.add_message("assistant", response_text)
        else:
            self.add_message("assistant", response.choices[0].message.content)
            return response.choices[0].message.content

    def describe(self, encoded_image, query="What is in this image?"):
        self.add_message("user", f"{query} [Image]")
        response = self.agent.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=512,
        )

        try:
            self.add_message("assistant", response.choices[0].message.content)
            return response.choices[0].message.content
        except:
            return "Something went wrong."

    def speak(self, text):
        if text == "":
            raise ValueError("Text cannot be empty.")

        if self.speaking:
            self.speak_prompt_queue.append(text)
            return
        else:
            self.speaking = True

        response = self.agent.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text,
            response_format="opus",
        )

        p = pyaudio.PyAudio()

        stream = p.open(
            format=pyaudio.paInt32,
            channels=1,
            rate=48000,
            output=True,
        )

        for chunk in response.iter_bytes():
            stream.write(AudioSegment.from_file(BytesIO(chunk), format="ogg").raw_data)

        stream.stop_stream()
        stream.close()

        p.terminate()

        self.speaking = False

        if len(self.speak_prompt_queue) > 0:
            self.speak(self.speak_prompt_queue.pop(0))

    def generate_image(self, text) -> str:
        if text == "":
            raise ValueError("Text cannot be empty.")

        response = self.agent.images.generate(
            model="dall-e-3",
            prompt=text,
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="b64_json",
        )

        return response.data[0].b64_json
