import discord
from discord.ext import commands
import DBA
from helpers.senders import send_to_debug_channel
from helpers.getters import get_lounge_guild
from config import LOUNGE, ADMIN_ROLE_ID, UPDATER_ROLE_ID, PING_DEVELOPER

class ZRevertCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zrevert",
        description="Undo a table",
        guild_ids=LOUNGE
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zrevert(self, ctx, mogi_id: discord.Option(int, 'Mogi ID / Table ID', required=True)):
        await ctx.defer()
        flag = 0

        # Make sure mogi exists
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT mogi_id FROM mogi WHERE mogi_id = %s;', (mogi_id,))
                if temp[0][0] is None:
                    await ctx.respond('``Error 34:`` Mogi could not be found.')
                    return
        except Exception as e:
            await send_to_debug_channel(self.client, ctx, f'zrevert error 35 wrong mogi id? | {e}')
            await ctx.respond('``Error 35:`` Mogi could not be found')
            return

        # Check for rank changes
        with DBA.DBAccess() as db:
            players_mogi = db.query('select p.player_id, p.player_name, p.mmr, pm.mmr_change, p.rank_id, t.results_id FROM player p JOIN player_mogi pm ON p.player_id = pm.player_id JOIN mogi m on pm.mogi_id = m.mogi_id JOIN tier t on t.tier_id = m.tier_id WHERE m.mogi_id = %s', (mogi_id,))
        with DBA.DBAccess() as db:
            db_ranks_table = db.query('SELECT rank_id, mmr_min, mmr_max FROM ranks WHERE rank_id > %s ORDER BY mmr_min DESC LIMIT 8;', (1,))
        for j in range(len(db_ranks_table)):
            for i in range(len(players_mogi)):
                rank_id = db_ranks_table[j][0]
                min_mmr = db_ranks_table[j][1]
                max_mmr = db_ranks_table[j][2]
                my_player_id = players_mogi[i][0]
                # my_player_name = players_mogi[i][1]
                my_player_mmr = int(players_mogi[i][2])
                my_player_new_mmr = my_player_mmr + (int(players_mogi[i][3])* -1)
                my_player_rank_id = players_mogi[i][4]
                results_channel_id = players_mogi[i][5]
                results_channel = self.client.get_channel(results_channel_id)
                # Rank back up
                #print(f'{min_mmr} - {max_mmr} | {my_player_name} {my_player_mmr} + {players_mogi[i][3] * -1} = {my_player_new_mmr}')
                try:
                    if my_player_mmr < min_mmr and my_player_new_mmr >= min_mmr and my_player_new_mmr < max_mmr:
                        guild = get_lounge_guild(self.client)
                        current_role = guild.get_role(my_player_rank_id)
                        new_role = guild.get_role(rank_id)
                        member = await guild.fetch_member(my_player_id)
                        await member.remove_roles(current_role)
                        await member.add_roles(new_role)
                        await results_channel.send(f'<@{my_player_id}> has been promoted to {new_role}')
                        with DBA.DBAccess() as db:
                            db.execute('UPDATE player SET rank_id = %s, mmr = %s WHERE player_id = %s;', (rank_id, my_player_new_mmr, my_player_id))
                    # Rank back down
                    elif my_player_mmr > max_mmr and my_player_new_mmr <= max_mmr and my_player_new_mmr > min_mmr:
                        guild = get_lounge_guild(self.client)
                        current_role = guild.get_role(my_player_rank_id)
                        new_role = guild.get_role(rank_id)
                        member = await guild.fetch_member(my_player_id)
                        await member.remove_roles(current_role)
                        await member.add_roles(new_role)
                        await results_channel.send(f'<@{my_player_id}> has been demoted to {new_role}')
                        with DBA.DBAccess() as db:
                            db.execute('UPDATE player SET rank_id = %s, mmr = %s WHERE player_id = %s;', (rank_id, my_player_new_mmr, my_player_id))
                except Exception as e:
                    await send_to_debug_channel(self.client, ctx, f'/zrevert FATAL ERROR | {e}')
                    flag = 1
                    pass
        for i in range(len(players_mogi)): # this is very bad because i should just loop the other way around
            # but im lazy and still need to make a dev server
            # but also who cares
            my_player_id = players_mogi[i][0]
            # my_player_name = players_mogi[i][1]
            my_player_mmr = int(players_mogi[i][2])
            my_player_new_mmr = my_player_mmr + (int(players_mogi[i][3])* -1)
            my_player_rank_id = players_mogi[i][4]
            results_channel_id = players_mogi[i][5]
            try:
                with DBA.DBAccess() as db:
                    db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (my_player_new_mmr, my_player_id))
            except Exception as e:
                await send_to_debug_channel(self.client, ctx, f'/zrevert FATAL ERROR 2 | {e}')
                flag = 1
                pass
        with DBA.DBAccess() as db:
            db.execute('DELETE FROM player_mogi WHERE mogi_id = %s;', (mogi_id,))
            db.execute('DELETE FROM mogi WHERE mogi_id = %s;', (mogi_id,))

        if flag == 1:
            fatal_error = f"FATAL ERROR WHILE UPDATING ROLES. CONTACT {PING_DEVELOPER}"
        else:
            fatal_error = ""
        await ctx.respond(f'Mogi ID `{mogi_id}` has been removed. {fatal_error}')

def setup(client):
    client.add_cog(ZRevertCog(client))