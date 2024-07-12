import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

jina_api_key = os.environ["JINA_APIKEY"]

def rerank_documents(result, query, top_n=2):

    documents = []
    document_dict = {}

    for item in result:
        document_dict[item["metadata"]["fullplot"]] = item
        documents.append(item["metadata"]["fullplot"])


    url = "https://api.jina.ai/v1/rerank"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + jina_api_key
    }
    payload = {
        "model": "jina-reranker-v2-base-multilingual",
        "query": query,
        "top_n": top_n,
        "documents": documents
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        respose_json = response.json()
        result = []
        for item in respose_json["results"]:
            result.append(document_dict[item["document"]["text"]])
        return result

    else:
        response.raise_for_status()