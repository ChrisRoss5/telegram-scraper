import json
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import time

# --- CONFIGURATION ---
# Use the larger, more powerful model
MODEL_NAME = "facebook/nllb-200-3.3B"
SRC_LANG = "rus_Cyrl"
TGT_LANG = "eng_Latn"
BATCH_SIZE = 16  # Experiment with this value. 16, 32, or 64 are good starting points.
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- MODEL LOADING ---
print("🔄 Loading model...")
start_time = time.time()

# Use AutoTokenizer for best practice
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, src_lang=SRC_LANG)

# Load the model with 8-bit quantization to fit on your GPU
# device_map="auto" lets accelerate handle placing the model on the right devices
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    load_in_8bit=True,
    device_map="auto",
    # You could also try 4-bit for even less VRAM and potentially faster speed
    # load_in_4bit=True,
)

print(f"✅ Model loaded on {model.device} in {time.time() - start_time:.2f} seconds")

# --- DATA PREPARATION ---
print("📂 Loading messages.json and preparing texts...")
try:
    with open("../messages.json", "r", encoding="utf-8") as f:
        messages_json = json.load(f)
except FileNotFoundError:
    print("❌ Error: messages.json not found.")
    exit()

# Collect all texts that need translation into a single list
# We store a reference to the original object to easily place the translation back
texts_to_translate = []
for msg in messages_json:
    if "message" in msg:
        texts_to_translate.append(
            {"text": msg["message"], "target_obj": msg, "key": "message_translated"}
        )

    """ if "comments" in msg:
        for comment in msg["comments"]:
            if "message" in comment:
                texts_to_translate.append(
                    {
                        "text": comment["message"],
                        "target_obj": comment,
                        "key": "message_translated",
                    }
                ) """

print(f"Found {len(texts_to_translate)} non-empty texts to translate.")

# --- BATCH TRANSLATION ---
print("🌐 Translating messages in batches...")
target_lang_id = tokenizer.convert_tokens_to_ids(TGT_LANG)

# Process in batches
for i in tqdm(
    range(0, len(texts_to_translate), BATCH_SIZE), desc="Translating Batches"
):
    batch_data = texts_to_translate[i : i + BATCH_SIZE]
    batch_texts = [item["text"] for item in batch_data]

    try:
        # Tokenize the whole batch at once. Padding is crucial for batching.
        inputs = tokenizer(
            batch_texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(model.device)

        # Generate translations for the whole batch
        generated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=target_lang_id,
            max_length=512,
        )

        # Decode the batch
        translations = tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True
        )

        # Place translations back into the original JSON structure
        for item, translation in zip(batch_data, translations):
            item["target_obj"][item["key"]] = translation

    except Exception as e:
        print(f"⚠️ Error processing batch starting at index {i}: {e}")
        for item in batch_data:
            item["target_obj"][item["key"]] = f"ERROR: {e}"

print("💾 Saving to messages-translated2.json...")
with open("../messages-translated2.json", "w", encoding="utf-8") as f:
    json.dump(messages_json, f, ensure_ascii=False, indent=2)

print("✅ Translation complete!")
