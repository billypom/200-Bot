import discord
from discord.ext import commands
import DBA
from helpers.senders import send_to_verification_log
from helpers.senders import send_to_name_change_log
from helpers.senders import send_to_debug_channel
from helpers.checkers import check_if_uid_exists
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.checkers import check_if_uid_can_drop
from helpers.checkers import check_if_banned_characters
from helpers import jp_kr_romanize
from helpers.getters import get_unix_time_now
from helpers import Confirm
import vlog_msg
from config import NAME_CHANGE_DELTA_LIMIT, SUPPORT_CHANNEL_ID, LOUNGE


class NameChangeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="name",
        description="Request a name change on the leaderboard",
        guild_ids=LOUNGE,
    )
    async def name(
        self,
        ctx,
        name: discord.Option(str, "Enter a new nickname here", required=True),  # type: ignore
    ):
        """/name slash command for requesting a nickname for the leaderboard.
        - Performs access checks
        - Romanizes the requested name
        - Asks for user confirmation of the cleaned name
        - Checks for duplicates
        - Sends the name request to staff channel for review
        - Sends ephemeral user feedback
        """
        await ctx.defer(ephemeral=True)
        original_name = ctx.author.display_name
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f"Unbanned after <t:{lounge_ban}:D>")
            return
        else:
            pass
        y = await check_if_uid_exists(ctx.author.id)
        if y:
            pass
        else:
            await ctx.respond("Use `/verify <mkc link>` to register with Lounge")
            return
        z = await check_if_uid_can_drop(ctx.author.id)
        if z:
            pass
        else:
            await ctx.respond("You cannot change your name while playing a Mogi.")
            return
        x = await check_if_banned_characters(name)
        if x:
            await send_to_verification_log(self.client, ctx, name, vlog_msg.error1)
            await ctx.respond("You cannot use this name")
            return
        else:
            pass
        name = await jp_kr_romanize(name)
        name = name.replace(" ", "-")

        # Confirm the player name request
        confirmation = Confirm(ctx.author.id)
        channel = self.client.get_channel(ctx.channel.id)
        await channel.send(
            f"Requested name: `{name}`\nIs this the name you want to request?",
            view=confirmation,
            delete_after=30,
        )
        await confirmation.wait()
        if confirmation.value is None:
            await channel.send("No response. Timed out.", delete_after=30)
            return
        elif confirmation.value:
            pass
        else:
            await channel.send("Name change request cancelled.", delete_after=30)
            return
        # Name length check
        if len(name) > 16:
            await channel.send(
                f"Requested name: `{name}` | Name is too long. 16 characters max",
                delete_after=30,
            )
            return
        # Name taken check
        is_name_taken = True
        try:
            with DBA.DBAccess() as db:
                test_name = db.query(
                    "SELECT player_name FROM player WHERE player_name = %s;", (name,)
                )[0][0]  # type: ignore
                if test_name is None:
                    is_name_taken = False
                else:
                    is_name_taken = True
        except Exception:
            is_name_taken = False
        if is_name_taken:
            await channel.send("Name is taken. Please try again.", delete_after=30)
            return
        # Good to request
        else:
            await channel.send("Sending request...", delete_after=30)
            try:
                with DBA.DBAccess() as db:
                    last_change = int(
                        db.query(
                            "SELECT UNIX_TIMESTAMP(create_date) FROM player_name_request WHERE player_id = %s ORDER BY create_date DESC;",
                            (ctx.author.id,),
                        )[0][0]  # type: ignore
                    )
                    unix_now = await get_unix_time_now()
                    difference = unix_now - last_change
                    # 2 months for every name change
                    if difference > NAME_CHANGE_DELTA_LIMIT:
                        pass
                    else:
                        await ctx.respond(
                            f"Request denied. You can change your name again on <t:{str(int(last_change) + int(NAME_CHANGE_DELTA_LIMIT))}:F>",
                            delete_after=30,
                        )
                        return
            except IndexError:
                pass  # If this player has never sent a request before, this will throw IndexError
            except Exception as e:
                await send_to_debug_channel(
                    self.client,
                    ctx,
                    f"First name change request from <@{ctx.author.id}>. Still logging this error 34 in case...\n{e}",
                )
            # Insert record of player name request
            try:
                with DBA.DBAccess() as db:
                    db.execute(
                        "INSERT INTO player_name_request (player_id, requested_name) VALUES (%s, %s);",
                        (ctx.author.id, name),
                    )
                    player_name_request_id = int(
                        db.query(
                            "SELECT id FROM player_name_request WHERE player_id = %s AND requested_name = %s ORDER BY create_date DESC LIMIT 1;",
                            (ctx.author.id, name),
                        )[0][0]  # type: ignore
                    )
                # Send request to staff channel for review
                request_message = await send_to_name_change_log(
                    self.client, ctx, player_name_request_id, name
                )
                request_message_id = request_message.id
                await request_message.add_reaction("✅")
                await request_message.add_reaction("❌")
            except Exception as e:
                await send_to_debug_channel(
                    self.client, ctx, f"Tried name: {name} |\n{e}"
                )
                await ctx.respond(
                    f"``Error 44:`` Oops! Something went wrong. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance.",
                    delete_after=30,
                )
                return
            # Store the message ID of the embed that staff is reviewing
            try:  # Once a decision, via reaction, is made - use this ID to automatically delete the request message from the channel
                with DBA.DBAccess() as db:
                    db.execute(
                        "UPDATE player_name_request SET embed_message_id = %s WHERE id = %s;",
                        (request_message_id, player_name_request_id),
                    )
                await ctx.respond(
                    f"Your name change request was submitted to the staff team for review.\n```{original_name} -> {name}```",
                    delete_after=30,
                )
                return
            except Exception as e:
                await send_to_debug_channel(
                    self.client, ctx, f"Tried name: {name} |\n{e}"
                )
                await ctx.respond(
                    f"``Error 35:`` Oops! Something went wrong. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance.",
                    delete_after=30,
                )
                return


def setup(client):
    client.add_cog(NameChangeCog(client))
