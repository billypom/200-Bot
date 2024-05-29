from helpers.getters import get_lounge_guild
import logging
from constants import SUGGESTION_VOTING_CHANNEL_ID
from discord import Color, Embed

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot


async def handle_suggestion_decision(
    client: "Bot",
    suggestion_id: int,
    suggestion: str,
    author_id: int,
    message_id: int,
    admin_id: int,
    approved: int,
    reason: str,
) -> bool:
    """Handles actions after making a suggestion decision
    - Updating the embed
    - Updating the database
    - Sending a soft ping (send & delete message immediately)

    Returns:
    True on success
    False on failure"""
    # Retrieve the author of the suggestion
    try:
        author = await get_lounge_guild(client).fetch_member(author_id)
    except Exception:
        author = None
        return False
    # Retrieve the staff member deciding
    try:
        admin = await get_lounge_guild(client).fetch_member(admin_id)
    except Exception:
        admin = None
        logging.error("handle_suggestion_decision | no admin found... among us moment")
        return False
    # Return if no decision was made
    if approved is None:
        return False
    # Edit the embed
    channel = client.get_channel(SUGGESTION_VOTING_CHANNEL_ID)
    if approved == 2:
        decision = f"Considered by {admin.display_name}"
        color = Color.greyple()
    elif approved:
        decision = f"Approved by {admin.display_name}"
        color = Color.green()
    else:
        decision = f"Denied by {admin.display_name}"
        color = Color.red()
    try:
        embed = Embed(title="Suggestion", description="", color=color)
        embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        embed.add_field(name=f"#{suggestion_id}", value=suggestion, inline=False)
        embed.add_field(name=decision, value=reason, inline=False)
        suggestion_message = await channel.fetch_message(message_id)
        await suggestion_message.edit(embed=embed)
        # Quickly send and delete a message to mark channel as unread
        dummy_msg = await channel.send(".")
        await dummy_msg.delete()
        return True
    except Exception:
        return False
