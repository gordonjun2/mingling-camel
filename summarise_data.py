import os
import re
import pandas as pd
import json
from typing import Dict
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from config import OPENAI_API_KEY, MODEL, PROMPT_TEMPLATE, TOKEN_LIMIT


class SummariseCounter:
    total_calls = 0
    successful_calls = 0
    failed_calls = 0

    @classmethod
    def increment(cls, success=True):
        cls.total_calls += 1
        if success:
            cls.successful_calls += 1
        else:
            cls.failed_calls += 1

    @classmethod
    def get_stats(cls):
        return {
            "total_calls": cls.total_calls,
            "successful_calls": cls.successful_calls,
            "failed_calls": cls.failed_calls
        }


def batch_df_by_date(df):

    # Drop unwanted columns
    df = df.drop(['Chat Title', 'Chat ID'], axis=1)

    # Ensure Date Time column is datetime type
    df['Date Time'] = pd.to_datetime(df['Date Time'])

    # Rename columns
    column_mapping = {
        'Date Time': 'dateTime',
        'Comment UUID': 'commentUuid',
        'User ID': 'userId',
        'Username': 'username',
        'Comment': 'comment',
        'Reply to Comment UUID': 'replyToCommentUuid',
        'Reply to Comment': 'replyToComment'
    }
    df = df.rename(columns=column_mapping)

    # Add date column for grouping
    df['date'] = df['dateTime'].dt.date

    # Group into daily DataFrames
    daily_batches = df.groupby('date')

    return daily_batches


def count_tokens(text):
    # Use a simple character-based estimation for token count
    # GPT models typically use ~4 characters per token on average
    # This is a rough approximation but works well for most use cases
    estimated_tokens = len(text) // 4
    return estimated_tokens


def is_token_limit_exceeded(content):

    # Combine text with the prompt template (if needed)
    full_prompt_text = PROMPT_TEMPLATE.replace("{content}", content)

    # Check token length
    token_count = count_tokens(full_prompt_text)

    return token_count > TOKEN_LIMIT


def summarise(text):
    if not text or not text.strip():
        SummariseCounter.increment(success=False)
        return ""

    try:
        llm = ChatOpenAI(model_name=MODEL,
                         openai_api_key=OPENAI_API_KEY,
                         temperature=0.7)

        # Create prompt template
        prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

        # Create and run the chain
        llm_chain = LLMChain(prompt=prompt, llm=llm)
        response = llm_chain.invoke(input={"content": text})
        SummariseCounter.increment(success=True)
        return response["text"]
    except Exception as e:
        print(f"Error during summarisation: {str(e)}")
        SummariseCounter.increment(success=False)
        return ""


def split_records_into_chunks(records, model_name="gpt-4o-mini"):
    """Split records into chunks that don't exceed the token limit."""
    chunks = []
    current_chunk = []
    current_chunk_str = ""

    for record in records:
        # Add record to test chunk
        test_chunk = current_chunk + [record]
        test_chunk_str = json.dumps(test_chunk)

        # Check if adding this record would exceed token limit
        if is_token_limit_exceeded(test_chunk_str):
            # If current chunk is not empty, add it to chunks
            if current_chunk:
                chunks.append(current_chunk)
            # Start new chunk with current record
            current_chunk = [record]
            current_chunk_str = json.dumps(current_chunk)
        else:
            # Add record to current chunk
            current_chunk = test_chunk
            current_chunk_str = test_chunk_str

    # Add the last chunk if not empty
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def clean_and_parse_summary(summary_str):
    # Remove ```json and ``` markers (and optional whitespace)
    try:
        cleaned = re.sub(r"```json\s*|\s*```", "", summary_str).strip()
        # Parse JSON string to list of dicts
        data = json.loads(cleaned)
        return pd.DataFrame(data)
    except (json.JSONDecodeError, Exception) as e:
        return pd.DataFrame()


if __name__ == "__main__":
    try:
        pickle_path = './raw_data/family_pig.pkl'
        df = pd.read_pickle(pickle_path)
        chat_id = df['Chat ID'].iloc[0]
        daily_batches = batch_df_by_date(df)
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        exit(1)

    # Initialize list to store all summary DataFrames
    all_summary_dfs = []

    # Loop through each batch
    for date, batch_df in daily_batches:
        try:
            # Sort chronologically
            batch_df = batch_df.sort_values('dateTime')
            batch_df['dateTime'] = batch_df['dateTime'].dt.strftime(
                '%Y-%m-%d %H:%M:%S')
            batch_df = batch_df.drop(columns='date')
            records = batch_df.to_dict('records')
            records_str = json.dumps(records)

            if is_token_limit_exceeded(records_str):
                # Split records into smaller chunks
                chunks = split_records_into_chunks(records)
                # Process each chunk
                for chunk in chunks:
                    chunk_str = json.dumps(chunk)
                    summary = summarise(chunk_str)
                    if summary:  # Only process if we got a non-empty summary
                        print(
                            f"Summary for chunk of {len(chunk)} records on {date}:"
                        )
                        print(summary)
                        print("\n")
                        summary_df = clean_and_parse_summary(summary)
                        if not summary_df.empty:
                            summary_df['chatId'] = chat_id
                            all_summary_dfs.append(summary_df)
            else:
                # Process the entire batch
                summary = summarise(records_str)
                if summary:  # Only process if we got a non-empty summary
                    print(f"Summary for {len(records)} records on {date}:")
                    print(summary)
                    print("\n")
                    summary_df = clean_and_parse_summary(summary)
                    if not summary_df.empty:
                        summary_df['chatId'] = chat_id
                        all_summary_dfs.append(summary_df)
        except Exception as e:
            print(f"Error processing batch for date {date}: {str(e)}")
            continue  # Continue with next batch

    # Combine all summary DataFrames
    if all_summary_dfs:
        try:
            final_summary_df = pd.concat(all_summary_dfs, ignore_index=True)

            # Sort by date
            final_summary_df = final_summary_df.sort_values('date')

            print("Final Summary DataFrame:")
            print(final_summary_df)

            # Create the summarised_data directory if it doesn't exist
            os.makedirs('./summarised_data', exist_ok=True)

            file_name = 'summarised_' + pickle_path.split('/')[-1]
            file_path = f'./summarised_data/{file_name}'
            final_summary_df.to_pickle(file_path)
            print(f"\nSummary saved to {file_path}")
        except Exception as e:
            print(f"Error saving final summary: {str(e)}")
    else:
        print("No summaries were generated successfully.")

    # Print summarisation statistics
    stats = SummariseCounter.get_stats()
    print("\nSummarisation Statistics:")
    print(f"Total calls to summarise(): {stats['total_calls']}")
    print(f"Successful calls: {stats['successful_calls']}")
    print(f"Failed calls: {stats['failed_calls']}")
