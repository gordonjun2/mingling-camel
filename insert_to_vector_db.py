from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
import os
import numpy as np
from config import OPENAI_API_KEY
from check_pkl_data import load_pickle_to_dataframe
import sys

sys.modules['numpy._core.numeric'] = np.core.numeric

# Set up the directory for ChromaDB
pkl_path = './summarised_data/summarised_family_pig.pkl'
collection_name = pkl_path.split('/')[-1].split('.')[0]
local_vector_db_path = './' + collection_name + '_vector_data'

os.makedirs(local_vector_db_path, exist_ok=True)

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=len,
)

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=local_vector_db_path)

# Initialize OpenAI embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY, model_name="text-embedding-3-large")

# Create or get collection
collection = client.get_or_create_collection(name=collection_name,
                                             embedding_function=openai_ef)

# Load the DataFrame
print("Loading data from pickle file...")
df = load_pickle_to_dataframe(pkl_path)
print(f"Loaded {len(df)} rows of data")

# Process each row in the DataFrame
doc_id = 0
total_rows = len(df)
for i, (_, row) in enumerate(df.iterrows()):
    print(f"Processing row {i+1}/{total_rows}")

    # Split the summarized comment into chunks
    chunks = text_splitter.split_text(row.summarisedComment)

    # Add each chunk with metadata
    for chunk in chunks:
        chunk = f"{chunk} This message was posted on the date {row.date}."
        collection.add(documents=[chunk],
                       ids=[f"comment_{doc_id}"],
                       metadatas=[{
                           "date": str(row.date),
                           "userId": str(row.userId),
                           "username": str(row.username)
                       }])
        doc_id += 1

print(f"Successfully processed and stored {doc_id} chunks with metadata")

# Example queries to test the system
results = collection.query(
    query_texts=["What is gordonjun's favourite investment?"], n_results=3)
print("\nSample query results:")
print(results)
