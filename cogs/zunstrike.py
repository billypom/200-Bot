import discord
from discord.ext import commands
import DBA
import logging
from config import ADMIN_ROLE_ID, UPDATER_ROLE_ID

class UnstrikeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zunstrike',
        description='Remove strike by ID',
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zunstrike(self, ctx, strike_id: discord.Option(int, description='Enter the strike ID', required=True)):
        await ctx.defer()
        # Check if strike exists
        with DBA.DBAccess() as db:
            try:
                temp = db.query('SELECT strike_id, player_id, reason, mmr_penalty, penalty_applied FROM strike WHERE strike_id = %s;', (strike_id,))
                # db_strike_id = temp[0][0]
                player_id = temp[0][1]
                # reason = temp[0][2]
                mmr_penalty = temp[0][3]
                penalty_applied = temp[0][4]
            except Exception:
                await ctx.respond('Strike ID not found')
                return
        if penalty_applied:
            # Undo the penalty
            with DBA.DBAccess() as db:
                # Get player mmr
                try:
                    player_mmr = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player_id,))[0][0]
                except Exception:
                    logging.info(f'UNSTRIKE Failed - {player_id} not found')
                    await ctx.respond('Something went wrong. Player on strike not found.')
                    
                # Do math to remove penalty
                player_new_mmr = (max(player_mmr+mmr_penalty, 1))

                # Update player MMR
                try:
                    db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (player_new_mmr, player_id))
                except Exception:
                    logging.info(f'UNSTRIKE Failed - {player_id} MMR ({player_mmr}) could not be updated to ({player_new_mmr})')
                    await ctx.respond('Something went wrong. Player MMR could not be updated.')
        else:
            pass
            
        # Delete the strike
        with DBA.DBAccess() as db:
            db.execute('DELETE FROM strike WHERE strike_id = %s;', (strike_id,))
        await ctx.respond(f'Strike ID {strike_id} has been removed.')

def setup(client):
    client.add_cog(UnstrikeCog(client))
