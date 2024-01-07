from helpers.getters import get_lounge_guild
import logging
from config import SUGGESTION_VOTING_CHANNEL_ID
from discord import Color, Embed

async def handle_suggestion_decision(client, suggestion_id, suggestion, author_id, message_id, admin_id, approved, reason):
    # Retrieve the author of the suggestion
    try:
        author = get_lounge_guild(client).fetch_member(author_id)
    except Exception:
        author = None
        
    # Retrieve the staff member deciding
    try:
        admin = get_lounge_guild(client).fetch_member(admin_id)
    except Exception:
        admin = None
        logging.info('handle_suggestion_decision | no admin found... among us moment')
    # Return if no decision was made
    if approved is None:
        return
    
    # Edit the embed
    channel = client.get_channel(SUGGESTION_VOTING_CHANNEL_ID)
    if approved:
        decision = f'Approved by {admin.display_name}'
        color = Color.green()
    else:
        decision = f'Denied by {admin.display_name}'
        color = Color.red()
    try:
        embed = Embed(title='Suggestion', description='', color = color)
        embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        
        embed.add_field(name=f'#{suggestion_id}', value=suggestion, inline=False)
        embed.add_field(name=decision, value=reason, inline=False)

        suggestion_message = await channel.fetch_message(message_id)
        await suggestion_message.edit(embed=embed)
        # Quickly send and delete a message to mark channel as unread
        dummy_msg = await channel.send('.')
        await dummy_msg.delete()
        return True
    except Exception:
        return False