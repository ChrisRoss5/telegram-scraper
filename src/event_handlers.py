"""Event handlers for Telegram messages"""

from .handle_message import handle_message


def create_new_message_handler(message_processor):
    """Create event handler for new messages in real-time mode"""

    async def new_message_handler(event):
        msg = event.message
        print(f"New message received (ID: {msg.id}). Processing...")

        root_rec = await handle_message(msg, is_comment=False)
        message_processor.process_new_message(root_rec, msg)

        print(
            f"Saved new message (ID: {msg.id}). Total messages: {len(message_processor.all_messages)}"
        )

        # Special output line for PowerShell to catch
        print(
            f"POWERSHELL_NOTIFICATION:NEW_MESSAGE:{msg.id}:{msg.text[:100] if msg.text else '[Media/No text]'}"
        )

    return new_message_handler
