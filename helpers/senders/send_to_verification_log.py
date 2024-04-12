from config import VERIFICATION_CHANNEL_ID
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from discord import ApplicationContext
    from discord import Bot, TextChannel


async def send_to_verification_log(
    client: "Bot", ctx: "ApplicationContext", message: str, title: str
):
    channel = cast("TextChannel", client.get_channel(VERIFICATION_CHANNEL_ID))
    await channel.send(f"{title}\n{ctx.author.id} | {ctx.author.mention}\n{message}")
