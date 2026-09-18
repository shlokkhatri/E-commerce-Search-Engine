from elasticsearch import Elasticsearch
import re
import time

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
            "multi_match": {
                "query": search_text,
                "fields": [
                    "name^4",
                    "description"
                ],
                "fuzziness": "AUTO"
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


# -----MAIN-----

if __name__ == "__main__":
    user_demand = input("Search the Product : \n")

    brands = get_brands()
    categories = get_categories()

    print("\nBrands")
    print(brands)

    print("\nCategories")
    print(categories)

    search_text, filters = parse_filter(user_demand)

    print("\nSearch text:")
    print(search_text)

    print("\nDetected filters:")
    print(filters)

    results = search_product(
        search_text,
        filters
    )

    print(f"\nFound {len(results)} products:\n")

    for result in results:

        product = result["_source"]

        print(
            f"{product['name']} | "
            f"Price : ₹{product['price']} | "
            f"Rating: {product['rating']} | "
            f"Stock: {product['stock']}"
        )