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
        print()
        speak_thread = threading.Thread(target=agent.speak, args=(response_text,))
        speak_thread.start()
