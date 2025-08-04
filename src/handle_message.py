import os

from .utils import format_date, transliterate_text
from . import globals as g
from telethon.tl.functions.messages import GetMessageReactionsListRequest

""" from telethon.utils import get_input_location
from telethon.tl import types """


def get_reaction_key(reaction):
    """Extract reaction identifier from a reaction object"""
    return (
        reaction.emoticon if hasattr(reaction, "emoticon") else type(reaction).__name__
    )


async def handle_message(msg, is_comment=False, skip_media_download=False):
    """Handle processing of a single message"""
    sender_id = msg.sender_id or None
    first_name = getattr(msg.sender, "first_name", None) if msg.sender else None
    last_name = getattr(msg.sender, "last_name", None) if msg.sender else None
    username = getattr(msg.sender, "username", None) if msg.sender else None
    sender_is_creator = not sender_id or username == g.config["channel_username"]

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
        creator_reactions = set()

        if is_comment:
            all_reactions = await g.client(
                GetMessageReactionsListRequest(peer=msg.peer_id, id=msg.id, limit=100)
            )
            for reaction_peer in all_reactions.reactions:
                # Check if the reaction is from the channel itself
                if (
                    hasattr(reaction_peer.peer_id, "channel_id")
                    and reaction_peer.peer_id.channel_id == msg.peer_id.channel_id
                ):
                    creator_reactions.add(get_reaction_key(reaction_peer.reaction))

        for reaction in msg.reactions.results:
            r = {
                "reaction": get_reaction_key(reaction.reaction),
                "count": reaction.count,
            }
            if r["reaction"] in creator_reactions:
                r["is_from_creator"] = True
            rec["reactions"].append(r)
    else:
        del rec["reactions"]

    if msg.media:
        if not is_comment or sender_is_creator:
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
                print(f"Downloading {media_type} media...")

                if media_type == "MessageMediaPhoto":
                    # Sometimes, largest PHOTO resolution is not the default... WTF!
                    """largest_size = max(
                        msg.photo.sizes,
                        key=lambda s: getattr(s, "w", 0) * getattr(s, "h", 0),
                    )
                    sorted_by_size = sorted(
                        msg.photo.sizes,
                        key=lambda s: getattr(s, "size", 0),
                    )
                    largest_idx_in_sorted = sorted_by_size.index(largest_size)"""
                    # input_location = get_input_location(largest_size)
                    """ input_location = types.InputPhotoFileLocation(
                        id=msg.photo.id,
                        access_hash=msg.photo.access_hash,
                        file_reference=msg.photo.file_reference,
                        thumb_size=largest_size.type,  # This correctly uses the 'y' type string
                    ) """
                    # path = await msg.client.download_file(input_location, file=folder)
                    # path = await g.client.download_file()
                    # path = await msg.download_media(thumb=largest_size, file=folder)
                    """ path = await msg.client.download_media(
                        msg.photo, thumb=largest_size, file=folder
                    ) """
                    """ path = await msg.download_media(
                        file=folder, thumb=largest_idx_in_sorted
                    ) """
                    # path = await g.client.download_media(largest_size, file=folder)
                    path = await msg.download_media(file=folder)
                else:
                    path = await msg.download_media(file=folder)

                if g.base_dir:
                    rel_path = os.path.relpath(path, g.base_dir)
                else:
                    rel_path = os.path.relpath(path)
                rec["media"] = [rel_path]
                print(f"Downloaded media to {rel_path}")

    return rec
