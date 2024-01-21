
# does not matter to put sub in lineups table
# /sub
# @client.slash_command(
#     name='sub',
#     description='Sub out a player',
#     # guild_ids=LOUNGE
# )
# async def sub(
#     ctx,
#     leaving_player: discord.Option(discord.Member, 'Leaving player', required=True),
#     subbing_player: discord.Option(discord.Member, 'Subbing player', required=True)
#     ):
#     await ctx.defer()
#     lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#     if lounge_ban:
#         await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
#         return
#     else:
#         pass
#     # Same player
#     if leaving_player.id == subbing_player.id:
#         await ctx.respond('<:bruh:1006883398607978537>')
#         return
#     # Player was already in lineup, got subbed out
#     with DBA.DBAccess() as db:
#         temp = db.query('SELECT player_id FROM sub_leaver WHERE player_id = %s;', (subbing_player.id,))
#         if temp:
#             if temp[0][0] == subbing_player.id:
#                 await ctx.respond('Player cannot sub into a mogi after being subbed out.')
#                 return
#         else:
#             pass
#     # Player exists
#     a = await check_if_uid_exists(leaving_player.id)
#     if a:
#         pass
#     else:
#         await ctx.respond('Use `/verify <mkc link>` to register for Lounge')
#         return
#     b = await check_if_uid_exists(subbing_player.id)
#     if b:
#         pass
#     else:
#         await ctx.respond(f'{subbing_player.name} is not registered for Lounge')
#         return
#     x = await check_if_mogi_is_ongoing(ctx)
#     if x:
#         pass
#     else:
#         await ctx.respond('Mogi has not started')
#         return
#     # Only players in the mogi can sub out others
#     y = await check_if_uid_in_first_12_of_tier(ctx.author.id, ctx.channel.id)
#     if y:
#         pass
#     else:
#         await ctx.respond('You are not in the mogi. You cannot sub out another player')
#         return
#     z = await check_if_uid_in_specific_tier(leaving_player.id, ctx.channel.id)
#     if z:
#         pass
#     else:
#         await ctx.respond(f'<@{leaving_player.id}> is not in this mogi.')
#         return
#     try:
#         with DBA.DBAccess() as db:
#             first_12 = db.query('SELECT player_id FROM (SELECT player_id FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT 12) as l WHERE player_id = %s;', (ctx.channel.id, subbing_player.id))
#             if first_12: # if there are players in lineup (first 12)
#                 if first_12[0][0] == subbing_player.id: # if subbing is already in lineup (first 12)
#                     await ctx.respond(f'{subbing_player.mention} is already in this mogi')
#                     return
#                 else:
#                     pass
#             try:
#                 leaving_player_name = db.query('SELECT player_name FROM player WHERE player_id = %s;', (leaving_player.id,))[0][0]
#                 subbing_player_name = db.query('SELECT player_name FROM player WHERE player_id = %s;', (subbing_player.id,))[0][0]
#                 teams_string = db.query('SELECT teams_string FROM tier WHERE tier_id = %s;', (ctx.channel.id,))[0][0]
#                 teams_string = teams_string.replace(leaving_player_name, subbing_player_name)
#                 teams_string += f'\n\n`EDITED`: `{leaving_player_name}` -> `{subbing_player_name}`'
#                 db.execute('DELETE FROM lineups WHERE player_id = %s;', (subbing_player.id,))
#                 db.execute('UPDATE lineups SET player_id = %s WHERE player_id = %s;', (subbing_player.id, leaving_player.id))
#                 db.execute('UPDATE tier SET teams_string = %s WHERE tier_id = %s;', (teams_string, ctx.channel.id))
#             except Exception:
#                 await ctx.respond(f'``Error 42:`` FATAL ERROR - {config.PING_DEVELOPER} help!!!')
#                 return
#     except Exception as e:
#         await ctx.respond(f'``Error 19:`` Oops! Something went wrong. Please contact {config.PING_DEVELOPER}')
#         await send_to_debug_channel(client, ctx, f'/sub error 19 {e}')
#         return
#     with DBA.DBAccess() as db:
#         db.execute('INSERT INTO sub_leaver (player_id, tier_id) VALUES (%s, %s);', (leaving_player.id, ctx.channel.id))
#     await ctx.respond(f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}>')
#     await send_to_sub_log(client, ctx, f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}> in {ctx.channel.mention}')
#     return