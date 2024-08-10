import discord
from discord import Option
from discord.ext import commands
import DBA
from helpers.checkers import check_if_banned_characters
from helpers.checkers import check_if_uid_exists
from helpers.senders import send_raw_to_debug_channel
from helpers.senders import send_to_danger_debug_channel
from constants import ADMIN_ROLE_ID, UPDATER_ROLE_ID, LOUNGE
import vlog_msg


class ChangeDiscordAccountCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zchange_discord_account",
        description="Change a player's Discord account",
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(ADMIN_ROLE_ID, UPDATER_ROLE_ID)
    async def zchange_discord_account(
        self,
        ctx,
        old_discord_id: Option(str, "Original Discord ID", required=True),  # type: ignore
        new_discord_id: Option(str, "New Discord ID", required=True),  # type: ignore
    ):
        await ctx.defer()

        bad = await check_if_banned_characters(old_discord_id)
        if bad:
            await send_to_danger_debug_channel(
                self.client, ctx, old_discord_id, discord.Color.red(), vlog_msg.error1
            )
            await ctx.respond("``Error 50:`` Invalid discord ID (Original Discord ID)")
            return

        bad = await check_if_banned_characters(new_discord_id)
        if bad:
            await send_to_danger_debug_channel(
                self.client, ctx, old_discord_id, discord.Color.red(), vlog_msg.error1
            )
            await ctx.respond("``Error 51:`` Invalid discord ID (New Discord ID)")
            return

        old_discord_id = int(old_discord_id)
        new_discord_id = int(new_discord_id)

        x = await check_if_uid_exists(old_discord_id)
        y = await check_if_uid_exists(new_discord_id)

        if not x:
            await ctx.respond(f"``Error 47:`` {old_discord_id} does not exist")
            return

        if y:
            await ctx.respond(f"``Error 48:`` {new_discord_id} already exists")
            return

        try:
            with DBA.DBAccess() as db:
                # get old player data
                temp = db.query(
                    "SELECT * FROM player WHERE player_id = %s;", (old_discord_id,)
                )
                # create new player
                db.execute(
                    "INSERT INTO player (player_id, player_name, mkc_id, country_code, fc, is_host_banned, is_chat_restricted, mmr, base_mmr, peak_mmr, rank_id, times_strike_limit_reached, twitch_link, mogi_media_message_id, banned_by_strikes_unban_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (
                        new_discord_id,
                        temp[0][1],  # type:ignore
                        temp[0][2],  # type:ignore
                        temp[0][3],  # type:ignore
                        temp[0][4],  # type:ignore
                        temp[0][5],  # type:ignore
                        temp[0][6],  # type:ignore
                        temp[0][7],  # type:ignore
                        temp[0][8],  # type:ignore
                        temp[0][9],  # type:ignore
                        temp[0][10],  # type:ignore
                        temp[0][11],  # type:ignore
                        temp[0][12],  # type:ignore
                        temp[0][13],  # type:ignore
                        temp[0][14],  # type: ignore
                    ),
                )
                # update player_mogi instances
                db.execute(
                    "UPDATE player_mogi SET player_id = %s WHERE player_id = %s;",
                    (new_discord_id, old_discord_id),
                )
                # update player_name_request instances
                db.execute(
                    "UPDATE player_name_request SET player_id = %s WHERE player_id = %s;",
                    (new_discord_id, old_discord_id),
                )
                # update strike instances
                db.execute(
                    "UPDATE strike SET player_id = %s WHERE player_id = %s;",
                    (new_discord_id, old_discord_id),
                )
                db.execute(
                    "UPDATE player_punishment SET player_id = %s WHERE player_id = %s;",
                    (new_discord_id, old_discord_id),
                )
                # update sub_leaver instances
                # db.execute('UPDATE sub_leaver SET player_id = %s WHERE player_id = %s;', (new_discord_id, old_discord_id))
                # delete old player
                db.execute(
                    "DELETE FROM player WHERE player_id = %s;", (old_discord_id,)
                )
        except Exception as e:
            await send_raw_to_debug_channel(
                self.client, "change discord account error", e
            )
            return

        await ctx.respond(
            f"Successfully moved player `{old_discord_id}` -> `{new_discord_id}`"
        )


def setup(client):
    client.add_cog(ChangeDiscordAccountCog(client))
