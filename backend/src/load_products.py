import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

ES_url = "http://localhost:9200"
INDEX_NAME = "products"

es = Elasticsearch(ES_url)


def load_products():

    # Read products from JSON
    with open(
        "backend/data/products.json",
        "r",
        encoding="utf-8"
    ) as file:
        products = json.load(file)

    print(f"Products loaded from JSON: {len(products)}")

    # Prepare documents for Elasticsearch
    actions = []

    for product in products:
        actions.append({
            "_index": INDEX_NAME,
            "_id": product["id"],
            "_source": product
        })

    print("Starting bulk insertion...")

    success, failed = bulk(
        es,
        actions,
        chunk_size=1000,
        request_timeout=120
    )

    print(f"Products inserted: {success}")
    print(f"Products failed: {len(failed)}")


if __name__ == "__main__":
    load_products()