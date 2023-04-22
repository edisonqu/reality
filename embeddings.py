from chromadb.api import Collection
from chromadb.utils.embedding_functions import EmbeddingFunction
from database import database_initialization_and_collection


def insert_to_db(collection: Collection, text: str, timestamp: str, embedding_function: EmbeddingFunction):

    embeddings = embedding_function([text])
    ids = [timestamp]
    collection.add(documents=[text], embeddings=embeddings, ids=ids)
    print(collection.count())


def query_db(collection: Collection, query_text: str, embedding_function: EmbeddingFunction, n_results=1):

    query_embed = embedding_function([query_text])

    results = collection.query(
        query_embeddings=query_embed,
        n_results=max(min(n_results, collection.count()), 1),
    )

    print(results)

    return results
