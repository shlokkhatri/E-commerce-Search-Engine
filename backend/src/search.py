from elasticsearch import Elasticsearch
import re
import time
from generate_embedding import generate_embeddings

ES_url = "http://localhost:9200"

INDEX_NAME = "products"

es = Elasticsearch(ES_url)


def search_product(search_text, filters):

    filter_queries = []

    # Brand filter

    if "brand" in filters:

        filter_queries.append({
            "term": {
                "brand": filters["brand"]
            }
        })

    # Category filter

    if "category" in filters:

        filter_queries.append({
            "term": {
                "category": filters["category"]
            }
        })

    # Minimum price

    if "min_price" in filters:

        filter_queries.append({
            "range": {
                "price": {
                    "gte": filters["min_price"]
                }
            }
        })

    # Maximum price

    if "max_price" in filters:

        filter_queries.append({
            "range": {
                "price": {
                    "lte": filters["max_price"]
                }
            }
        })

    # Minimum rating

    if "min_rating" in filters:

        filter_queries.append({
            "range": {
                "rating": {
                    "gte": filters["min_rating"]
                }
            }
        })

    # Text search

    must_queries = []

    if search_text.strip():

        must_queries.append({
            "bool" : {
                "should" : [

                    # Fuzzy search
                    {
                        "multi_match" :{
                            "query" : search_text,
                            "fields" : ["name^4","description"],
                            "fuzziness" : "AUTO"
                        }
                    },

                    # Prefix Search
                    {
                        "multi_match" : {
                            "query" : search_text,
                            "type" : "bool_prefix",
                            "fields" : [
                                "name", "name._2gram", "name._3gram"
                            ]
                        }
                    }
                ],
                "minimum_should_match" : 1
            }
        })

    # Elasticsearch search

    start_time = time.perf_counter()

    response = es.search(
        index=INDEX_NAME,
        size=10,
        query={
            "bool": {
                "must": must_queries,
                "filter": filter_queries
            }
        }
    )
    end_time = time.perf_counter()
    search_time_ms = (end_time - start_time) * 1000
    print(f"\nSearch time: {search_time_ms:.2f} ms")

    return response["hits"]["hits"]

def hybrid_search(search_text, filters, original_query=None):
    print("\nHybrid search")

    # If filters removed all words from search_text,
    # Use the original user query for simentic/vector search
    vector_text = original_query if original_query else search_text

    # KEYWORD SEARCH
    keyword_result = search_product(
        search_text,
        filters
    )

    print(f"\nKeyword Result : {len(keyword_result)}")
    
    # VECTOR SEARCH
    query_embedding = generate_embeddings([vector_text])[0]

    print(f"Query Embedding Dimensions: {len(query_embedding)}")

    # Build the same filter for Vector Search
    filter_queries = []

    if "brand" in filters:
        filter_queries.append({
            "term": {
                "brand": filters["brand"]
            }
        })

    if "category" in filters:
        filter_queries.append({
            "term": {
                "category": filters["category"]
            }
        })

    if "min_price" in filters:
        filter_queries.append({
            "range": {
                "price": {
                    "gte": filters["min_price"]
                }
            }
        })

    if "max_price" in filters:
        filter_queries.append({
            "range": {
                "price": {
                    "lte": filters["max_price"]
                }
            }
        })

    if "min_rating" in filters:
        filter_queries.append({
            "range": {
                "rating": {
                    "gte": filters["min_rating"]
                }
            }
        })

    vector_query = {
        "script_score": {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_all": {}
                        }
                    ],
                    "filter": filter_queries
                }
            },
            "script": {
                "source": """
                    cosineSimilarity(
                        params.query_vector,
                        'description_embedding'
                    ) + 1.0
                """,
                "params": {
                    "query_vector": query_embedding
                }
            }
        }
    }

    vector_response = es.search(
        index=INDEX_NAME,
        size=10,
        query=vector_query
    )

    vector_result = vector_response["hits"]["hits"]

    print(f"Vector Result : {len(vector_result)}")
    
    # COMBINE KEYWORD + VECTOR RESULTS
    combined = {}

    # Add keyword results
    for result in keyword_result:

        product_id = result["_id"]

        combined[product_id] = {
            "product": result,
            "keyword_score": result["_score"] or 0,
            "vector_score": 0
        }

    # Add vector results
    for result in vector_result:

        product_id = result["_id"]

        if product_id not in combined:

            combined[product_id] = {
                "product": result,
                "keyword_score": 0,
                "vector_score": result["_score"] or 0
            }

        else:

            combined[product_id]["vector_score"] = (
                result["_score"] or 0
            )
    
    # CALCULATE HYBRID SCORE
    for item in combined.values():

        item["hybrid_score"] = (
            item["keyword_score"] * 0.5
            +
            item["vector_score"] * 0.5
        )
    
    # SORT RESULTS
    results = sorted(
        combined.values(),
        key=lambda x: x["hybrid_score"],
        reverse=True
    )

    return results

