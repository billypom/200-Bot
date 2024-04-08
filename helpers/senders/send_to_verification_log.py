from config import VERIFICATION_CHANNEL_ID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import ApplicationContext
    from discord import Bot


async def send_to_verification_log(
    client: Bot, ctx: ApplicationContext, message: str, title: str
):
    channel = client.get_channel(VERIFICATION_CHANNEL_ID)
    await channel.send(f"{title}\n{ctx.author.id} | {ctx.author.mention}\n{message}")
