import discord
from config import SUGGESTION_VOTING_CHANNEL_ID


async def send_to_suggestion_voting_channel(client, ctx, suggestion_id, message):
    channel = client.get_channel(SUGGESTION_VOTING_CHANNEL_ID)
    embed = discord.Embed(
        title="Suggestion", description="", color=discord.Color.blurple()
    )
    embed.add_field(name=f"#{suggestion_id}", value=message, inline=False)
    try:
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    except Exception:
        embed.set_author(name=ctx.author.display_name)
    x = await channel.send(content=None, embed=embed)
    return x
