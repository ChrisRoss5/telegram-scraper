import asyncio
from telethon import TelegramClient
from src.utils import (
    load_config,
    setup_transliteration_schema,
    setup_directories,
    load_messages,
    save_messages,
)
from src.handle_message import handle_message

# Load configuration and setup
c = load_config()
setup_directories(c["media_folder"], c["media_comments_folder"])
transliteration_schema = setup_transliteration_schema(c)


async def main():
    client = TelegramClient("session", c["api_id"], c["api_hash"])
    await client.start()  # type: ignore

    # Necessary to ensure the client is cached when using channel title instead of username
    # await list_channels(client)

    all_messages = load_messages(c["output_json"])
    count = 0
    last_grouped_id = -1
    default_offset_id = 0 if not all_messages else all_messages[-1]["id"] + 1

    # Prompt user for offset_id
    offset_input = input(f"Enter offset_id (default: {default_offset_id}): ").strip()
    offset_id = int(offset_input) if offset_input else default_offset_id

    # Prompt user for stop_count
    stop_input = input("Enter stop_count (leave empty for no limit): ").strip()
    stop_count = int(stop_input) if stop_input else None

    async for msg in client.iter_messages(
        c["channel_username"], offset_id=offset_id, reverse=True
    ):
        print(f"Processing message {count} (ID: {msg.id})...")

        root_rec = await handle_message(
            client, msg, c, transliteration_schema, is_comment=False
        )

        if msg.grouped_id == last_grouped_id:
            all_messages[-1]["media"].append(root_rec["media"][0])
        else:
            try:
                async for comment in client.iter_messages(
                    c["channel_username"], reply_to=msg.id, reverse=True
                ):
                    comment_rec = await handle_message(
                        client, comment, c, transliteration_schema, is_comment=True
                    )
                    if "comments" not in root_rec:
                        root_rec["comments"] = []
                    root_rec["comments"].append(comment_rec)
            except Exception as e:
                print(f"Error processing comments {msg.id}: {e}")

            all_messages.append(root_rec)
            count += 1

        last_grouped_id = msg.grouped_id if msg.grouped_id is not None else -1
        save_messages(all_messages, c["output_json"])

        # Check if we should stop based on stop_count
        if stop_count is not None and count >= stop_count:
            print(f"Reached stop_count of {stop_count}. Stopping.")
            break

    print(
        f"Saved {count} new messages to {c['output_json']}, totaling {len(all_messages)} messages."
    )


if __name__ == "__main__":
    asyncio.run(main())
