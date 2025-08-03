import asyncio
import os
from src.utils import (
    load_config,
    setup_transliteration_schema,
    setup_directories,
    load_messages,
)
from src.client_manager import TelegramClientManager
from src.message_processor import MessageProcessor

# Load configuration and setup
c = load_config()
transliteration_schema = setup_transliteration_schema(c)

# Setup paths and load existing messages
current_dir = os.path.dirname(os.path.abspath(__file__))
output_json_path = os.path.join(current_dir, c["output_json"])
all_messages = load_messages(output_json_path)


async def main():
    setup_directories(c["media_folder"], c["media_comments_folder"], current_dir)

    # Initialize message processor and client manager
    message_processor = MessageProcessor(all_messages, output_json_path)
    client_manager = TelegramClientManager(
        c, transliteration_schema, current_dir, message_processor
    )

    # Run with automatic reconnection
    await client_manager.run_with_reconnection(output_json_path)


if __name__ == "__main__":
    asyncio.run(main())
