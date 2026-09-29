# import json
# from generate_embedding import generate_embeddings
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk

# ES_url = "http://localhost:9200"
# INDEX_NAME = "products"

# es = Elasticsearch(ES_url)


# def load_products():

#     # Read products from JSON
#     with open(
#         "backend/data/products.json",
#         "r",
#         encoding="utf-8"
#     ) as file:
#         products = json.load(file)

#     print(f"Products loaded from JSON: {len(products)}")

#     # Prepare text for embedding
#     texts = []
#     for product in products:
#         text = (
#             f"{product['name']}."
#             f"{product['brand']}."
#             f"{product['category']}."
#             f"{product['description']}."
#         )
#         texts.append(text)

#     # Generate Embedding
#     print("\nGenerating Embedding.....")

#     embedding = generate_embeddings(texts)

#     print("Embedding Generated!")
#     print(f"Numbers of Embedding: {len(embedding)}")
#     print(f"Dimensions of Embedding: {len(embedding[0])}")

#     # Prepare documents for Elasticsearch
#     actions = []

#     for product in products:
#         actions.append({
#             "_index": INDEX_NAME,
#             "_id": product["id"],
#             "_source": product
#         })

#     print("Starting bulk insertion...")

#     success, failed = bulk(
#         es,
#         actions,
#         chunk_size=1000,
#         request_timeout=120
#     )

#     print(f"Products inserted: {success}")
#     print(f"Products failed: {len(failed)}")


# if __name__ == "__main__":
#     load_products()



import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from generate_embedding import generate_embeddings


ES_URL = "http://localhost:9200"
INDEX_NAME = "products"

es = Elasticsearch(ES_URL)


BATCH_SIZE = 32


def load_products():

    with open(
        "backend/data/products.json",
        "r",
        encoding="utf-8"
    ) as file:

        products = json.load(file)

    print(f"Products loaded from JSON: {len(products)}")

    print(f"Preparing to embed {len(products)} products")

    total_inserted = 0

    # --------------------------------
    # Process products in batches
    # --------------------------------

    for start in range(0, len(products), BATCH_SIZE):

        batch = products[start:start + BATCH_SIZE]

        print(
            f"\nProcessing products "
            f"{start + 1} - {start + len(batch)}"
        )

        # ----------------------------
        # Prepare text
        # ----------------------------

        texts = []

        for product in batch:

            text = (
                f"{product['name']}. "
                f"{product['brand']}. "
                f"{product['category']}. "
                f"{product['description']}"
            )

            texts.append(text)

        # ----------------------------
        # Generate embeddings
        # ----------------------------

        print("Generating embeddings...")

        embeddings = generate_embeddings(texts)

        print(
            f"Generated {len(embeddings)} embeddings"
        )

        # ----------------------------
        # Prepare Elasticsearh action
        # ----------------------------

        actions = []

        for product, embedding in zip(
            batch,
            embeddings
        ):

            product_with_embedding = product.copy()

            product_with_embedding[
                "description_embedding"
            ] = embedding

            actions.append({
                "_index": INDEX_NAME,
                "_id": product["id"],
                "_source": product_with_embedding
            })

        # ----------------------------
        # Insert batch
        # ----------------------------

        success, failed = bulk(
            es,
            actions,
            chunk_size=BATCH_SIZE,
            request_timeout=120
        )

        total_inserted += success

        print(
            f"Inserted: {success}"
        )

        if failed:
            print(
                f"Failed: {len(failed)}"
            )

    print("\n-----------------------------")
    print("Loading completed!")
    print(f"Total inserted: {total_inserted}")
    print("-----------------------------")


if __name__ == "__main__":
    load_products()