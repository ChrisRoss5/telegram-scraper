"""Telegram client connection and reconnection management"""

import asyncio
import time
from telethon import TelegramClient, events
from .utils import send_windows_notification
from .globals import initialize_globals
from .event_handlers import create_new_message_handler
from .modes import HistoricalSyncMode, RealTimeMode, get_mode_choice


class TelegramClientManager:
    def __init__(self, config, transliteration_schema, current_dir, message_processor):
        self.config = config
        self.transliteration_schema = transliteration_schema
        self.current_dir = current_dir
        self.message_processor = message_processor
        self.session_path = f"{current_dir}/session"

    async def run_with_reconnection(self, output_json_path):
        """Main loop with automatic reconnection on failure"""
        while True:
            try:
                await self._run_client_session(output_json_path)
            except (ConnectionError, asyncio.TimeoutError) as e:
                print(f"Network error: {e}. Reconnecting in 60 seconds...")
                send_windows_notification(
                    "Telethon Script Error",
                    f"The script stopped with a network error: {e}. It will now restart.",
                )
                print("Restarting in 60 seconds...")
                time.sleep(60)
            except Exception as e:
                print(f"An unexpected error occurred: {e}. The script will restart.")
                send_windows_notification(
                    "Telethon Script Error",
                    f"The script stopped with an error: {e}. It will now restart.",
                )
                print("Restarting in 30 seconds...")
                time.sleep(30)

    async def _run_client_session(self, output_json_path):
        """Run a single client session"""
        client = TelegramClient(
            self.session_path, self.config["api_id"], self.config["api_hash"]
        )

        try:
            initialize_globals(
                client, self.config, self.transliteration_schema, self.current_dir
            )

            async with client:
                mode = get_mode_choice()

                if mode == "1":
                    historical_mode = HistoricalSyncMode(self.message_processor)
                    await historical_mode.run(
                        client, self.config["channel_username"], output_json_path
                    )
                elif mode == "2":
                    # Set up event handler for real-time mode
                    handler = create_new_message_handler(self.message_processor)
                    client.add_event_handler(
                        handler,
                        events.NewMessage(chats=self.config["channel_username"]),
                    )
                    await RealTimeMode.run(client)
                else:
                    print("Invalid mode selected. Exiting.")
                    exit(1)
        finally:
            if client.is_connected():
                client.disconnect()
            print("Client disconnected. Will attempt to reconnect.")
