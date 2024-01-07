# Requests & async requests
import concurrent.futures
import requests
import re
import json
from config import JAZZY_MKC_NAME, JAZZY_MKC_PASSWORD
from bs4 import BeautifulSoup as Soup

async def mkc_request_forum_info(mkc_user_id):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_mkc_request_forum_info, mkc_user_id)
        return_value = future.result()
    return return_value

def mt_mkc_request_forum_info(mkc_user_id):
    try:
        # Get shared ips
        login_url = 'https://www.mariokartcentral.com/forums/index.php?login/login'
        data_url = (f'https://www.mariokartcentral.com/forums/index.php?members/{mkc_user_id}/shared-ips')
        with requests.Session() as s:
            html = s.get(login_url).content
            soup = Soup(html, 'html.parser')
            token = soup.select_one('[name=_xfToken]').attrs['value']
            payload = {
            'login': str(JAZZY_MKC_NAME),
            'password': str(JAZZY_MKC_PASSWORD),
            '_xfToken': str(token),
            '_xfRedirect': 'https://www.mariokartcentral.com/mkc/'
            }
            response = s.post(login_url, data=payload)
            response = s.get(data_url)
            response_string = str(response.content)
            response_lines = response_string.split('\\n')
            list_of_user_matches = []
            for line in response_lines:
                # this h3 div is only used to show shared ips. so it works as a unique identifier
                if '<h3 class="contentRow-header"><a href="/forums/index.php?members/' in line:
                    regex_pattern = 'members/.*\.\d*'
                    if re.search(regex_pattern, line):
                        regex_group = re.search(regex_pattern, line)
                        x = regex_group.group()
                        reg_array = re.split('/', x)
                        list_of_user_matches.append(reg_array[1])

        data_url = (f'https://www.mariokartcentral.com/forums/index.php?members/{mkc_user_id}')
        with requests.Session() as s:
            html = s.get(login_url).content
            soup = Soup(html, 'html.parser')
            token = soup.select_one('[name=_xfToken]').attrs['value']
            payload = {
            'login': str(JAZZY_MKC_NAME),
            'password': str(JAZZY_MKC_PASSWORD),
            '_xfToken': str(token),
            '_xfRedirect': 'https://www.mariokartcentral.com/mkc/'
            }
            response = s.post(login_url, data=payload)
            response = s.get(data_url)
            response_string = str(response.content)
            response_lines = response_string.split('\\n')
            # \t\t\t\t\t\t\t\t\t\t\t<time  class="u-dt" dir="auto" datetime="2022-07-30T11:07:30-0400" data-time="1659193650" data-date-string="Jul 30, 2022" data-time-string="11:07 AM" title="Jul 30, 2022 at 11:07 AM">A moment ago</time> <span role="presentation" aria-hidden="true">&middot;</span> Viewing member profile <em><a href="/forums/index.php?members/popuko.154/" dir="auto">popuko</a></em>
            for idx, line in enumerate(response_lines):
                # print(line)
                if 'Last seen' in line:
                    last_seen_string = response_lines[idx+2]
                    regex_pattern = 'data-time="\d*"'
                    if re.search(regex_pattern, last_seen_string):
                        regex_group = re.search(regex_pattern, last_seen_string)
                        x = regex_group.group()
                        reg_array = re.split('"', x)
                        # print(reg_array)
                        last_seen_unix_timestamp = reg_array[1]
                        break
        return [last_seen_unix_timestamp, list_of_user_matches]
    except Exception:
        return [-1, [-1, -1]]

async def mkc_request_mkc_player_id(mkc_user_id):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_mkc_request_mkc_player_id, mkc_user_id)
        return_value = future.result()
    return return_value

def mt_mkc_request_mkc_player_id(mkc_user_id):
    try:
        login_url = 'https://www.mariokartcentral.com/forums/index.php?login/login'
        data_url = 'https://www.mariokartcentral.com/mkc/api/registry/players/all'
        with requests.Session() as s:
            html = s.get(login_url).content
            soup = Soup(html, 'html.parser')
            token = soup.select_one('[name=_xfToken]').attrs['value']
            payload = {
            'login': str(JAZZY_MKC_NAME),
            'password': str(JAZZY_MKC_PASSWORD),
            '_xfToken': str(token),
            '_xfRedirect': 'https://www.mariokartcentral.com/mkc/'
            }
            response = s.post(login_url, data=payload)
            response = s.get(data_url)
        registry_data = response.json()
        response = json.dumps(registry_data)
        response = json.loads(response)
        for player in response["data"]:
            if player["user_id"] == int(mkc_user_id):
                mkc_player_id = player["player_id"]
                break
            else:
                continue
        if mkc_player_id is not None:
            return mkc_player_id
        else:
            return -1
    except Exception:
        return -1

async def mkc_request_registry_info(mkc_player_id):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_mkc_request_registry_info, mkc_player_id)
        return_value = future.result()
    return return_value

# returs user_id, country_code, is_banned
# Input: mkc registry id
# Output: (mkc user id, alpha-2 iso country code, boolean is_banned)
def mt_mkc_request_registry_info(mkc_player_id):
    try:
        mkcresponse = requests.get("https://www.mariokartcentral.com/mkc/api/registry/players/" + str(mkc_player_id))
        mkc_data = mkcresponse.json()
        buh = json.dumps(mkc_data)
        mkc_data_dict = json.loads(buh)
        return_value = [mkc_data_dict['user_id'], mkc_data_dict['country_code'], mkc_data_dict['is_banned']]
        return return_value
    except Exception:
        return [-1, -1, -1]
