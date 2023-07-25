COMPLETIONS_MODEL = "text-davinci-003"
EMBEDDINGS_MODEL = "text-embedding-ada-002"
CHAT_MODEL = 'gpt-3.5-turbo'
TEXT_EMBEDDING_CHUNK_SIZE=200
VECTOR_FIELD_NAME='content_vector'
PREFIX = "hkstpdocs"  
INDEX_NAME = "hkstp-index"
VECTOR_DIM = 1536
DISTANCE_METRIC = "COSINE"
RETRIEVE_NUM = 12
TEMPERATURE = 0.8

EXTRACT_METHOD = {
    "pdf"  : "pdfminer",
    "docx" : "docx2txt",
    "dox"  : "antiword"
}
