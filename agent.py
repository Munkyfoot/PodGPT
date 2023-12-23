import asyncio
import os
from io import BytesIO
from time import time
from enum import Enum
from typing import Literal

import pyaudio
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from dataclasses import dataclass

load_dotenv()


@dataclass
class Character:
    name: str
    description: str
    voice_name: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


class Agent:
    def __init__(self, character: Character):
        self.character = character
        self.agent = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.messages = []
        self.token_limit = 4096
        self.model = "gpt-4-1106-preview"
        self.token_encoder = tiktoken.encoding_for_model(self.model)

        self.speaking = False
        self.speak_prompt_queue = []

    def get_system_message(self):
        return {
            "role": "system",
            "content": f"You are {self.character.name}. {self.character.description}",
        }

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
        total_tokens = self.get_message_token_usage(self.get_system_message())
        for message in messages:
            total_tokens += self.get_message_token_usage(message)
        return total_tokens

    def get_messages_in_token_limit(self):
        messages = self.messages.copy()
        token_usage = self.get_message_token_usage(self.get_system_message())
        for i in range(len(messages)):
            token_usage += self.get_message_token_usage(messages[-(i + 1)])
            if token_usage > self.token_limit:
                print(
                    f"In-context Tokens: {self.get_total_token_usage(messages[-i:])} / {self.token_limit}. Total Tokens: {self.get_total_token_usage(messages)}"
                )
                return [self.get_system_message()] + messages[-i:]
        return [self.get_system_message()] + messages

    def add_system_message(self, content):
        self.messages.append({"role": "system", "content": content})

    def add_user_message(self, content, name=None):
        if name is not None:
            self.messages.append({"role": "user", "content": content, "name": name})
        else:
            self.messages.append({"role": "user", "content": content})

    def add_agent_message(self, content):
        self.messages.append({"role": "assistant", "content": content})

    def reply(self, text, stream=False, user_name=None):
        if text == "":
            raise ValueError("Text cannot be empty.")

        self.add_user_message(text, user_name)
        messages = self.get_messages_in_token_limit()

        response = self.agent.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=512,
            stream=stream,
        )

        if stream:
            response_text = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    response_text += chunk.choices[0].delta.content
                    yield chunk.choices[0].delta.content
            self.add_agent_message(response_text)
        else:
            self.add_agent_message(response.choices[0].message.content)
            return response.choices[0].message.content

    def speak(self, text):
        if text == "":
            raise ValueError("Text cannot be empty.")

        self.speak_prompt_queue.append(text)

        if self.speaking:
            return
        else:
            self.speaking = True

        p = pyaudio.PyAudio()

        stream = p.open(
            format=pyaudio.paInt32,
            channels=1,
            rate=48000,
            output=True,
        )

        while len(self.speak_prompt_queue) > 0:
            text = self.speak_prompt_queue.pop(0)
            response = self.agent.audio.speech.create(
                model="tts-1",
                voice=self.character.voice_name,
                input=text,
                response_format="opus",
            )

            for chunk in response.iter_bytes():
                stream.write(
                    AudioSegment.from_file(BytesIO(chunk), format="ogg").raw_data
                )

        stream.stop_stream()
        stream.close()

        p.terminate()

        self.speaking = False
