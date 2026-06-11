# retriever.py
# This file connects to Pinecone and finds the most relevant
# table schemas based on the user's question.

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from django.conf import settings

# Load the embedding model once when the server starts
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to Pinecone
pc    = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)


def retrieve_schemas(user_query):
    # Step 1: Convert the user's question into a vector (list of numbers)
    query_vector = embedder.encode(user_query).tolist()

    # Step 2: Search Pinecone for the 3 most similar table descriptions
    results = index.query(vector=query_vector, top_k=3, include_metadata=True)

    # Step 3: Extract the text descriptions from the results
    schemas = [match["metadata"]["text"] for match in results["matches"]]

    # Step 4: Join them into one big string and return
    return "\n\n".join(schemas)