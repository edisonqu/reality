import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

API_KEY = "MY_API_KEY"

chroma_settings = Settings(
    chroma_db_impl="duckdb+parquet", persist_directory=".chromadb/")

chroma_client = chromadb.Client(chroma_settings)

cohere_ef = embedding_functions.CohereEmbeddingFunction(
    api_key=API_KEY,  model_name="large")

documents = ["I like burgers", "I hate pizza"]

embeddings = cohere_ef(texts=documents)

metadatas = [{"id": "1", "metadata2": "123"},
             {"id": "2", "metadata2": "456"}]
ids = ["id1", "id2"]

collection = chroma_client.get_or_create_collection(
    name="test_collection", embedding_function=cohere_ef)

collection.add(documents=documents, embeddings=embeddings,
               metadatas=metadatas, ids=ids)

results = collection.query(query_texts=["burger"], n_results=2)
print(results)
