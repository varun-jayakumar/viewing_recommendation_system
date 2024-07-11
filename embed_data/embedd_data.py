import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

Jina_api_key = os.environ["JINA_APIKEY"]
# Function to get embeddings for multiple plots from the API
def get_embeddings(plots):
    url = "https://api.jina.ai/v1/embeddings"  # Replace with the actual API endpoint
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + Jina_api_key  # Replace with your actual API key
    }
    payload = {"input": plots, 
                'model': 'jina-embeddings-v2-base-en'}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        response.raise_for_status()

# Function to process the JSON file and add embeddings
def process_json_file(input_file, output_file, progress_file, limit=10, batch_size=10):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile, open(progress_file, 'w') as progfile:
        data = json.load(infile)
        progress = []
        total_objects = min(len(data), limit)
        outfile.write("[")
        
        for start in range(0, total_objects, batch_size):
            end = min(start + batch_size, total_objects)
            batch = data[start:end]
            
            plots = [obj.get("plot", "") for obj in batch]
            embeddings = get_embeddings(plots)
            
            for i, obj in enumerate(batch):
                if "plot" in obj:
                    obj["plot_embedding"] = embeddings[i]["embedding"]
                json.dump(obj, outfile)
                if not (start + i + 1 == total_objects):  # Don't add comma after the last element
                    outfile.write(',')
                progress.append(f"Processed {start + i + 1}/{total_objects} objects")
                
                # Write the progress to the progress file
                progfile.write(f"Processed {start + i + 1}/{total_objects} objects\n")
        outfile.write("]")

# Example usage
input_file = "movies.json"        # Path to the input JSON file
output_file = "embedded_movies.json"      # Path to the output JSON file
progress_file = "progress.txt"   # Path to the progress file

process_json_file(input_file, output_file, progress_file, limit=22000, batch_size=1000)
