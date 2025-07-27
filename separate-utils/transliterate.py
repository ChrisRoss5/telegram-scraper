import iuliia
import json
from tqdm import tqdm

test = False
add_transliteration = False  # Set to True to add, False to remove
schema = iuliia.schemas.get("scientific")
new_key = "message_latin_scientific"


def transliterate(text: str) -> str:
    return schema.translate(text).replace("X", "H").replace("x", "h")


def add_transliterations(messages):
    """Add transliteration to messages and comments"""
    for msg in tqdm(messages, desc="Adding transliteration"):
        if "message" in msg:
            try:
                msg[new_key] = transliterate(msg["message"])
            except Exception as e:
                print(f"Error Transliterating message ID {msg.get('id')}: {e}")
                msg[new_key] = ""
        if "comments" in msg:
            for comment in msg["comments"]:
                if "message" in comment:
                    try:
                        comment[new_key] = transliterate(comment["message"])
                    except Exception as e:
                        print(
                            f"Error Transliterating comment ID {comment.get('id')}: {e}"
                        )
                        comment[new_key] = ""


def remove_transliterations(messages):
    """Remove transliteration from messages and comments"""
    for msg in tqdm(messages, desc="Removing transliteration"):
        if new_key in msg:
            del msg[new_key]
            print(f"Removed {new_key} from message ID {msg.get('id')}")
        if "comments" in msg:
            for comment in msg["comments"]:
                if new_key in comment:
                    del comment[new_key]
                    print(f"Removed {new_key} from comment ID {comment.get('id')}")


if test:
    text = """Юлия Щеглова, Хрущёв, Счастье, Любовь"""

    for name, s in iuliia.schemas.items():
        print(name, "\t\t", s.translate(text))

    print("Modified Scientific Schema:\n", transliterate(text))
    exit()

# -------------------------

print("Loading messages.json...")
with open("../messages.json", "r", encoding="utf-8") as f:
    messages = json.load(f)

if add_transliteration:
    add_transliterations(messages)
    action = "Addition"
else:
    remove_transliterations(messages)
    action = "Removal"

print("Saving to messages.json...")
with open("../messages.json", "w", encoding="utf-8") as f:
    json.dump(messages, f, ensure_ascii=False, indent=2)

print(f"{action} complete!")
