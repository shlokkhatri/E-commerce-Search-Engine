import torch

from transformers import AutoTokenizer, AutoModel

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print("Loading model...,")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

print("Model loaded!")

text = "Samsung wireless earbuds with noise cancellation"
# Convert text into tokens
inputs = tokenizer(
    text,
    return_tensors="pt",
    padding=True,
    truncation=True
)

# Generate model output
with torch.no_grad():
    outputs = model(**inputs)


# Mean pooling
token_embeddings = outputs.last_hidden_state

attention_mask = inputs["attention_mask"]

mask = attention_mask.unsqueeze(-1).expand(
    token_embeddings.size()
).float()

sum_embeddings = torch.sum(
    token_embeddings * mask,
    dim=1
)

sum_mask = torch.clamp(
    mask.sum(dim=1),
    min=1e-9
)

embedding = sum_embeddings / sum_mask


# Normalize the embedding
embedding = torch.nn.functional.normalize(
    embedding,
    p=2,
    dim=1
)


embedding = embedding[0].tolist()


print("\nEmbedding generated successfully!")

print("Vector dimensions:", len(embedding))

print("First 10 values:")
print(embedding[:10])