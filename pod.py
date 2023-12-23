import random
import re

import threading
import time
from typing import List

from agent import Agent, Character


class Pod:
    def __init__(
        self,
        title: str,
        description: str,
        topic: str,
        hosts: List[Agent],
        guests: List[Agent],
    ):
        self.title = title
        self.description = description
        self.topic = topic
        self.hosts = hosts
        self.guests = guests

    def start(self):
        guest_text = (
            f"Your guests are {', '.join([guest.character.name for guest in self.guests])}. "
            if len(self.guests) > 0
            else "There are no guests on this episode. "
        )
        for a in self.hosts:
            a.character.description = f"{a.character.description} You are a host of {self.title}. {self.description}. Today's episode is about {self.topic}. Your co-hosts are {', '.join([host.character.name for host in self.hosts if host != a])}. {guest_text} Keep your responses short and entertaining to keep the conversation going! Do not speak for other characters."

        for a in self.guests:
            guest_text = (
                f"The other guests are {', '.join([guest.character.name for guest in self.guests if guest != a])}. "
                if len(self.guests) > 1
                else ""
            )
            a.character.description = f"{a.character.description} You are a guest of {self.title}. {self.description}. Today's episode is about {self.topic}. The hosts of the podcast are {', '.join([host.character.name for host in self.hosts])}. {guest_text}Keep your responses short and entertaining to keep the conversation going! Do not speak for other characters."

        names = [a.character.name.lower() for a in (self.hosts + self.guests)]

        prompt_message = {
            "content": "Let's start the show in 5... 4... 3... 2... 1...",
            "name": "Producer",
        }

        speaker = random.choice(self.hosts)
        while True:
            for a in [
                a
                for a in (self.hosts + self.guests)
                if a != speaker and a.character.name != prompt_message["name"]
            ]:
                a.add_user_message(prompt_message["content"], prompt_message["name"])
            print(f"[{speaker.character.name} replying to {prompt_message['name']}]")
            response = speaker.reply(
                prompt_message["content"], True, prompt_message["name"]
            )
            print(f"{speaker.character.name}: ", end="", flush=True)
            full_response_text = ""
            response_text = ""
            for chunk in response:
                full_response_text += chunk
                response_text += chunk
                print(chunk, end="", flush=True)
                speak_split = "\n\n" if speaker.speaking else "\n"
                if len(response_text.split(speak_split)) > 1:
                    sentence = response_text.split(speak_split)[0] + speak_split
                    sentence = sentence.strip()
                    # speaker.speak(sentence)
                    speak_thread = threading.Thread(
                        target=speaker.speak, args=(sentence,)
                    )
                    speak_thread.start()
                    response_text = response_text.split(speak_split)[1].strip()
            print()
            if response_text != "":
                # speaker.speak(response_text)
                speak_thread = threading.Thread(
                    target=speaker.speak, args=(response_text,)
                )
                speak_thread.start()

            while speaker.speaking:
                time.sleep(0.1)

            prompt_message = {
                "content": full_response_text,
                "name": speaker.character.name,
            }
            words = full_response_text.split(" ")
            mentioned_names = [
                re.sub(r"[^a-zA-Z]", "", word).lower()
                for word in words
                if re.sub(r"[^a-zA-Z]", "", word).lower() in names
                and re.sub(r"[^a-zA-Z]", "", word).lower()
                != speaker.character.name.lower()
            ]

            if len(mentioned_names) > 0:
                speaker = [
                    a
                    for a in (self.hosts + self.guests)
                    if a.character.name.lower() == mentioned_names[-1]
                ][0]
            else:
                speaker = random.choice(
                    [a for a in (self.hosts + self.guests) if a != speaker]
                )


if __name__ == "__main__":
    cusomize_response = input("Do you want to customize the podcast? (y/[n])")
    if cusomize_response == "y":
        title = input("Title: ")
        description = input("Description: ")
        topic = input("Episode Topic: ")
        hosts = []
        while input("Add a host? (y/[n])") == "y":
            host_name = input("Host Name: ")
            host_description = input("Host Description: ")
            host_voice = ""
            while host_voice not in [
                "alloy",
                "echo",
                "fable",
                "onyx",
                "nova",
                "shimmer",
            ]:
                host_voice = input(
                    "Host Voice ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']: "
                )
                if host_voice not in [
                    "alloy",
                    "echo",
                    "fable",
                    "onyx",
                    "nova",
                    "shimmer",
                ]:
                    print("Invalid voice name. Please try again.")
            host = Agent(
                Character(
                    name=host_name.strip().capitalize().split(" ")[0],
                    description=host_description.strip(),
                    voice_name=host_voice,
                )
            )
            hosts.append(host)
        guests = []
        while input("Add a guest? (y/[n])") == "y":
            guest_name = input("Guest Name: ")
            guest_description = input("Guest Description: ")
            guest_voice = ""
            while guest_voice not in [
                "alloy",
                "echo",
                "fable",
                "onyx",
                "nova",
                "shimmer",
            ]:
                guest_voice = input(
                    "Guest Voice ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']: "
                )
                if guest_voice not in [
                    "alloy",
                    "echo",
                    "fable",
                    "onyx",
                    "nova",
                    "shimmer",
                ]:
                    print("Invalid voice name. Please try again.")
            guest = Agent(
                Character(
                    name=guest_name.strip().capitalize(),
                    description=guest_description.strip(),
                    voice_name=guest_voice,
                )
            )
            guests.append(guest)
    else:
        title = "The AI Podcast"
        description = "A podcast where an AI hosts debates between AI guests."
        topic = "AI"
        hosts = [
            Agent(
                Character(
                    name="Alloy",
                    description="Alloy is very balanced about AI and serves as a moderator.",
                    voice_name="alloy",
                )
            )
        ]
        guests = [
            Agent(
                Character(
                    name="Echo",
                    description="Echo is very optimistic about AI.",
                    voice_name="echo",
                )
            ),
            Agent(
                Character(
                    name="Fable",
                    description="Fable is very pessimistic about AI.",
                    voice_name="fable",
                )
            ),
        ]

    pod = Pod(
        title=title,
        description=description,
        topic=topic,
        hosts=hosts,
        guests=guests,
    )
    pod.start()
