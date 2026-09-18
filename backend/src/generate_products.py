import json
import random


OUTPUT_FILE = "backend/data/products.json"

TOTAL_PRODUCTS = 100_000


# REALISTIC BRAND -> CATEGORY RELATIONSHIPS

BRAND_CATEGORIES = {

    "Samsung": [
        "Smartphones",
        "Televisions",
        "Monitors",
        "Tablets",
        "Smartwatches",
        "Storage"
    ],

    "Apple": [
        "Smartphones",
        "Laptops",
        "Tablets",
        "Smartwatches",
        "Headphones"
    ],

    "OnePlus": [
        "Smartphones",
        "Earbuds",
        "Smartwatches",
        "Televisions"
    ],

    "Xiaomi": [
        "Smartphones",
        "Smartwatches",
        "Televisions",
        "Smart Home",
        "Tablets",
        "Earbuds"
    ],

    "Realme": [
        "Smartphones",
        "Earbuds",
        "Smartwatches",
        "Tablets"
    ],

    "Motorola": [
        "Smartphones",
        "Tablets"
    ],

    "Vivo": [
        "Smartphones",
        "Earbuds",
        "Smartwatches"
    ],

    "Nothing": [
        "Smartphones",
        "Earbuds"
    ],

    "Huawei": [
        "Smartphones",
        "Tablets",
        "Smartwatches",
        "Earbuds"
    ],

    "Dell": [
        "Laptops",
        "Monitors",
        "Storage"
    ],

    "HP": [
        "Laptops",
        "Monitors"
    ],

    "Lenovo": [
        "Laptops",
        "Tablets",
        "Monitors"
    ],

    "Asus": [
        "Laptops",
        "Monitors",
        "Gaming",
        "Keyboards",
        "Mice"
    ],

    "MSI": [
        "Laptops",
        "Monitors",
        "Gaming",
        "Keyboards",
        "Mice"
    ],

    "Acer": [
        "Laptops",
        "Monitors",
        "Gaming"
    ],

    "Sony": [
        "Headphones",
        "Earbuds",
        "Cameras",
        "Televisions",
        "Gaming"
    ],

    "JBL": [
        "Headphones",
        "Earbuds"
    ],

    "Boat": [
        "Headphones",
        "Earbuds",
        "Smartwatches"
    ],

    "Canon": [
        "Cameras"
    ],

    "Nikon": [
        "Cameras"
    ],

    "LG": [
        "Televisions",
        "Monitors",
        "Smart Home"
    ],

    "Corsair": [
        "Gaming",
        "Keyboards",
        "Mice",
        "Storage"
    ],

    "Keychron": [
        "Keyboards"
    ],

    "Logitech": [
        "Keyboards",
        "Mice",
        "Gaming"
    ],

    "WD": [
        "Storage"
    ],

    "Seagate": [
        "Storage"
    ],

    "Anker": [
        "Chargers",
        "Power Banks",
        "Earbuds"
    ],

    "Belkin": [
        "Chargers",
        "Power Banks"
    ]
}


# PRODUCT NAME TEMPLATES

PRODUCT_TEMPLATES = {

    "Smartphones": [
        "Galaxy Pro Smartphone",
        "Galaxy Ultra Smartphone",
        "Galaxy Max Smartphone",
        "Premium Smartphone",
        "Flagship Smartphone",
        "Pro Max Smartphone",
        "5G Smartphone",
        "Performance Smartphone"
    ],

    "Laptops": [
        "Business Laptop",
        "Performance Laptop",
        "Professional Laptop",
        "Ultra Laptop",
        "Slim Laptop",
        "Gaming Laptop",
        "Portable Laptop",
        "Premium Laptop"
    ],

    "Headphones": [
        "Wireless Headphones",
        "Noise Cancelling Headphones",
        "Premium Headphones",
        "Studio Headphones",
        "Bluetooth Headphones",
        "Over Ear Headphones"
    ],

    "Earbuds": [
        "Wireless Earbuds",
        "Pro Wireless Earbuds",
        "Noise Cancelling Earbuds",
        "Bluetooth Earbuds",
        "Premium Earbuds"
    ],

    "Keyboards": [
        "Mechanical Keyboard",
        "Wireless Keyboard",
        "Gaming Keyboard",
        "RGB Mechanical Keyboard",
        "Professional Keyboard"
    ],

    "Mice": [
        "Wireless Mouse",
        "Gaming Mouse",
        "Ergonomic Mouse",
        "RGB Gaming Mouse",
        "Precision Mouse"
    ],

    "Monitors": [
        "Gaming Monitor",
        "4K Monitor",
        "UltraWide Monitor",
        "Professional Monitor",
        "LED Monitor",
        "High Refresh Rate Monitor"
    ],

    "Cameras": [
        "Mirrorless Camera",
        "Digital Camera",
        "Professional Camera",
        "DSLR Camera",
        "4K Camera"
    ],

    "Smartwatches": [
        "Smartwatch",
        "Fitness Smartwatch",
        "Pro Smartwatch",
        "GPS Smartwatch",
        "Premium Smartwatch"
    ],

    "Gaming": [
        "Gaming Console",
        "Gaming Controller",
        "Gaming Setup",
        "Gaming Accessory",
        "Gaming Device"
    ],

    "Televisions": [
        "4K Smart Television",
        "OLED Smart Television",
        "QLED Television",
        "Smart LED Television",
        "Ultra HD Television"
    ],

    "Smart Home": [
        "Smart Home Hub",
        "Smart Speaker",
        "Smart Camera",
        "Smart Light",
        "Smart Home Device"
    ],

    "Tablets": [
        "Android Tablet",
        "Pro Tablet",
        "Premium Tablet",
        "10 Inch Tablet",
        "Performance Tablet"
    ],

    "Storage": [
        "Portable SSD",
        "External SSD",
        "External Hard Drive",
        "NVMe SSD",
        "Portable Storage Drive"
    ],

    "Chargers": [
        "Fast Charger",
        "USB C Charger",
        "GaN Charger",
        "Multi Port Charger",
        "Wireless Charger"
    ],

    "Power Banks": [
        "10000mAh Power Bank",
        "20000mAh Power Bank",
        "30000mAh Power Bank",
        "Fast Charging Power Bank",
        "Portable Power Bank"
    ]
}


