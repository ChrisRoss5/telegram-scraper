import os
import json
import asyncio
from telethon import TelegramClient
from datetime import timedelta

with open("config.json", "r", encoding="utf-8") as f:
    c = json.load(f)

os.makedirs(c["media_folder"], exist_ok=True)
os.makedirs(c["media_comments_folder"], exist_ok=True)


async def handle_message(_, msg, is_comment=False):
    sender_id = msg.sender_id or None
    first_name = getattr(msg.sender, "first_name", None) if msg.sender else None
    last_name = getattr(msg.sender, "last_name", None) if msg.sender else None
    username = getattr(msg.sender, "username", None) if msg.sender else None

    rec = {
        "id": msg.id,
        "date": format_date(msg.date),
    }

    if msg.forward:
        rec["is_forwarded"] = True
        if msg.forward.from_name:
            rec["forward"] = {
                "from_name": msg.forward.from_name,
            }
        elif msg.forward.chat:
            rec["forward"] = {
                "username": (
                    msg.forward.chat.username
                    if hasattr(msg.forward.chat, "username")
                    else msg.forward.chat.title
                ),
                "id": msg.forward.channel_post,
            }
    if msg.reply_to_msg_id is not None:
        rec["reply_to"] = msg.reply_to_msg_id
    if sender_id is not None:
        rec["sender_id"] = sender_id
    if first_name:
        rec["first_name"] = first_name
    if last_name:
        rec["last_name"] = last_name
    if username:
        rec["username"] = username
    if msg.message:
        rec["message"] = msg.message

    rec["reactions"] = []

    if not is_comment:
        if msg.views:
            rec["views"] = msg.views
        if msg.forwards:
            rec["forwards"] = msg.forwards

    if msg.reactions:
        for reaction in msg.reactions.results:
            rec["reactions"].append(
                {
                    "reaction": (
                        "Paid emoji"
                        if type(reaction.reaction).__name__ == "ReactionPaid"
                        else (
                            "Custom emoji"
                            if type(reaction.reaction).__name__ == "ReactionCustomEmoji"
                            else reaction.reaction.emoticon
                        )
                    ),
                    "count": reaction.count,
                }
            )
    else:
        del rec["reactions"]

    if msg.media:
        if not is_comment or not sender_id or username == c["channel_username"]:
            folder = c["media_comments_folder"] if is_comment else c["media_folder"]
            media_type = type(msg.media).__name__
            if media_type == "MessageMediaPoll":
                rec["poll"] = {
                    "question": msg.media.poll.question.text,
                    "answers": [option.text.text for option in msg.media.poll.answers],
                    "results": [
                        result.voters for result in msg.media.results.results or []
                    ],
                    "total_voters": msg.media.results.total_voters,
                }
            elif media_type != "MessageMediaWebPage":
                path = await msg.download_media(file=folder)
                rel_path = os.path.relpath(path)
                rec["media"] = [{"media_type": media_type, "media_path": rel_path}]

    return rec


async def main():
    client = TelegramClient("session", c["api_id"], c["api_hash"])
    await client.start()

    # Necessary to ensure the client is cached when using channel title instead of username
    # await list_channels(client)

    all_messages = load_messages()
    count = 0
    last_grouped_id = -1
    offset_id = 0 if not all_messages else all_messages[-1]["id"]

    async for msg in client.iter_messages(
        c["channel_username"], offset_id=offset_id, reverse=True
    ):
        print(f"Processing message {count} (ID: {msg.id})...")

        root_rec = await handle_message(client, msg, is_comment=False)

        if msg.grouped_id == last_grouped_id:
            all_messages[-1]["media"].append(root_rec["media"][0])
        else:
            try:
                async for comment in client.iter_messages(
                    c["channel_username"], reply_to=msg.id, reverse=True
                ):
                    comment_rec = await handle_message(client, comment, is_comment=True)
                    if "comments" not in root_rec:
                        root_rec["comments"] = []
                    root_rec["comments"].append(comment_rec)
            except Exception as e:
                print(f"Error processing comments {msg.id}: {e}")

            all_messages.append(root_rec)
            count += 1

        last_grouped_id = msg.grouped_id if msg.grouped_id is not None else -1
        save_messages(all_messages)

    print(
        f"Saved {count} new messages to {c['output_json']}, totaling {len(all_messages)} messages."
    )


def load_messages():
    if not os.path.exists(c["output_json"]):
        return []
    with open(c["output_json"], "r", encoding="utf-8") as f:
        return json.load(f)


def save_messages(data):
    with open(c["output_json"], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def list_channels(client):
    print("\nList of channels joined by account: ")
    async for dialog in client.iter_dialogs():
        print(f"* {dialog.title} (id: {dialog.id})")


def format_date(date):
    # This works reliably for Moscow since 2014, no DST
    return (date + timedelta(hours=3)).strftime("%d.%m.%Y. %H:%M:%S")


if __name__ == "__main__":
    asyncio.run(main())
