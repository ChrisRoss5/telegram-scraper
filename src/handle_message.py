import os
from .utils import format_date, transliterate_text
from . import globals as g


async def handle_message(msg, is_comment=False, skip_media_download=False):
    """Handle processing of a single message"""
    sender_id = msg.sender_id or None
    first_name = getattr(msg.sender, "first_name", None) if msg.sender else None
    last_name = getattr(msg.sender, "last_name", None) if msg.sender else None
    username = getattr(msg.sender, "username", None) if msg.sender else None

    rec = {
        "id": msg.id,
        "date": format_date(
            msg.date, g.config["timezone_offset_hours"], g.config["date_format"]
        ),
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
        if g.config.get("transliterate_key"):
            transliterated = transliterate_text(msg.message, g.transliteration_schema)
            if transliterated:
                rec[g.config["transliterate_key"]] = transliterated

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
                        reaction.reaction.emoticon
                        if hasattr(reaction.reaction, "emoticon")
                        else type(reaction.reaction).__name__
                    ),
                    "count": reaction.count,
                }
            )
    else:
        del rec["reactions"]

    if msg.media:
        if not is_comment or not sender_id or username == g.config["channel_username"]:
            folder = (
                g.config["media_comments_folder"]
                if is_comment
                else g.config["media_folder"]
            )
            # Make folder path absolute relative to base_dir if provided
            if g.base_dir:
                folder = os.path.join(g.base_dir, folder)

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
            elif media_type != "MessageMediaWebPage" and not skip_media_download:
                path = await msg.download_media(file=folder)
                if g.base_dir:
                    rel_path = os.path.relpath(path, g.base_dir)
                else:
                    rel_path = os.path.relpath(path)
                rec["media"] = [rel_path]

    return rec
