import concurrent.futures
import requests
import json


# Takes ctx and Discord ID, returns mkc_user_id
async def lounge_request_mkc_user_id(ctx):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_lounge_request_mkc_user_id, ctx)
        return_value = future.result()
    return return_value


def mt_lounge_request_mkc_user_id(ctx):
    headers = {"User-Agent": "200-Lounge Bot"}
    try:
        player_id = ctx.author.id
        loungeresponse = requests.get(
            "https://www.mk8dx-lounge.com/api/player?discordId=" + str(player_id),
            headers=headers,
        )
        lounge_data = loungeresponse.json()
        guh = json.dumps(lounge_data)  # dump to a string
        lounge_data_dict = json.loads(guh)  # loads to a dict
        mkc_user_id = lounge_data_dict["mkcId"]
    except Exception:
        return -1
    return mkc_user_id
