# format_list = [1, 2, 3, 5, 5]

# max_val = max(format_list)
# ind = [i for i, v in enumerate(format_list) if v == max_val]

# print(ind)

import requests
import secrets
import re
from bs4 import BeautifulSoup as Soup
# try:
# mkcresponse = requests.get("https://www.mariokartcentral.com/forums/index.php?members/popuko.154/user-ips")
# print(mkcresponse.status_code)
# mkc_data = mkcresponse.json()
# buh = json.dumps(mkc_data)
# mkc_data_dict = json.loads(buh)
# return_value = mkc_data_dict[field_name]
# return return_value

login_url = 'https://www.mariokartcentral.com/forums/index.php?login/login'
data_url = 'https://www.mariokartcentral.com/forums/index.php?members/tonola.37179/shared-ips'
with requests.Session() as s:
    html = s.get(login_url).content
    soup = Soup(html, 'html.parser')
    token = soup.select_one('[name=_xfToken]').attrs['value']
    payload = {
    'login': str(secrets.mkc_name),
    'password': str(secrets.mkc_password),
    '_xfToken': str(token),
    '_xfRedirect': 'https://www.mariokartcentral.com/mkc/'
    }
    response = s.post(login_url, data=payload)
    response = s.get(data_url)
# print(response.status_code)
# print(response.content)
response_string = str(response.content)
# print(type(response_string))
# print(response_string)
response_lines = response_string.split('\\n')
# print(response_lines)
for line in response_lines:
    if '<h3 class="contentRow-header"><a href="/forums/index.php?members/' in line:
        regex_pattern = 'members/.*\.\d*'
        # if the regex pattern is found in the line
        if re.search(regex_pattern, line):
            # find the exact place (index-characters of string or w/e) where the pattern matches
            regex_group = re.search(regex_pattern, line)
            # get the string from that exact place
            x = regex_group.group()
            # split on a slash (its always slash)
            reg_array = re.split('/', x)
            print(f'regex group: {regex_group}')
            print(f'x: {x}')
        # print(line)
# get_data = response.json()
# response = json.dumps(get_data)
# response = json.loads(response)
# for player in response["data"]:
    # if player["user_id"] == int(mkc_user_id):
        # mkc_player_id = player["player_id"]
        # break
    # else:
        # continue
# if mkc_player_id != None:
    # return mkc_player_id
# else:
    # return -1
