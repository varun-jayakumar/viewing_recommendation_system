from pinecone.grpc import PineconeGRPC as Pinecone
import uuid
import json
import os
from dotenv import load_dotenv

load_dotenv()

pine_cone_api_key = os.environ["PINECONE_APIKEY"]

pc = Pinecone(api_key=pine_cone_api_key)
index = pc.Index("movies")

def loadData(input_file: str, progress_file: str,skip_file: str, limit: int = 10, batch_size = 10):
    with open(input_file, 'r') as infile,open(skip_file, 'w') as skipfile, open(progress_file, 'w') as progfile:
        data = json.load(infile)
        total_objects = min(len(data), limit)
    
        for start in range(0, total_objects, batch_size):
            end = min(start + batch_size, total_objects)
            batch = data[start:end]

            vectors = [obj.get("plot_embedding", "") for obj in batch]
            batch_array = []

            for i, obj in enumerate(batch):
                if obj.get("plot_embedding", None):
                    newObj = {}
                    newObj["values"] = obj["plot_embedding"]
                    newObj["metadata"] = {
                            "plot": obj.get("plot", ""),
                            "genres": obj.get("genres", []),
                            "runtime": obj.get("runtime", 0),
                            "cast": obj.get("cast", []),
                            # "poster": obj.get("poster", None),
                            "title": obj.get("title", ""),
                            "fullplot": obj.get("fullplot", ""),
                            # "languages": obj.get("languages", None),
                            # "released": obj.get("released", None),
                            "directors": obj.get("directors", []),
                            "rated": obj.get("rated", 0),
                            # "awards": obj.get("awards", {}),
                            "year": obj.get("year", 0),
                            "imdb": obj.get("imdb", {}).get("rating", 0),
                            "countries": obj.get("countries", []),
                            "type": obj.get("type", ""),
                            # "tomatoes": obj.get("tomatoes", {}),
                            "num_mflix_comments": obj.get("num_mflix_comments", 0)
}
                    newObj["id"] = str(uuid.uuid1())
                    batch_array.append(newObj)
                else:
                    skipfile.write(str("Skipped vector missing at " + str(start + i+1) + " " +obj.get("title", "")))
                    skipfile.write(obj.get("plot", ""))
                    skipfile.write("\n")
                    skipfile.write("\n")

            
            index.upsert(
                vectors=batch_array,
                namespace = "moviePlot"
            )
            out = str("inserted "+ str(end) + "/" +str(total_objects))
            progfile.write(out)
            
            progfile.write("\n")


input_file = "embedded_movies.json"
progress_file = "progress.txt"
skip_file = "skip.txt"

loadData(input_file, progress_file,skip_file, 22000, 10)
