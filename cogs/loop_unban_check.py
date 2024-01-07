import discord
from discord.ext import commands, tasks
import time
import datetime
import DBA
import config
import logging


class unban_check(commands.Cog):
    def __init__(self, client):
        self.check.start()
        self.punishment_check.start()
        self.client = client

    async def get_unix_time_now(self):
        return time.mktime(datetime.datetime.now().timetuple())

    async def send_embed(self, anything, error):
        channel = self.client.get_channel(config.DEBUG_CHANNEL_ID)
        embed = discord.Embed(title='Hourly Unban Check', description='🔨', color = discord.Color.blue())
        embed.add_field(name='Description: ', value=anything, inline=False)
        embed.add_field(name='Details: ', value=str(error), inline=False)
        try:
            await channel.send(content=None, embed=embed)
        except Exception as e:
            logging.info(f'cogs | send_embed | channel does not exist | {e}')
            pass
    
    async def send_error_embed(self, anything, error):
        channel = self.client.get_channel(config.DEBUG_CHANNEL_ID)
        embed = discord.Embed(title='Hourly Unban Check', description='🔨', color = discord.Color.red())
        embed.add_field(name='Description: ', value=anything, inline=False)
        embed.add_field(name='Details: ', value=str(error), inline=False)
        try:
            await channel.send(content=None, embed=embed)
        except Exception as e:
            logging.info(f'cogs | send_error_embed | channel does not exist | {e}')
            pass

    async def set_player_roles(self, uid):
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT rank_id FROM player WHERE player_id = %s;', (uid,))
            # Remove all potential ranks first
            guild = await self.client.fetch_guild(config.LOUNGE[0])
            logging.info(f'cogs | unban_check | set_player_roles | fetched guild: {guild}')
            role = guild.get_role(temp[0][0])
            logging.info(f'cogs | unban_check | set_player_roles | got role: {role}')
            member = await guild.fetch_member(uid)
            logging.info(f'cogs | unban_check | set_player_roles | fetched member: {member}')
            await member.add_roles(role)
            # this log will fail in dev environment bcus of rank ids
            logging.info('cogs | unban_check | set_player_roles | added member roles')
        except Exception as e:
            await self.send_error_embed(f'<@{uid}>', f'set_player_roles exception: {e}')
            return False

    def cog_unload(self):
        self.check.cancel()
        self.punishment_check.cancel()
    
    @tasks.loop(hours=1)
    async def check(self):
        current_time = datetime.datetime.now()
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_id FROM player WHERE unban_date < %s;', (current_time,))
        except Exception as e:
            await self.send_error_embed(f'unban_check error 1 {config.PING_DEVELOPER}', e)
            return
        
        try:
            guild = await self.client.fetch_guild(config.LOUNGE[0])
        except Exception as e:
            await self.send_error_embed(f'unban_check error 2 {config.PING_DEVELOPER}', e)
            return
        try:
            loungeless_role = guild.get_role(config.LOUNGELESS_ROLE_ID)
        except Exception as e:
            await self.send_error_embed(f'unban_check error 3 {config.PING_DEVELOPER}', e)
            return
        
        for player in temp:
            try:
                user = await guild.fetch_member(player[0])
                await user.remove_roles(loungeless_role)
                await self.set_player_roles(player[0])
                await self.send_embed(f'<@{player[0]}>\nPlayer unbanned - Loungeless removed', player[0])
            except Exception:
                await self.send_embed(f'<@{player[0]}>\nPlayer unbanned - Not found in server - roles not assigned', player[0])
                pass
            with DBA.DBAccess() as db:
                db.execute('UPDATE player SET unban_date = NULL WHERE player_id = %s;', (player[0],))
    
    @tasks.loop(hours=1)
    async def punishment_check(self):
        # current time to compare against ban dates
        unix_now = await self.get_unix_time_now()
        current_time = datetime.datetime.now()
        # guild object
        guild = await self.client.fetch_guild(config.LOUNGE[0])

            
        with DBA.DBAccess() as db:
            temp = db.query('SELECT pp.player_id, pp.reason, pp.unban_date, pp.id, pp.punishment_id, p.punishment_type FROM player_punishment pp JOIN punishment p ON p.id = pp.punishment_id WHERE pp.unban_date < %s;', (unix_now,))
        for player in temp:
            logging.info(f'Punishment checking {player}')
            # check if already banned by automatic strike system
            try:
                with DBA.DBAccess() as db:
                    player_id_retrieved = db.query('SELECT player_id FROM player WHERE unban_date > %s AND player_id = %s;', (current_time, player[0]))[0][0]
                if player_id_retrieved == player[0]:
                    await self.send_embed(f'cogs | unban_check | punishment_check | PLAYER <@{player[0]}> IS STILL BANNED BY STRIKES. NOT UNBANNING', 'nope')
                    logging.info(f'POP_LOG | cogs unban_check | PLAYER <@{player[0]}> IS STILL BANNED BY STRIKES. NOT UNBANNING')
                    continue # continue to go to next loop player
                else:
                    pass
            except IndexError:
                # list index out of range means there is nobody that is already banned
                pass
            except Exception:
                logging.warning('cogs | unban_check | this is the error ? non index error')
                pass

            # Find the punishment type for nice messages to admins
            if player[4] == 1:
                punishment_role = guild.get_role(config.CHAT_RESTRICTED_ROLE_ID)
            elif player[4] == 2:
                punishment_role = guild.get_role(config.LOUNGELESS_ROLE_ID)
            try:
                # Get the user
                user = await guild.fetch_member(player[0])
                # Remove roles - doesn't work in dev env
                try:
                    await user.remove_roles(punishment_role)
                except Exception:
                    logging.info('cogs | unban_check | punishment_check | could not remove user roles (OK in dev env)')
                    pass
                # Add roles - doesn't work in dev env
                try:
                    await self.set_player_roles(player[0])
                except Exception:
                    logging.info('cogs | unban_check | punishment_check | could not add user roles (OK in dev env)')
                    pass

                await self.send_embed(f'<@{player[0]}>\nPlayer unbanned - {player[5]} removed\nOriginal reason: {player[1]}', player[0])
                
            except Exception as e:
                await self.send_error_embed('POP_LOG | cogs unban_check | punishment check failed',e)
                await self.send_embed(f'<@{player[0]}>\nPlayer unbanned - Not found in server - {player[5]} roles not assigned', player[0])
                logging.info(f'cogs | unban_check | punishment check | failed because: {e}')
                pass
                
            with DBA.DBAccess() as db:
                db.execute('UPDATE player_punishment SET unban_date = NULL WHERE id = %s;', (player[3],))
            with DBA.DBAccess() as db:
                db.execute('UPDATE player SET is_chat_restricted = 0 WHERE player_id = %s;', (player[0],))
            logging.info(f'{player} - Punishment removed | {punishment_role}')

    @check.before_loop
    async def before_check(self):
        print('unban waiting...')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(unban_check(client))