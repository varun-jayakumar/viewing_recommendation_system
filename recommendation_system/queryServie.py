from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv
import os

load_dotenv()
pine_cone_api_key = os.environ["PINECONE_APIKEY"]
pc = Pinecone(api_key=pine_cone_api_key)
index = pc.Index("movies")


def queryVectorDB(vector, parsed_output, top_k = 10):
    if parsed_output.imdb == -1 and parsed_output.imdb == -1:
    # direclt query for plot only
        result = index.query(vector = vector, top_k=top_k, include_metadata = True, namespace = "moviePlot")

    elif parsed_output.imdb != -1 and parsed_output.year == -1:
        if parsed_output.imdb_greaterthan:
            # write query to query by > than imdb  
            result = index.query(vector = vector, top_k=top_k, filter = {"imdb": {"$gte": parsed_output.imdb }},include_metadata = True,  namespace = "moviePlot")
        elif parsed_output.imdb_lessthan:
            # write query to qery by < than imdb
            result = index.query(vector = vector, top_k=top_k, filter = {"imdb": {"$lte": parsed_output.imdb }},include_metadata = True,  namespace = "moviePlot")
        elif parsed_output.imdb_equal:
            # write query for equal
            result = index.query(vector = vector, top_k=top_k, filter = {"imdb": {"$eq": parsed_output.imdb }},include_metadata = True,  namespace = "moviePlot")
        else:
            # just query by prompt

            result = index.query(vector = vector, top_k=top_k, include_metadata = True,  namespace = "moviePlot")


    elif parsed_output.imdb == -1 and parsed_output.year != -1:
        if parsed_output.year_greaterthan:
            # write query to query by > than imdb
            result = index.query(vector = vector, top_k=top_k, filter = {"year": {"$gte": parsed_output.year }},include_metadata = True,  namespace = "moviePlot")
        elif parsed_output.year_lessthan:
            # write query to qery by < than imdb
            result = index.query(vector = vector, top_k=top_k, filter = {"year": {"$lte": parsed_output.year }},include_metadata = True,  namespace = "moviePlot")
        elif parsed_output.year_equal:
            # write query for equal
            result = index.query(vector = vector, top_k=top_k, filter = {"year": {"$eq": parsed_output.year }},include_metadata = True,  namespace = "moviePlot")
        else:
            # just query by prompt
            result = index.query(vector = vector, top_k=top_k, include_metadata = True)

        
    elif parsed_output.imdb != -1 and parsed_output.imdb != -1:
        if parsed_output.imdb_greaterthan and parsed_output.year_greaterthan:
            result = index.query(vector = vector, top_k=top_k, filter = {"year": {"$gte": parsed_output.imdb }, "imdb": {"$gte": parsed_output.imdb }},include_metadata = True,  namespace = "moviePlot")
        elif parsed_output.imdb_lessthan and parsed_output.year_lessthan:
            result = index.query(vector = vector, top_k=top_k, filter = {"year": {"$lte": parsed_output.imdb }, "imdb": {"$lte": parsed_output.imdb }},include_metadata = True ,  namespace = "moviePlot")
        elif parsed_output.imdb_greaterthan and parsed_output.year_lessthan:
            result = index.query(vector = vector, top_k=top_k, filter = {"year": {"$lte": parsed_output.imdb }, "imdb": {"$gte": parsed_output.imdb }},include_metadata = True,  namespace = "moviePlot")
        elif parsed_output.imdb_lessthan and parsed_output.year_greaterthan:
            result = index.query(vector = vector, top_k=top_k, filter = {"year": {"$gte": parsed_output.imdb }, "imdb": {"$lte": parsed_output.imdb }},include_metadata = True,  namespace = "moviePlot")
        elif parsed_output.year_equal and parsed_output.imdb_equal:
            result = index.query(vector = vector, top_k=top_k, filter = {"year": {"$eq": parsed_output.imdb }, "imdb": {"$eq": parsed_output.imdb }},include_metadata = True,  namespace = "moviePlot")

        else:
            result = index.query(vector = vector, top_k=top_k, include_metadata = True,  namespace = "moviePlot")
        
    
    return result
        