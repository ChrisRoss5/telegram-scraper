import asyncio
import os
import time
from telethon import TelegramClient, events
from src.utils import (
    load_config,
    send_windows_notification,
    setup_transliteration_schema,
    setup_directories,
    load_messages,
    save_messages,
)
from src.handle_message import handle_message
from src.globals import initialize_globals

# Load configuration and setup
c = load_config()
transliteration_schema = setup_transliteration_schema(c)

# Global variables to be accessible within the event handler
current_dir = os.path.dirname(os.path.abspath(__file__))
output_json_path = os.path.join(current_dir, c["output_json"])
all_messages = load_messages(output_json_path)
last_grouped_id = -1


async def main():
    global last_grouped_id
    setup_directories(c["media_folder"], c["media_comments_folder"], current_dir)
    session_path = os.path.join(current_dir, "session")

    while True:  # Loop to attempt reconnection on failure
        try:
            client = TelegramClient(session_path, c["api_id"], c["api_hash"])
            initialize_globals(client, c, transliteration_schema, current_dir)

            # Define the event handler for new messages
            @client.on(events.NewMessage(chats=c["channel_username"]))
            async def new_message_handler(event):
                global last_grouped_id
                msg = event.message
                print(f"New message received (ID: {msg.id}). Processing...")

                root_rec = await handle_message(msg, is_comment=False)

                if msg.grouped_id and msg.grouped_id == last_grouped_id:
                    # Append media to the last message if it's part of the same group
                    if all_messages and "media" in all_messages[-1]:
                        all_messages[-1]["media"].append(root_rec["media"][0])
                else:
                    # This part for handling comments might need adjustment in real-time
                    # as comments might arrive after the root message.
                    # A more robust solution might involve a delay or a separate mechanism.
                    all_messages.append(root_rec)

                last_grouped_id = msg.grouped_id if msg.grouped_id is not None else -1
                save_messages(all_messages, output_json_path)
                print(
                    f"Saved new message (ID: {msg.id}). Total messages: {len(all_messages)}"
                )

            async with client:
                # Ask the user for the desired mode
                mode = (
                    input(
                        "Choose mode: [1] Historical Sync [2] Real-time Listening (default: 2): "
                    ).strip()
                    or "2"
                )

                if mode == "1":
                    print("Starting in Historical Sync mode...")
                    default_offset_id = 0
                    try:
                        if all_messages:
                            last_message = all_messages[-1]
                            media_count = len(last_message.get("media", []))
                            default_offset_id = last_message["id"] + media_count - 1
                    except (IndexError, KeyError):
                        default_offset_id = 0

                    offset_input = input(
                        f"Enter offset_id (default: {default_offset_id}): "
                    ).strip()
                    offset_id = int(offset_input) if offset_input else default_offset_id

                    stop_input = input(
                        "Enter stop_count (leave empty for no limit): "
                    ).strip()
                    stop_count = int(stop_input) if stop_input else None
                    count = 1

                    async for msg in client.iter_messages(
                        c["channel_username"], offset_id=offset_id, reverse=True
                    ):
                        print(f"Processing message {count} (ID: {msg.id})...")
                        root_rec = await handle_message(msg, is_comment=False)

                        if msg.grouped_id and msg.grouped_id == last_grouped_id:
                            if all_messages and "media" in all_messages[-1]:
                                all_messages[-1]["media"].append(root_rec["media"][0])
                        else:
                            try:
                                async for comment in client.iter_messages(
                                    c["channel_username"], reply_to=msg.id, reverse=True
                                ):
                                    comment_rec = await handle_message(
                                        comment, is_comment=True
                                    )
                                    if "comments" not in root_rec:
                                        root_rec["comments"] = []
                                    root_rec["comments"].append(comment_rec)
                            except Exception as e:
                                print(
                                    f"Error processing comments for message {msg.id}: {e}"
                                )

                            all_messages.append(root_rec)
                            count += 1

                        last_grouped_id = (
                            msg.grouped_id if msg.grouped_id is not None else -1
                        )
                        save_messages(all_messages, output_json_path)

                        if stop_count is not None and count >= stop_count:
                            print(f"Reached stop_count of {stop_count}. Stopping.")
                            break

                    print(
                        f"Saved {count} new messages to {output_json_path}, totaling {len(all_messages)} messages."
                    )

                elif mode == "2":
                    print(
                        "Starting in Real-time Listening mode. Waiting for new messages..."
                    )
                    print("Press Ctrl+C to stop.")
                    await client.run_until_disconnected()  # type: ignore

                else:
                    print("Invalid mode selected. Exiting.")
                    exit(1)

        except (ConnectionError, asyncio.TimeoutError) as e:
            print(f"Network error: {e}. Reconnecting in 60 seconds...")
            send_windows_notification(
                "Telethon Script Error",
                f"The script stopped with a network error: {e}. It will now restart.",
            )
            time.sleep(60)
        except Exception as e:
            print(f"An unexpected error occurred: {e}. The script will restart.")
            send_windows_notification(
                "Telethon Script Error",
                f"The script stopped with an error: {e}. It will now restart.",
            )
            print("Restarting in 30 seconds...")
            time.sleep(30)
        finally:
            if "client" in locals() and client.is_connected():  # type: ignore
                await client.disconnect()  # type: ignore
            print("Client disconnected. Will attempt to reconnect.")


if __name__ == "__main__":
    asyncio.run(main())
