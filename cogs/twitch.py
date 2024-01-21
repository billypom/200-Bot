# # /twitch
# @client.slash_command(
#     name='twitch',
#     description='Link your Twitch stream - Enter your Username',
#     #guild_ids=LOUNGE
# )
# async def twitch(
#     ctx,
#     username: discord.Option(str, 'Enter your twitch username - your mogi streams will appear in the media channel', required=True)
#     ):
#     await ctx.defer(ephemeral=True)
#     lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#     if lounge_ban:
#         await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
#         return
#     else:
#         pass
#     x = await check_if_uid_exists(ctx.author.id)
#     if x:
#         pass
#     else:
#         await ctx.respond('Use `/verify` to register with Lounge')
#         return
#     y = await check_if_banned_characters(username)
#     if y:
#         await ctx.respond("Invalid twitch username")
#         await send_to_verification_log(client, ctx, username, vlog_msg.error1)
#         return
#     if len(str(username)) > 25:
#         await ctx.respond("Invalid twitch username")
#         return
#     try:
#         with DBA.DBAccess() as db:
#             db.execute("UPDATE player SET twitch_link = %s WHERE player_id = %s;", (str(username), ctx.author.id))
#             await ctx.respond("Twitch username updated.")
#     except Exception:
#         await ctx.respond("``Error 33:`` Player not found. Use ``/verify <mkc link>`` to register with Lounge")