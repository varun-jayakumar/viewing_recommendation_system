import requests
import os
from dotenv import load_dotenv

load_dotenv()
url = 'https://api.jina.ai/v1/embeddings'

jina_api_key = os.environ["JINA_APIKEY"]

headers = {
      'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + jina_api_key
}


data = {
      'input': ["My Sample text ", "I love pokemon I am going to write gibbersis to see what difference it makes I dont kniw if it will make a difference or not"],
  'model': 'jina-embeddings-v2-base-en'
}

response = requests.post(url, headers=headers, json=data)
data = response.json()


print(data)
