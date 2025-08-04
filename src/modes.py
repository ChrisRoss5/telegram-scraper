"""Different operating modes for the telegram scraper"""

from .utils import save_messages


class HistoricalSyncMode:
    def __init__(self, message_processor):
        self.message_processor = message_processor

    def get_default_offset_id(self):
        """Calculate default offset ID based on existing messages"""
        default_offset_id = 0
        try:
            if self.message_processor.all_messages:
                last_message = self.message_processor.all_messages[-1]
                media_count = len(last_message.get("media", []))
                if media_count:
                    media_count -= 1  # Because first message carries media!
                default_offset_id = last_message["id"] + media_count
        except (IndexError, KeyError):
            default_offset_id = 0
        return default_offset_id

    def get_user_input(self, args=None):
        """Get user input for historical sync parameters"""
        default_offset_id = self.get_default_offset_id()

        # Use args if available and no_prompts is set
        if args and args.no_prompts:
            offset_id = (
                args.offset_id if args.offset_id is not None else default_offset_id
            )
            stop_count = args.stop_count
            print(f"Using offset_id: {offset_id}")
            if stop_count:
                print(f"Using stop_count: {stop_count}")
            else:
                print("No stop_count limit set")
            return offset_id, stop_count

        # Interactive mode
        offset_input = input(
            f"Enter offset_id (default: {default_offset_id}): "
        ).strip()
        offset_id = int(offset_input) if offset_input else default_offset_id

        stop_input = input("Enter stop_count (leave empty for no limit): ").strip()
        stop_count = int(stop_input) if stop_input else None

        return offset_id, stop_count

    async def run(self, client, channel_username, output_json_path, args=None):
        """Run historical sync mode"""
        print("Starting in Historical Sync mode...")
        offset_id, stop_count = self.get_user_input(args)
        count = 1

        async for msg in client.iter_messages(
            channel_username, offset_id=offset_id, reverse=True
        ):
            print(f"Processing message {count} (ID: {msg.id})...")

            await self.message_processor.process_message_with_comments(
                client, msg, channel_username
            )
            count += 1

            save_messages(self.message_processor.all_messages, output_json_path)

            if stop_count is not None and count >= stop_count:
                print(f"Reached stop_count of {stop_count}. Stopping.")
                break

        print(
            f"Saved {count - 1} new messages to {output_json_path}, totaling {len(self.message_processor.all_messages)} messages."
        )


class RealTimeMode:
    @staticmethod
    async def run(client):
        """Run real-time listening mode"""
        print("Starting in Real-time Listening mode. Waiting for new messages...")
        print("Press Ctrl+C to stop.")
        await client.run_until_disconnected()


def get_mode_choice(args=None):
    """Get user's choice of operating mode"""
    if args and args.no_prompts:
        if args.mode in ["1", "historical"]:
            return "1"
        elif args.mode in ["2", "realtime"]:
            return "2"
        else:
            return "2"  # Default to real-time

    return (
        input(
            "Choose mode: [1] Historical Sync [2] Real-time Listening (default: 2): "
        ).strip()
        or "2"
    )