# GET BRANDS

def get_brands():

    response = es.search(
        index=INDEX_NAME,
        size=0,
        aggs={
            "brands": {
                "terms": {
                    "field": "brand",
                    "size": 100
                }
            }
        }
    )

    return [
        bucket["key"]
        for bucket in response["aggregations"]["brands"]["buckets"]
    ]


# GET CATEGORIES-----------------

def get_categories():

    response = es.search(
        index=INDEX_NAME,
        size=0,
        aggs={
            "categories": {
                "terms": {
                    "field": "category",
                    "size": 100
                }
            }
        }
    )

    return [
        bucket["key"]
        for bucket in response["aggregations"]["categories"]["buckets"]
    ]


# CATEGORY ALIASES-----------------

CATEGORY_ALIASES = {

    "smartphone": "Smartphones",
    "smartphones": "Smartphones",
    "phone": "Smartphones",
    "phones": "Smartphones",

    "laptop": "Laptops",
    "laptops": "Laptops",

    "headphone": "Headphones",
    "headphones": "Headphones",

    "earbud": "Earbuds",
    "earbuds": "Earbuds",

    "keyboard": "Keyboards",
    "keyboards": "Keyboards",

    "mouse": "Mice",
    "mice": "Mice",

    "monitor": "Monitors",
    "monitors": "Monitors",

    "camera": "Cameras",
    "cameras": "Cameras",

    "smartwatch": "Smartwatches",
    "smartwatches": "Smartwatches",

    "tablet": "Tablets",
    "tablets": "Tablets",

    "television": "Televisions",
    "televisions": "Televisions",
    "tv": "Televisions",
    "tvs": "Televisions",

    "charger": "Chargers",
    "chargers": "Chargers",

    "power bank": "Power Banks",
    "power banks": "Power Banks",

    "storage": "Storage",

    "gaming": "Gaming",

    "smart home": "Smart Home",

}


# PARSE USER FILTERS-----------------

