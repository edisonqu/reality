from chromadb.api import Collection
from chromadb.utils.embedding_functions import EmbeddingFunction


def insert_to_db(collection: Collection, text: str, timestamp: str, embedding_function: EmbeddingFunction):

    embeddings = embedding_function([text])
    ids = [timestamp]
    collection.add(documents=[text], embeddings=embeddings, ids=ids)


def query_db(collection: Collection, query_text: str, embedding_function: EmbeddingFunction):

    query_embed = embedding_function([query_text])

    results = collection.query(
        query_embeddings=query_embed,
        n_results=1,
    )

    print(results)
