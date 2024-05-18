from discord.ext import commands, tasks
from discord import Embed, Color
import time
import datetime
import DBA
from constants import (
    DEBUG_CHANNEL_ID,
    PING_DEVELOPER,
    CHAT_RESTRICTED_ROLE_ID,
    LOUNGELESS_ROLE_ID,
    LOUNGE,
)
from helpers import set_uid_roles
import logging
from typing import Any


class Unban_check(commands.Cog):
    def __init__(self, client):
        self.check.start()  # type: ignore
        self.punishment_check.start()
        self.client = client
        self.title = "Hourly Unban Check"

    async def get_unix_time_now(self):
        return time.mktime(datetime.datetime.now().timetuple())

    async def send_embed(self, anything: Any, details: str):
        channel = self.client.get_channel(DEBUG_CHANNEL_ID)
        embed = Embed(title=self.title, description="🔨", color=Color.blue())
        embed.add_field(name="Description: ", value=str(anything), inline=False)
        embed.add_field(name="Details: ", value=str(details), inline=False)
        await channel.send(content=None, embed=embed)

    async def send_error_embed(self, anything: Any, error: Exception):
        channel = self.client.get_channel(DEBUG_CHANNEL_ID)
        await channel.send(f"### Error\n{str(anything)}\n`{str(error)}`")

    def cog_unload(self):
        self.check.cancel()
        self.punishment_check.cancel()

    @tasks.loop(hours=1)
    async def check(self):
        current_time = datetime.datetime.now()
        try:
            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT player_id FROM player WHERE banned_by_strikes_unban_date < %s;",
                    (current_time,),
                )
        except Exception as e:
            await self.send_error_embed(f"unban_check error 1 {PING_DEVELOPER}", e)
            return

        try:
            guild = await self.client.fetch_guild(LOUNGE[0])
        except Exception as e:
            await self.send_error_embed(f"unban_check error 2 {PING_DEVELOPER}", e)
            return
        try:
            loungeless_role = guild.get_role(LOUNGELESS_ROLE_ID)
        except Exception as e:
            await self.send_error_embed(f"unban_check error 3 {PING_DEVELOPER}", e)
            return

        for player in temp:
            player_id = int(player[0])  # type: ignore
            try:
                user = await guild.fetch_member(player_id)
                await user.remove_roles(loungeless_role)
                await set_uid_roles(self.client, player_id)
                await self.send_embed(
                    f"<@{player_id}>\nPlayer unbanned - Loungeless removed",
                    str(player_id),
                )
            except Exception:
                await self.send_embed(
                    f"<@{player_id}>\nPlayer unbanned - Not found in server - roles not assigned",
                    str(player_id),
                )
                pass
            try:
                with DBA.DBAccess() as db:
                    db.execute(
                        "UPDATE player SET banned_by_strikes_unban_date = NULL WHERE player_id = %s;",
                        (player_id,),
                    )
            except Exception as e:
                await self.send_error_embed(f"unban_check error 4 {PING_DEVELOPER}", e)
                return

    @tasks.loop(hours=1)
    async def punishment_check(self):
        # current time to compare against ban dates
        unix_now = await self.get_unix_time_now()
        print(unix_now)
        current_time = datetime.datetime.now()
        # guild object
        guild = await self.client.fetch_guild(LOUNGE[0])

        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT pp.player_id, pp.reason, pp.unban_date, pp.id, pp.punishment_id, p.punishment_type FROM player_punishment pp JOIN punishment p ON p.id = pp.punishment_id WHERE pp.unban_date < %s;",
                (unix_now,),
            )
        for player in temp:
            player_id = int(player[0])  # type: ignore
            reason = player[1]  # type: ignore
            _ = player[2]  # type: ignore
            player_punishment_id = player[3]  # type: ignore
            punishment_id = player[4]  # type: ignore
            punishment_type = player[5]  # type: ignore
            logging.info(
                f"loop_unban_check punishment_check() | Punishment checking {player}"
            )
            await self.send_embed(
                f"loop_unban_check | punishment checking <@{player_id}>",
                "I found someone who has a punishment that should be removed. I will attempt to process the removal.",
            )
            # check if already banned by automatic strike system
            try:
                with DBA.DBAccess() as db:
                    player_id_retrieved = db.query(
                        "SELECT player_id FROM player WHERE banned_by_strikes_unban_date > %s AND player_id = %s;",
                        (unix_now, player_id),
                    )[0][0]  # type: ignore
                if player_id_retrieved == player_id:
                    await self.send_embed(
                        f"loop_unban_check | <@{player_id}> is still banned by strikes, so I will not unban them here yet.",
                        "nope",
                    )
                    continue  # next player
                else:
                    pass
            except IndexError:
                # list index out of range means there is nobody that is already banned
                pass
            except Exception:
                logging.warning("loop_unban_check | generic error")
                pass

            # Find the punishment id for nice messages to admins
            # 1 = Restricted
            # 2 = Loungeless
            if punishment_id == 1:
                punishment_role = guild.get_role(CHAT_RESTRICTED_ROLE_ID)
            elif punishment_id == 2:
                punishment_role = guild.get_role(LOUNGELESS_ROLE_ID)
            else:
                continue
            try:
                # Get the user
                try:
                    user = await guild.fetch_member(player_id)
                except Exception:
                    await self.send_embed(
                        f"loop_unban_check | Player <@{player_id}> is not in the server. Therefore I cannot remove their punishment. I will attempt to remove their punishment during the next hour of checks.",
                        "Player not found in server",
                    )
                    continue
                try:
                    await user.remove_roles(punishment_role)
                except Exception:
                    logging.info(
                        "loop_unban_check | could not remove user roles (OK in dev env)"
                    )
                    pass
                try:
                    await set_uid_roles(self.client, player_id)
                except Exception:
                    logging.info(
                        "loop_unban_check | could not add user roles (OK in dev env)"
                    )
                    pass
                await self.send_embed(
                    f"loop_unban_check | <@{player_id}>\nPlayer unbanned - {punishment_type} removed\nOriginal reason: {reason}",
                    str(player_id),
                )
            except Exception as e:
                await self.send_error_embed(
                    "cogs | unban_check | punishment check failed", e
                )
                await self.send_embed(
                    f"loop_unban_check | <@{player_id}>\nPlayer unbanned - Not found in server - {punishment_type} roles not assigned",
                    str(player_id),
                )
                logging.info(f"loop_unban_check | failed because: {e}")
                pass
            try:
                with DBA.DBAccess() as db:
                    db.execute(
                        "UPDATE player_punishment SET unban_date = NULL WHERE id = %s;",
                        (player_punishment_id,),
                    )
            except Exception as e:
                await self.send_error_embed(
                    f"loop_unban_check | Could not remove unban_date field for player {player_id}",
                    e,
                )
            if punishment_id == 1:
                try:
                    with DBA.DBAccess() as db:
                        db.execute(
                            "UPDATE player SET is_chat_restricted = 0 WHERE player_id = %s;",
                            (player_id,),
                        )
                    logging.info(f"{player} - Punishment removed | {punishment_role}")
                except Exception as e:
                    await self.send_error_embed(
                        "loop_unban_check | Could not update player table", e
                    )

    @check.before_loop
    async def before_check(self):
        print("unban waiting...")
        await self.client.wait_until_ready()

    @punishment_check.before_loop
    async def before_punishment_check(self):
        print("punishment waiting...")
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(Unban_check(client))
