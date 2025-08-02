import os
import json
from datetime import timedelta
import iuliia


def load_config():
    """Load configuration from config.json"""
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def setup_transliteration_schema(config):
    """Setup transliteration schema based on config"""
    if config.get("transliterate_key") and config.get("transliterate_schema"):
        return iuliia.schemas.get(config["transliterate_schema"])
    return None


def transliterate_text(text: str, schema) -> str:
    """Transliterate text using the provided schema"""
    if not schema or not text:
        return ""
    return schema.translate(text).replace("X", "H").replace("x", "h")


def load_messages(output_json_path):
    """Load messages from JSON file"""
    if not os.path.exists(output_json_path):
        return []
    with open(output_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_messages(data, output_json_path):
    """Save messages to JSON file"""
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def list_channels(client):
    """List all channels joined by the account"""
    print("\nList of channels joined by account: ")
    async for dialog in client.iter_dialogs():
        print(f"* {dialog.title} (id: {dialog.id})")


def format_date(date, timezone_offset_hours, date_format):
    """Format date with timezone offset"""
    return (date + timedelta(hours=timezone_offset_hours)).strftime(date_format)


def setup_directories(media_folder, media_comments_folder):
    """Create necessary directories"""
    os.makedirs(media_folder, exist_ok=True)
    os.makedirs(media_comments_folder, exist_ok=True)
