import asyncio
import argparse
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


async def main(args=None):
    setup_directories(c["media_folder"], c["media_comments_folder"], current_dir)

    # Initialize message processor and client manager
    message_processor = MessageProcessor(all_messages, output_json_path)
    client_manager = TelegramClientManager(
        c, transliteration_schema, current_dir, message_processor
    )

    # Run with automatic reconnection
    await client_manager.run_with_reconnection(output_json_path, args)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Telegram Scraper - Download messages and media from Telegram channels"
    )

    parser.add_argument(
        "--mode",
        "-m",
        choices=["1", "2", "historical", "realtime"],
        default="2",
        help="Operating mode: 1/historical = Historical Sync, 2/realtime = Real-time Listening (default: 2)",
    )

    parser.add_argument(
        "--offset-id",
        "-o",
        type=int,
        help="Starting message ID for historical sync (default: calculated from last message)",
    )

    parser.add_argument(
        "--stop-count",
        "-s",
        type=int,
        help="Maximum number of messages to process in historical sync (default: no limit)",
    )

    parser.add_argument(
        "--no-prompts",
        "-n",
        action="store_true",
        help="Run without interactive prompts (use defaults or provided flags)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(main(args))
