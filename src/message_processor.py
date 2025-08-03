"""Message processing utilities for handling grouped messages and comments"""

from .handle_message import handle_message
from .utils import save_messages


class MessageProcessor:
    def __init__(self, all_messages, output_json_path):
        self.all_messages = all_messages
        self.output_json_path = output_json_path
        self.last_grouped_id = -1
        self._message_index = self._build_message_index()
        self._processed_grouped_messages = set()  # Track processed grouped message IDs
        self._initialize_processed_grouped_messages()  # Initialize from existing data

    def _build_message_index(self):
        """Build an index of messages by their ID for quick lookup"""
        index = {}
        for i, message in enumerate(self.all_messages):
            index[message["id"]] = i
        return index

    def _initialize_processed_grouped_messages(self):
        """Initialize the set of processed grouped messages from existing data"""
        # Look through existing messages to find those that have multiple media items
        # and estimate which message IDs were likely grouped together
        for msg in self.all_messages:
            media_list = msg.get("media", [])
            if len(media_list) > 1:
                # This message likely contains grouped media
                # The subsequent message IDs (msg.id + 1, msg.id + 2, etc.) were probably grouped
                for i in range(1, len(media_list)):
                    self._processed_grouped_messages.add(msg["id"] + i)

    def _get_next_message_version(self, existing_message):
        """Get the next version number for a message"""
        version = 2
        while f"messageV{version}" in existing_message:
            version += 1
        return version

    def _update_message_text(self, existing_message, new_message):
        """Update message text with versioning if different"""
        if "message" in new_message and "message" in existing_message:
            if existing_message["message"] != new_message["message"]:
                version = self._get_next_message_version(existing_message)
                existing_message[f"messageV{version}"] = new_message["message"]

                # Also update transliterated version if present
                try:
                    from .utils import transliterate_text
                    from . import globals as g

                    if (
                        g.config
                        and g.config.get("transliterate_key")
                        and new_message.get("message")
                    ):
                        transliterated = transliterate_text(
                            new_message["message"], g.transliteration_schema
                        )
                        if transliterated:
                            existing_message[
                                f"{g.config['transliterate_key']}V{version}"
                            ] = transliterated
                except (AttributeError, ImportError):
                    # Globals not initialized or transliteration not available
                    pass

    def _update_comments(self, existing_message, new_comments):
        """Update existing comments with new reactions and add new comments"""
        if not new_comments:
            return

        existing_comments = existing_message.get("comments", [])
        existing_comment_ids = {
            comment["id"]: i for i, comment in enumerate(existing_comments)
        }

        for new_comment in new_comments:
            comment_id = new_comment["id"]
            if comment_id in existing_comment_ids:
                # Update existing comment reactions and views
                idx = existing_comment_ids[comment_id]
                if "reactions" in new_comment:
                    existing_comments[idx]["reactions"] = new_comment["reactions"]
                elif "reactions" in existing_comments[idx]:
                    # Remove reactions field if new comment has no reactions
                    del existing_comments[idx]["reactions"]

                if "views" in new_comment:
                    existing_comments[idx]["views"] = new_comment["views"]
                if "forwards" in new_comment:
                    existing_comments[idx]["forwards"] = new_comment["forwards"]

                # Handle message text versioning for comments too
                self._update_message_text(existing_comments[idx], new_comment)
            else:
                # Add new comment
                existing_comments.append(new_comment)

        existing_message["comments"] = existing_comments

    def update_existing_message(self, existing_message, new_message):
        """Update an existing message with new data while preserving history"""
        # Update reactions only if they exist in new message
        if "reactions" in new_message:
            existing_message["reactions"] = new_message["reactions"]
        elif "reactions" in existing_message:
            # Remove reactions field if new message has no reactions
            del existing_message["reactions"]

        if "views" in new_message:
            existing_message["views"] = new_message["views"]
        if "forwards" in new_message:
            existing_message["forwards"] = new_message["forwards"]

        # Update message text with versioning if different
        self._update_message_text(existing_message, new_message)

        # Handle comments if present in new message
        if "comments" in new_message:
            self._update_comments(existing_message, new_message["comments"])

    def find_existing_message(self, message_id):
        """Find existing message by ID"""
        if message_id in self._message_index:
            return (
                self._message_index[message_id],
                self.all_messages[self._message_index[message_id]],
            )
        return None, None

    def rebuild_message_index(self):
        """Rebuild the message index (useful if messages are manually modified)"""
        self._message_index = self._build_message_index()

    def _handle_grouped_message(self, root_rec, msg):
        """Handle grouped message logic and return whether message was appended to existing group"""
        if msg.grouped_id and msg.grouped_id == self.last_grouped_id:
            # Append media to the last message if it's part of the same group
            if self.all_messages and "media" in self.all_messages[-1]:
                self.all_messages[-1]["media"].append(root_rec["media"][0])
            self.last_grouped_id = msg.grouped_id
            # Track this message as part of a processed group
            self._processed_grouped_messages.add(msg.id)
            return True
        else:
            self.last_grouped_id = msg.grouped_id if msg.grouped_id is not None else -1
            return False

    def _should_skip_grouped_message(self, msg):
        """Check if this grouped message should be skipped because it's already part of an existing group"""
        if not msg.grouped_id:
            return False

        # If this message ID has already been processed as part of a group, skip it
        return msg.id in self._processed_grouped_messages

    def process_new_message(self, root_rec, msg):
        """Process a new message and handle grouping logic"""
        # Check if message already exists (for real-time updates)
        existing_index, existing_message = self.find_existing_message(msg.id)

        if existing_message is not None:
            # Message exists, update it
            print(f"Updating existing message {msg.id} in real-time")
            self.update_existing_message(existing_message, root_rec)
        else:
            # New message, handle normally
            if not self._handle_grouped_message(root_rec, msg):
                self.all_messages.append(root_rec)
                # Update the index for the new message
                self._message_index[msg.id] = len(self.all_messages) - 1

        save_messages(self.all_messages, self.output_json_path)

    async def process_message_with_comments(self, client, msg, channel_username):
        """Process a message and its comments for historical sync"""
        # Check if this is a grouped message that should be skipped
        if self._should_skip_grouped_message(msg):
            print(
                f"Skipping grouped message {msg.id} (part of existing group {msg.grouped_id})"
            )
            return None

        # Check if message already exists
        existing_index, existing_message = self.find_existing_message(msg.id)

        if existing_message is not None:
            # Message exists, update it (skip media download)
            print(f"Updating existing message {msg.id}")
            root_rec = await handle_message(
                msg, is_comment=False, skip_media_download=True
            )

            # Process comments separately and merge them properly
            try:
                new_comments = []
                existing_comments = existing_message.get("comments", [])
                existing_comment_ids = {comment["id"] for comment in existing_comments}

                async for comment in client.iter_messages(
                    channel_username, reply_to=msg.id, reverse=True
                ):
                    # Skip media download only for existing comments
                    skip_media = comment.id in existing_comment_ids
                    comment_rec = await handle_message(
                        comment, is_comment=True, skip_media_download=skip_media
                    )
                    new_comments.append(comment_rec)

                # Update the existing message first (without comments)
                self.update_existing_message(existing_message, root_rec)

                # Then merge comments properly
                if new_comments:
                    self._update_comments(existing_message, new_comments)

            except Exception as e:
                print(f"Error processing comments for message {msg.id}: {e}")
                # Still update the message even if comment processing fails
                self.update_existing_message(existing_message, root_rec)

        else:
            # New message, process normally with media download
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
                # Update the index for the new message
                self._message_index[msg.id] = len(self.all_messages) - 1

        return root_rec
