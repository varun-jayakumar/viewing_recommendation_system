import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()

jina_api_key = os.environ["JINA_APIKEY"]
# Function to get embeddings for multiple plots from the API
def get_embeddings(text):
    url = "https://api.jina.ai/v1/embeddings"  # Replace with the actual API endpoint
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + jina_api_key  # Replace with your actual API key
    }
    payload = {"input": [text], 
                'model': 'jina-embeddings-v2-base-en'}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["data"][0]['embedding']
    else:
        response.raise_for_status()