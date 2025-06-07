from ollama import Client
import os
import re
from shutil import copyfile
# Initialize Ollama client
ollama_client = Client(host='http://10.130.148.206:11434')

def get_embedding(text: str, model: str = "all-minilm:l6-v2") :
    response = ollama_client.embeddings(model=model, prompt='hello')
    print(response)

get_embedding("hello")
