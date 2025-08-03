"""Message processing utilities for handling grouped messages and comments"""

from .handle_message import handle_message
from .utils import save_messages


class MessageProcessor:
    def __init__(self, all_messages, output_json_path):
        self.all_messages = all_messages
        self.output_json_path = output_json_path
        self.last_grouped_id = -1

    def _handle_grouped_message(self, root_rec, msg):
        """Handle grouped message logic and return whether message was appended to existing group"""
        if msg.grouped_id and msg.grouped_id == self.last_grouped_id:
            # Append media to the last message if it's part of the same group
            if self.all_messages and "media" in self.all_messages[-1]:
                self.all_messages[-1]["media"].append(root_rec["media"][0])
            self.last_grouped_id = msg.grouped_id
            return True
        else:
            self.last_grouped_id = msg.grouped_id if msg.grouped_id is not None else -1
            return False

    def process_new_message(self, root_rec, msg):
        """Process a new message and handle grouping logic"""
        if not self._handle_grouped_message(root_rec, msg):
            self.all_messages.append(root_rec)
        save_messages(self.all_messages, self.output_json_path)

    async def process_message_with_comments(self, client, msg, channel_username):
        """Process a message and its comments for historical sync"""
        root_rec = await handle_message(msg, is_comment=False)

        if not self._handle_grouped_message(root_rec, msg):
            # Process comments
            try:
                async for comment in client.iter_messages(
                    channel_username, reply_to=msg.id, reverse=True
                ):
                    comment_rec = await handle_message(comment, is_comment=True)
                    if "comments" not in root_rec:
                        root_rec["comments"] = []
                    root_rec["comments"].append(comment_rec)
            except Exception as e:
                print(f"Error processing comments for message {msg.id}: {e}")

            self.all_messages.append(root_rec)

        return root_rec
