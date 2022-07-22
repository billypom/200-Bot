# creates a string formatted for hlorenzi's gameboards table maker
# !scoreboard 4 miarun, usagi, Jeanne, ANIMALSASLEADERS, ta_go, FULLPOWER, kerokke, Takagisan, tracks, dasu_go, Slowbro, megane

# This ^ shouldn't be necessary anymore with the new bot that I want to make







# ^lt - In 150 lounge, this command takes this entire multiline input and parses through to find each team, and instructs the user to enter scores in order (top down, left right) 
# ---
# Poll Ended!

# 1. FFA - 0
# 2. 2v2 - 6 (Ayaka, babycartel, Syndicate, Demani, ShadowMK, Trae)
# 3. 3v3 - 0
# 4. 4v4 - 0
# 6. 6v6 - 0
# Winner: 2v2

# Room MMR: 4818
# Team 1: Euan, babycartel (MMR: 7800)
# Team 2: ShadowMK, Trae (MMR: 6633)
# Team 3: Splinkle, Warp Star (MMR: 4342)
# Team 4: gomigomi, Demani (MMR: 3503)
# Team 5: Zal, Syndicate (MMR: 3361)
# Team 6: Ayaka, Cyan (MMR: 3268)

# Table: !scoreboard 6 Euan, babycartel, ShadowMK, Trae, Splinkle, Warp Star, gomigomi, Demani, Zal, Syndicate, Ayaka, Cyan









# Submits table to specific tier or w/e. this bot sucks cynda
# this is the order that u get from the previous command tutorial above
# ---
# !submit 3 d
# miarun 58
# usagi 89
# Jeanne 107
# ANIMALSASLEADERS 75
# ta_go 65
# FULLPOWER 72
# kerokke 98
# Takagisan 96
# tracks 90
# dasu_go 81
# Slowbro 64
# megane 89



# Can up - 




@client.slash_command(
    name="c",
    description="Can up for a mogi"
)
async def c(
    ctx,
    ):
    await ctx.defer()
    x = await check_if_in_tier
    if x:
        pass
    else:
        await ctx.respond("")
        return
    return