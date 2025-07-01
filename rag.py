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
from neo4j.debug import watch

watch("neo4j")

# Specify the path to your .pkl file
pkl_path = './summarised_data/summarised_family_pig.pkl'

# Initialise LLM and RAG agent
llm = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI,
    model_type=ModelType.GPT_4_1_NANO,
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

# # # Set retriever
# # camel_retriever = AutoRetriever(
# #     vector_storage_local_path="local_data/embedding_storage",
# #     storage_type=StorageType.QDRANT,
# #     embedding_model=MistralEmbedding(),
# # )

# def row_to_graph_elements(row):
#     username = row["username"]
#     chat_id = row["chatId"]
#     comment_text = row["summarisedComment"]
#     date = row["date"]

#     return [
#         {
#             "type": "node",
#             "label": "User",
#             "properties": {
#                 "username": username
#             }
#         },
#         {
#             "type": "node",
#             "label": "Chat",
#             "properties": {
#                 "chatId": chat_id
#             }
#         },
#         {
#             "type": "node",
#             "label": "Comment",
#             "properties": {
#                 "text": comment_text,
#                 "date": date
#             }
#         },
#         {
#             "type": "relationship",
#             "from": {
#                 "label": "User",
#                 "key": "username",
#                 "value": username
#             },
#             "to": {
#                 "label": "Comment",
#                 "key": "text",
#                 "value": comment_text
#             },
#             "type": "POSTED"
#         },
#         {
#             "type": "relationship",
#             "from": {
#                 "label": "Comment",
#                 "key": "text",
#                 "value": comment_text
#             },
#             "to": {
#                 "label": "Chat",
#                 "key": "chatId",
#                 "value": chat_id
#             },
#             "type": "IN_CHAT"
#         },
#     ]

# if __name__ == "__main__":

#     # Load the data
#     print("Loading data from pickle file...")
#     df = load_pickle_to_dataframe(pkl_path)
#     print(f"Loaded {len(df)} rows of data")

#     for i, row in enumerate(df.itertuples(index=True)):
#         print(f"\nProcessing row {i+1}/{len(df)}")

#         # Step 1: Manual structure
#         graph_elements = row_to_graph_elements(row)
#         n4j.add_graph_elements(graph_elements=graph_elements)
#         print(f"Added {len(graph_elements)} graph elements to Neo4j")

#         # Step 2: Semantic enrichment
#         element = uio.create_element_from_text(text=row.summarisedComment,
#                                                element_id=str(row.commentUuid))
#         enriched_graph = kg_agent.run(element, parse_graph_elements=True)
#         n4j.add_graph_elements(graph_elements=enriched_graph)
#         print(f"Added {len(enriched_graph)} enriched graph elements to Neo4j")
