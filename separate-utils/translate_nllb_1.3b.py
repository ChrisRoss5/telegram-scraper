import json
import torch
from tqdm import tqdm
from transformers import NllbTokenizer, AutoModelForSeq2SeqLM

# Config
MODEL_NAME = "facebook/nllb-200-distilled-1.3B"
SRC_LANG = "rus_Cyrl"
TGT_LANG = "eng_Latn"

# Load model and tokenizer
print("🔄 Loading model...")
tokenizer = NllbTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(
    "cuda" if torch.cuda.is_available() else "cpu"
)
device = model.device
print(f"✅ Model loaded on {device}")

# Load Telegram messages
print("📂 Loading messages.json...")
with open("../messages.json", "r", encoding="utf-8") as f:
    messages = json.load(f)


# Translation function
def translate_text(text: str) -> str:
    tokenizer.src_lang = SRC_LANG
    tokens = tokenizer(text, truncation=False)["input_ids"]
    if len(tokens) > 512:
        print(f"⚠️ Warning: Message will be truncated ({len(tokens)} tokens)")

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(
        device
    )
    generated_tokens = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(TGT_LANG),
        max_length=512,
    )
    return tokenizer.decode(generated_tokens[0], skip_special_tokens=True)


# Process messages and comments
print("🌐 Translating messages and comments...")
for msg in tqdm(messages, desc="Translating"):
    # Top-level message
    if "message" in msg:
        try:
            msg["message_translated"] = translate_text(msg["message"])
        except Exception as e:
            print(f"⚠️ Error translating message ID {msg.get('id')}: {e}")
            msg["message_translated"] = ""

    # One-level deep comments
    if "comments" in msg:
        for comment in msg["comments"]:
            if (
                "message" in comment
                and isinstance(comment["message"], str)
                and comment["message"].strip()
            ):
                try:
                    comment["message_translated"] = translate_text(comment["message"])
                except Exception as e:
                    print(f"⚠️ Error translating comment ID {comment.get('id')}: {e}")
                    comment["message_translated"] = ""

print("💾 Saving to messages-translated.json...")
with open("../messages-translated.json", "w", encoding="utf-8") as f:
    json.dump(messages, f, ensure_ascii=False, indent=2)

print("✅ Translation complete!")
