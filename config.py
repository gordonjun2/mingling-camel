from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MODEL = "gpt-4.1-nano"

TOKEN_LIMIT = 16384

PROMPT_TEMPLATE = """
You are given a list of Telegram chat messages in the following structured format:

```json
[
  {{
    "dateTime": "...",
    "userId": "...",
    "username": "...",
    "commentUuid": "...",
    "comment": "...",
    "replyToCommentUuid": "...",
    "replyToComment": "..."
  }},
  ...
]
```

Your task is to summarize the conversation in batches by providing a user-level summary of each participant's comments within the batch. Each user's comments (including their replies to others) should be analyzed for recurring themes, opinions, or contributions, and then summarized into a single sentence per user. If the original comments are in a language other than English, you must provide the summary in English regardless of the source language.
The output must strictly follow this format:

```json
[
  {{
    "date": "...",  
    "userId": "User A ID",
    "username": "User A",  
    "summarisedComment": "..."  
  }},
  {{
    "date": "...",  
    "userId": "User B ID",
    "username": "User B",  
    "summarisedComment": "..."  
  }},
  ...
]
```

Guidelines:
- The summary should reflect the main points or sentiments expressed by each user during the batch.
- If a user engages in multiple topics, provide an integrated summary covering their key points.
- Include references to replies if they significantly contribute to the user's message intent.
- Preserve the original language used in the comments, whether English, Chinese, or others.

DO NOT include any additional output or explanatory text. Only return the JSON array described above.

Example Input:
```json
[
  {{
    "dateTime": "2024-06-01 10:12:33",
    "userId": "001",
    "username": "Alice",
    "commentUuid": "001",
    "comment": "Did anyone see the BTC pump this morning?",
    "replyToCommentUuid": "",
    "replyToComment": ""
  }},
  {{
    "dateTime": "2024-06-01 10:13:11",
    "userId": "002",
    "username": "Bob",
    "commentUuid": "002",
    "comment": "Yeah, crazy how it broke $70K. Might be a fakeout though.",
    "replyToCommentUuid": "001",
    "replyToComment": "Did anyone see the BTC pump this morning?"
  }},
  {{
    "dateTime": "2024-06-01 10:14:45",
    "userId": "001",
    "username": "Alice",
    "commentUuid": "003",
    "comment": "It's probably because of the ETF approval rumor going around.",
    "replyToCommentUuid": "002",
    "replyToComment": "Yeah, crazy how it broke $70K. Might be a fakeout though."
  }},
  {{
    "dateTime": "2024-06-01 10:15:30",
    "userId": "003",
    "username": "Charlie",
    "commentUuid": "004",
    "comment": "I'm still waiting for it to retrace to $65K before entering.",
    "replyToCommentUuid": "",
    "replyToComment": ""
  }}
]
```

Example Output:
```json
[
  {{
    "date": "2024-06-01",
    "userId": "001",
    "username": "Alice",
    "summarisedComment": "Alice speculates the BTC pump is linked to ETF approval rumors and initially flagged the price movement."
  }},
  {{
    "date": "2024-06-01",
    "userId": "002",
    "username": "Bob",
    "summarisedComment": "Bob confirms the BTC surge and expresses caution, suggesting it may be a fakeout."
  }},
  {{
    "date": "2024-06-01",
    "userId": "003",
    "username": "Charlie",
    "summarisedComment": "Charlie remains cautious and plans to re-enter the market if BTC retraces to $65K."
  }}
]
```

Here is the input data:
{content}
"""