# PRICE RANGES

PRICE_RANGES = {

    "Smartphones": (8000, 150000),
    "Laptops": (25000, 250000),
    "Headphones": (1000, 40000),
    "Earbuds": (800, 30000),
    "Keyboards": (700, 25000),
    "Mice": (400, 15000),
    "Monitors": (7000, 100000),
    "Cameras": (25000, 300000),
    "Smartwatches": (1500, 50000),
    "Gaming": (2000, 100000),
    "Televisions": (15000, 250000),
    "Smart Home": (1000, 40000),
    "Tablets": (8000, 120000),
    "Storage": (1000, 50000),
    "Chargers": (500, 10000),
    "Power Banks": (800, 8000)
}


# DESCRIPTIONS

DESCRIPTION_TEMPLATES = {

    "Smartphones":
        "High performance smartphone with modern processor, "
        "excellent camera, long battery life and 5G connectivity",

    "Laptops":
        "Powerful laptop designed for work, productivity, "
        "entertainment and demanding applications",

    "Headphones":
        "Premium wireless headphones with clear audio, "
        "comfortable design and long battery life",

    "Earbuds":
        "Compact wireless earbuds with high quality sound, "
        "Bluetooth connectivity and comfortable fit",

    "Keyboards":
        "High quality keyboard with responsive keys, "
        "durable construction and comfortable typing experience",

    "Mice":
        "Precision mouse with accurate tracking, "
        "ergonomic design and responsive controls",

    "Monitors":
        "High resolution monitor with excellent colors, "
        "smooth refresh rate and modern connectivity",

    "Cameras":
        "High quality camera designed for photography "
        "and professional video recording",

    "Smartwatches":
        "Feature rich smartwatch with fitness tracking, "
        "notifications and long battery life",

    "Gaming":
        "High performance gaming product designed "
        "for immersive gaming and competitive performance",

    "Televisions":
        "Modern smart television with high resolution display, "
        "excellent picture quality and streaming support",

    "Smart Home":
        "Connected smart home device with easy setup, "
        "mobile control and intelligent automation",

    "Tablets":
        "Portable tablet with bright display, powerful processor "
        "and long battery life",

    "Storage":
        "Reliable high speed storage device for files, "
        "applications, backups and media",

    "Chargers":
        "Fast charging power adapter with multiple ports "
        "and modern charging technology",

    "Power Banks":
        "Portable high capacity power bank with fast charging "
        "and multiple charging ports"
}


# GENERATE PRODUCTS

def generate_products():

    products = []

    brands = list(BRAND_CATEGORIES.keys())

    for product_id in range(1, TOTAL_PRODUCTS + 1):

        # Choose brand
        brand = random.choice(brands)

        # Choose only a category that this brand actually sells
        category = random.choice(
            BRAND_CATEGORIES[brand]
        )

        # Product name
        template = random.choice(
            PRODUCT_TEMPLATES[category]
        )

        product_name = (
            f"{brand} "
            f"{template} "
            f"{random.randint(1, 999)}"
        )

        # Price
        min_price, max_price = PRICE_RANGES[category]

        price = random.randint(
            min_price,
            max_price
        )

        # Rating
        rating = round(
            random.uniform(3.0, 5.0),
            1
        )

        # Reviews
        reviews = random.randint(
            10,
            25000
        )

        # Stock
        stock = random.randint(
            0,
            500
        )

        description = DESCRIPTION_TEMPLATES[
            category
        ]

        product = {
            "id": product_id,
            "name": product_name,
            "brand": brand,
            "category": category,
            "description": description,
            "price": price,
            "rating": rating,
            "reviews": reviews,
            "stock": stock
        }

        products.append(product)

        # Progress
        if product_id % 10000 == 0:
            print(
                f"Generated {product_id:,} products..."
            )

    # Save
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            products,
            file,
            indent=2
        )

    print()
    print("=" * 50)
    print("DATASET GENERATION COMPLETE")
    print("=" * 50)
    print(f"Products generated: {len(products):,}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_products()