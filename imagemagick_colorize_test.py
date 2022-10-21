rank_filename = f'/home/lounge/200-Lounge-Mogi-Bot/images/rank.png'
stats_rank_filename = f'/home/lounge/200-Lounge-Mogi-Bot/images/stats_rank.png'

correct = subprocess.run(['convert', f'{rank_filename}'], '-fill', f'"rgb({red},{green},{blue})"', '-tint', '100', f'{stats_rank_filename}')
f=discord.File(rank_filename, filename='rank.jpg')
sf=discord.File(f'/home/lounge/200-Lounge-Mogi-Bot/images/stats_rank.png', filename='stats_rank.jpg')

# Create imagemagick image
# https://imagemagick.org/script/color.php
pango_string = f'pango:<tt>{mmr_table_string}</tt>'
mmr_filename = f'/home/lounge/200-Lounge-Mogi-Bot/images/{hex(ctx.author.id)}mmr.jpg'
# correct = subprocess.run(['convert', '-background', 'gray21', '-fill', 'white', pango_string, mmr_filename], check=True, text=True)
correct = subprocess.run(['convert', '-background', 'None', '-fill', 'white', pango_string, 'mkbg.jpg', '-compose', 'DstOver', '-layers', 'flatten', mmr_filename], check=True, text=True)
# '+swap', '-compose', 'Over', '-composite', '-quality', '100',
# '-fill', '#00000040', '-draw', 'rectangle 0,0 570,368',
f=discord.File(mmr_filename, filename='mmr.jpg')
sf=discord.File(f'/home/lounge/200-Lounge-Mogi-Bot/images/{hex(ctx.author.id)}table.png', filename='table.jpg')

# Create embed
embed2 = discord.Embed(title=f'Tier {tier_name.upper()} Results', color = discord.Color.blurple())
embed2.add_field(name='Table ID', value=f'{str(db_mogi_id)}', inline=True)
embed2.add_field(name='Tier', value=f'{tier_name.upper()}', inline=True)
embed2.add_field(name='Submitted by', value=f'<@{ctx.author.id}>', inline=True)
embed2.add_field(name='View on website', value=f'https://200-lounge.com/mogi/{db_mogi_id}', inline=False)
embed2.set_image(url='attachment://table.jpg')
table_message = await results_channel.send(content=None, embed=embed2, file=sf)
table_url = table_message.embeds[0].image.url