import chromadb
from chromadb.utils import embedding_functions
import os
from config import OPENAI_API_KEY
import numpy as np
import sys

sys.modules['numpy._core.numeric'] = np.core.numeric


def load_embeddings(vector_db_path, collection_name):
    """
    Load embeddings from a copied vector_data directory.
    
    Args:
        vector_db_path: Path to the copied vector_data directory
        collection_name: Name of the collection to load
    """
    # Initialize ChromaDB client with the vector_db_path
    client = chromadb.PersistentClient(path=vector_db_path)

    # Initialize the same embedding function (must match what was used to create the embeddings)
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY, model_name="text-embedding-3-large")

    # Get the existing collection
    collection = client.get_collection(name=collection_name,
                                       embedding_function=openai_ef)

    return collection


if __name__ == "__main__":
    # Example usage
    # Point this to wherever you copied the vector_data directory
    VECTOR_DB_PATH = './summarised_family_pig_vector_data'
    COLLECTION_NAME = 'summarised_family_pig'

    # Load the embeddings
    collection = load_embeddings(VECTOR_DB_PATH, COLLECTION_NAME)

    # Test query to verify loading worked
    results = collection.query(
        query_texts=["What is chanel currently working as?"], n_results=3)
    print("\nQuery results:")
    print(results)

    # Example with metadata filtering
    results = collection.query(query_texts=["What do you like to do?"],
                               where={"username": "gordonjun"},
                               n_results=3)
    print("\nFiltered results:")
    print(results)