def parse_filter(user_demand):

    filters = {}

    search_text = user_demand

    # Get brands from Elasticsearch

    brands = get_brands()
    for brand in brands:

        pattern = rf"\b{re.escape(brand)}\b"

        if re.search(
            pattern,
            user_demand,
            re.IGNORECASE
        ):

            filters["brand"] = brand

            search_text = re.sub(
                pattern,
                "",
                search_text,
                flags=re.IGNORECASE
            )

            break

    # Detect exact Elasticsearch categories

    categories = get_categories()
    for category in categories:
        pattern = rf"\b{re.escape(category)}\b"

        if re.search(
            pattern,
            user_demand,
            re.IGNORECASE
        ):

            filters["category"] = category

            search_text = re.sub(
                pattern,
                "",
                search_text,
                flags=re.IGNORECASE
            )

            break

    # Detect category aliases

    if "category" not in filters:

        # Sort by length so that ;"power bank" is checked before "bank", etc.
        aliases = sorted(
            CATEGORY_ALIASES.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )

        for alias, category in aliases:
            pattern = rf"\b{re.escape(alias)}\b"

            if re.search(
                pattern,
                user_demand,
                re.IGNORECASE
            ):

                filters["category"] = category

                search_text = re.sub(
                    pattern,
                    "",
                    search_text,
                    flags=re.IGNORECASE
                )

                break

    # ------------------------------------------------------
    # Maximum price
    # Examples:
    # under 50000
    # below 50000
    # less than 50000
    # ------------------------------------------------------

    under_match = re.search(
        r"(?:under|below|less than)\s*[₹]?\s*([\d,]+)",
        search_text,
        re.IGNORECASE
    )

    if under_match:

        filters["max_price"] = float(
            under_match.group(1).replace(",", "")
        )

        search_text = re.sub(
            r"(?:under|below|less than)\s*[₹]?\s*[\d,]+",
            "",
            search_text,
            flags=re.IGNORECASE
        )

    # ------------------------------------------------------
    # Minimum price
    # Examples:
    # above 20000
    # over 20000
    # more than 20000
    # ------------------------------------------------------

    above_match = re.search(
        r"(?:above|over|more than)\s*[₹]?\s*([\d,]+)",
        search_text,
        re.IGNORECASE
    )

    if above_match:

        filters["min_price"] = float(
            above_match.group(1).replace(",", "")
        )

        search_text = re.sub(
            r"(?:above|over|more than)\s*[₹]?\s*[\d,]+",
            "",
            search_text,
            flags=re.IGNORECASE
        )

    # ------------------------------------------------------
    # Minimum rating
    # Examples:
    # rating above 4
    # rated above 4
    # rating 4.5
    # ------------------------------------------------------

    rating_match = re.search(
        r"(?:rating|rated)\s*(?:above|over|at least)?\s*(\d+(?:\.\d+)?)",
        search_text,
        re.IGNORECASE
    )

    if rating_match:

        filters["min_rating"] = float(
            rating_match.group(1)
        )

        search_text = re.sub(
            r"(?:rating|rated)\s*(?:above|over|at least)?\s*\d+(?:\.\d+)?",
            "",
            search_text,
            flags=re.IGNORECASE
        )

    # Clean search text

    search_text = re.sub(
        r"\s+",
        " ",
        search_text
    ).strip()

    return search_text, filters

def autocomplete(query):

    response = es.search(
        index=INDEX_NAME,
        size=10,
        query={
            "multi_match": {
                "query": query,
                "type": "bool_prefix",
                "fields": [
                    "name",
                    "name._2gram",
                    "name._3gram"
                ]
            }
        }
    )

    return response["hits"]["hits"]

def vector_search(query_text) :
    query_embedding = generate_embeddings([query_text])[0]

    response = es.search(
        index = INDEX_NAME,
        size = 10,
        query = {
            "script_score" : {
                "query" : {
                    "match_all" : {}
                },
                "script" : {
                    "source" : "cosineSimilarity(params.query_vector, 'description_embedding') + 1.0",
                    "params" : {
                        "query_vector" :query_embedding
                    }
                }
            }
        }
    )
    return response ["hits"]["hits"]

# -----MAIN-----

if __name__ == "__main__":
    user_demand = input("Search the Product : \n")

    # Autocomplet

    suggestions = autocomplete(user_demand)
    print(f"\nSuggestions for '{user_demand}' :\n")
    for result in suggestions:
        product = result["_source"]
        print(product["name"])

    # Normal search

    brands = get_brands()
    categories = get_categories()

    print("\nBrands")
    print(brands)

    print("\nCategories")
    print(categories)

    # Parse filter from user query 
    search_text, filters = parse_filter(user_demand)

    print("\nSearch text:")
    print(search_text)

    print("\nDetected filters:")
    print(filters)

    results = hybrid_search(     # Hybrid search
        search_text,
        filters
    )

    print(f"\nFound {len(results)} products:\n")

    for result in results:

        product = result["product"]["_source"]

        print(
            f"{product['name']} | "
            f"Price : ₹{product['price']} | "
            f"Rating: {product['rating']} | "
            f"Stock: {product['stock']}"
        )
    print("\nSemantic Search Test")

    semantic_query = input(
        "\nEnter a semantic search query: "
    )

    semantic_results = vector_search(
        semantic_query
    )

    print("\nSemantic Search Results:\n")

    for result in semantic_results:

        product = result["_source"]

        print(
            f"{product['name']} | "
            f"Price: ₹{product['price']} | "
            f"Rating: {product['rating']} | "
            f"Score: {result['_score']:.4f}"
        )

    print("\nHybrid Results:\n")

    for item in results:

        product = item["product"]["_source"]

        print(
            f"{product['name']} | "
            f"Hybrid Score: {item['hybrid_score']:.4f} | "
            f"Keyword: {item['keyword_score']:.4f} | "
            f"Vector: {item['vector_score']:.4f}"
        )