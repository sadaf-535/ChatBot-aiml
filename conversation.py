from aiml import Kernel
import os
my_bot = Kernel()
def load_aiml_files():
    aiml_directory = "data"
    aiml_files = [os.path.join(aiml_directory, file) for file in os.listdir(aiml_directory) if file.endswith(".aiml")]
    for aiml_file in aiml_files:
        my_bot.learn(aiml_file)
def chat_bot(message):
    try:
        response = my_bot.respond(message)
        if response == "unknown":
            response = None
    except Exception as e:
        print("Error:", e)
        response = None
    return response
load_aiml_files()
while True:
    Query= input("user>")
    response = chat_bot(Query)
    print(response)