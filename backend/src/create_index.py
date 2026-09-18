from elasticsearch import Elasticsearch

ES_url = "http://localhost:9200"
INDEX_NAME = "products"

es = Elasticsearch(ES_url)


def create_index():

    # Delete old index if it exists
    if es.indices.exists(index=INDEX_NAME):
        print(f"Deleting existing index '{INDEX_NAME}'...")
        es.indices.delete(index=INDEX_NAME)

    mapping = {
        "mappings": {
            "properties": {
                "id": {
                    "type": "integer"
                },
                "name": {
                    "type": "text"
                },
                "brand": {
                    "type": "keyword"
                },
                "category": {
                    "type": "keyword"
                },
                "description": {
                    "type": "text"
                },
                "price": {
                    "type": "float"
                },
                "rating": {
                    "type": "float"
                },
                "reviews": {
                    "type": "integer"
                },
                "stock": { 
                    "type": "integer"
                }
            }
        }
    }

    es.indices.create(
        index=INDEX_NAME,
        body=mapping
    )

    print(f"Index '{INDEX_NAME}' created successfully!")


if __name__ == "__main__":
    create_index()