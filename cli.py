import threading
from agent import Agent

if __name__ == "__main__":
    agent = Agent()
    while True:
        message = input("You: ")
        response = agent.reply(message, True)
        print("GPT: ", end="", flush=True)
        response_text = ""
        for chunk in response:
            response_text += chunk
            print(chunk, end="", flush=True)
            speak_split = "\n" if agent.speaking else "."
            if len(response_text.split(speak_split)) > 1:
                sentence = response_text.split(speak_split)[0] + speak_split
                sentence = sentence.strip()
                speak_thread = threading.Thread(target=agent.speak, args=(sentence,))
                speak_thread.start()
                response_text = response_text.split(speak_split)[1].strip()
        print()
        if response_text != "":
            speak_thread = threading.Thread(target=agent.speak, args=(response_text,))
            speak_thread.start()
