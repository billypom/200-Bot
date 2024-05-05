import discord
from discord.ext import commands
import DBA
from helpers.senders import send_to_debug_channel, send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from constants import LOUNGE, REPORTER_ROLE_ID, PING_DEVELOPER
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from discord import ApplicationContext


class RevertCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="revert_mogi", description="Undo a mogi/table", guild_ids=LOUNGE
    )
    @commands.has_any_role(REPORTER_ROLE_ID)
    async def revert(
        self,
        ctx: "ApplicationContext",
        mogi_id: discord.Option(int, "Mogi ID / Table ID", required=True),  # type: ignore
    ):
        await ctx.defer()
        results_channel = None
        flag = 0
        # Make sure mogi exists
        try:
            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT mogi_id, table_message_id, mmr_message_id, has_reduced_loss FROM mogi WHERE mogi_id = %s;",
                    (mogi_id,),
                )
                if temp[0][0] is None:  # type: ignore
                    await ctx.respond("``Error 34:`` Mogi could not be found.")
                    return
                # Grab message IDs to delete later
                table_message_id = int(temp[0][1])  # type: ignore
                mmr_message_id = int(temp[0][2])  # type: ignore
                has_reduced_loss = bool(temp[0][3])  # type: ignore
        except Exception as e:
            await send_to_debug_channel(
                self.client, ctx, f"revert error 35 wrong mogi id? | {e}"
            )
            await ctx.respond("``Error 35:`` Mogi could not be found")
            return
        # If mogi has reduced loss, do not revert
        if has_reduced_loss:
            await ctx.respond(
                f"You cannot `/revert` a mogi that has reduced loss. :warning: {PING_DEVELOPER}"
            )
            return
        # Check for rank changes
        try:
            with DBA.DBAccess() as db:
                players_mogi = db.query(
                    "select p.player_id, p.player_name, p.mmr, pm.mmr_change, p.rank_id, t.results_id FROM player p JOIN player_mogi pm ON p.player_id = pm.player_id JOIN mogi m on pm.mogi_id = m.mogi_id JOIN tier t on t.tier_id = m.tier_id WHERE m.mogi_id = %s",
                    (mogi_id,),
                )
        except Exception as e:
            await ctx.respond(
                f"`Database error`: Could not retrieve the mogi {PING_DEVELOPER}"
            )
            return
        try:
            with DBA.DBAccess() as db:
                db_ranks_table = db.query(
                    "SELECT rank_id, mmr_min, mmr_max FROM ranks WHERE rank_id > %s ORDER BY mmr_min DESC LIMIT 8;",
                    (1,),
                )
        except Exception as e:
            await ctx.respond(
                f"`Database error`: Could not retrieve ranks {PING_DEVELOPER}"
            )
            return
        for j in range(len(db_ranks_table)):
            for i in range(len(players_mogi)):
                rank_id = int(db_ranks_table[j][0])  # type: ignore
                min_mmr = int(db_ranks_table[j][1])  # type: ignore
                max_mmr = int(db_ranks_table[j][2])  # type: ignore
                my_player_id = int(players_mogi[i][0])  # type: ignore
                # my_player_name = players_mogi[i][1]
                my_player_mmr = int(players_mogi[i][2])  # type: ignore
                my_player_new_mmr = my_player_mmr + (int(players_mogi[i][3]) * -1)  # type: ignore
                my_player_rank_id = int(players_mogi[i][4])  # type: ignore
                results_channel_id = int(players_mogi[i][5])  # type: ignore
                results_channel = self.client.get_channel(results_channel_id)
                # Rank back up
                try:
                    if (
                        my_player_mmr < min_mmr
                        and my_player_new_mmr >= min_mmr
                        and my_player_new_mmr < max_mmr
                    ):
                        guild = get_lounge_guild(self.client)
                        current_role = guild.get_role(my_player_rank_id)
                        new_role = guild.get_role(rank_id)
                        try:
                            member = await guild.fetch_member(my_player_id)
                            await member.remove_roles(current_role)  # type: ignore
                            await member.add_roles(new_role)  # type: ignore
                        except Exception as e:
                            await send_raw_to_debug_channel(
                                self.client,
                                "Member not found. Skipping role assignment",
                                e,
                            )
                            pass
                        await results_channel.send(
                            f"<@{my_player_id}> has been promoted to {new_role}"
                        )
                        try:
                            with DBA.DBAccess() as db:
                                db.execute(
                                    "UPDATE player SET rank_id = %s, mmr = %s WHERE player_id = %s;",
                                    (rank_id, my_player_new_mmr, my_player_id),
                                )
                        except Exception as e:
                            await send_raw_to_debug_channel(
                                self.client,
                                f"revert_mogi error - unable to update player {my_player_id} from {my_player_mmr} mmr -> {my_player_new_mmr}, with new rank {rank_id}",
                                e,
                            )
                            continue
                    # Rank down
                    elif (
                        my_player_mmr > max_mmr
                        and my_player_new_mmr <= max_mmr
                        and my_player_new_mmr > min_mmr
                    ):
                        guild = get_lounge_guild(self.client)
                        current_role = guild.get_role(my_player_rank_id)
                        new_role = guild.get_role(rank_id)
                        try:
                            member = await guild.fetch_member(my_player_id)
                            await member.remove_roles(current_role)  # type: ignore
                            await member.add_roles(new_role)  # type: ignore
                        except Exception as e:
                            await send_raw_to_debug_channel(
                                self.client,
                                "Member not found. Skipping role assignment",
                                e,
                            )
                            pass
                        await results_channel.send(
                            f"<@{my_player_id}> has been demoted to {new_role}"
                        )
                        try:
                            with DBA.DBAccess() as db:
                                db.execute(
                                    "UPDATE player SET rank_id = %s, mmr = %s WHERE player_id = %s;",
                                    (rank_id, my_player_new_mmr, my_player_id),
                                )
                        except Exception as e:
                            await send_raw_to_debug_channel(
                                self.client,
                                f"revert_mogi error - unable to update player {my_player_id} from {my_player_mmr} mmr -> {my_player_new_mmr}, with new rank {rank_id}",
                                e,
                            )
                            continue
                except Exception as e:
                    await send_to_debug_channel(
                        self.client, ctx, f"/revert_mogi FATAL ERROR | {e}"
                    )
                    flag = 1
                    pass
        for i in range(len(players_mogi)):
            # this is very bad. i should just loop the other way around
            my_player_id = int(players_mogi[i][0])  # type: ignore
            # my_player_name = players_mogi[i][1]
            my_player_mmr = int(players_mogi[i][2])  # type: ignore
            my_player_new_mmr = my_player_mmr + (int(players_mogi[i][3]) * -1)  # type: ignore
            my_player_rank_id = int(players_mogi[i][4])  # type: ignore
            results_channel_id = int(players_mogi[i][5])  # type: ignore
            try:
                with DBA.DBAccess() as db:
                    db.execute(
                        "UPDATE player SET mmr = %s WHERE player_id = %s;",
                        (my_player_new_mmr, my_player_id),
                    )
            except Exception as e:
                await send_to_debug_channel(
                    self.client, ctx, f"/revert_mogi FATAL ERROR 2 | {e}"
                )
                flag = 1
                pass
        # Delete DB records, order matters
        with DBA.DBAccess() as db:
            db.execute("DELETE FROM player_mogi WHERE mogi_id = %s;", (mogi_id,))
            db.execute("DELETE FROM mogi WHERE mogi_id = %s;", (mogi_id,))
        # Delete results channel messages
        embed_message = await results_channel.fetch_message(table_message_id)  # type: ignore
        await embed_message.delete()
        embed_message = await results_channel.fetch_message(mmr_message_id)  # type: ignore
        await embed_message.delete()
        if flag == 1:
            fatal_error = f"FATAL ERROR WHILE UPDATING ROLES. CONTACT {PING_DEVELOPER}"
        else:
            fatal_error = ""
        await ctx.respond(f"Mogi ID `{mogi_id}` has been removed. {fatal_error}")


def setup(client):
    client.add_cog(RevertCog(client))
