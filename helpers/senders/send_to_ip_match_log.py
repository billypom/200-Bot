import discord
from constants import IP_MATCH_CHANNEL_ID


async def send_to_ip_match_log(
    client: discord.Bot, ctx, message, verify_color, user_matches_list
):
    """
    Sends an embed to the IP Match log channel

    Args:
    - `client` (discord.Bot): The bot
    - `ctx` (discord.ApplicationContext): The context of the command
    - `message` (str): A message
    - `verify_color` (discord.Color): Color of the embed
    - `user_matches_list`
    """
    channel = client.get_channel(IP_MATCH_CHANNEL_ID)
    embed = discord.Embed(
        title="Verification",
        description=f"IP Matches for <@{ctx.author.id}>",
        color=verify_color,
    )
    try:
        embed.add_field(name="Issuer: ", value=ctx.author, inline=False)
        embed.add_field(name="Link sent: ", value=message, inline=False)
        for user in user_matches_list:
            ip_match_forum_link = (
                f"https://www.mariokartcentral.com/forums/index.php?members/{user}"
            )
            embed.add_field(name=f"{user}", value=ip_match_forum_link, inline=False)
        embed.add_field(name="Discord ID: ", value=ctx.author.id, inline=False)
        await channel.send(content=None, embed=embed)
    except Exception as e:
        await channel.send(f"TOO MANY MATCHES: {e} {user_matches_list}")
