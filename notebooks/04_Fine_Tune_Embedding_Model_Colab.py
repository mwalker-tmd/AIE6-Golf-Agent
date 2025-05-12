# =========================
# 🏌️‍♂️ Fine-Tune Embedding Model (Colab Ready)
# =========================

# 1. Install dependencies
# (Uncomment the next line if running in Colab)
# !pip install sentence-transformers datasets torch pandas

# 2. Prompt for model name (and any other secrets)
import os
EMBEDDING_MODEL = input("Enter the base embedding model (e.g., thenlper/gte-small): ")
os.environ["EMBEDDING_MODEL"] = EMBEDDING_MODEL

# 3. Upload your CSV file (must have 'query' and 'passage' columns)
try:
    from google.colab import files
    uploaded = files.upload()
    CSV_PATH = list(uploaded.keys())[0]
except ImportError:
    CSV_PATH = input("Enter the path to your CSV file: ")

# 4. Load sentence pairs (query, passage)
import pandas as pd
from sentence_transformers import InputExample

df = pd.read_csv(CSV_PATH)
df = df[['query', 'passage']].dropna()

train_samples = [
    InputExample(texts=[row['query'], row['passage']])
    for _, row in df.iterrows()
]
print(f"Loaded {len(train_samples)} training pairs")

# 5. Build model (using e5 which expects 'query: ' and 'passage: ' prefixes)
from sentence_transformers import SentenceTransformer, models, losses
from torch.utils.data import DataLoader

MODEL_NAME = EMBEDDING_MODEL
word_embedding_model = models.Transformer(MODEL_NAME)
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

# 6. Set up training
train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model)

num_epochs = 1  # You can increase this later
OUTPUT_DIR = f"./{MODEL_NAME.replace('/', '_')}_finetuned"

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=num_epochs,
    warmup_steps=100,
    output_path=OUTPUT_DIR
)
print(f"✅ Model saved to {OUTPUT_DIR}")

# 7. (Optional) Push to Hugging Face Hub
# from huggingface_hub import notebook_login
# notebook_login()
# model.push_to_hub('your-username/your-model-name') 