import pandas as pd
import pickle
import os
import numpy as np
import sys
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.configs import MistralConfig, OllamaConfig
from camel.loaders import UnstructuredIO
from camel.storages import Neo4jGraph
from camel.retrievers import AutoRetriever
from camel.embeddings import MistralEmbedding
from camel.types import StorageType
from camel.agents import ChatAgent, KnowledgeGraphAgent
from camel.messages import BaseMessage
from langchain_openai import ChatOpenAI
from camel.configs import ChatGPTConfig
from check_pkl_data import load_pickle_to_dataframe
from config import (OPENAI_API_KEY, MODEL, NEO4J_URI, NEO4J_USERNAME,
                    NEO4J_PASSWORD)

sys.modules['numpy._core.numeric'] = np.core.numeric

# Specify the path to your .pkl file
pkl_path = './summarised_data/summarised_family_pig.pkl'

# Initialise LLM and RAG agent
llm = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI,
    model_type=ModelType.GPT_4O_MINI,
    model_config_dict=ChatGPTConfig(temperature=0.7).as_dict(),
    api_key=OPENAI_API_KEY,
)
uio = UnstructuredIO()
kg_agent = KnowledgeGraphAgent(model=llm)

# Set Neo4j instance
try:
    n4j = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
    )
    print("CAMEL Neo4jGraph initialized successfully")
except Exception as e:
    print("CAMEL Neo4jGraph error:", str(e))

if __name__ == "__main__":

    # Load the data
    print("Loading data from pickle file...")
    df = load_pickle_to_dataframe(pkl_path)
    print(f"Loaded {len(df)} rows of data")

    # Generate the graph
    for i, row in enumerate(df.itertuples(index=True)):
        print(f"\nProcessing row {i+1}/{len(df)}")

        text = f"{row.summarisedComment} This message was posted on the date {row.date}."
        element = uio.create_element_from_text(text=text,
                                               element_id=str(row.Index))
        graph_elements = kg_agent.run(element, parse_graph_elements=True)
        n4j.add_graph_elements(graph_elements=[graph_elements])
