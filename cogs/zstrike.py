import discord
from discord.ext import commands
import DBA
import logging
import datetime
from helpers.checkers import check_if_uid_is_placement
from helpers.checkers import check_if_banned_characters
from helpers.getters import get_number_of_strikes_for_uid
from helpers.getters import get_lounge_guild
from helpers.getters import get_unix_time_now
from helpers.getters import get_rank_id_list
from helpers.getters import get_discord_role
from config import ADMIN_ROLE_ID, UPDATER_ROLE_ID, PING_DEVELOPER, LOUNGELESS_ROLE_ID, STRIKES_CHANNEL_ID

class StrikeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zstrike',
        description='Add strike & -mmr penalty to a player',
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zstrike(self, ctx,
                     player: discord.Option(str, description='Player name', required=True),
                     mmr_penalty: discord.Option(int, description='How much penalty to apply? (Do not put the - sign)', required=True),
                     reason: discord.Option(str, description='Why?', required=True)):
        await ctx.defer()
        if len(reason) > 32:
            await ctx.respond('Reason too long (32 character limit)')
            return
        try:
            with DBA.DBAccess() as db:
                player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
        except Exception:
            await ctx.respond('Player not found')
            return
        y = await check_if_banned_characters(reason)
        if y:
            await ctx.respond('Invalid reason')
            return

        # Send info to strikes table
        mmr_penalty = abs(mmr_penalty)
        # Update player MMR
        current_time = datetime.datetime.now()
        expiration_date = current_time + datetime.timedelta(days=30)
        mmr = 0
        num_of_strikes = 0

        # if placement player, insert a strike, penalty applied = 0
        player_is_placement = await check_if_uid_is_placement(player_id)
        if player_is_placement:
            with DBA.DBAccess() as db:
                # Create strike
                db.execute('INSERT INTO strike (player_id, reason, mmr_penalty, expiration_date, penalty_applied) VALUES (%s, %s, %s, %s, %s);', (player_id, reason, mmr_penalty, expiration_date, 0))
                # Get inserted strike
                try:
                    strike_id = db.query('SELECT strike_id FROM strike WHERE player_id = %s AND reason = %s AND mmr_penalty = %s ORDER BY create_date DESC;', (player_id, reason, mmr_penalty))[0][0]
                except Exception:
                    logging.info('Strike application failed - could not retrieve last inserted strike')
                    return
        else:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player_id,))
                if temp[0][0] is None:
                    await ctx.respond(f'This player has no MMR! Contact {PING_DEVELOPER}')
                    return
                else:
                    mmr = temp[0][0]

            with DBA.DBAccess() as db:
                # Create strike
                db.execute('INSERT INTO strike (player_id, reason, mmr_penalty, expiration_date) VALUES (%s, %s, %s, %s);', (player_id, reason, mmr_penalty, expiration_date))
                # Get inserted strike
                try:
                    strike_id = db.query('SELECT strike_id FROM strike WHERE player_id = %s AND reason = %s AND mmr_penalty = %s ORDER BY create_date DESC;', (player_id, reason, mmr_penalty))[0][0]
                except Exception:
                    logging.info('Strike application failed - could not retrieve last inserted strike')
                    return

                # Update player MMR
                db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', ((max(mmr-mmr_penalty, 1)), player_id))

        num_of_strikes = await get_number_of_strikes_for_uid(player_id)
        if num_of_strikes >= 3:
            times_strike_limit_reached = 0
            with DBA.DBAccess() as db:
                temp = db.query('SELECT times_strike_limit_reached FROM player WHERE player_id = %s;', (player_id,))
                times_strike_limit_reached = temp[0][0] + 1
                logging.info(f'Strike limit reached. {7*times_strike_limit_reached} day ban will be applied to: {player_id}')
                unban_unix_time = await get_unix_time_now() + 7*24*60*60*times_strike_limit_reached  # multiply their ban length by 7x how many times they have reached strike limit before
                dt = datetime.datetime.utcfromtimestamp(unban_unix_time).strftime('%Y-%m-%d %H:%M:%S')  # create the dt object
                db.execute('UPDATE player SET times_strike_limit_reached = %s, unban_date = %s WHERE player_id = %s;', (times_strike_limit_reached, dt, player_id))  # insert the dt object

            try:
                user = await get_lounge_guild(self.client).fetch_member(player_id)
                loungeless_role = get_discord_role(self.client, LOUNGELESS_ROLE_ID)
                await user.add_roles(loungeless_role)
                for rank in get_rank_id_list:
                    bye = get_lounge_guild(self.client).get_role(rank)
                    await user.remove_roles(bye)
            except Exception:
                pass

            channel = self.client.get_channel(STRIKES_CHANNEL_ID)
            await channel.send(f'<@{player_id}> has reached 3 strikes. Loungeless role applied\n`# of offenses:` {times_strike_limit_reached}')

        await ctx.respond(f'Strike applied to <@{player_id}> | Penalty: {mmr_penalty}\n`ID: {strike_id}`')


def setup(client):
    client.add_cog(StrikeCog(client))
