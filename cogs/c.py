import DBA
from datetime import datetime, timedelta
from discord.ext import commands
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.senders import send_here_ping_message
from helpers import convert_datetime_to_unix_timestamp
from config import LOUNGE, LOUNGE_QUEUE_JOIN_CHANNEL_ID, LOUNGE_QUEUE_START_MINUTE
import logging


class CanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="c", description="🙋 Can up for Lounge Queue", guild_ids=LOUNGE
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def c(self, ctx):
        await ctx.defer(ephemeral=False)
        sent_from_channel_id = ctx.channel.id
        player_id = ctx.author.id
        if sent_from_channel_id != LOUNGE_QUEUE_JOIN_CHANNEL_ID:
            await ctx.respond(
                "You cannot use this command in this channel", delete_after=30
            )
            return

        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f"Unbanned after <t:{lounge_ban}:D>")
            return
        # Check if player already in queue
        try:
            with DBA.DBAccess() as db:
                _ = db.query(  # type: ignore
                    "SELECT player_id FROM lounge_queue_player WHERE player_id = %s;",
                    (player_id,),
                )[0][0]
            await ctx.respond("You are already in the queue.", delete_after=30)
            return
        except Exception:
            # Player not in queue OK
            pass

        # Add player to the queue
        try:
            with DBA.DBAccess() as db:
                db.execute(
                    "INSERT INTO lounge_queue_player (player_id, last_active) VALUES (%s, %s)",
                    (player_id, datetime.now()),
                )
        except Exception as e:
            logging.warning(
                f"CanCog error: unable to add player to lounge_queue_player | {e}"
            )
            return

        # Count players
        try:
            with DBA.DBAccess() as db:
                number_of_players = db.query(  # type: ignore
                    "SELECT COUNT(*) from lounge_queue_player;", ()
                )[0][0]
        except Exception as e:
            logging.warning(
                f"CanCog error: unable to count player from lounge_queue_player | {e}"
            )
            return

        # Retrieve the next queue time
        current_time = datetime.now()
        add_minutes = (
            LOUNGE_QUEUE_START_MINUTE - current_time.minute % LOUNGE_QUEUE_START_MINUTE
        ) % LOUNGE_QUEUE_START_MINUTE
        target_time = current_time + timedelta(minutes=add_minutes)
        target_unix_time = await convert_datetime_to_unix_timestamp(target_time)

        # Provide feedback to player that they have joined the a queue that will start at a particular time
        await ctx.respond(
            f"You have been added to the queue in <t:{target_unix_time}:R> `[{number_of_players} players]`"
        )

        if number_of_players == 6:
            await send_here_ping_message(ctx, "@here +6")
        if number_of_players == 11:
            await send_here_ping_message(ctx, "@here +1")


def setup(bot):
    bot.add_cog(CanCog(bot))
