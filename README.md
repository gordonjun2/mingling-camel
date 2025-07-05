# Chat Analysis and Agent Simulation System

A sophisticated system for analyzing chat conversations, generating summaries, and simulating agent interactions using vector and graph databases.

## Overview

This project provides a comprehensive solution for:

1. Summarizing chat conversations
2. Storing and querying conversation data using both vector and graph databases
3. Simulating agent interactions based on historical chat data

## Core Components

### 1. Data Summarization (`summarise_data.py`)

- Processes raw chat data from Telegram
- Generates concise summaries of conversations
- Handles multi-language content with English summaries
- Uses OpenAI's GPT models for summarization

### 2. Vector Database Integration (`insert_to_vector_db.py`, `load_embeddings.py`)

- Utilizes ChromaDB for vector storage
- Implements OpenAI embeddings for semantic search
- Supports efficient retrieval of similar conversations
- Includes metadata filtering capabilities

### 3. Graph Database Integration (`insert_to_graph_db.py`)

- Uses Neo4j for knowledge graph storage
- Extracts relationships and entities from conversations
- Enables complex relationship queries
- Powered by CAMEL AI framework

### 4. Agent Simulation (`agent_simulation.ipynb`)

- Simulates conversations between AI agents
- Leverages historical chat data for context
- Combines vector and graph search for enhanced responses
- Supports dynamic conversation flow

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key
- Neo4j database instance
- ChromaDB

### Environment Variables

Create a `.env` file with the following:

```
OPENAI_API_KEY=your_openai_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install CAMEL AI with all dependencies:
   ```bash
   pip install "camel-ai[all]==0.2.16"
   ```

## Usage

### 1. Data Summarization

```python
python summarise_data.py
```

### 2. Vector Database Population

```python
python insert_to_vector_db.py
```

### 3. Graph Database Population

```python
python insert_to_graph_db.py
```

### 4. Agent Simulation

Run the `agent_simulation.ipynb` notebook in Jupyter or Google Colab.

## Project Structure

```
.
├── summarise_data.py           # Chat summarization logic
├── insert_to_vector_db.py      # Vector database insertion
├── insert_to_graph_db.py       # Graph database insertion
├── load_embeddings.py          # Vector embedding utilities
├── agent_simulation.ipynb      # Agent simulation notebook
├── config.py                   # Configuration settings
└── requirements.txt           # Project dependencies
```

## Features

- **Multi-language Support**: Automatically translates non-English content to English during summarization
- **Semantic Search**: Utilizes vector embeddings for meaning-based conversation search
- **Knowledge Graph**: Extracts and stores relationships between entities in conversations
- **Agent Memory**: Implements both short-term and long-term memory for agent interactions
- **Configurable Parameters**: Easily adjust model parameters, chunk sizes, and search settings

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
