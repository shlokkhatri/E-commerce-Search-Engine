import json
import torch
from transformers import AutoTokenizer, AutoModel


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print("Loading Embedding Model.......")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

model.eval()

print("Model Loaded!")


def mean_pooling(model_output, attention_mask):

    token_embedding = model_output.last_hidden_state

    mask = attention_mask.unsqueeze(-1).expand(
        token_embedding.size()
    ).float()

    sum_embedding = torch.sum(
        token_embedding * mask,
        dim=1
    )

    sum_mask = torch.clamp(
        mask.sum(dim=1),
        min=1e-9
    )

    return sum_embedding / sum_mask


def generate_embeddings(texts):

    inputs = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True
    )

    with torch.no_grad():

        outputs = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"]
        )

    embeddings = mean_pooling(
        outputs,
        inputs["attention_mask"]
    )

    embeddings = torch.nn.functional.normalize(
        embeddings,
        p=2,
        dim=1
    )

    return embeddings.tolist()


def main():

    with open(
        "backend/data/products.json",
        "r",
        encoding="utf-8"
    ) as file:

        products = json.load(file)

    print(f"\nProducts Loaded: {len(products)}")

    # Test with 100 products
    test_products = products[:100]

    texts = []

    for product in test_products:

        text = (
            f"{product['name']}. "
            f"{product['brand']}. "
            f"{product['category']}. "
            f"{product['description']}"
        )

        texts.append(text)

    print("\nGenerating embeddings for 100 products...")

    embeddings = generate_embeddings(texts)

    print("\nEmbeddings Generated!")

    print("Number of embeddings:", len(embeddings))

    print("Embedding Dimensions:", len(embeddings[0]))

    print("\nFirst Product:")
    print(test_products[0]["name"])

    print("First 5 Values:")
    print(embeddings[0][:5])

    print("\nSecond Product:")
    print(test_products[1]["name"])

    print("First 5 Values:")
    print(embeddings[1][:5])


if __name__ == "__main__":
    main()