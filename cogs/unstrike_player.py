import discord
from discord.ext import commands
import DBA
import logging
from datetime import datetime
from config import REPORTER_ROLE_ID, LOUNGE, SECONDS_IN_A_DAY
from helpers.getters import get_unix_time_now

class UnstrikeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='unstrike_player',
        description='Remove strike by ID',
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(REPORTER_ROLE_ID)
    async def unstrike(self, ctx, strike_id: discord.Option(int, description='Enter the strike ID', required=True)):
        await ctx.defer()
        # Check if strike exists
        unix_now = await get_unix_time_now()
        with DBA.DBAccess() as db:
            try:
                temp = db.query('SELECT strike_id, player_id, reason, mmr_penalty, penalty_applied, UNIX_TIMESTAMP(create_date) FROM strike WHERE strike_id = %s;', (strike_id,))
                # db_strike_id = temp[0][0]
                player_id = temp[0][1]
                # reason = temp[0][2]
                mmr_penalty = temp[0][3]
                penalty_applied = temp[0][4]
                unix_strike = temp[0][5]
            except Exception:
                await ctx.respond('Strike ID not found')
                return
        if unix_now - unix_strike > SECONDS_IN_A_DAY:
            await ctx.respond('You cannot remove this strike. Too old')
            return
        if player_id == ctx.author.id:
            await ctx.respond('You cannot unstrike yourself.')
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
