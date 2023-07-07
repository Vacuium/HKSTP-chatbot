import openai
import os
import requests
import numpy as np
import pandas as pd
from typing import Iterator
import tiktoken
import textract
from numpy import array, average
import configparser

from hkstp_chatbot.database import get_redis_connection
from hkstp_chatbot.transformers import handle_file_string

# Set our default models and chunking size
from hkstp_chatbot.config import COMPLETIONS_MODEL, EMBEDDINGS_MODEL, CHAT_MODEL, TEXT_EMBEDDING_CHUNK_SIZE, VECTOR_FIELD_NAME
INDEX_NAME = "f1-index"

# Ignore unclosed SSL socket warnings - optional in case you get these errors
import warnings

warnings.filterwarnings(action="ignore", message="unclosed", category=ImportWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning) 


pd.set_option('display.max_colwidth', 0)

# Connect to Redis
config = configparser.ConfigParser()
config.read('config.ini')

redis_client = get_redis_connection(host=(config['REDIS']['HOST']), password=(config['REDIS']
                ['PASSWORD']), port=(config['REDIS']['REDISPORT']))

data_dir = os.path.join(os.curdir,'data')
pdf_files = sorted([x for x in os.listdir(data_dir) if 'DS_Store' not in x])
tokenizer = tiktoken.get_encoding("cl100k_base")

# Process each PDF file and prepare for embedding
for pdf_file in pdf_files:
    
    pdf_path = os.path.join(data_dir,pdf_file)
    print(pdf_path)
    
    # Extract the raw text from each PDF using textract
    text = textract.process(pdf_path, method='pdfminer')
    
    # Chunk each document, embed the contents and load to Redis
    handle_file_string((pdf_file,text.decode("utf-8")),tokenizer,redis_client,VECTOR_FIELD_NAME,INDEX_NAME)

# Check that our docs have been inserted
print(redis_client.ft(INDEX_NAME).info()['num_docs'])